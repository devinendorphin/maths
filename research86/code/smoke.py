"""Disjoint pre-freeze implementation controls, never used to select inputs."""
from pathlib import Path
import tempfile,random
import certificates,theories,checker,economy
from checker import Checker

def run():
 saved=[certificates.ROOT,theories.ROOT,checker.ROOT];checks=0
 with tempfile.TemporaryDirectory(dir='/tmp',prefix='maths86-smoke-') as folder:
  certificates.ROOT=theories.ROOT=checker.ROOT=Path(folder)
  try:
   for seed in range(4):
    rng=random.Random(3868600+seed);row=dict(stage=-1,case_id=f'smoke{seed}',n=6,seed=seed,weights=[rng.randint(1,9) for _ in range(6)],profits=[rng.randint(-5,20) for _ in range(6)],slopes=[rng.randint(-3,3) for _ in range(6)],capacity=15,end=5,observations=list(range(6)))
    for method in ('interval','gap','subset','expiry','integrity','epochs'):
     r=theories.DISPATCH[method](row);assert Checker(row).run(row,r)['passed'];checks+=1
    for method in ('points','envelope','guarded','factor'):
     r=economy.run(row,method);assert Checker(row).run(row,r)['passed'];checks+=1
    quad=dict(row,quadratic=[rng.randint(-2,2) for _ in range(6)]);r=theories.curvature(quad);assert Checker(quad).run(quad,r)['passed'];checks+=1
   for intercept in (1,10):
    row=dict(stage=-1,case_id='smoke-quadratic-'+str(intercept),n=2,weights=[1,1],profits=[intercept,0],slopes=[0,8],quadratic=[0,-4],capacity=1,end=2,observations=[0,1,2]);r=theories.curvature(row);assert Checker(row).run(row,r)['passed'];assert r['naive_same_endpoint'] and r['exact_margin_certified']==(intercept==10);checks+=1
  finally:certificates.ROOT,theories.ROOT,checker.ROOT=saved
 return dict(passed=True,fixtures=6,checks=checks,selection_use=False,disjoint_random_seeds=True)
if __name__=='__main__':print(run())
