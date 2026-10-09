"""Independent oracle and audit calculations; never imports checker/producer."""
import itertools
from fractions import Fraction


def network_simplex(m):
    import networkx as nx
    g = nx.MultiDiGraph()
    demands = [-v for v in m['b']]
    constant = 0
    for i, e in enumerate(m['edges']):
        demands[e['a']] += e['l']; demands[e['z']] -= e['l']
        constant += e['c']*e['l']
        g.add_edge(e['a'],e['z'],key=i,capacity=e['u']-e['l'],weight=e['c'])
    for i,d in enumerate(demands):g.add_node(i,demand=d)
    try:
        value,flow = nx.network_simplex(g)
        return value+constant, [e['l']+flow[e['a']][e['z']][i] for i,e in enumerate(m['edges'])]
    except nx.NetworkXUnfeasible:
        return None, None


def enumerate_static(m):
    best, count = None, 0
    for x in itertools.product(*(range(e['l'],e['u']+1) for e in m['edges'])):
        count += 1
        b=[0]*m['n']
        for e,v in zip(m['edges'],x):b[e['a']]+=v;b[e['z']]-=v
        if b!=m['b']:continue
        value=sum(e['c']*v for e,v in zip(m['edges'],x))
        best=value if best is None else min(best,value)
    return best,count


def enumerate_fair(case):
    m,demands=case['model'],case['demands']
    best_rate,best_cost,scalar=None,None,None
    count=0
    for x in itertools.product(*(range(e['u']+1) for e in m['edges'][:6])):
        count+=1
        used=[sum(x[3*a:3*a+3]) for a in range(2)]
        served=[x[r]+x[3+r] for r in range(3)]
        if any(used[a]>m['b'][a] for a in range(2)):continue
        if any(not case['floors'][r]<=served[r]<=demands[r] for r in range(3)):continue
        cost=sum(e['c']*v for e,v in zip(m['edges'][:6],x))
        scalar=cost if scalar is None else min(scalar,cost)
        rate=min(Fraction(s,d) for s,d in zip(served,demands))
        if best_rate is None or rate>best_rate:best_rate,best_cost=rate,cost
        elif rate==best_rate:best_cost=min(best_cost,cost)
    return {'coverage':None if best_rate is None else str(best_rate),'cost_units':best_cost,'scalar_cost_units':scalar,'assignments':count}


def check_certificate(m,p):
    # Separate proof calculation, ignoring only binding fields checked elsewhere.
    if p['kind']=='cut':
        s=set(p['set'])
        b=sum(m['b'][v] for v in s)
        boundary=sum(e['u'] for e in m['edges'] if e['a'] in s and e['z'] not in s)-sum(e['l'] for e in m['edges'] if e['a'] not in s and e['z'] in s)
        return b>boundary
    x,pi=p['flow'],p['pi'];b=[0]*m['n']
    for e,v in zip(m['edges'],x):
        if not e['l']<=v<=e['u']:return False
        b[e['a']]+=v;b[e['z']]-=v
        if v<e['u'] and e['c']+pi[e['a']]-pi[e['z']]<0:return False
        if v>e['l'] and e['c']+pi[e['a']]-pi[e['z']]>0:return False
    return b==m['b'] and p['cost_units']==sum(e['c']*v for e,v in zip(m['edges'],x))
