"""Independent exhaustive original-problem audit; no imports of producer/checker/SCIP."""
import hashlib,json,pathlib,subprocess,time
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
cache={};counts=dict(answer_checks=0,valid_dp=0,invalid_dp_rejected=0,vipr_valid=0,vipr_weakened_rejected=0)
def oracle(row,t):
 t=Fraction(t);key=json.dumps([row['weights'],row['capacity'],row['profits'],row['slopes'],str(t)])
 if key not in cache:
  q=[t.denominator*p+t.numerator*s for p,s in zip(row['profits'],row['slopes'])];best=0
  weights=[0]*(1<<row['n']);values=[0]*(1<<row['n'])
  for mask in range(1,1<<row['n']):
   bit=mask&-mask;i=bit.bit_length()-1;previous=mask^bit
   weights[mask]=weights[previous]+row['weights'][i];values[mask]=values[previous]+q[i]
   if weights[mask]<=row['capacity']:best=max(best,values[mask])
  cache[key]=best
 return cache[key]
def answer(row,t,mask,obj=None):
 t=Fraction(t);assert type(mask)==int and 0<=mask<(1<<row['n'])
 assert sum(v for i,v in enumerate(row['weights']) if mask>>i&1)<=row['capacity']
 value=sum((t.denominator*p+t.numerator*s) for i,(p,s) in enumerate(zip(row['profits'],row['slopes'])) if mask>>i&1)
 assert value==oracle(row,t)
 if obj is not None:assert value==obj
 counts['answer_checks']+=1

def table_valid(row,t,c):
 try:
  t=Fraction(t);q=[t.denominator*p+t.numerator*s for p,s in zip(row['profits'],row['slopes'])]
  if c['status']!='complete' or any(c[k]!=row[k] for k in ['weights','capacity','profits','slopes']) or c['coefficients']!=q or c['time']!=[t.numerator,t.denominator]:return False
  a=c['table'];cap=row['capacity']
  if len(a)!=row['n']+1 or any(len(x)!=cap+1 for x in a) or any(a[0]):return False
  for i,w in enumerate(row['weights']):
   for b in range(cap+1):
    choices=[a[i][b]]
    if b>=w:choices.append(a[i][b-w]+q[i])
    if type(a[i+1][b])!=int or a[i+1][b]!=max(choices):return False
  mask=c['packing']
  return 0<=mask<(1<<row['n']) and sum(w for i,w in enumerate(row['weights']) if mask>>i&1)<=cap and c['objective']==a[-1][-1]==sum(v for i,v in enumerate(q) if mask>>i&1)==oracle(row,t)
 except (KeyError,ValueError,TypeError,IndexError):return False

