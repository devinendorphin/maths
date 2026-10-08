"""Small, deterministic cases: mechanisms and matched density, not gate tuning."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inputs():
 old=json.loads((ROOT/'dependencies/research86/Inputs.json').read_text())
 selected=['86-n8-s0','86-n8-s1','86-n12-s0','86-n12-s1','86-crossing','86-ties']
 rows=[]
 for stage in (96,97,98,99):
  names=selected[:4] if stage in (96,99) else selected
  for name in names:
   r=dict(next(x for x in old if x['case_id']==name));r.update(stage=stage,case_id=f'{stage}-{name}',source_case=name,timing=False);rows.append(r)
 for name in ['91-n8-wide','91-n12-scaling','95-n10-zero','95-negative_factor']:
  for density in ['dense','sparse']:
   r=dict(next(x for x in old if x['case_id']==name));end=r['end']
   obs=list(range(end+1)) if density=='dense' else sorted(set([0,end//2,end]))
   r.update(stage=100,case_id=f'100-{name}-{density}',source_case=name,density=density,observations=obs,timing=True);rows.append(r)
 return rows
def protocol():
 return dict(experiments=[96,97,98,99,100],model='fixed-feasibility signed-affine 0-1 knapsack',
  prior_commit='ad857b7f3ec4004f2eed7e5720fe86eb9f9eb05c',
  limits=dict(campaign_wall_seconds=300,source_wall_seconds=30,source_steps=500000,witness_cells=4096,checker_wall_seconds=10,checkpoint_nodes_per_step=1,checkpoint_total_nodes=8191,checkpoint_wall_seconds=10,formal_wall_seconds=60),
  timing=dict(methods=['points','guarded','factor','compact'],repeats=3,ordering='cyclic rotation by case and repeat',statistic='median complete algorithm CPU, including checker child CPU',
   included=['discovery','native construction/cleanup','compiler','proof file I/O','external VIPR checks','receipt and dependency hashing','witness admission and loading','observation output'],
   excluded=['development','Lean deployment and one-time compilation, recorded separately','independent audit','deliberately false-proof controls','packaging']),
  witness='four integers per scalar cell, expanded into the unchanged original-problem VIPR route',
  checkpoint='bounded exhaustive branch tree: sound partial upper/lower bounds; small n only, not a production replacement',
  trust='Lean theorem checked separately; Python original-model translation/admission/cache not formally verified; no Comparator execution',
  freeze='Inputs, protocol, source and dependency hashes before headline execution; earlier Lean proof development recorded separately',
  stop='unsupported routes and capped builds remain explicit; do not relax proof obligations')
