"""Exact single-edge sensitivity producer. All costs are rational strings.
No solver is imported by the independent checker in audit.py.
"""
from fractions import Fraction as Q
import copy


def arcs(model, flow, omit=None):
    out=[]
    for i,(edge,x) in enumerate(zip(model['edges'],flow)):
        if i == omit: continue
        a,z,l,u,c=edge['a'],edge['z'],edge['l'],edge['u'],Q(edge['c'])
        if x < u: out.append((a,z,c,i,1))
        if x > l: out.append((z,a,-c,i,-1))
    return out


def shortest(model, flow, omit, source, target):
    residual=arcs(model,flow,omit)
    n=model['n'];d=[None]*n;d[source]=Q(0)
    # Synchronous distances and explicit paths avoid predecessor cycles at ties.
    paths=[None]*n;paths[source]=[]
    for _ in range(n-1):
        new=d.copy();newpaths=copy.deepcopy(paths)
        for a,z,c,i,sign in residual:
            if d[a] is not None and (new[z] is None or d[a]+c < new[z]):
                new[z]=d[a]+c;newpaths[z]=paths[a]+[[i,sign]]
        if new==d: break
        d,paths=new,newpaths
    for a,z,c,_,_ in residual:
        assert d[a] is None or (d[z] is not None and d[z] <= d[a]+c), 'negative cycle or incomplete shortest distances'
    return {'source':source,'target':target,
            'labels':[None if x is None else str(x) for x in d],
            'path':paths[target]}


def interval(model, flow, edge_id):
    e=model['edges'][edge_id];x=flow[edge_id];c=Q(e['c'])
    forward=shortest(model,flow,edge_id,e['z'],e['a']) if x < e['u'] else None
    reverse=shortest(model,flow,edge_id,e['a'],e['z']) if x > e['l'] else None
    df=None if forward is None else forward['labels'][e['a']]
    dr=None if reverse is None else reverse['labels'][e['z']]
    return {'edge':edge_id,'lower':None if df is None else str(-c-Q(df)),
            'upper':None if dr is None else str(Q(dr)-c),
            'forward_return':forward,'reverse_return':reverse}


def changed_model(model, changes):
    out=copy.deepcopy(model)
    for i,delta in changes.items():out['edges'][i]['c']=str(Q(out['edges'][i]['c'])+Q(delta))
    return out


def potential(model, flow):
    residual=arcs(model,flow);n=model['n'];d=[Q(0)]*n
    for _ in range(n):
        new=d.copy()
        for a,z,c,_,_ in residual:new[z]=min(new[z],d[a]+c)
        if new==d:return [str(x) for x in d]
        d=new
    raise ValueError('flow is no longer optimal')


def boundary_competitor(model, flow, proof, side):
    i=proof['edge'];sign=1 if side=='lower' else -1
    path=proof['forward_return' if sign==1 else 'reverse_return']['path']
    cycle=[[i,sign]]+path
    amount=min(model['edges'][j]['u']-flow[j] if s==1 else flow[j]-model['edges'][j]['l'] for j,s in cycle)
    out=flow.copy()
    for j,s in cycle:out[j]+=amount*s
    return {'flow':out,'amount':amount,'cycle':cycle}
