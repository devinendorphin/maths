"""Prospective fixed inputs and comparisons; no timing-selected thresholds."""
import random
METHODS={66:['real_gate','real_gatebb','real_bb','real_dense_gcd'],67:['real_dense_gcd','real_bb'],68:['real_dense_gcd','integer_dense_gcd','cross_dense_gcd','real_bb'],69:['point_bb_cold','point_bb_incumbent','point_bb_tree'],70:['point_bb_incumbent','point_bb_tree','point_bb_small_tree'],71:['real_dense_gcd','integer_dense_gcd','cross_dense_gcd'],72:['real_dense_gcd','real_sparse_gcd','real_bb'],73:['real_dense_gcd','real_bb','real_gatebb'],74:['real_dense_gcd'],75:['real_gate','real_gatebb','integer_gatebb','cross_gatebb','real_bb']}
def make(stage,label,n,seed,end=64,regime='wide',large=False):
 rng=random.Random(1660000+10000*(stage-66)+100*n+seed)
 w=[rng.randint(2,30) for _ in range(n)];p=[rng.randint(-15,80) for _ in range(n)]
 v=[rng.randint(-24,24) if regime=='wide' else rng.randint(-2,2) for _ in range(n)]
 if large:w=[wi*1009+j+1 for j,wi in enumerate(w)]
 return dict(stage=stage,case_id=f'{stage}-{label}',n=n,seed=seed,weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=end,regime=regime,split='prospective',timing=False)
def inputs():
 rows=[]
 for n in (12,20):
  for large in (False,True):
   for seed in (0,1):rows.append(dict(make(66,f'n{n}-large{large}-s{seed}',n,seed,large=large),timing=seed==1))
 for seed in (0,1):
  base=make(67,'base',12,seed)
  for bits in (0,128,512):
   k=1<<bits;rows.append(dict(base,case_id=f'67-s{seed}-bits{bits}',profits=[k*x for x in base['profits']],slopes=[k*x for x in base['slopes']],bits=bits,matched_group=f'67-s{seed}',timing=seed==1))
 fixtures=[([10,10,0,0],[0,0,0,0],2),([16,12,4,0],[-2,0,2,0],1),([30,20,10,0],[0,1,2,3],1),([-1,-2,-3,-4],[-1,-1,-1,-1],2),([0,0,0,0],[0,1,-1,0],2),([10,10,10,10],[-1,-1,1,1],2)]
 for j,(p,v,c) in enumerate(fixtures):rows.append(dict(stage=68,case_id=f'68-ties{j}',n=4,seed=-1,weights=[1]*4,profits=p,slopes=v,capacity=c,end=32,regime='ties',split='boundary',timing=j in (1,5)))
 for seed in (0,1):
  base=make(69,'base',14,seed)
  for end in (16,64,256):rows.append(dict(base,case_id=f'69-s{seed}-H{end}',end=end,matched_group=f'69-s{seed}',timing=seed==1))
 for n in (10,14,18):
  for seed in (0,1):rows.append(dict(make(70,f'n{n}-s{seed}',n,seed),timing=seed==1))
 for seed in (0,1):
  base=make(71,'base',12,seed)
  for end in (64,1024):rows.append(dict(base,case_id=f'71-s{seed}-H{end}',end=end,matched_group=f'71-s{seed}',timing=seed==1))
 rows.append(dict(stage=71,case_id='71-subinteger',n=6,seed=-1,weights=[1]*6,profits=[100,99,97,94,90,85],slopes=[0,20,40,60,80,100],capacity=1,end=1024,regime='subinteger',split='boundary',timing=True))
 for seed in (0,1):
  base=make(72,'base',16,seed)
  for numerator in (1,4,7):rows.append(dict(base,case_id=f'72-s{seed}-capacity{numerator}of8',capacity=sum(base['weights'])*numerator//8,matched_group=f'72-s{seed}',timing=seed==1))
 for n in (16,20):
  for seed in (0,1):
   r=make(73,f'n{n}-s{seed}',n,seed,end=32);rng=random.Random(2673000+100*n+seed)
   r['weights']=[rng.randint(200,500) for _ in range(n)];r['profits']=list(r['weights']);r['slopes']=[rng.choice((-1,0,1)) for _ in range(n)]
   r['capacity']=sum(r['weights'])//2;r['regime']='strongly_correlated';r['timing']=seed==1;rows.append(r)
 for seed in (0,1,2):rows.append(make(74,f's{seed}',8,seed,end=32,regime='bounded'))
 for n,large,regime in ((12,True,'wide'),(20,False,'wide'),(24,True,'bounded'),(40,False,'bounded')):
  for seed in (0,1):
   r=make(75,f'n{n}-large{large}-s{seed}',n,seed,end=128,large=large,regime=regime)
   if n==40:r['capacity']=96
   r['timing']=seed==1;rows.append(r)
 return rows
def timing_methods(stage):return METHODS[stage]
