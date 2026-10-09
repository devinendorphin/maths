from fractions import Fraction as Q
import copy,json,subprocess,time
from support import *
import design,external as X,snapshot as S,witness as W

def native(row):
 r=economy.run(row,'points');r['claims']=[dict(time=t,packing=m) for t,m in zip(r['observations'],r['packings'])];return r
def cp(row):
 start=meter();records=[X.cp_point(row,t) for t in row['observations']]
 return dict(status='complete',records=records,claims=[dict(time=t,packing=r['packing']) for t,r in zip(row['observations'],records)],certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),**elapsed(start))
def guard(row):
 r=economy.run(row,'guarded');r['claims']=[dict(time=t,packing=m) for t,m in zip(r['observations'],r['packings'])];return r
def controls(row):
 start=meter();snap,records,curve=S.build(row);epoch=dependencies();tests=[]
 def query(label,r=row,t=0,e=epoch,expected=True):
  try:m=snap.query(r,t,e)
  except ValueError:accepted=False;m=None
  else:accepted=True
  assert accepted==expected;tests.append(dict(label=label,accepted=accepted,packing=m))
 query('same-model');query('same-model-copy',dict(row))
 query('changed-profit',dict(row,profits=[p+1 for p in row['profits']]),expected=False)
 query('capacity-restriction',dict(row,capacity=row['capacity']-1),expected=False)
 query('capacity-expansion',dict(row,capacity=row['capacity']+1),expected=False)
 query('nonlinear',dict(row,quadratic=[1]*row['n']),expected=False)
 query('variable-domain',dict(row,feasible_type='variable'),expected=False)
 query('outside-interval',t=row['end']+1,expected=False)
 for k in epoch:query(k+'-epoch',e=dict(epoch,**{k:'0'*64}),expected=False)
 rec=records[0];path=ROOT/rec['witness_path'];original=path.read_bytes()
 try:
  path.write_bytes(original+b' ');assert not W.valid(row,Q(*rec['time']),rec)
  query('captured-facts-survive-disk-rewrite')
 finally:path.write_bytes(original)
 rec['objective']+=1;query('captured-facts-survive-diagnostic-rewrite');rec['objective']-=1
 return dict(status='complete',records=records,tests=tests,claims=[dict(time=t,packing=snap.query(row,t,epoch)) for t in [0,row['end']]],**elapsed(start))

def resume(row):
 start=meter();m,xs=X.scip_model(row,limited=True);t=Q(1,3);q=X.qvalues(row,t);m.setObjective(X.quicksum(p*x for p,x in zip(q,xs)),'maximize')
 m.setParam('limits/nodes',0);m.optimize();first=str(m.getStatus());mask=X.extract(m,xs,row,t)
 # A root price gives an exact global upper bound independently of SCIP's float bound.
 prices=[Q(0)]+[Q(p,w) for p,w in zip(q,row['weights']) if p>0]
 upper=min(int((a*row['capacity']+sum(max(Q(0),p-a*w) for p,w in zip(q,row['weights']))).__floor__()) for a in prices)
 lower=shared.value(q,mask);assert lower<=upper
 m.setParam('limits/nodes',100000);m.optimize();finalmask=X.extract(m,xs,row,t);rec=W.produce(row,t);assert shared.value(q,finalmask)==rec['objective']
 return dict(status='complete',records=[rec],claims=[dict(time=[t.numerator,t.denominator],packing=finalmask)],
  initial_status=first,initial_packing=mask,exact_lower=lower,exact_upper=upper,initial_gap=upper-lower,final_status=str(m.getStatus()),
  partial_status='optimal' if lower==upper else 'bounded-gap',floating_solver_bound_used=False,**elapsed(start))

def exact_capability():
 # Fresh subprocess isolates error messages and proves what this installed wheel supports.
 script="import sys;sys.path.append(sys.argv[1]);from pyscipopt import Model;m=Model();m.hideOutput();m.enableExactSolving(True)"
 p=subprocess.run(['python3','-c',script,meta['tools_root']+'/python'],capture_output=True,text=True,timeout=10)
 return dict(status='unsupported' if p.returncode else 'enabled',exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,scope='this PySCIPOpt 6.0.0 / SCIP 10.0.0 wheel, not SCIP in general')
def worker(row,method):
 if method in ['native','points']:return native(row)
 if method=='cp':return cp(row)
 if method=='scip_cold':return X.scip_sequence(row,False)
 if method=='scip_reopt':return X.scip_sequence(row,True)
 if method=='native_curve':return S.run(row)
 if method=='cp_curve':return S.run(row,route='cp')
 if method=='guarded':return guard(row)
 if method=='factor':
  r=economy.run(row,'factor');r['claims']=[dict(time=t,packing=m) for t,m in zip(r['observations'],r['packings'])];return r
 if method=='repeat':return S.run(row,repeat=True)
 if method=='snapshot':return S.run(row)
 if method=='controls':return controls(row)
 if method=='window4':return S.window(row,4)
 if method=='window16':return S.window(row,16)
 if method=='resume':return resume(row)
 if method=='lru1':return S.lru(row,1)
 if method=='lru4':return S.lru(row,4)
 if method=='unbounded':return S.lru(row,None)
 raise ValueError(method)
def run():
 start=time.perf_counter();seal=json.loads((ROOT/'Freeze.json').read_text())
 for p,h in seal['files'].items():assert hashfile(ROOT/p)==h,p
 external_seal=json.loads((ROOT/'External-dependencies.json').read_text())
 for p,h in external_seal['files'].items():assert hashfile(p)==h,p
 cap=exact_capability();save('SCIP-exact-capability.json',cap);assert cap['status']=='unsupported'
 rows=json.loads((ROOT/'Inputs.json').read_text());results=[]
 for i,row in enumerate(rows):
  methods=design.METHODS[row['stage']];repeats=1 if row['stage'] in [102,106,108] else 3
  for rep in range(repeats):
   offset=(i+rep)%len(methods);order=methods[offset:]+methods[:offset]
   for method in order:
    if time.perf_counter()-start>600:raise TimeoutError('campaign wall cap')
    result=worker(row,method);assert result['status']=='complete'
    results.append(dict(case_id=row['case_id'],stage=row['stage'],method=method,repeat=rep,result=result))
  print(f'{row["case_id"]}: {len(methods)*repeats} completed workers',flush=True)
  save('evidence/Results-progress.json',results)
 save('Results.json',results);save('Execution.json',dict(status='complete',workers=len(results),wall=time.perf_counter()-start,wall_cap=600))
if __name__=='__main__':run()
