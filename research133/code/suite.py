"""Deterministic fixtures and held-out sequences; no result-dependent selection."""
import copy
import json
import random
from pathlib import Path


def transport(name, size, seed):
    rng = random.Random(seed)
    edges = [{'a': a, 'z': size+z, 'l': 0, 'u': 3, 'c': rng.randint(-3, 7)}
             for a in range(size) for z in range(size)]
    return {'id': name, 'n': 2*size, 'b': [2]*size+[-2]*size,
            'denominator': 2, 'edges': edges}


def sequences(base):
    streams = []
    size = base['n']//2
    for kind in ['small-cost', 'alternating-cost', 'feasibility']:
        models = []
        for step in range(9):
            m = copy.deepcopy(base)
            m['id'] = base['id']+'/'+kind+'/'+str(step)
            if kind == 'small-cost':
                m['edges'][0]['c'] += [0, 1, 2, 1, 0, 1, 0, 1, 0][step]
            elif kind == 'alternating-cost':
                m['edges'][0]['c'] = -9 if step % 2 == 0 else 9
            elif step == 1:
                m['edges'][0]['u'] = 1
            elif step == 2:
                m['b'][0], m['b'][1] = 3, 1
            elif step == 3:
                m['edges'][0]['l'] = 2
            elif step == 4:
                for e in m['edges'][:size]: e['u'] = 0
            elif step == 5:
                m['edges'][0]['l'] = 1
                m['b'][0], m['b'][1] = 1, 3
            elif step == 6:
                m['edges'][0]['u'] = 0
            elif step == 7:
                m['edges'][0]['l'] = 2
                m['b'][0], m['b'][1] = 1, 3
            models.append(m)
        streams.append({'id': base['id']+'/'+kind, 'models': models})
    return streams


def tiny():
    base = transport('tiny', 2, 1)
    for e, c in zip(base['edges'], [2, 8, 6, 2]):
        e['u'], e['c'] = 2, c
    fixtures = [copy.deepcopy(base)]
    def add(name, mutate):
        m = copy.deepcopy(base); m['id'] = name; mutate(m); fixtures.append(m)
    add('crossing', lambda m: [e.update(c=c) for e, c in zip(m['edges'], [2, 0, 2, 2])])
    add('tie', lambda m: [e.update(c=2) for e in m['edges']])
    add('lower', lambda m: m['edges'][0].update(l=1))
    add('capacity', lambda m: m['edges'][0].update(u=1))
    add('supply', lambda m: m.update(b=[3, 1, -2, -2]))
    add('infeasible-capacity', lambda m: [e.update(u=0) for e in m['edges'][:2]])
    add('infeasible-floor', lambda m: (m['edges'][0].update(l=2), m.update(b=[1, 3, -2, -2])))
    fixtures.append({'id': 'negative-cycle', 'n': 3, 'b': [1, 0, -1], 'denominator': 2,
                     'edges': [dict(a=a, z=z, l=0, u=u, c=c) for a,z,u,c in [(0,1,2,2),(1,2,2,2),(0,2,1,8),(2,0,1,-6)]]})
    fixtures.append({'id': 'self-loop', 'n': 2, 'b': [1,-1], 'denominator': 2,
                     'edges': [dict(a=0,z=1,l=0,u=2,c=2),dict(a=0,z=0,l=0,u=2,c=-3)]})
    fixtures.append({'id': 'parallel', 'n': 2, 'b': [1,-1], 'denominator': 2,
                     'edges': [dict(a=0,z=1,l=0,u=2,c=2),dict(a=0,z=1,l=0,u=2,c=1)]})
    return fixtures


def fair_cases():
    cases = []
    for k in range(8):
        # Two suppliers, three recipients, a sink, and explicit unused-supply arcs.
        supplies = [3, 3] if k < 4 else [2, 2]
        edges = [dict(a=a, z=2+r, l=0, u=3, c=[1,4,7,6,2,5][a*3+r]) for a in range(2) for r in range(3)]
        if k in (2, 6): edges[2]['u'] = edges[5]['u'] = 0
        floors = [0,0,0]
        if k in (1,5): floors = [1,1,1]
        if k in (3,7): floors = [3,3,3]
        edges += [dict(a=2+r,z=5,l=floors[r],u=d,c=0) for r,d in enumerate([3,4,5])]
        edges += [dict(a=a,z=5,l=0,u=supplies[a],c=0) for a in range(2)]
        cases.append({'id': 'fair-'+str(k), 'demands':[3,4,5], 'floors':floors,
                      'model':dict(id='fair-'+str(k),n=6,b=supplies+[0,0,0,-sum(supplies)],denominator=2,edges=edges)})
    return cases


def build():
    seed = 13320261009
    return {'seed':seed, 'static':tiny(),
            'development':[transport('D2',2,seed-2),transport('D3',3,seed-3)],
            'heldout':[s for size in [2,3,4,5] for s in sequences(transport('H'+str(2*size),size,seed+size))],
            'fairness':fair_cases(),
            'counterexample':{'costs':[-1,1,-1,1,-1,1], 'model':dict(id='counter',n=2,b=[1,-1],denominator=1,
              edges=[dict(a=0,z=1,l=0,u=1,c=0),dict(a=0,z=1,l=0,u=1,c=0)])}}


if __name__ == '__main__':
    (Path(__file__).resolve().parents[1]/'Inputs.json').write_text(json.dumps(build(),indent=2)+'\n')
