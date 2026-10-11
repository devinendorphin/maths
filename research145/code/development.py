"""Excluded general directed multigraph checks and mixed-session pilot."""
import copy
import random
from basis import Basis
from checker import verify
from producer import networkx_flow
from worker import proof


def run():
    records=[]
    for seed in range(20):
        rng=random.Random(916145+seed);n=2+seed%9;edges=[];balance=[0]*n
        for i in range(n*3):
            a=rng.randrange(n);z=(a+rng.randrange(1,n))%n;l=rng.randrange(3);u=l+rng.randrange(5)
            x=rng.randint(l,u);balance[a]+=x;balance[z]-=x
            edges.append({'a':a,'z':z,'l':l,'u':u,'c':rng.randint(-9,9)})
        m={'id':'development-'+str(seed),'n':n,'b':balance,'denominator':1,'edges':edges};s=Basis(m)
        for step in range(9):
            if step:
                i=rng.randrange(len(edges));z={'edge':i,'old':m['edges'][i]['c'],'new':rng.randint(-15,15)}
                s.change_costs([z]);m['edges'][i]['c']=z['new']
            x=s.optimize();p=proof(m,x,'development-only');value,_=networkx_flow(m)
            assert p['cost_units']==value and verify(m,p,'development-only')
            records.append({'seed':seed,'step':step,'value':value,'pivots':s.last_pivots})
    return {'excluded_from_headline':True,'general_directed_multigraph_observations':len(records),'records':records,'passed':True}


if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
