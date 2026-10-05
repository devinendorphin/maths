"""Independent seeded-vector audit against the handoff RNG specification."""
import random,json,sys
from pathlib import Path
from runner import ROOT,read,save
for stage in [int(s) for s in sys.argv[1:]]:
 total=0
 for split in ('development','held'):
  rows=read(ROOT/'stages'/str(stage)/split/'Inputs.json');base=146000+(stage-31)*1000;seeds=[base] if split=='development' else [base+500,base+501,base+502]
  for n in (12,16):
   for seed in seeds:
    rng=random.Random(seed);w=[rng.randint(2,20) for i in range(n)];pfs=[('random',[rng.randint(5,50) for i in range(n)]),('proportional',[wi+15+rng.randint(-2,2) for wi in w]),('mixed',[rng.randint(-15,40) for i in range(n)]),('negative',[-rng.randint(1,10) for i in range(n)])];ctrl={f:rng.randrange(n) for f,p in pfs} if stage in (32,33) else {}
    for family,p in pfs:
     group=[r for r in rows if r['n']==n and r['seed']==seed and r['family']==family];assert len(group)==4
     if stage in (31,34,35):
      sparse=[0]*n;sparse[rng.randrange(n)]=rng.choice((-1,1));signed=[rng.randint(-3,3) for i in range(n)];m=group[0]['packing'];expected=dict(sparse=sparse,signed=signed,scale=p,harm=[-1 if m>>i&1 else 1 for i in range(n)])
     elif stage==32:
      near=[1]*n;near[ctrl[family]]=2;expected=dict(uniform_plus=[1]*n,uniform_minus=[-1]*n,zero=[0]*n,near_uniform=near)
     else:
      near=[x+1 for x in p];near[ctrl[family]]+=1;expected=dict(scale=p,affine_plus=[x+1 for x in p],affine_negative=[-x+1 for x in p],near_affine=near)
     for row in group:assert row['weights']==w and row['capacity']==sum(w)//3 and row['profits']==p and row['slopes']==expected[row['regime']];total+=1
  assert len(rows)==(32 if split=='development' else 96)
 save(ROOT/'stages'/str(stage)/'Input-audit.json',dict(passed=True,cases=total,fresh_seeds=True,RNG_generation_independently_checked=True))
 print('INPUT AUDIT',stage,total,flush=True)
