"""All mathematical controls, methods and timing selections frozen prospectively."""
import random
METHODS={86:['interval'],87:['gap'],88:['subset'],89:['curvature'],90:['expiry'],91:['points','envelope','guarded'],92:['points','envelope','guarded'],93:['integrity'],94:['epochs'],95:['points','envelope','guarded','factor']}
def make(stage,label,n,seed,end=32,profile='wide'):
 rng=random.Random(1860000+10000*(stage-86)+100*n+seed)
 w=[rng.randint(2,20) for _ in range(n)];p=[rng.randint(-8,50) for _ in range(n)];v=[rng.randint(-8,8) for _ in range(n)]
 if profile=='scaling':v=list(p)
 if profile=='zero':v=[0]*n
 if profile=='negative_factor':v=[-x for x in p]
 return dict(stage=stage,case_id=f'{stage}-{label}',n=n,seed=seed,weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=end,profile=profile,timing=False,observations=list(range(end+1)))
def fixture(stage,label,p,v,c,end=8,w=None,quad=None):
 n=len(p);r=dict(stage=stage,case_id=f'{stage}-{label}',n=n,seed=-1,weights=w or [1]*n,profits=p,slopes=v,capacity=c,end=end,profile='constructed',timing=False,observations=list(range(end+1)))
 if quad is not None:r['quadratic']=quad
 return r

def inputs():
 rows=[]
 for st in (86,87,88):
  for n in (8,12):
   for seed in (0,1):rows.append(make(st,f'n{n}-s{seed}',n,seed))
 rows.extend([fixture(86,'ties',[10,10,0],[0,0,0],1),fixture(86,'crossing',[30,20,0],[0,2,4],1,end=16),fixture(87,'stable',[10,1],[0,0],1),fixture(87,'switch',[100,0],[0,10],1,end=32),fixture(88,'expansion',[3,4],[0,0],3,w=[2,3]),fixture(88,'infeasible',[5,3],[0,0],2,w=[2,1])])
 for seed in range(4):
  r=make(89,f's{seed}',8,seed,end=4);rng=random.Random(2868900+seed);r['quadratic']=[rng.randint(-2,2) for _ in range(8)];rows.append(r)
 rows.extend([fixture(89,'interior_failure',[1,0],[0,8],1,end=2,quad=[0,-4]),fixture(89,'margin_safe',[10,0],[0,8],1,end=2,quad=[0,-4])])
 for n in (10,12):
  for seed in (0,1):
   for profile in ('wide','scaling','zero'):rows.append(make(90,f'n{n}-s{seed}-{profile}',n,seed,end=32,profile=profile))
 rows.append(fixture(90,'expiry_without_loss',[3,4],[3,4],3,end=32,w=[2,3]))
 for n in (8,12):
  for profile in ('wide','scaling'):rows.append(dict(make(91,f'n{n}-{profile}',n,0,end=16 if n==8 else 32,profile=profile),timing=True))
 for seed in (0,1):
  base=make(92,'base',10,seed)
  for stride in (1,8,32):rows.append(dict(base,case_id=f'92-s{seed}-stride{stride}',observations=list(range(0,33,stride)),stride=stride,matched_group=f'92-s{seed}',timing=seed==1))
 for seed in (0,1):rows.append(dict(make(93,f's{seed}',8,seed,end=8),observations=[0]))
 for seed in (0,1):rows.append(make(94,f's{seed}',8,seed,end=8))
 rows.extend([fixture(94,'objective_jump',[10,1],[0,0],1),fixture(94,'capacity_expansion',[3,4],[0,0],3,w=[2,3])])
 for n in (10,12):
  for profile in ('wide','scaling','zero'):rows.append(dict(make(95,f'n{n}-{profile}',n,0,end=64,profile=profile),timing=True))
 rows.append(dict(make(95,'negative_factor',10,1,end=4,profile='negative_factor'),timing=True))
 return sorted(rows,key=lambda x:(x['stage'],x['case_id']))
def timing_methods(stage):return METHODS[stage] if stage in (91,92,95) else []