def run():
 start=time.perf_counter();rows={r['case_id']:r for r in json.loads((ROOT/'Inputs.json').read_text())};results=json.loads((ROOT/'Results.json').read_text());proofs={};streams=set();valid=invalid=observations=0
 def check(row,t,c):
  nonlocal valid
  assert table_valid(row,t,c);answer(row,t,c['packing'],c['objective']);valid+=1
 def stream(row,ref):
  nonlocal observations
  p=ROOT/ref['evidence'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['evidence_sha256'];data=json.loads(p.read_text());assert data['model']=={k:row[k] for k in ['n','weights','capacity','profits','slopes']};assert data['packings']==ref['packings'];assert len(data['packings'])==len(data['observations'])
  for t,mask in zip(data['observations'],data['packings']):answer(row,t,mask);observations+=1
  if ref['evidence'] in streams:return
  streams.add(ref['evidence'])
  for c in data['dp_proofs']:check(row,Fraction(*c['time']),c)
  for w in data['windows']:
   lo,hi=Fraction(*w['left']),Fraction(*w['right']);assert lo<=hi
   answer(row,lo,w['packing']);answer(row,hi,w['packing'])
   assert any(Fraction(*c['time'])==lo and c['packing']==w['packing'] for c in data['dp_proofs'])
   assert any(Fraction(*c['time'])==hi and c['packing']==w['packing'] for c in data['dp_proofs'])
  if 'vipr' in data:
   v=data['vipr'];assert v['status']=='complete'
   for c in v['records']:
    p=ROOT/c['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['proof_sha256'];proofs[c['proof_sha256']]=p;answer(row,Fraction(*c['time']),c['packing'],c['objective'])
   for w in v['bundles']:answer(row,Fraction(*w['left']),w['packing']);answer(row,Fraction(*w['right']),w['packing'])
 stages={}
 for r in results:
  stage=r['stage'];stages[str(stage)]=stages.get(str(stage),0)+1;row=rows[r['case_id']];assert r['cpu']>=0 and r['wall']>=0
  if stage==113:
   assert len(r['requests'])==len(r['decisions'])==20
   for request,decision in zip(r['requests'],r['decisions']):
    expected=table_valid(request['row'],request['time'],request['certificate']);assert expected==decision==request['expected']
    if expected:check(request['row'],request['time'],request['certificate'])
    else:invalid+=1
  if stage==114:
   c=json.loads((ROOT/r['certificate']).read_text());check(row,4,c);assert r['exact_objective']==oracle(row,4);assert abs(sum(r['components'].values())-r['component_sum'])<1e-10 and r['component_sum']<=r['cpu']+1e-5
  if stage in [115,116]:
   check(row,Fraction(*r['time']),r['certificate'])
   if stage==115:assert r['bytes']<=r['storage_cap_bytes'] and r['certificate']['cells']<=r['cell_cap']
  if stage in [117,118]:stream(row,r['route'])
  if stage==119:
   from collections import OrderedDict
   cache=OrderedDict();evictions=hits=0
   for event in r['history']:
    t=event['time'];hit=t in cache;assert event['hit']==hit
    if hit:cache.pop(t);hits+=1
    cache[t]=True
    if len(cache)>2:cache.popitem(last=False);evictions+=1
    assert len(cache)==event['entries']<=2 and event['serialized_bytes']>0
    answer(row,t,event['packing'],event['objective'])
   assert r['hits']==hits and r['evictions']==evictions and r['changed_model_miss'];check(r['changed_model'],0,r['changed_certificate'])
  if stage==120:
   check(row,4,r['certificate']);assert r['restored_accepted'] and len(r['controls'])==6
   for c in r['controls']:
    identity=c['identity']==r['dependency'];scope=c['changed_model'].get('domain','binary')=='binary' and c['changed_model'].get('objective_class','affine')=='affine' and not any(c['changed_model'].get('quadratic',[]));decision=identity and scope and table_valid(c['changed_model'],c['time'],r['certificate']);assert decision==c['accepted']==False;invalid+=1
 expected={'113':2,'114':5,'115':15,'116':42,'117':60,'118':150,'119':5,'120':5};assert stages==expected
 train=json.loads((ROOT/'Training.json').read_text());assert train['heldout_used']==False and all(rows[x['case_id']]['split']=='training' for x in train['records'])
 for r in train['records']:stream(rows[r['case_id']],r)
 for r in results:
  if r['stage']==117 and r['policy']=='trained':assert r['route']['width']==train['window_width']
  if r['stage']==118 and r['method']=='policy':assert r['selected']==train['density_policy'][r['density']]
 binary=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
 import tempfile
 with tempfile.TemporaryDirectory() as tmp:
  for sha,p in proofs.items():
   checked=subprocess.run([str(binary),str(p)],capture_output=True,text=True,timeout=10);assert checked.returncode==0 and 'Successfully verified optimal value range' in checked.stdout;counts['vipr_valid']+=1
   lines=p.read_text().splitlines();tokens=lines[-1].split();tokens[2]=str(int(tokens[2])-1);lines[-1]=' '.join(tokens);bad=pathlib.Path(tmp)/(sha+'.vipr');bad.write_text('\n'.join(lines)+'\n');checked=subprocess.run([str(binary),str(bad)],capture_output=True,text=True,timeout=10);assert checked.returncode!=0;counts['vipr_weakened_rejected']+=1
 availability=json.loads((ROOT/'Availability.json').read_text());assert availability['112']['status']=='unsupported' and availability['112']['native_scip_certificates']==0
 report=dict(passed=True,workers=len(results),heldout_models=5,training_models=2,control_models=1,stage_counts=stages,dp_certificates_checked=valid,invalid_admissions_rejected=invalid,stream_observations_checked=observations,answer_checks=counts['answer_checks'],distinct_oracle_queries=len(cache) if isinstance(cache,dict) else 0,vipr_valid=counts['vipr_valid'],vipr_weakened_rejected=counts['vipr_weakened_rejected'],unsupported=[112],wall=time.perf_counter()-start)
 # oracle cache is module-level; local LRU variable above is separate.
 report['distinct_oracle_queries']=len(globals()['cache'])
 (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':run()
