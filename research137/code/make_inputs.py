"""Deterministic input construction; run before freezing validation inputs."""
import copy,json,random
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def model(name,n,edges,flow):
    b=[0]*n
    out=[]
    for (a,z,l,u,c),x in zip(edges,flow):
        b[a]+=x;b[z]-=x
        out.append(dict(a=a,z=z,l=l,u=u,c=str(Fraction(c))))
    return dict(id=name,n=n,b=b,edges=out)


def build():
    fixtures=[
        model('parallel-proof-gap',2,[(0,1,0,1,0),(0,1,0,1,2)],[1,0]),
        model('interior-bridge',2,[(0,1,0,3,7)],[1]),
        model('fixed-edge',2,[(0,1,2,2,-3)],[2]),
        model('loops',2,[(0,0,0,2,-2),(1,1,0,2,3),(0,1,0,1,1)],[2,0,1]),
        model('rational-lower-parallel',3,[(0,1,1,2,'-1/2'),(0,1,0,2,'3/2'),(1,2,1,2,'2/3'),(0,2,0,2,'5/3')],[1,0,1,0]),
        model('disconnected-components',4,[(0,1,0,2,-3),(0,1,0,2,1),(2,3,0,2,'1/3')],[1,0,1]),
        model('tied-interior',2,[(0,1,0,2,1),(0,1,0,2,1)],[1,1]),
    ]
    rng=random.Random(13720261018)
    for k in range(24):
        n=rng.randint(2,4);count=rng.randint(2,7);edges=[];flow=[]
        for _ in range(count):
            a,z=rng.randrange(n),rng.randrange(n)
            l=rng.randrange(2);u=l+rng.randrange(3)
            edges.append((a,z,l,u,f'{rng.randint(-6,6)}/{rng.randint(1,4)}'))
            flow.append(rng.randint(l,u))
        fixtures.append(model(f'seeded-{k:02d}',n,edges,flow))
    old=json.loads((ROOT/'research133/Inputs.json').read_text())
    held=[];seen=set()
    for stream in old['heldout']:
        m=stream['models'][0]
        # One base from each named graph family; streams share the same base.
        key=json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True)
        if key in seen:continue
        seen.add(key);new=copy.deepcopy(m);den=new.pop('denominator')
        from fractions import Fraction
        for e in new['edges']:e['c']=str(Fraction(e['c'],den))
        held.append(new)
    return {'seed':13720261018,'tiny':fixtures,'heldout':held,
            'policy':'Tiny inputs are finite validation; heldout means inherited from research133, not newly unseen model families.'}

if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'Inputs.json'
    assert not path.exists(),'Refuse to replace frozen inputs'
    path.write_text(json.dumps(build(),indent=2)+'\n')
