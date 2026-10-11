"""Six fresh mixed streams; development inputs explicitly disjoint."""
import copy
import random
from checker import digest


def model(n, family, seed):
    rng = random.Random(seed)
    edges = []
    if family == 'transport':
        h = n//2
        for a in range(h):
            for z in (h+a, h+(a+1)%h, h+(a+3)%h):
                edges.append({'a': a, 'z': z, 'l': 0, 'u': 12, 'c': rng.randrange(-4, 17)})
        x = [2 if i%3 == 0 else 0 for i in range(len(edges))]
    else:
        # Backbone, reverse arcs, random directed chords, parallel arc and self-loop.
        pairs = [(a,(a+1)%n) for a in range(n)] + [((a+1)%n,a) for a in range(n)]
        pairs += [(rng.randrange(n),rng.randrange(n)) for _ in range(4*n-2)]
        pairs += [(0,1),(1,1)]
        edges = [{'a':a,'z':z,'l':0,'u':12,'c':rng.randrange(-6,17)} for a,z in pairs]
        x = [2 if i == 0 else 0 for i in range(len(edges))]
    b = [0]*n
    for e,v in zip(edges,x):
        b[e['a']] += v; b[e['z']] -= v
    return {'id':f'{family}-{n}-{seed}', 'n':n, 'b':b, 'denominator':1, 'edges':edges}


def stream(n, family, seed, steps=24):
    base = model(n,family,seed); m = copy.deepcopy(base); rng = random.Random(seed+12345); updates=[]
    for step in range(1,steps+1):
        new = copy.deepcopy(m); kind = 'cost'
        if step in (3,9):
            # Some selected used arcs will necessarily be cut below previous flow;
            # the audit records actual intersections instead of assuming this.
            i = 0 if step == 3 else 1
            new['edges'][i]['u'] = 1; kind = 'capacity-reduction'
        elif step in (5,11):
            a,z = (0,n//2) if family == 'transport' else (0,1)
            new['b'][a] += 2; new['b'][z] -= 2; kind = 'balanced-needs'
        elif step in (7,13):
            i = 2 if step == 7 else 3
            new['edges'][i]['l'] = 1; kind = 'lower-bound'
        elif step == 15:
            # Guaranteed shortage at node 0 independent of the route's chosen plan.
            new['b'][0] += 10000; new['b'][1] -= 10000; kind = 'forced-shortage'
        elif step == 17:
            new['b'][0] -= 10000; new['b'][1] += 10000; kind = 'restore-needs'
        elif step == 19:
            for e in new['edges'][:4]:
                e['u'] = 14
            kind = 'capacity-increase'
        elif step == 21:
            for e in new['edges'][:4]:
                e['l'] = 0
            kind = 'restore-lower'
        else:
            for i in rng.sample(range(len(m['edges'])),4):
                new['edges'][i]['c'] += rng.choice([-4,-2,2,4])
        changes = [{'edge':i,'field':field,'old':e[field],'new':new['edges'][i][field]}
                   for i,e in enumerate(m['edges']) for field in ('l','u','c') if e[field] != new['edges'][i][field]]
        balances = [{'node':v,'old':old,'new':new['b'][v]} for v,old in enumerate(m['b']) if old != new['b'][v]]
        updates.append({'kind':kind,'message':{'version':step-1,'old_model':digest(m),'edges':changes,'balances':balances}})
        m = new
    return {'model':base,'family':family,'updates':updates}


def make():
    return {'heldout':[stream(n,f,148000+n+(1000 if f=='cyclic' else 0)) for f in ('transport','cyclic') for n in (16,32,64)],
            'development':[stream(n,f,915148+n+(1000 if f=='cyclic' else 0)) for f in ('transport','cyclic') for n in (6,10,20)]}
