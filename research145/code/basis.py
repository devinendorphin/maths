"""Cost-only persistent NetworkX 3.4.2 tree adapter, not an upstream API.

Pivot loop adapted from NetworkX (BSD-3-Clause), whose complete pinned source
and copyright/license accompany this experiment. All returned flows receive
separate exact residual-potential completion and certificate admission.
"""
import copy
import networkx as nx
from networkx.algorithms.flow.networksimplex import _DataEssentialsAndFunctions
from checker import validate


def fixed(m):
    value=copy.deepcopy(m)
    for e in value['edges']:e['c']=0
    return value


class Basis:
    def __init__(self,m):
        if not validate(m) or any(e['a']==e['z'] for e in m['edges']):
            raise ValueError('adapter requires validated loop-free finite model')
        self.m=copy.deepcopy(m);self.signature=fixed(m);self.total_pivots=0;self.last_pivots=0
        g=nx.MultiDiGraph();b=m['b'].copy()
        for v in range(m['n']):g.add_node(v)
        for i,e in enumerate(m['edges']):
            b[e['a']]-=e['l'];b[e['z']]+=e['l']
            g.add_edge(e['a'],e['z'],key=i,capacity=e['u']-e['l'],weight=e['c'])
        for v in range(m['n']):g.nodes[v]['demand']=-b[v]
        d=self.d=_DataEssentialsAndFunctions(g,True)
        self.mapping=[d.edge_indices.get((e['a'],e['z'],i)) for i,e in enumerate(m['edges'])]
        # One fixed envelope for all future allowed costs; never shrink it online.
        bound=3*max(sum(d.edge_capacities),max(1,len(d.edge_indices))*1000000,
                    max(abs(v) for v in d.node_demands),1)
        n=m['n'];self.artificial_bound=bound
        for i,v in enumerate(d.node_demands):
            d.edge_sources.append(-1 if v>0 else i);d.edge_targets.append(i if v>0 else -1)
        d.edge_weights.extend([bound]*n);d.edge_capacities.extend([bound]*n)
        d.initialize_spanning_tree(n,bound)

    def require_fixed(self,m):
        if not validate(m) or fixed(m)!=self.signature:raise ValueError('basis reset required')

    def change_costs(self,changes):
        seen=set()
        for z in changes:
            if not isinstance(z,dict) or set(z)!={'edge','old','new'} or any(type(z[k]) is not int for k in z):
                raise ValueError('invalid cost patch')
            i=z['edge']
            if i in seen or not 0<=i<len(self.m['edges']) or self.m['edges'][i]['c']!=z['old'] or abs(z['new'])>1000000:
                raise ValueError('invalid cost patch')
            seen.add(i)
        for z in changes:
            i=z['edge'];self.m['edges'][i]['c']=z['new'];j=self.mapping[i]
            if j is not None:self.d.edge_weights[j]=z['new']

    def tree_potentials(self):
        d=self.d
        for v in list(d.trace_subtree(-1))[1:]:
            parent=d.parent[v];e=d.parent_edge[v];pv=0 if parent==-1 else d.node_potentials[parent]
            d.node_potentials[v]=pv-d.edge_weights[e] if d.edge_sources[e]==parent else pv+d.edge_weights[e]

    def optimize(self):
        self.tree_potentials();d=self.d;self.last_pivots=0
        # Upstream pivot operations and entering/leaving rules, retained intact.
        for i,p,q in d.find_entering_edges():
            self.last_pivots+=1
            if self.last_pivots>100000:raise RuntimeError('declared pivot guard')
            nodes,edges=d.find_cycle(i,p,q);j,s,t=d.find_leaving_edge(nodes,edges)
            d.augment_flow(nodes,edges,d.residual_capacity(j,s))
            if i!=j:
                if d.parent[t]!=s:s,t=t,s
                if edges.index(i)>edges.index(j):p,q=q,p
                d.remove_edge(s,t);d.make_root(q);d.add_edge(i,p,q);d.update_potentials(i,p,q)
        self.total_pivots+=self.last_pivots
        if any(d.edge_flow[i]!=0 for i in range(d.edge_count,len(d.edge_flow))):
            raise nx.NetworkXUnfeasible('retained artificial flow')
        return [e['l']+(d.edge_flow[j] if j is not None else 0) for e,j in zip(self.m['edges'],self.mapping)]
