"""Independent rational witness evaluation; imports no optimizer/producer.
Uses edge-by-edge balances, shortest-path dual inequalities and explicit paths.
"""
from fractions import Fraction as Q
from itertools import product


def valid_model(m):
    try:
        if set(m)!={"id","n","b","edges"} or not isinstance(m["id"],str):return False
        if type(m["n"]) is not int or m["n"]<1 or len(m["b"])!=m["n"]:return False
        if any(type(v) is not int for v in m["b"]) or sum(m["b"])!=0:return False
        for e in m["edges"]:
            if set(e)!={"a","z","l","u","c"} or any(type(e[k]) is not int for k in ("a","z","l","u")):return False
            if not 0<=e["a"]<m["n"] or not 0<=e["z"]<m["n"] or not 0<=e["l"]<=e["u"]:return False
            if not isinstance(e["c"],str) or str(Q(e["c"]))!=e["c"]:return False
        return True
    except (ValueError,TypeError,KeyError,IndexError,ZeroDivisionError):return False


def feasible(m,x):
    if len(x)!=len(m['edges']) or any(type(v) is not int for v in x):return False
    b=[0]*m['n']
    for e,v in zip(m['edges'],x):
        if not e['l']<=v<=e['u']:return False
        b[e['a']]+=v;b[e['z']]-=v
    return b==m['b']


def value(m,x):return sum((Q(e['c'])*v for e,v in zip(m['edges'],x)),Q(0))


def optimal(m,x,pi):
    try:
        if not valid_model(m) or not feasible(m,x) or len(pi)!=m['n']:return False
        for e,v in zip(m['edges'],x):
            r=Q(e['c'])+Q(pi[e['a']])-Q(pi[e['z']])
            if v<e['u'] and r<0 or v>e['l'] and r>0:return False
        return True
    except (ValueError,TypeError,KeyError,IndexError,ZeroDivisionError):return False


def return_proof(m,x,i,proof,source,target):
    if proof['source']!=source or proof['target']!=target:return False
    d=[None if v is None else Q(v) for v in proof['labels']]
    if len(d)!=m['n'] or d[source]!=0:return False
    # All outgoing arcs from the claimed reachable set stay inside it.
    # Triangle inequalities lower-bound every source-target walk by d[target].
    for j,(e,v) in enumerate(zip(m['edges'],x)):
        if j==i:continue
        for a,z,c,active in [(e['a'],e['z'],Q(e['c']),v<e['u']),
                             (e['z'],e['a'],-Q(e['c']),v>e['l'])]:
            if active and d[a] is not None and (d[z] is None or d[z]>d[a]+c):return False
    if d[target] is None:return proof['path'] is None
    if proof['path'] is None:return False
    node=source;cost=Q(0);seen={node}
    for j,s in proof['path']:
        if type(j) is not int or j==i or not 0<=j<len(m['edges']) or s not in (-1,1):return False
        e=m['edges'][j]
        a,z=(e['a'],e['z']) if s==1 else (e['z'],e['a'])
        if a!=node or (s==1 and x[j]>=e['u']) or (s==-1 and x[j]<=e['l']):return False
        if z in seen:return False
        seen.add(z);node=z;cost+=s*Q(e['c'])
    return node==target and cost==d[target]


def interval(m,x,p):
    try:
        if not feasible(m,x):return False
        i=p['edge']
        if type(i) is not int or not 0<=i<len(m['edges']):return False
        e=m['edges'][i];c=Q(e['c'])
        for field,active,s,t,key,sgn in [
            ('forward_return',x[i]<e['u'],e['z'],e['a'],'lower',-1),
            ('reverse_return',x[i]>e['l'],e['a'],e['z'],'upper',1)]:
            w=p[field]
            if not active:
                if w is not None or p[key] is not None:return False
            else:
                if not return_proof(m,x,i,w,s,t):return False
                d=w['labels'][t]
                expected=None if d is None else sgn*Q(d)-c
                if (p[key] is None)!=(expected is None):return False
                if expected is not None and Q(p[key])!=expected:return False
        return True
    except (ValueError,TypeError,KeyError,IndexError,ZeroDivisionError):return False


def enumerate_flows(m):
    return [list(x) for x in product(*(range(e['l'],e['u']+1) for e in m['edges'])) if feasible(m,x)]


def exhaustive_interval(m,x,i,flows):
    """Compare directly with every feasible competitor; no residual/path logic."""
    low=high=None;base=value(m,x)
    for y in flows:
        diff=y[i]-x[i];gap=value(m,y)-base
        if diff==0:
            assert gap>=0
        elif diff>0:
            v=-gap/diff;low=v if low is None else max(low,v)
        else:
            v=-gap/diff;high=v if high is None else min(high,v)
    return None if low is None else str(low),None if high is None else str(high)


def admit_interval(m,x,pi,p):
    """The base optimum is mandatory: a local path proof alone is insufficient."""
    return optimal(m,x,pi) and interval(m,x,p)
