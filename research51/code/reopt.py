"""Controlled exact branch-and-bound with incumbent/terminal-partition reuse.

This is a literature-inspired reference implementation, not SCIP or the original
generator. All modes use the same rational bound, branch rule and root heuristic.
"""
from fractions import Fraction
import time
from shared import value


class Guard(Exception):
    pass


def optimize(row,t,domains=None,incumbent=0):
    w=row['weights']; q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]; c=row['capacity']
    n=len(w); full=(1<<n)-1; nodes=sort_terms=0; splits=[]; leaves=[]
    best=value(q,incumbent); mask=incumbent
    def bound(f,u,r):
        nonlocal nodes,sort_terms,best,mask
        nodes+=1
        if nodes>120000: raise Guard('node cap')
        order=sorted([i for i in range(n) if u>>i&1 and q[i]>0],key=lambda i:(-Fraction(q[i],w[i]),i))
        sort_terms+=len(order); residual=r; chosen=f; upper=Fraction(value(q,f)); pivot=None
        for i in order:
            if w[i]<=residual:
                residual-=w[i]; chosen|=1<<i; upper+=q[i]
            else:
                if residual>0: upper+=Fraction(q[i]*residual,w[i]); pivot=i
                break
        candidate=value(q,chosen)
        if candidate>best or candidate==best and chosen<mask: best,mask=candidate,chosen
        return upper.numerator//upper.denominator,pivot
    # Identical root heuristic, even when the saved frontier supplies subproblems.
    bound(0,full,c)
    stack=list(reversed(domains or [[0,full,c]]))
    while stack:
        f,u,r=stack.pop(); upper,pivot=bound(f,u,r)
        if upper<=best:
            leaves.append([f,u,r])
            if len(leaves)+len(stack)>4096: raise Guard('terminal-partition cap')
            continue
        assert pivot is not None
        bit=1<<pivot; children=[[f,u^bit,r]]
        if w[pivot]<=r: children.append([f|bit,u^bit,r-w[pivot]])
        splits.append(dict(domain=[f,u,r],pivot=pivot,children=children))
        stack.extend(reversed(children))
    return dict(time=t,packing=mask,objective=best,domains=leaves,split_trace=splits,
                nodes=nodes,sort_terms=sort_terms)


def sequence(row,mode):
    start=time.process_time(); retained=None; mask=0; solves=[]
    for t in row['solve_times']:
        r=optimize(row,t,retained if mode=='tree' else None,mask if mode!='cold' else 0)
        solves.append(r); mask=r['packing']; retained=r['domains']
    return dict(method='reopt_'+mode,algorithm_cpu=time.process_time()-start,solves=solves,
                nodes=sum(x['nodes'] for x in solves),sort_terms=sum(x['sort_terms'] for x in solves),
                peak_terminal_cells=max(len(x['domains']) for x in solves),
                scope='Exact controlled reference implementation; not a SCIP measurement')
