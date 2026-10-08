"""Independent subset enumeration, certificate bounds and progress-cover audit.

Does not import the solver, compiler, witness checker or checkpoint implementation.
"""
from fractions import Fraction as Q
import hashlib,json,pathlib,subprocess,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def masks(row):
 n=row['n'];ws=[0]*(1<<n);ps=ws.copy();vs=ws.copy()
 for m in range(1,1<<n):
  bit=m&-m;j=bit.bit_length()-1;prev=m^bit
  ws[m]=ws[prev]+row['weights'][j];ps[m]=ps[prev]+row['profits'][j];vs[m]=vs[prev]+row['slopes'][j]
 return ws,ps,vs,[m for m in range(1<<n) if ws[m]<=row['capacity']]
def run(full=True):
 start=time.perf_counter();seal=json.loads((ROOT/'Freeze.json').read_text())
 for p,d in seal['files'].items():assert h(ROOT/p)==d,p
 rows={r['case_id']:r for r in json.loads((ROOT/'Inputs.json').read_text())};cache={};bestcache={};unique={};counts=dict(answer_checks=0,endpoint_checks=0,progress_enclosures=0,feasible_coverage_checks=0,receipt_controls=0,witness_controls=0,checkpoint_controls=0)
 def arrays(row):
  key=json.dumps([row[k] for k in ['weights','profits','slopes','capacity']])
  if key not in cache:cache[key]=masks(row)
  return cache[key]
 def best(row,t):
  t=Q(t);key=(row['case_id'],t)
  if key not in bestcache:
   ws,ps,vs,feasible=arrays(row);bestcache[key]=max(ps[m]+t*vs[m] for m in feasible)
  return bestcache[key]
 def answer(row,t,m):
  ws,ps,vs,feasible=arrays(row);assert 0<=m<len(ws) and ws[m]<=row['capacity'] and ps[m]+Q(t)*vs[m]==best(row,t);counts['answer_checks']+=1
 def record(row,r):
  ws,ps,vs,feasible=arrays(row);t=Q(*r['time']);d=t.denominator;q=[d*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
  assert Q(r['objective'],d)==best(row,t);answer(row,t,r['packing'])
  p=ROOT/r.get('proof_path',r.get('path'));assert h(p)==r['proof_sha256'];unique[r['proof_sha256']]=p
  lines=p.read_text().splitlines();assert lines[:2]==['VER 1.0',f'VAR {row["n"]}']
  objline=lines[6].split();assert objline[0]==str(sum(x!=0 for x in q))
  parsed={int(objline[k]):int(objline[k+1]) for k in range(1,len(objline),2)};assert parsed=={j:v for j,v in enumerate(q) if v}
  assert f'capacity L {row["capacity"]} '+str(row['n'])+' '+' '.join(f'{j} {w}' for j,w in enumerate(row['weights'])) in lines
  source=r['source'];assert source['empty'];proof=source['proof'];coverage={m:0 for m in feasible}
  for f,u,res,a,b,num in proof:
   assert not f&u and f|u<(1<<row['n']) and res==row['capacity']-ws[f] and res>=0 and a>=0 and b>0
   calc=b*sum(q[j] for j in range(row['n']) if f>>j&1)+a*res+sum(max(0,b*q[j]-a*row['weights'][j]) for j in range(row['n']) if u>>j&1)
   assert calc==num and num//b<=r['objective']
   for m in feasible:
    if m&f==f and m&~(f|u)==0:
     assert sum(q[j] for j in range(row['n']) if m>>j&1)<=num//b;coverage[m]+=1
  assert all(coverage.values());counts['feasible_coverage_checks']+=len(feasible)
  if 'witness_path' in r:
   wp=ROOT/r['witness_path'];assert h(wp)==r['witness_sha256'];w=json.loads(wp.read_text())
   assert w['model']=={k:row[k] for k in ['n','weights','capacity','profits','slopes']}
   assert w['time']==r['time'] and w['packing']==r['packing'] and w['objective']==r['objective']
   assert w['cells']==[[f,u,a,b] for f,u,res,a,b,num in proof]
  counts['endpoint_checks']+=1
 workers=json.loads((ROOT/'Results.json').read_text())
 assert len(workers)==116
 for path in workers:
  row=rows[path['case_id']];r=path['result'];st=path['stage'];assert r['status']=='complete'
  for rec in r.get('records',[]):record(row,rec)
  if st==96:
   assert len(r['tests'])==11
   for c in r['tests']:assert c['accepted']==(c['label'] in ['same-model','exact-model-restored'])
   counts['receipt_controls']+=len(r['tests'])
  elif st==97:
   last=Q(0)
   for bundle in r['bundles']:
    a,b=Q(*bundle['left']),Q(*bundle['right']);assert a==last and a<b;last=b
    answer(row,a,bundle['packing']);answer(row,b,bundle['packing'])
   assert last==row['end']
   for c in r['claims']:answer(row,Q(*c['time']),c['packing'])
  elif st==98:
   assert len(r['controls'])==12 and all(x['rejected'] for x in r['controls']);counts['witness_controls']+=12
   assert r['compact_bytes']==sum(x['witness_bytes'] for x in r['records']) and r['vipr_bytes']==sum(x['bytes'] for x in r['records'])
  elif st==99:
   t=Q(1,3);ws,ps,vs,feasible=arrays(row);opt=best(row,t)*3;prevlo=0;prevhi=None
   for s in r['snapshots']:
    low=3*ps[s['packing']]+vs[s['packing']];assert low==s['lower'] and low<=opt<=s['upper'] and s['gap']==s['upper']-low
    assert low>=prevlo and (prevhi is None or s['upper']<=prevhi);prevlo=low;prevhi=s['upper']
    finished={m for d,m in s['processed'] if d==row['n'] and ws[m]<=row['capacity']}
    for m in feasible:
     assert int(m in finished)+sum((m&((1<<d)-1))==prefix for d,prefix in s['todo'])==1
    assert (s['status']=='optimal')==(s['gap']==0);counts['progress_enclosures']+=1
   assert not r['snapshots'][-1]['todo'] and r['resumed_nodes']==r['cold_nodes']
   assert len(r['controls'])==6 and all(x['rejected'] and x['status']=='invalid' for x in r['controls']);counts['checkpoint_controls']+=6
   assert r['aborted_source']['empty'] and r['aborted_source']['construction_steps']==1;record(row,r['fallback'])
  elif st==100:
   assert len(r['observations'])==len(r['packings'])
   for t,m in zip(r['observations'],r['packings']):answer(row,t,m)
   assert r['algorithm_cpu']>=r['parent_cpu'] and r['algorithm_cpu']>=r['child_cpu']
 formal=json.loads((ROOT/'Formal-check.json').read_text());assert formal['status']=='checked' and formal['rejected_statement']['exit_code']!=0
 assert all(x['exit_code']==0 and 'sorryAx' not in x['stdout'] for x in formal['records'])
 valid=invalid=0
 if full:
  binary=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
  with tempfile.TemporaryDirectory(dir='/tmp',prefix='maths96-audit-') as td:
   for sha,p in unique.items():
    o=subprocess.run([str(binary),str(p)],capture_output=True,text=True,timeout=10);assert o.returncode==0;valid+=1
    lines=p.read_text().splitlines();tokens=lines[-1].split();tokens[2]=str(int(tokens[2])-1);lines[-1]=' '.join(tokens);bad=pathlib.Path(td)/(sha+'.vipr');bad.write_text('\n'.join(lines)+'\n')
    o=subprocess.run([str(binary),str(bad)],capture_output=True,text=True,timeout=10);assert o.returncode!=0;invalid+=1
 result=dict(passed=True,workers=len(workers),inputs=len(rows),unique_valid_vipr=valid,unique_false_bounds_rejected=invalid,**counts,audit_wall=time.perf_counter()-start)
 (ROOT/'Audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
if __name__=='__main__':run()
