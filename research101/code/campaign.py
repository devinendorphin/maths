from fractions import Fraction
import copy,gzip,hashlib,json,pathlib,resource,sys,time
import dp,checker
from pyscipopt import Model,quicksum,__version__
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dependencies/research86/code'))
import certificates,economy
certificates.ROOT=ROOT

def save(name,obj):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clock():
 r=resource.getrusage(resource.RUSAGE_CHILDREN);return time.process_time(),r.ru_utime+r.ru_stime,time.perf_counter()
def elapsed(c):
 now=clock();return dict(cpu=now[0]-c[0]+now[1]-c[1],wall=now[2]-c[2])
def checked(row,t):
 c=dp.produce(row,t);assert checker.verify(row,t,c);return c
counter=0
def persist(cert):
 global counter
 counter+=1;p=f'evidence/dp/{counter:05}.json';save(p,cert)
 return dict(path=p,sha256=sha(ROOT/p),bytes=(ROOT/p).stat().st_size,gzip_bytes=len(gzip.compress((ROOT/p).read_bytes(),mtime=0)))
def scip(row,t):
 q=dp.coefficients(row,t);m=Model();m.hideOutput();m.setRealParam('limits/time',5);m.setIntParam('parallel/maxnthreads',1);m.setIntParam('randomization/randomseedshift',0)
 x=[m.addVar(vtype='B',name=f'x{i}') for i in range(row['n'])]
 m.addCons(quicksum(a*b for a,b in zip(row['weights'],x))<=row['capacity']);m.setObjective(quicksum(a*b for a,b in zip(q,x)),'maximize');m.optimize()
 assert str(m.getStatus())=='optimal',m.getStatus()
 vals=[m.getVal(v) for v in x];assert all(min(abs(v),abs(v-1))<1e-7 for v in vals)
 mask=sum(1<<i for i,v in enumerate(vals) if v>0.5);cert=checked(row,t)
 assert sum(w for i,w in enumerate(row['weights']) if mask>>i&1)<=row['capacity']
 assert sum(v for i,v in enumerate(q) if mask>>i&1)==cert['objective']
 return dict(status=str(m.getStatus()),packing=mask,objective=cert['objective'],reported_objective=m.getObjVal(),nodes=m.getNNodes(),exact_mode=m.isExact()),cert

