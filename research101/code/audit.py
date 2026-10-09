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

def load_cert(ref):
 p=ROOT/ref['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['sha256'];return json.loads(p.read_text())
def run():
 start=time.perf_counter();rows={r['case_id']:r for r in json.loads((ROOT/'Inputs.json').read_text())};results=json.loads((ROOT/'Results.json').read_text());stages={};unique={}
 for r in results:
  stage=r['stage'];stages[str(stage)]=stages.get(str(stage),0)+1;row=r.get('model',rows[r['case_id']]);t=Fraction(*r.get('time',[4,1]))
  assert r['cpu']>=0 and r['wall']>=0
  refs=[r[k] for k in ['certificate','fallback_certificate'] if k in r]+r.get('dp_certificates',[])
  if isinstance(r.get('certificates'),list):refs+=r['certificates']
  for ref in refs:
   cert=load_cert(ref);ct=Fraction(*cert['time']);assert table_valid(row,ct,cert);answer(row,ct,cert['packing'],cert['objective']);counts['valid_dp']+=1
  if stage==102:answer(row,t,r['solver']['packing'],r['solver']['objective']);assert r['solver']['status']=='optimal'
  if stage==103:assert oracle(row,4)==oracle(rows[r['case_id']],4)
  if stage==106:
   assert len(r['controls'])==6
   for control in r['controls']:assert control['rejected'] and not table_valid(row,t,load_cert(control['certificate']));counts['invalid_dp_rejected']+=1
  if stage==107:assert r['attempt']['status']=='incomplete' and r['attempt']['required_cells']>r['attempt']['cell_cap']
  if stage==108:
   original=rows[r['case_id']];assert r['old_capacity']==original['capacity'] and row['capacity']!=original['capacity']
   assert r['old_objective']==oracle(original,4) and r['old_rejected']
   if r['subset_transfer']:
    assert row['capacity']<=original['capacity'];answer(row,4,r['old_packing'],r['old_objective'])
  if stage==109:
   assert r['answers']==[oracle(row,t) for t in r['observations']]
   assert r['cache_hits']==(12 if r['variant']=='memo' else 0)
  if stage==110:
   for t,mask in zip(r['observations'],r['packings']):answer(row,t,mask)
   for t,solver in zip(r['observations'],r.get('solvers',[])):answer(row,t,solver['packing'],solver['objective'])
   if r['method'].startswith('vipr'):
    data=json.loads((ROOT/r['evidence']).read_text());assert data['status']=='complete'
    for record in data['records']:
     p=ROOT/record['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==record['proof_sha256'];unique[record['proof_sha256']]=p;answer(row,Fraction(*record['time']),record['packing'],record['objective'])
    for bundle in data['bundles']:
     answer(row,Fraction(*bundle['left']),bundle['packing']);answer(row,Fraction(*bundle['right']),bundle['packing'])
 assert set(map(int,stages))==set(range(101,111))
 binary=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
 import tempfile
 with tempfile.TemporaryDirectory() as tmp:
  for sha,p in unique.items():
   o=subprocess.run([str(binary),str(p)],capture_output=True,text=True,timeout=10);assert o.returncode==0 and 'Successfully verified optimal value range' in o.stdout;counts['vipr_valid']+=1
   lines=p.read_text().splitlines();tokens=lines[-1].split();tokens[2]=str(int(tokens[2])-1);lines[-1]=' '.join(tokens);bad=pathlib.Path(tmp)/(sha+'.vipr');bad.write_text('\n'.join(lines)+'\n')
   o=subprocess.run([str(binary),str(bad)],capture_output=True,text=True,timeout=10);assert o.returncode!=0;counts['vipr_weakened_rejected']+=1
 result=dict(passed=True,workers=len(results),models=len(rows),stages=stages,**counts,distinct_oracle_queries=len(cache),wall=time.perf_counter()-start)
 (ROOT/'Audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
