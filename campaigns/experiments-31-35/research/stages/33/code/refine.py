"""Refine only uncertified cells, branching on fractional relaxed items."""
from fractions import Fraction
import horizon as H
from renewal import reprice

def greedy(cell,w,q):
    fixed,free,r,*_=cell;mask=fixed;pivot=None
    items=sorted((i for i in range(len(w)) if free>>i&1 and q[i]>0),key=lambda i:(-Fraction(q[i],w[i]),i))
    for i in items:
        if r>=w[i]:mask|=1<<i;r-=w[i]
        elif r>0:pivot=i;break
        else:break
    return mask,pivot

def repair(proof,w,q,chosen):
    target=H.value(q,chosen);out=[];origins=[];trace=[];evaluations=0;retained=[];max_depth=0
    for origin,root in enumerate(proof):
        if root[5]//root[4]<=target:
            out.append(list(root));origins.append(origin);retained.append(origin);continue
        stack=[(list(root),0)]
        while stack:
            cell,depth=stack.pop();max_depth=max(max_depth,depth)
            priced,n=reprice(cell,w,q);evaluations+=n
            if priced[5]//priced[4]<=target:
                out.append(priced);origins.append(origin);continue
            witness,pivot=greedy(priced,w,q)
            if pivot is None:
                assert H.value(q,witness)>target
                return dict(success=False,witness=witness,trace=trace,splits=len(trace),evaluations=evaluations,max_depth=max_depth)
            fixed,free,residual,*_=priced;bit=1<<pivot;children=[[fixed,free^bit,residual,0,1,0]]
            if w[pivot]<=residual:children.append([fixed|bit,free^bit,residual-w[pivot],0,1,0])
            trace.append(dict(origin=origin,depth=depth,fixed=fixed,free=free,residual=residual,pivot=pivot,children=[x[:3] for x in children]))
            stack.extend((x,depth+1) for x in reversed(children))
    return dict(success=True,proof=out,origins=origins,retained=retained,trace=trace,splits=len(trace),evaluations=evaluations,max_depth=max_depth)
