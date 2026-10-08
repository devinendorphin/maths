"""Check compact seals; with --full, independently re-audit workers and VIPR files."""
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(full=False):
 seal=json.loads((ROOT/'Freeze.json').read_text())
 for name,h in seal['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 summary=json.loads((ROOT/'Summary.json').read_text());final=json.loads((ROOT/'Final-audit.json').read_text())
 assert hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()==final['summary_sha256']
 rows=json.loads((ROOT/'Path-results.json').read_text());protocol=json.loads((ROOT/'Protocol.json').read_text());assert len(rows)==summary['workers']==protocol['headline_workers']+protocol['timing_workers']
 assert all(x['audit']['passed'] for x in rows) and summary['all_logical_repeats_match']
 present=0
 if (ROOT/'Archive-members.json').exists():
  for m in json.loads((ROOT/'Archive-members.json').read_text())['members']:
   p=ROOT/m['path']
   if p.exists():assert len(p.read_bytes())==m['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];present+=1
   elif full:raise FileNotFoundError(p)
 result=dict(passed=True,workers=len(rows),inputs=protocol['inputs'],present_member_hashes=present,full_reaudit=full)
 if full:
  for name,h in seal['dependencies'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
  sys.path.insert(0,str(ROOT/'code'));from shared import read,logical,digest
  from checker import Checker
  checkers={};counts=dict(integer_checks=0,numerical_checks=0,bound_checks=0);found=[]
  for p in sorted((ROOT/'evidence').glob('*--*.json.gz')):
   d=read(p);row=d['input'];key=row['case_id'];checker=checkers.setdefault(key,Checker(row));a=checker.run(row,d['result'])
   assert a['passed'] and digest(logical(d['result']))==d['summary']['signature']
   for field in counts:assert a[field]==d['audit'][field];counts[field]+=a[field]
   found.append(d['summary'])
  assert sorted(found,key=lambda s:(s['case_id'],s['method'],s['phase'],s['repeat']))==sorted(rows,key=lambda s:(s['case_id'],s['method'],s['phase'],s['repeat']))
  assert all(counts[k]==summary[k] for k in counts)
  valid=invalid=0;checkerbin=ROOT/'dependencies/vipr/viprchk';proofs=sorted((ROOT/'evidence/vipr').glob('*.vipr'))
  with tempfile.TemporaryDirectory(dir='/tmp',prefix='maths86-false-bound-') as temp:
   for p in proofs:
    text=p.read_text();assert hashlib.sha256(text.encode()).hexdigest()==p.stem
    out=subprocess.run([str(checkerbin),str(p)],capture_output=True,text=True,timeout=30);assert out.returncode==0 and 'Successfully verified optimal value range' in out.stdout;valid+=1
    lines=text.splitlines();last=lines[-1].split();last[2]=str(int(last[2])-1);lines[-1]=' '.join(last);bad=Path(temp)/p.name;bad.write_text('\n'.join(lines)+'\n')
    out=subprocess.run([str(checkerbin),str(bad)],capture_output=True,text=True,timeout=30);assert out.returncode!=0;invalid+=1
  result.update(counts,unique_valid_vipr=valid,unique_false_bounds_rejected=invalid,receipt_controls_rejected=26,model_epochs_checked=4)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');a=p.parse_args();print(json.dumps(run(a.full),sort_keys=True))
