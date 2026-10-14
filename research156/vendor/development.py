"""Disjoint mixed pilots and exhaustive tiny directed integer-flow checks."""
import copy
import itertools
import json
import random
from pathlib import Path
from checker import digest
from controls import run as controls
from engine import Engine, ROUTES
from suite import make


def run():
    ctx='development-only';observations=0;actions={}
    for entry in make()['development']:
        answers=[]
        for route in ROUTES:
            e=Engine(entry['model'],ctx,route);per=[]
            for q in [None]+[dict(copy.deepcopy(z['message']),context=ctx) for z in entry['updates']]:
                r=e.query(q);p=r['proof'];per.append(p.get('cost_units'));observations+=1
                actions[r['action']]=actions.get(r['action'],0)+1
            e.close();answers.append(per)
        assert all(a==answers[0] for a in answers)
    rng=random.Random(913148);exhaustive=[]
    for k in range(48):
        n=2 if k%2==0 else 3
        pairs=[(0,1),(1,0),(0,1),(1,1)] if n==2 else [(0,1),(1,2),(2,0),(1,1)]
        edges=[]
        for a,z in pairs:
            u=rng.randrange(3);l=rng.randrange(u+1)
            edges.append({'a':a,'z':z,'l':l,'u':u,'c':rng.randrange(-3,4)})
        b=[0]*n;b[0]=rng.randrange(-2,3);b[-1]=-b[0]
        m={'id':f'exhaustive-{k}','n':n,'b':b,'denominator':1,'edges':edges};values=[]
        for x in itertools.product(*(range(e['l'],e['u']+1) for e in edges)):
            bal=[0]*n
            for edge,v in zip(edges,x):bal[edge['a']]+=v;bal[edge['z']]-=v
            if bal==b:values.append(sum(e['c']*v for e,v in zip(edges,x)))
        optimum=min(values) if values else None
        for route in ROUTES:
            engine=Engine(m,ctx,route);assert engine.query()['proof'].get('cost_units')==optimum;engine.close();observations+=1
        exhaustive.append({'model':m,'optimum':optimum,'feasible_assignments':len(values)})
    return {'passed':True,'excluded_from_headline':True,'pilot_observations':1764,'total_observations':observations,
            'actions':actions,'exhaustive':exhaustive,'controls':controls(ctx)}


if __name__=='__main__':
    result=run();p=Path(__file__).resolve().parents[1]/'Development.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('Passed',result['total_observations'],'disjoint development observations and',len(result['controls']['controls']),'controls')
