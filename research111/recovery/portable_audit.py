"""Independent finite-model, original-file, interval and partial-bound audit.

Imports no producer, optimizer, admission checker or cache implementation.
"""
from fractions import Fraction as Q
import hashlib,json,pathlib,subprocess,tempfile,time,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(full=True):
 start=time.perf_counter();seal=json.loads((ROOT/'Freeze.json').read_text())
 for p,d in seal['files'].items():assert h(ROOT/p)==d,p
 # Original SDK is unavailable; the recovery harness identifies the new checker separately.
 rows={x['case_id']:x for x in json.loads((ROOT/'Inputs.json').read_text())};arrays={};bestcache={};certcache=set();vipr={};pb={}
 counts=dict(answer_checks=0,point_records=0,feasible_cover_checks=0,interval_endpoint_checks=0,snapshot_decisions=0,partial_bounds=0)
 def model(row):return tuple(json.dumps(row[k]) for k in ['weights','profits','slopes','capacity'])
 def values(row):
  key=model(row)
  if key not in arrays:
   n=row['n'];w=[0]*(1<<n);p=w.copy();v=w.copy()
   for m in range(1,1<<n):
    bit=m&-m;j=bit.bit_length()-1;s=m^bit;w[m]=w[s]+row['weights'][j];p[m]=p[s]+row['profits'][j];v[m]=v[s]+row['slopes'][j]
   arrays[key]=(w,p,v,[m for m in range(1<<n) if w[m]<=row['capacity']])
  return arrays[key]
 def best(row,t):
  t=Q(t);key=(model(row),t)
  if key not in bestcache:
   w,p,v,feas=values(row);bestcache[key]=max(p[m]+t*v[m] for m in feas)
  return bestcache[key]
 def answer(row,t,m):
  t=Q(t);w,p,v,feas=values(row);assert 0<=m<len(w) and w[m]<=row['capacity'] and p[m]+t*v[m]==best(row,t);counts['answer_checks']+=1
 def record(row,r):
  t=Q(*r['time']);answer(row,t,r['packing']);assert Q(r['objective'],t.denominator)==best(row,t);counts['point_records']+=1
  q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
  path=ROOT/r.get('proof_path',r.get('path'));assert h(path)==r['proof_sha256']
  if 'formula_path' in r:
   formula=ROOT/r['formula_path'];assert h(formula)==r['formula_sha256']
   expected='min:'+''.join(f' {-x} x{j}' for j,x in enumerate(q))+' ;\n'+''.join(f'-{w} x{j} ' for j,w in enumerate(row['weights']))+f'>= -{row["capacity"]} ;\n'
   assert formula.read_text()==expected
   text=path.read_text();bounds=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);assert bounds and int(bounds[1])==int(bounds[2])==-r['objective']
   original=next(l for l in text.splitlines() if l.startswith('soli ')).split()[1:];assigned=[x for x in original if re.fullmatch('~?x\d+',x)]
   assert len(assigned)==row['n'];m=sum(1<<int(x[1:]) for x in assigned if x.startswith('x'));assert m==r['packing']
   pb[(r['formula_sha256'],r['proof_sha256'])]=(formula,path)
  else:
   vipr[r['proof_sha256']]=path
   text=path.read_text();lines=text.splitlines();terms=lines[6].split();actual={int(terms[i]):int(terms[i+1]) for i in range(1,len(terms),2)};assert actual=={j:x for j,x in enumerate(q) if x}
   assert f'capacity L {row["capacity"]} '+str(row['n'])+' '+' '.join(f'{j} {w}' for j,w in enumerate(row['weights'])) in lines
   key=(model(row),t,r['proof_sha256'])
   if key not in certcache:
    ws,ps,vs,feas=values(row);covered={m:False for m in feas}
    for f,u,res,a,b,num in r['source']['proof']:
     assert not f&u and f|u<(1<<row['n']) and res==row['capacity']-ws[f] and res>=0 and a>=0 and b>0
     calculated=b*sum(q[j] for j in range(row['n']) if f>>j&1)+a*res+sum(max(0,b*q[j]-a*row['weights'][j]) for j in range(row['n']) if u>>j&1)
     assert calculated==num and num//b<=r['objective']
     for m in feas:
      if m&f==f and m&~(f|u)==0:assert t.denominator*ps[m]+t.numerator*vs[m]<=num//b;covered[m]=True
    assert all(covered.values());counts['feasible_cover_checks']+=len(feas);certcache.add(key)
   if 'witness_path' in r:
    wp=ROOT/r['witness_path'];assert h(wp)==r['witness_sha256'];w=json.loads(wp.read_text());assert w['model']=={k:row[k] for k in ['n','weights','capacity','profits','slopes']};assert w['time']==r['time'] and w['objective']==r['objective'] and w['packing']==r['packing']
    assert w['cells']==[[f,u,a,b] for f,u,res,a,b,num in r['source']['proof']]
 workers=json.loads((ROOT/'Results.json').read_text());assert len(workers)==300
 for worker in workers:
  row=rows[worker['case_id']];r=worker['result'];st=worker['stage'];assert r['status']=='complete'
  for rec in r['records']:record(row,rec)
  for c in r['claims']:answer(row,Q(*c['time']) if isinstance(c['time'],list) else c['time'],c['packing'])
  for a,b,m in r.get('intervals',[]):
   left,right=Q(*a),Q(*b);assert 0<=left<right<=row['end'];answer(row,left,m);answer(row,right,m);counts['interval_endpoint_checks']+=2
  if st==106:
   assert len(r['tests'])==14
   allowed={'same-model','same-model-copy','captured-facts-survive-disk-rewrite','captured-facts-survive-diagnostic-rewrite'}
   for c in r['tests']:assert c['accepted']==(c['label'] in allowed)
   counts['snapshot_decisions']+=14
  if st==108:
   t=Q(1,3);w,p,v,feas=values(row);m=r['initial_packing'];lo=3*p[m]+v[m];opt=3*best(row,t)
   assert w[m]<=row['capacity'] and lo==r['exact_lower'] and lo<=opt<=r['exact_upper']
   assert r['initial_status']=='nodelimit' and r['final_status']=='optimal' and not r['floating_solver_bound_used'];counts['partial_bounds']+=1
  if st==109:
   limit={'lru1':1,'lru4':4,'unbounded':None}[worker['method']]
   if limit is not None:assert r['peak_entries']<=limit
   assert len(r['records'])+r['hits']==len(row['observations'])
  assert r.get('algorithm_cpu',0)>=r.get('parent_cpu',0) and r.get('algorithm_cpu',0)>=r.get('child_cpu',0)
 exact=json.loads((ROOT/'SCIP-exact-capability.json').read_text());assert exact['status']=='unsupported' and 'compiled without exact solve support' in exact['stderr']
 valid_vipr=bad_vipr=valid_pb=bad_pb=0
 if full:
  binary=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
  with tempfile.TemporaryDirectory(dir='/tmp',prefix='maths101-audit-') as tmp:
   td=pathlib.Path(tmp)
   for sha,path in vipr.items():
    p=subprocess.run([str(binary),str(path)],capture_output=True,text=True,timeout=30);assert p.returncode==0 and 'Successfully verified' in p.stdout;valid_vipr+=1
    lines=path.read_text().splitlines();tokens=lines[-1].split();tokens[2]=str(int(tokens[2])-1);lines[-1]=' '.join(tokens);bad=td/(sha+'.vipr');bad.write_text('\n'.join(lines)+'\n')
    p=subprocess.run([str(binary),str(bad)],capture_output=True,text=True,timeout=30);assert p.returncode!=0;bad_vipr+=1
   for (fsha,psha),(formula,proof) in pb.items():
    args=[__import__('sys').executable,'-m','veripb',str(formula)];p=subprocess.run(args+[str(proof)],capture_output=True,text=True,timeout=30)
    assert p.returncode==0 and 'Verification succeeded' in p.stdout and 'Verification failed' not in p.stdout;valid_pb+=1
    text=proof.read_text();m=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);new=int(m[1])-1;broken=text[:m.start()]+f'conclusion BOUNDS {new} {new}'+text[m.end():];bad=td/(psha+'.pbp');bad.write_text(broken)
    p=subprocess.run(args+[str(bad)],capture_output=True,text=True,timeout=30);assert p.returncode!=0 and 'Verification succeeded' not in p.stdout;bad_pb+=1
 result=dict(passed=True,inputs=len(rows),distinct_models=len(arrays),workers=len(workers),**counts,unique_vipr_accepted=valid_vipr,false_vipr_bounds_rejected=bad_vipr,unique_pb_accepted=valid_pb,false_pb_bounds_rejected=bad_pb,audit_wall=time.perf_counter()-start,auditor_sha256=h(pathlib.Path(__file__)))
 (ROOT/'Portable-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
if __name__=='__main__':run()
