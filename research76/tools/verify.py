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
  checkers={};count=integer=endpoint=noncanonical=0
  splits=rewrites=0;depth_max=0;split_metrics=[]
  for p in sorted((ROOT/'evidence').glob('*--*.json.gz')):
   r=read(p);row=r['input'];key=row['case_id']
   if key not in checkers:checkers[key]=independent.Auditor(row)
   checked=checkers[key].check(r['result']);assert checked['passed'];assert digest(logical(r['result']))==r['summary']['signature']
   for field in ('integer_checks','rational_checks','primary_optimal_noncanonical'):assert checked[field]==r['audit'][field]
   log=r['result'].get('split_log',[])
   if log:
    qmap={tuple(q['time']):q for q in r['result']['queries'] if q['side']==1};depth={(0,row['end']):0};maximum=changed=0
    for item in log:
     l,h,x=item['left'],item['right'],item['query'];assert l<x<h
     a,b=qmap[(l,1)],qmap[(h,1)];mid=(l+h)//2;kind=r['result']['kind']
     if kind in ('cross','balanced') and a['slope']!=b['slope']:
      crossing=Fraction(a['intercept']-b['intercept'],b['slope']-a['slope']);mid=max(l+1,min(h-1,crossing.numerator//crossing.denominator))
     assert item['proposed']==mid
     if kind=='balanced' and not l+(h-l)//4<=mid<=h-(h-l)//4:mid=(l+h)//2
     assert x==mid and (x,1) in qmap;changed+=x!=item['proposed'];d=depth[(l,h)];maximum=max(maximum,d+1);depth[(l,x)]=depth[(x,h)]=d+1
    splits+=len(log);rewrites+=changed;depth_max=max(depth_max,maximum)
    if r['summary']['phase']=='headline':split_metrics.append(dict(stage=row['stage'],case_id=key,method=r['summary']['method'],splits=len(log),max_split_depth=maximum,balance_replacements=changed,oracle_calls=r['result']['oracle_calls']))
   integer+=checked['integer_checks'];endpoint+=checked['rational_checks'];noncanonical+=checked['primary_optimal_noncanonical'];count+=1
   if r['result']['status']=='complete' and r['result']['kind']=='real':
    intervals=r['result']['intervals'];assert Fraction(*intervals[0]['left'])==0 and Fraction(*intervals[-1]['right'])==row['end']
    for a,b in zip(intervals,intervals[1:]):assert Fraction(*a['right'])==Fraction(*b['left'])
  assert count==expected
  valid=invalid=references=bundles=proof_integer=0
  from scope_cache import BoundCache
  for p in sorted((ROOT/'evidence').glob('proof-*.json.gz')):
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
  controls=read(ROOT/'Cache-tests.json');rejected=accepted=0
  for record in controls:
   assert record['passed'] and record['rejected']==12 and record['accepted_same_model']==2
   row=next(x for x in read(ROOT/'Inputs.json') if x['case_id']==record['case_id']);proof=read(ROOT/'evidence'/('proof-'+row['case_id']+'-reuse.json.gz'));q=proof['records'][0];t=Fraction(*q['time']);mask=q['packing'];cache=BoundCache();cache.put(row,t,0,q['info']['scaled_objective'],q['valid']);assert cache.get(row,t,mask)==0
   for changed in (dict(row,capacity=row['capacity']+1),dict(row,weights=[row['weights'][0]+1]+row['weights'][1:]),dict(row,profits=[row['profits'][0]+1]+row['profits'][1:]),dict(row,slopes=[row['slopes'][0]+1]+row['slopes'][1:]),dict(row,n=row['n']+1)):assert cache.get(changed,t,mask) is None
   assert cache.get(row,t+1,mask) is None
   for bad in (-1,1<<row['n'],(1<<row['n'])-1):assert cache.get(row,t,bad) is None
   bad=next(m for m in range(1<<row['n']) if value(row['weights'],m)<=row['capacity'] and t.denominator*value(row['profits'],m)+t.numerator*value(row['slopes'],m)!=q['info']['scaled_objective']);assert cache.get(row,t,bad) is None
   entry=cache.entries[cache.key(row,t)];entry['accepted']=False;assert cache.get(row,t,mask) is None;entry['accepted']=True;entry['key']=('wrong','wrong',t);assert cache.get(row,t,mask) is None
   cache.put(row,t,0,q['info']['scaled_objective'],True);assert cache.get(dict(row,case_id='alias-label'),t,mask)==0;rejected+=12;accepted+=2
  result.update(cache_scope_rejections=rejected,cache_valid_hits=accepted,query_split_checks=splits,balance_replacements=rewrites,max_split_depth=depth_max)
  if not (ROOT/'Split-metrics.json').exists():(ROOT/'Split-metrics.json').write_text(json.dumps(split_metrics,sort_keys=True,separators=(',',':'))+'\n')
  assert integer+proof_integer==summary['integer_checks'] and endpoint==summary['rational_checks']
  result.update(vipr_valid=valid,vipr_invalid_rejected=invalid,endpoint_references=references,interval_bundles=bundles,integer_checks=integer+proof_integer,rational_checks=endpoint,primary_optimal_noncanonical=noncanonical,lean_counters_replayed=True)
 print(json.dumps(result))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args();run(args.full)
