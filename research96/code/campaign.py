"""Frozen bounded comparisons with compact evidence and explicit failure statuses."""
from fractions import Fraction as Q
import copy,json,os,pathlib,subprocess,time
from support import *
import witness as W,checkpoint as K

def change_dep(key):
 d=dependencies();d[key]='0'*64;return d
def scope(row):
 r=W.produce(row,0);tests=[]
 def test(label,modelrow=row,t=0,dep=None,expected=False):
  got=W.valid(modelrow,t,r,dep);assert got==expected;tests.append(dict(label=label,accepted=got))
 test('same-model',expected=True);test('exact-model-restored',modelrow=dict(row),expected=True)
 test('other-time',t=1)
 test('objective-change',modelrow=dict(row,profits=[p+1 for p in row['profits']]))
 test('capacity-expansion',modelrow=dict(row,capacity=row['capacity']+1))
 test('capacity-restriction',modelrow=dict(row,capacity=max(0,row['capacity']-1)))
 test('nonlinear-model',modelrow=dict(row,quadratic=[1]*row['n']))
 test('changing-feasibility',modelrow=dict(row,feasible_type='variable'))
 for key in ['rule','admission','checker']:test(key+'-version-change',dep=change_dep(key))
 return dict(status='complete',records=[r],tests=tests)

def interval(row):
 curve=curves.run(row,'real','dense',True);assert curve['status']=='complete';cache={};claims=[];bundles=[]
 for seg in curve['intervals']:
  a,b=Q(*seg['left']),Q(*seg['right']);m=seg['line'][2];refs=[]
  for t in [a,b]:
   if t not in cache:cache[t]=W.produce(row,t)
   r=cache[t];assert W.valid(row,t,r)
   scaled=shared.value([t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])],m)
   assert scaled==r['objective'];refs.append(r['proof_sha256'])
  bundles.append(dict(left=seg['left'],right=seg['right'],packing=m,endpoint_proofs=refs))
  for l in [Q(0),Q(1,3),Q(1,2),Q(2,3),Q(1)]:
   t=(1-l)*a+l*b;val=shared.value(row['profits'],m)+t*shared.value(row['slopes'],m)
   claims.append(dict(time=[t.numerator,t.denominator],packing=m,value=[val.numerator,val.denominator]))
 return dict(status='complete',records=list(cache.values()),curve=curve,bundles=bundles,claims=claims)

def compact(row):
 start=meter();curve=curves.run(row,'real','dense',True);assert curve['status']=='complete';cache={};bundles=[];hits=0
 for seg in curve['intervals']:
  m=seg['line'][2]
  for t in [Q(*seg['left']),Q(*seg['right'])]:
   if t not in cache:cache[t]=W.produce(row,t)
   else:hits+=1
   assert W.valid(row,t,cache[t])
   assert shared.value([t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])],m)==cache[t]['objective']
  bundles.append(dict(left=seg['left'],right=seg['right'],packing=m))
 packings=[]
 for t in row['observations']:
  seg=next(s for s in bundles if Q(*s['left'])<=t<=Q(*s['right']))
  for endpoint in ['left','right']:assert W.valid(row,Q(*seg[endpoint]),cache[Q(*seg[endpoint])])
  m=seg['packing'];assert shared.value(row['weights'],m)<=row['capacity'];packings.append(m)
 records=list(cache.values())
 return dict(status='complete',method='compact',packings=packings,observations=row['observations'],curve=curve,bundles=bundles,records=records,
  certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),witness_bytes=sum(r['witness_bytes'] for r in records),
  derivations=sum(r['info']['derivations'] for r in records),cache_hits=hits,**elapsed(start))

def witness_comparison(row):
 start=meter();records=[];controls=[]
 for t in [Q(0),Q(1,3),Q(row['end'])]:
  r=W.produce(row,t);w=json.loads((ROOT/r['witness_path']).read_bytes());assert W.valid(row,t,r)
  reconstructed,checked=W.check(row,t,w)
  assert reconstructed==[list(c) for c in r['source']['proof']]
  def bad(label,edit):
   x=copy.deepcopy(w);edit(x)
   try:W.check(row,t,x)
   except (ValueError,KeyError,ZeroDivisionError):accepted=False
   else:accepted=True
   assert not accepted;controls.append(dict(time=w['time'],label=label,rejected=True))
  bad('deleted-cover-cell',lambda x:x['cells'].pop())
  bad('false-objective',lambda x:x.update(objective=x['objective']-1))
  bad('zero-denominator',lambda x:x['cells'][0].__setitem__(3,0))
  bad('model-change',lambda x:x['model'].update(capacity=x['model']['capacity']+1))
  records.append(r)
 return dict(status='complete',records=records,controls=controls,
  compact_bytes=sum(r['witness_bytes'] for r in records),vipr_bytes=sum(r['bytes'] for r in records),
  cells=sum(r['admission']['cells'] for r in records),vipr_derivations=sum(r['info']['derivations'] for r in records),
  established_route='unchanged original-problem VIPR compiler and viprchk; no CP-2024 DP or VeriPB implementation claimed',**elapsed(start))

