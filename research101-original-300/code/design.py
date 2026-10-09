"""Ten mechanisms with frozen small fixtures and new held-out seeds."""
import json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inputs():
 old=json.loads((ROOT/'dependencies/research86/Inputs.json').read_text());rows=[]
 def copy(stage,name,obs=None,label=None):
  r=dict(next(x for x in old if x['case_id']==name));r.update(stage=stage,source_case=name,case_id=f'{stage}-{label or name}')
  if obs is not None:r['observations']=obs
  rows.append(r);return r
 for st in [101,102,104,106,108]:
  for name in ['86-n8-s0','86-n12-s1','86-ties','86-crossing']:copy(st,name,[0,4,8])
 for st in [103,105,107]:
  for name in ['91-n8-wide','91-n12-scaling']:
   end=next(x['end'] for x in old if x['case_id']==name)
   for den in ['dense','sparse']:
    obs=list(range(end+1)) if den=='dense' else sorted(set([0,end//2,end]))
    copy(st,name,obs,name+'-'+den)
 for name in ['86-n8-s0','86-n12-s1','91-n8-wide','91-n12-scaling']:
  copy(109,name,[0,1,2,0,1,2,3,0,2,1,3,0])
 rows.sort(key=lambda r:(r['stage'],r['case_id']))
 for seed in [9101,9102]:
  rng=random.Random(seed);n=12;w=[rng.randint(2,20) for _ in range(n)];p=[rng.randint(-12,45) for _ in range(n)];v=[rng.randint(-6,6) for _ in range(n)]
  for den in ['dense','sparse']:
   rows.append(dict(stage=110,case_id=f'110-held-{seed}-{den}',source_case='new held-out seed',n=n,seed=seed,weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=24,observations=list(range(25)) if den=='dense' else [0,2,9,24],density=den))
 return rows
METHODS={101:['cp','native'],102:['scip_cold'],103:['native','scip_cold','scip_reopt'],104:['cp_curve','native_curve'],105:['guarded','factor','repeat','snapshot'],106:['controls'],107:['points','factor','snapshot','window4','window16'],108:['resume'],109:['lru1','lru4','unbounded'],110:['points','guarded','factor','repeat','snapshot']}
def protocol():
 return dict(experiments=list(range(101,111)),methods=METHODS,inputs=40,
  model='fixed-feasibility signed-affine integer 0-1 knapsack, rational parameter queries',prior_commit='d059ed26f8ee73e56deb6c918feda1768c11ab25',
  limits=dict(campaign_wall_seconds=600,source_seconds=30,external_producer_seconds=10,external_checker_seconds=15,cp_proof_bytes=8*1024**2,scip_nodes=100000,scip_seconds=5),
  timing=dict(repeats=3,ordering='cyclic method rotation by case and repeat',includes=['solver setup','native proof construction','model encoding','proof and witness I/O','required external checker child CPU','admission','lookup','fallback and abandoned probes'],excludes=['development','dependency deployment separately recorded','independent audit','false-proof controls','packaging'],statistic='median complete algorithm CPU'),
  external_baselines=dict(cp='CP2024 knapsack DP with disclosed I/O and signed-profit big-M changes, unchanged state/proof algorithm',scip='ordinary SCIP proposals followed by independent native/VIPR certificates; exact wheel capability probed and recorded'),
  snapshot_contract='trusted admission into immutable in-memory facts, exact model identity at each query, explicit dependency epoch at batch start; captured facts need not track later external file edits',
  stop='caps and unsupported exact features stay explicit; incomplete or unverified output is never admitted')
