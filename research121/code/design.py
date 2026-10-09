import json
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    rows=[]
    for name,n,seed in [('train8',8,30121),('train10',10,30122),('eval8',8,48121),('eval10',10,48122),('eval12',12,48123),('factor12',12,48124)]:
        rng=random.Random(seed);w=[rng.randint(2,10) for _ in range(n)];p=[rng.randint(-4,18) for _ in range(n)];v=[rng.randint(-3,3) for _ in range(n)]
        if name=='factor12':p=[rng.randint(1,14) for _ in range(n)];v=p.copy()
        rows.append(dict(case_id=name,split='training' if name.startswith('train') else 'heldout',n=n,seed=seed,weights=w,profits=p,slopes=v,capacity=2*sum(w)//5,end=6))
    rows.append(dict(case_id='crossing',split='control',n=3,weights=[1,1,2],profits=[3,0,-1],slopes=[0,2,0],capacity=1,end=6))
    p=ROOT/'Inputs.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':main()
