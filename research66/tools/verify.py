"""Check compact seals, or independently re-audit every worker and external proof."""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(full=False):
 seal=json.loads((ROOT/'Freeze.json').read_text())
 for name,h in seal['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 summary=json.loads((ROOT/'Summary.json').read_text());final=json.loads((ROOT/'Final-audit.json').read_text())
 assert hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()==final['summary_sha256']
 protocol=json.loads((ROOT/'Protocol.json').read_text());rows=json.loads((ROOT/'Path-results.json').read_text());expected=protocol['headline_workers']+protocol['timing_workers']
 assert len(rows)==expected==summary['workers'];groups=defaultdict(list)
 for s in rows:
  assert s['audit']['passed'];groups[(s['case_id'],s['method'])].append(s)
 for key,samples in groups.items():
  if all(s['status']=='complete' for s in samples):assert len({s['signature'] for s in samples})==1,key
 assert len({s['case_id'] for s in rows if s['status']=='complete'})==protocol['input_records']
 present=0;manifest_path=ROOT/'Archive-members.json'
 if manifest_path.exists():
  for m in json.loads(manifest_path.read_text())['members']:
   p=ROOT/m['path']
   if p.exists():assert p.stat().st_size==m['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];present+=1
   elif full:raise FileNotFoundError(p)
 result=dict(passed=True,workers=expected,inputs=protocol['input_records'],all_inputs_have_complete_answers=True,present_member_hashes=present,full_reaudit=full)
 if full:
  for name,h in seal['dependencies'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
  sys.path.insert(0,str(ROOT/'code'));from shared import read,logical,digest,value,vipr_adapter
  import audit as independent
  checkers={};count=integer=endpoint=noncanonical=0;scaled=defaultdict(list)
  for p in sorted((ROOT/'evidence').glob('*--*.json.gz')):
   r=read(p);row=r['input'];key=row['case_id']
   if key not in checkers:checkers[key]=independent.Auditor(row)
   checked=checkers[key].check(r['result']);assert checked['passed'];assert digest(logical(r['result']))==r['summary']['signature']
   for field in ('integer_checks','rational_checks','primary_optimal_noncanonical'):assert checked[field]==r['audit'][field]
   integer+=checked['integer_checks'];endpoint+=checked['rational_checks'];noncanonical+=checked['primary_optimal_noncanonical'];count+=1
   if r['result']['status']=='complete' and r['result']['kind']=='real':
    intervals=r['result']['intervals'];assert Fraction(*intervals[0]['left'])==0 and Fraction(*intervals[-1]['right'])==row['end']
    for a,b in zip(intervals,intervals[1:]):assert Fraction(*a['right'])==Fraction(*b['left'])
   if row['stage']==67 and r['summary']['phase']=='headline':scaled[(row['seed'],r['summary']['method'])].append(r['result']['packings'])
  assert count==expected
  for packings in scaled.values():assert len(packings)==3 and all(x==packings[0] for x in packings)
  valid=invalid=references=bundles=proof_integer=0
  for p in sorted((ROOT/'evidence').glob('74-proof-*.json.gz')):
   data=read(p);row=next(x for x in read(ROOT/'Inputs.json') if x['case_id']==data['case_id']);checker=checkers[row['case_id']];records=data['records'];references+=len(records)
   mode='reuse' if p.name.endswith('-reuse.json.gz') else 'fresh';fresh=0
   for i,r in enumerate(records):
    t=Fraction(*r['time']);q=[t.denominator*a+t.numerator*b for a,b in zip(row['profits'],row['slopes'])]
    assert value(row['weights'],r['packing'])<=row['capacity'] and value(q,r['packing'])==checker.optimum(t)[0]==r['info']['scaled_objective']
    assert r['domain']==digest([row['n'],row['weights'],row['capacity']]) and r['coefficients']==digest([row['profits'],row['slopes']])
    if 'reused_from' in r:
     old=records[r['reused_from']];assert r['reused_from']<i and old['time']==r['time'] and old['info']['scaled_objective']==r['info']['scaled_objective'];continue
    text,info=vipr_adapter.certificate(row,t,r['packing'],r['source']['proof']);assert info==r['info']
    path=ROOT/'evidence/vipr'/f'{row["case_id"]}-{mode}--{i}.vipr';assert path.read_text()==text
    checked=subprocess.run([str(ROOT/'dependencies/vipr/viprchk'),str(path)],capture_output=True,text=True,timeout=30);assert checked.returncode==0;valid+=1;fresh+=1
    path=path.with_name(path.stem+'-invalid.vipr');checked=subprocess.run([str(ROOT/'dependencies/vipr/viprchk'),str(path)],capture_output=True,text=True,timeout=30);assert checked.returncode!=0;invalid+=1
   last=Fraction(0)
   for b in data['bundles']:
    left,right=[records[j] for j in b['endpoints']];l,h=Fraction(*b['left']),Fraction(*b['right']);assert l==last and l<h;last=h
    assert left['time']==b['left'] and right['time']==b['right'] and left['packing']==right['packing']==b['packing'];checks=0
    for t in range((l.numerator+l.denominator-1)//l.denominator,h.numerator//h.denominator+1):assert value(row['profits'],b['packing'])+t*value(row['slopes'],b['packing'])==checker.optimum(t)[0];checks+=1
    assert checks==b['integer_checks'];proof_integer+=checks;bundles+=1
   assert last==row['end'] and len(data['rejected_scopes'])==6
  assert valid==invalid==sum(p['certificates'] for p in summary['proofs'])
  assert integer+proof_integer==summary['integer_checks'] and endpoint==summary['rational_checks']
  result.update(vipr_valid=valid,vipr_invalid_rejected=invalid,endpoint_references=references,interval_bundles=bundles,integer_checks=integer+proof_integer,rational_checks=endpoint,primary_optimal_noncanonical=noncanonical,matched_scale_packings_identical=True)
 print(json.dumps(result))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args();run(args.full)