def run():
 start=time.perf_counter();freeze=json.loads((ROOT/'Freeze.json').read_text())
 for p,h in freeze['files'].items():assert sha(ROOT/p)==h,p
 rows=json.loads((ROOT/'Inputs.json').read_text());results=[]
 m=Model();m.hideOutput();exact=False;reason=None
 try:m.enableExactSolving(True);exact=m.isExact()
 except Exception as e:reason='Packaged SCIP compiled without exact solve support; '+str(e)
 save('Capabilities.json',dict(python=sys.version,pyscipopt=__version__,scip=[m.getMajorVersion(),m.getMinorVersion(),m.getTechVersion()],scip_exact_available=exact,exact_failure=reason,requirements=['pyscipopt==6.0.0','numpy==2.5.3']))
 def emit(stage,row,variant,body,c):
  assert time.perf_counter()-start<300
  results.append(dict(stage=stage,case_id=row['case_id'],variant=variant,**body,**elapsed(c)))
 for row in rows:
  for t in [0,4,8]:
   c=clock();cert=checked(row,t);emit(101,row,str(t),dict(time=[t,1],objective=cert['objective'],packing=cert['packing'],certificate=persist(cert)),c)
   c=clock();solver,cert=scip(row,t);emit(102,row,str(t),dict(time=[t,1],solver=solver,certificate=persist(cert)),c)
   c=clock();controls=[]
   for mutation in ['base','interior','final','coefficients','packing','time']:
    bad=copy.deepcopy(cert)
    if mutation=='base':bad['table'][0][0]=1
    elif mutation=='interior':bad['table'][1][0]+=1
    elif mutation=='final':bad['table'][-1][-1]+=1
    elif mutation=='coefficients':bad['coefficients'][0]+=1
    elif mutation=='packing':bad['packing']=1<<row['n']
    else:bad['time']=[t+1,1]
    assert not checker.verify(row,t,bad);controls.append(dict(mutation=mutation,rejected=True,certificate=persist(bad)))
   emit(106,row,str(t),dict(time=[t,1],controls=controls),c)
  for scale in [1,4,16]:
   c=clock();scaled=copy.deepcopy(row);scaled['weights']=[w*scale for w in row['weights']];scaled['capacity']*=scale
   cert=checked(scaled,4);emit(103,row,str(scale),dict(model=scaled,time=[4,1],scale=scale,objective=cert['objective'],cells=cert['cells'],certificate=persist(cert)),c)
  for t in [Fraction(1,3),Fraction(7,5),Fraction(15,2)]:
   c=clock();cert=checked(row,t);emit(105,row,str(t),dict(time=[t.numerator,t.denominator],objective=cert['objective'],certificate=persist(cert)),c)
  c=clock();failed=dp.produce(row,4,1);assert failed['status']=='incomplete' and not checker.verify(row,4,failed)
  cert=dp.produce(row,4,failed['required_cells']);assert checker.verify(row,4,cert)
  emit(107,row,'cap-and-fallback',dict(time=[4,1],attempt=failed,fallback_certificate=persist(cert),objective=cert['objective']),c)
  for capacity in sorted(set([max(0,row['capacity']//2),row['capacity']+1])-{row['capacity']}):
   c=clock();changed=copy.deepcopy(row);changed['capacity']=capacity;old=checked(row,4);assert not checker.verify(changed,4,old)
   new=checked(changed,4);feasible=sum(w for i,w in enumerate(row['weights']) if old['packing']>>i&1)<=capacity
   transfer=capacity<=row['capacity'] and feasible
   if transfer:assert new['objective']==old['objective']
   emit(108,row,str(capacity),dict(time=[4,1],model=changed,old_capacity=row['capacity'],old_packing=old['packing'],old_objective=old['objective'],old_rejected=True,subset_transfer=transfer,certificate=persist(new)),c)
  if row['case_id'] in ['ties','zero-capacity']:
   for t in range(9):
    c=clock();cert=checked(row,t);emit(104,row,str(t),dict(time=[t,1],objective=cert['objective'],certificate=persist(cert)),c)
  observations=[0,4,8]*5
  for method in ['fresh','memo']:
   c=clock();cache={};certs=[];answers=[];hits=0
   for t in observations:
    if method=='memo' and t in cache:
     cert=cache[t];assert checker.verify(row,t,cert);hits+=1
    else:
     cert=checked(row,t);cache[t]=cert;certs.append(persist(cert))
    answers.append(cert['objective'])
   emit(109,row,method,dict(observations=observations,answers=answers,cache_hits=hits,certificates=certs),c)
 # Full-cost paths: four mathematical models, matched streams, rotated methods.
 for original in [rows[i] for i in [0,2,4,6]]:
  for density,obs in [('dense',list(range(9))),('sparse',[0,4,8])]:
   row=copy.deepcopy(original);row['observations']=obs
   for repeat in range(3):
    methods=['dp','scip_dp','vipr_points','vipr_guarded'];offset=repeat%4;methods=methods[offset:]+methods[:offset]
    for method in methods:
     c=clock()
     if method.startswith('vipr'):
      data=economy.run(row,'points' if method=='vipr_points' else 'guarded');save(f'evidence/vipr-runs/{len(results)}.json',data)
      body=dict(observations=obs,packings=data['packings'],certificates=data['certificates'],certificate_bytes=data['certificate_bytes'],evidence=f'evidence/vipr-runs/{len(results)}.json')
     else:
      certs=[];packings=[];solvers=[]
      for t in obs:
       if method=='dp':cert=checked(row,t);mask=cert['packing']
       else:solver,cert=scip(row,t);mask=solver['packing'];solvers.append(solver)
       certs.append(persist(cert));packings.append(mask)
      body=dict(observations=obs,packings=packings,certificates=len(certs),certificate_bytes=sum(x['bytes'] for x in certs),dp_certificates=certs,solvers=solvers)
     emit(110,row,f'{density}/{repeat}/{method}',dict(density=density,repeat=repeat,method=method,**body),c)
 save('Results.json',results);save('Execution.json',dict(status='complete',workers=len(results),wall=time.perf_counter()-start,stages=sorted(set(r['stage'] for r in results))))
 print(json.dumps(json.loads((ROOT/'Execution.json').read_text())),flush=True)
if __name__=='__main__':run()
