"""Bounded exact feasible-flow repair and negative-cycle cancellation."""
from collections import deque
from checker import digest


class Budget(Exception):
    pass


def residual(m, x):
    arcs = []
    for i, (e, v) in enumerate(zip(m['edges'], x)):
        if v < e['u']:
            arcs.append((e['a'], e['z'], e['c'], e['u'] - v, i, 1))
        if v > e['l']:
            arcs.append((e['z'], e['a'], -e['c'], v - e['l'], i, -1))
    return arcs


def feasibility(m, initial=None, counters=None):
    counters = counters if counters is not None else {}
    x = [e['l'] for e in m['edges']] if initial is None else [max(e['l'], min(e['u'], v)) for e, v in zip(m['edges'], initial)]
    imbalance = m['b'].copy()
    for e, v in zip(m['edges'], x):
        imbalance[e['a']] -= v
        imbalance[e['z']] += v
    n, source, sink = m['n'] + 2, m['n'], m['n'] + 1
    graph = [[] for _ in range(n)]

    def add(a, z, cap):
        f, r = [z, len(graph[z]), cap], [a, len(graph[a]), 0]
        # Self loops require the forward index to refer to the following arc.
        if a == z:
            f[1] += 1
        graph[a].append(f)
        graph[z].append(r)
        return f

    records = []
    for a, z, _, cap, i, sign in residual(m, x):
        records.append((add(a, z, cap), cap, i, sign))
    required = 0
    for v, amount in enumerate(imbalance):
        if amount > 0:
            add(source, v, amount)
            required += amount
        elif amount < 0:
            add(v, sink, -amount)
    sent, augmentations = 0, 0
    while sent < required:
        pred = [None] * n
        seen = {source}
        queue = deque([source])
        while queue and sink not in seen:
            a = queue.popleft()
            for e in graph[a]:
                if e[2] > 0 and e[0] not in seen:
                    seen.add(e[0])
                    pred[e[0]] = (a, e)
                    queue.append(e[0])
        if sink not in seen:
            counters['augmentations'] = augmentations
            return None, sorted(v for v in seen if v < m['n'])
        amount = required - sent
        v = sink
        while v != source:
            a, e = pred[v]
            amount = min(amount, e[2])
            v = a
        v = sink
        while v != source:
            a, e = pred[v]
            e[2] -= amount
            graph[v][e[1]][2] += amount
            v = a
        sent += amount
        augmentations += 1
        if augmentations > 10000:
            raise Budget('augmentation limit')
    for e, capacity, i, sign in records:
        x[i] += sign * (capacity - e[2])
    counters['augmentations'] = augmentations
    return x, None


def potentials(m, x, counters=None):
    arcs, n = residual(m, x), m['n']
    d, pred = [0] * n, [None] * n
    for _ in range(n):
        changed = None
        for edge in arcs:
            a, z, cost, _, _, _ = edge
            if counters is not None:
                counters['relaxations'] = counters.get('relaxations', 0) + 1
            if d[z] > d[a] + cost:
                d[z], pred[z], changed = d[a] + cost, edge, z
        if changed is None:
            return d, None
    v = changed
    for _ in range(n):
        v = pred[v][0]
    start, cycle = v, []
    while True:
        e = pred[v]
        cycle.append(e)
        v = e[0]
        if v == start:
            break
        assert len(cycle) <= n
    assert sum(e[2] for e in cycle) < 0
    return None, cycle


def certificate(m, dependency, flow=None, pi=None, cut=None):
    base = {'model': digest(m), 'dependency': dependency}
    if cut is not None:
        return dict(base, kind='cut', set=cut)
    return dict(base, kind='optimal', flow=flow, pi=pi,
                cost_units=sum(e['c'] * v for e, v in zip(m['edges'], flow)))


def optimize(m, x, dependency, counters, timing=None):
    import time
    cycles = 0
    while True:
        start = time.perf_counter()
        pi, cycle = potentials(m, x, counters)
        if timing is not None:
            key = 'proof_s' if cycle is None else 'solver_s'
            timing[key] = timing.get(key, 0) + time.perf_counter()-start
        if cycle is None:
            counters['cycles'] = cycles
            start = time.perf_counter()
            p = certificate(m, dependency, flow=x, pi=pi)
            if timing is not None:
                timing['proof_s'] = timing.get('proof_s', 0) + time.perf_counter()-start
            return p
        if cycles >= 1000:
            raise Budget('negative-cycle cancellation limit')
        start = time.perf_counter()
        amount = min(e[3] for e in cycle)
        for _, _, _, _, i, sign in cycle:
            x[i] += sign * amount
        cycles += 1
        if timing is not None:
            timing['solver_s'] = timing.get('solver_s', 0) + time.perf_counter()-start


def networkx_flow(m):
    import networkx as nx
    g = nx.MultiDiGraph()
    balance = m['b'].copy()
    constant = 0
    for i, e in enumerate(m['edges']):
        balance[e['a']] -= e['l']
        balance[e['z']] += e['l']
        constant += e['c'] * e['l']
        g.add_edge(e['a'], e['z'], key=i, capacity=e['u']-e['l'], weight=e['c'])
    for v, b in enumerate(balance):
        g.add_node(v, demand=-b)
    try:
        value, f = nx.network_simplex(g)
        x = [e['l'] + f[e['a']][e['z']][i] for i, e in enumerate(m['edges'])]
        return value + constant, x
    except nx.NetworkXUnfeasible:
        return None, None