def interruption(row):
 start=meter();s=K.setup(row,Q(1,3));snapshots=[];controls=[]
 for budget in [0,1,7,64,8191]:
  s=K.advance(row,Q(1,3),s,budget);snapshots.append(copy.deepcopy(s))
 assert s['status']=='optimal' and not s['todo']
 cold=K.advance(row,Q(1,3),K.setup(row,Q(1,3)),8191)
 assert cold['lower']==s['lower'] and cold['packing']==s['packing'] and cold['processed']==s['processed']
 for label,new,dep in [('changed-objective',dict(row,profits=[p+1 for p in row['profits']]),None),('changed-capacity',dict(row,capacity=row['capacity']+1),None)]+[(k+'-changed',row,change_dep(k)) for k in ['rule','admission','checker']]:
  x=copy.deepcopy(snapshots[2])
  try:K.advance(new,Q(1,3),x,1,dep)
  except ValueError:rejected=True
  else:rejected=False
  assert rejected;controls.append(dict(label=label,rejected=True,status='invalid'))
 x=copy.deepcopy(snapshots[2]);x['todo'].pop()
 try:K.advance(row,Q(1,3),x,1)
 except ValueError:rejected=True
 else:rejected=False
 assert rejected;controls.append(dict(label='lost-pending-branch',rejected=True,status='invalid'))
 # A deliberately capped native production attempt is not admitted; fallback is charged.
 try:shared.SG.solve(row['weights'],row['profits'],row['capacity'],max_steps=1)
 except shared.SG.SourceCap as exc:aborted=exc.cost
 else:raise AssertionError('forced source cap did not trigger')
 fallback=W.produce(row,0)
 return dict(status='complete',snapshots=snapshots,controls=controls,aborted_source=aborted,
  fallback=fallback,cold_nodes=cold['nodes'],resumed_nodes=s['nodes'],**elapsed(start))

def formal():
 setup=json.loads((ROOT/'Lean-setup.json').read_text())
 if setup['status']!='available':return dict(status='unsupported',reason=setup.get('reason'))
 env=dict(os.environ,LEAN_PATH=str(ROOT/'formal'));records=[]
 for name in ['Endpoint','Spec']:
  start=meter();args=[setup['binary'],'-o',str(ROOT/'formal'/f'{name}.olean'),str(ROOT/'formal'/f'{name}.lean')]
  p=subprocess.run(args,capture_output=True,text=True,env=env,cwd=ROOT/'formal',timeout=60)
  assert p.returncode==0 and 'sorryAx' not in p.stdout+p.stderr
  allowed={'propext','Classical.choice','Quot.sound'}
  for line in p.stdout.splitlines():
   if 'depends on axioms:' in line:
    axioms={x.strip() for x in line.split('[',1)[1].rstrip(']').split(',') if x.strip()}
    assert axioms<=allowed
  records.append(dict(file=name+'.lean',exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,**elapsed(start)))
 # Kernel ascription rejects a stronger, false statement; no Comparator claim.
 text='import Endpoint\nexample : False := TemporalProof.affine_interval_optimal\n'
 (ROOT/'formal/RejectedStatement.lean').write_text(text)
 p=subprocess.run([setup['binary'],str(ROOT/'formal/RejectedStatement.lean')],capture_output=True,text=True,env=env,timeout=60)
 assert p.returncode!=0
 return dict(status='checked',lean_version=setup['version_output'],mathlib=None,comparator_executed=False,
  records=records,rejected_statement=dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))

def run():
 start=time.perf_counter();rows=json.loads((ROOT/'Inputs.json').read_text());results=[]
 freeze=json.loads((ROOT/'Freeze.json').read_text())
 for p,h in freeze['files'].items():assert hashfile(ROOT/p)==h,p
 fr=formal();save('Formal-check.json',fr)
 for index,row in enumerate(rows):
  if time.perf_counter()-start>300:raise TimeoutError('campaign cap')
  st=row['stage']
  if st==100:
   methods=['points','guarded','factor','compact']
   for repeat in range(3):
    order=methods[(index+repeat)%4:]+methods[:(index+repeat)%4]
    for method in order:
     r=compact(row) if method=='compact' else economy.run(row,method)
     results.append(dict(case_id=row['case_id'],stage=st,repeat=repeat,method=method,result=r))
   print(row['case_id']+' completed 12 timed paths',flush=True)
  else:
   fn={96:scope,97:interval,98:witness_comparison,99:interruption}[st];r=fn(row)
   results.append(dict(case_id=row['case_id'],stage=st,repeat=0,method=fn.__name__,result=r));print(row['case_id']+' '+r['status'],flush=True)
  save('evidence/Results-progress.json',results)
 save('Results.json',results);save('Execution.json',dict(status='complete',workers=len(results),wall=time.perf_counter()-start,wall_cap=300))

if __name__=='__main__':run()
