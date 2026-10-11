"""Deterministic development / held-out suites without calls to a solver."""
import copy
import random


def model(size, dense, seed):
    rng = random.Random(seed)
    edges = []
    for a in range(size):
        targets = range(size) if dense else sorted({a, (a+1)%size, (a+3)%size, (a+5)%size})
        for z in targets:
            edges.append({'a': a, 'z': size+z, 'l': 0, 'u': 3,
                          'c': -5 if a == z else rng.randint(3, 9)})
    return {'id': f'{size}-{dense}-{seed}', 'n': size*2, 'b': [2]*size+[-2]*size,
            'denominator': 3, 'edges': edges}


def stream(m, seed):
    rng = random.Random(seed)
    cur = copy.deepcopy(m)
    deltas = []
    off = [i for i,e in enumerate(m['edges']) if e['a'] + m['n']//2 != e['z']]
    diag = [i for i,e in enumerate(m['edges']) if e['a'] + m['n']//2 == e['z']]
    for step in range(24):
        k = [1,4,8][step%3]
        ids = rng.sample(off, min(k,len(off)))
        if step in (7,15,23):
            ids[0] = diag[(step//8)%len(diag)]
        changes = []
        for i in ids:
            old = cur['edges'][i]['c']
            new = 30 if i in diag else old+1
            changes.append({'edge':i, 'old':old, 'new':new})
            cur['edges'][i]['c'] = new
        deltas.append(changes)
    return deltas


def suite():
    heldout = []
    for dense in (False, True):
        for size in (8,24,64):
            seed = 137000 + size + 1000*int(dense)
            m = model(size,dense,seed)
            heldout.append({'model':m, 'changes':stream(m,seed+31)})
    dev = model(6,False,9127)
    return {'heldout':heldout, 'development':{'model':dev,'changes':stream(dev,999)},
            'policy': 'fixed needs and eligibility; cost-only stream, no fairness claim'}
