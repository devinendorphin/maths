"""Pre-freeze independent tests, including deliberately invalid certificates."""
import random,time,copy
from fractions import Fraction
from pathlib import Path
import engine as E
import frontier as F
from check_frontier import Checker,check_samples,independent_dp
from source_guarded import solve

def run(stage,out):
 import runner as R
 cases=[]
 fixtures=[
 ('negative_uniform',[2,3,4],[-4,-2,-8],[1,1,1],5,'uniform'),
 ('capacity_zero',[2,3],[3,-2],[1,1],0,'uniform'),
 ('ties_crossings',[1,1,1],[0,0,-1],[1,1,1],2,'uniform'),
 ('negative_gamma',[1,2,3],[4,4,-2],[-1,-1,-1],3,'uniform'),
 ('zero_gamma',[2,2],[5,-3],[0,0],2,'uniform'),
 ('many_switches',[1,1,1],[-1,-3,-6],[1,1,1],3,'uniform'),
 ('near_uniform',[1,2,3],[4,7,-2],[1,1,2],3,'uniform'),
 ('alpha_zero',[1,2,3],[4,7,-2],[1,1,1],3,'affine_pair'),
 ('alpha_one',[1,2,3],[-2,4,5],[-1,5,6],3,'affine_pair'),
 ('alpha_minus_one',[1,2,3],[-2,4,5],[3,-3,-4],3,'affine_pair'),
 ('alpha_minus_half',[1,2,3],[2,4,-6],[0,-1,4],3,'affine_pair'),
 ('zero_between_integers',[1,2,3],[0,2,4],[1,-2,-5],3,'affine_pair'),
 ('max_handoff',[1,2,3],[-2,4,5],[3,-3,-4],3,'affine_max'),
 ('constant',[1,1],[2,2],[-1,-1],1,'affine_pair'),
 ('near_affine',[1,2,3,4],[2,5,7,9],[3,6,9,10],5,'affine_pair'),
 ('one_class',[1,2,3],[3,-2,5],[1,1,1],3,'two_class'),
 ('two_classes',[1,2,2,3],[3,-2,5,5],[-1,1,1,-1],3,'two_class'),
 ('duplicate_slope',[1,1,1,1],[4,-2,2,3],[1,2,1,2],3,'two_class'),
 ('three_class',[1,2,3],[4,-2,6],[-1,0,2],3,'two_class'),
 ('prune_adversarial',[1,1,2,3,2,1],[2,4,-3,6,-7,0],[1,1,3,-2,5,0],5,'pruned'),
 ('slope_signed',[1,1,2,3],[2,4,-3,6],[1,1,3,-2],4,'slope')]
 rng=random.Random(146999)
 for i in range(12):
  w=[rng.randint(1,7) for _ in range(6)];p=[rng.randint(-9,15) for _ in w];v=[rng.randint(-4,4) for _ in w]
  for policy in ('slope','pruned'):fixtures.append((f'random-{i}-{policy}',w,p,v,sum(w)//3,policy))
 for label,w,p,v,c,pol in fixtures:
  ct=R.counts();cert=F.build(w,p,v,c,pol,time.perf_counter()+120,ct)
  if cert is not None:
   ck=Checker(w,p,v,c)
   for table in cert['tables']:
    for j in range(len(table['layers'])):(ck.dense_layer if table['kind']=='dense' else ck.sparse_layer)(table,j)
   terminal=ck.terminal(cert);samples=check_samples(w,p,v,c,cert)
   # Exact horizon for current optimum at several anchors, with tied optima retained.
   for t in (0,1,2,5,64,256):
    if cert['interval'][1] is not None and t>cert['interval'][1]:continue
    feas=[m for m in range(1<<len(w)) if sum(x for i,x in enumerate(w) if m>>i&1)<=c]
    value=lambda m:sum(p[i]+t*v[i] for i in range(len(w)) if m>>i&1)
    m=max(feas,key=value);loss,mask=F.horizon(cert,p,v,m,t,ct)
    expected=[]
    for A,s,mm,*_ in cert['lines']:
     d=s-sum(v[i] for i in range(len(w)) if m>>i&1)
     if d>0:expected.append(t+(value(m)-A-s*t)//d+1)
    assert loss==(min(expected) if expected else None)
   if pol=='pruned':
    try:F.at(cert,257);raise AssertionError('accepted 257')
    except ValueError:pass
   # Verify mutated recurrence entries are rejected.
   broken=copy.deepcopy(cert['tables'][0]);j=len(broken['layers'])-1
   if broken['kind']=='dense':next(x for x in broken['layers'][j] if x[2] is not None)[2]+=1
   else:broken['layers'][j]['raw'][0][2]+=1
   try:(ck.dense_layer if broken['kind']=='dense' else ck.sparse_layer)(broken,j);raise RuntimeError('checker accepted mutation')
   except AssertionError:pass
   cases.append(dict(label=label,weights=w,profits=p,slopes=v,capacity=c,policy=pol,certificate=cert,counters=ct,checks=terminal,samples=samples,mutation_rejected=True))
  else:cases.append(dict(label=label,weights=w,profits=p,slopes=v,capacity=c,policy=pol,rejected=True))
 # One-endpoint dominance counterexamples and equality handling.
 X=(1,10,-1);Y=(2,0,1);assert X[1]>=Y[1] and X[1]+256*X[2]<Y[1]+256*Y[2]
 X=(1,-1,3);Y=(2,0,0);assert X[1]<Y[1] and X[1]+256*X[2]>=Y[1]+256*Y[2]
 # v=p normalization rejects nonpositive requested factor/domain.
 opt=solve([1,1],[2,1],1)
 for factor,interval in [((1,-1),(0,None)),((0,1),(0,None)),((1,1),(-2,None))]:
  try:E.normalized_certificate([1,1],[2,1],[2,1],1,opt['packing'],opt['proof'],factor,interval);raise RuntimeError('invalid normalization accepted')
  except ValueError:pass
 # Full trajectory handoff repair and strict-switch agreement with independent audit.
 trajectory=[]
 for pol in ('maintain','affine_max','affine_pair','pruned'):
  w=[1,2,3];p=[-2,4,5];v=[3,-3,-4];c=3;source=solve(w,p,c);row=dict(weights=w,profits=p,slopes=v,capacity=c,packing=source['packing'],initial_proof=source['proof'],source=source,end=256,case_id='handoff')
  path=R.run_policy(row,pol,pol,{});row['paths']=[path];R.audit_path(row,path,out/'fixture-audits'/(pol+'.json'));trajectory.append(row)
 # Construction guard: failed DP retained and charged, scalar fallback then audited.
 original=F.Guard.check
 def forced(self,partial):
  if self.ct['dp_entries']>=12:raise F.ConstructionCap('fixture entry guard',partial)
  return original(self,partial)
 F.Guard.check=forced
 row=copy.deepcopy(trajectory[0]);row.pop('paths');path=R.run_policy(row,'uniform','uniform',{});assert path['partial_frontier'] is None # rejected slope vector: no construction
 row['slopes']=[1]*3;path=R.run_policy(row,'uniform','uniform',{});assert path['partial_frontier'] is not None and path['totals']['dp_entries']>=12 and path['frontier'] is None
 F.Guard.check=original;R.audit_path(row,path,out/'fixture-audits/guard.json');trajectory.append(dict(**{k:v for k,v in row.items() if k!='paths'},paths=[path]))
 R.save(out/'Verification.json',dict(passed=True,fixtures=cases,trajectory_fixtures=trajectory,one_endpoint_counterexamples=True,interval257_rejected=True,invalid_positive_factor_rejected=True,partial_fallback_verified=True))
 print('FIXTURES',stage,len(cases),'passed',flush=True)
