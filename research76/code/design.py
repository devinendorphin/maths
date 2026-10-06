"""Prospective bounded comparisons with disclosed retained controls."""
import random,json
from shared import ROOT
METHODS={76:['real_bb','real_lean','real_dense_gcd'],77:['real_lean','real_portfolio','real_dense_gcd'],78:['integer_dense_gcd','cross_dense_gcd','balanced_dense_gcd','real_dense_gcd'],79:['integer_dense_gcd','cross_dense_gcd','balanced_dense_gcd','real_dense_gcd'],80:['integer_dense_gcd','cross_dense_gcd','balanced_dense_gcd','integer_lean','cross_lean','balanced_lean'],81:['real_gatelean','real_portfolio','real_forcedportfolio','real_deadportfolio','real_dense_gcd'],82:['real_dense_gcd'],83:['real_dense_gcd'],84:['point_bb_cold','point_bb_incumbent','point_bb_lean_cold','point_bb_lean_incumbent'],85:['real_gatebb','real_gatelean','real_portfolio','cross_gatelean','balanced_gatelean']}
def make(stage,label,n,seed,end=64,large=False,correlated=False):
 rng=random.Random(1760000+10000*(stage-76)+100*n+seed)
 w=[rng.randint(2,30) for _ in range(n)];p=[rng.randint(-15,80) for _ in range(n)];v=[rng.randint(-24,24) for _ in range(n)]
 if large:w=[wi*1009+j+1 for j,wi in enumerate(w)]
 if correlated:w=[rng.randint(700,1700) for _ in range(n)];p=list(w);v=[rng.choice((-1,0,1)) for _ in range(n)]
 return dict(stage=stage,case_id=f'{stage}-{label}',n=n,seed=seed,weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=end,regime='correlated' if correlated else 'large' if large else 'bounded',split='prospective',timing=False)
def inputs():
 rows=[]
 for old in json.loads((ROOT/'dependencies/prior73-inputs.json').read_text()):
  rows.append(dict(old,stage=76,case_id='76-retained-'+old['case_id'],retained_from=old['case_id'],split='retained_control',timing=old['seed']==1))
 for n in (16,20):
  for seed in (0,1):rows.append(dict(make(76,f'fresh-n{n}-s{seed}',n,seed,end=32,correlated=True),timing=seed==1))
 for n in (18,22,24):
  for seed in (0,1):rows.append(dict(make(77,f'n{n}-s{seed}',n,seed,end=16,correlated=True),timing=seed==1 and n in (18,22)))
 for end in (128,1024):
  for direction in ('early','late'):
   for profile in ('increasing','decreasing'):
    n=16;increments=[2**(j if profile=='increasing' else n-j) for j in range(1,n)]
    positions=list(range(1,n)) if direction=='early' else list(range(end-n+1,end))
    v=[0];p=[1000000]
    for step,x in zip(increments,positions):v.append(v[-1]+step);p.append(p[-1]-x*step)
    rows.append(dict(stage=78,case_id=f'78-H{end}-{direction}-{profile}',n=n,seed=-1,weights=[1]*n,profits=p,slopes=v,capacity=1,end=end,regime='skewed_chain',split='boundary',timing=end==1024))
 for n in (12,20):
  for seed in (0,1):
   base=make(79,'base',n,seed)
   for end in (64,1024):rows.append(dict(base,case_id=f'79-n{n}-s{seed}-H{end}',end=end,matched_group=f'79-n{n}-s{seed}',timing=seed==1 and end==1024))
 for n in (12,20):
  for seed in (0,1):rows.append(dict(make(80,f'n{n}-s{seed}',n,seed,end=128),timing=seed==1))
 for n in (12,20):
  for seed in (0,1):rows.append(dict(make(81,f'n{n}-s{seed}',n,seed,end=32,correlated=True),timing=seed==1))
 for n in (10,12):
  for seed in (0,1):rows.append(make(82,f'n{n}-s{seed}',n,seed,end=32))
 for seed in (0,1):rows.append(make(83,f's{seed}',8,seed,end=32))
 for n in (10,14,18):
  for seed in (0,1):rows.append(dict(make(84,f'n{n}-s{seed}',n,seed),timing=seed==1))
 for n,kind in ((12,'large'),(20,'correlated'),(24,'bounded'),(40,'bounded')):
  for seed in (0,1):
   r=make(85,f'n{n}-{kind}-s{seed}',n,seed,end=128,large=kind=='large',correlated=kind=='correlated')
   if n==40:r['capacity']=96
   r['timing']=seed==1;rows.append(r)
 return rows
def timing_methods(stage):return [] if stage in (82,83) else METHODS[stage]
