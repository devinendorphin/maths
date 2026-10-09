import json,pathlib,random
r=pathlib.Path(__file__).resolve().parents[1];rng=random.Random(111120);rows=[]
for split,ns in [('training',[12,12]),('heldout',[18,18,20,20])]:
 for i,n in enumerate(ns):
  w=[rng.randint(1,15) for _ in range(n)]
  rows.append(dict(case_id=f'{split}-n{n}-{i}',split=split,n=n,weights=w,capacity=sum(w)//3,profits=[rng.randint(-10,30) for _ in w],slopes=[rng.randint(-3,3) for _ in w],end=8,observations=list(range(9))))
w=[rng.randint(1,15) for _ in range(18)];p=[rng.randint(1,20) for _ in w]
rows.append(dict(case_id='heldout-factor',split='heldout',n=18,weights=w,capacity=sum(w)//3,profits=p,slopes=p,end=8,observations=list(range(9))))
rows.append(dict(case_id='crossing',split='control',n=6,weights=[1,1,6,7,8,9],capacity=1,profits=[3,0,-1,-2,-3,-4],slopes=[0,2,0,0,0,0],end=4,observations=[0,1,2,3,4]))
(r/'Inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
