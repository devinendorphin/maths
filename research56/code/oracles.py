"""Exact lexicographic knapsack oracles, prospective work caps and input gate.

Primary objective is scaled integer profit; secondary is signed slope; tertiary
is the smallest mask. None of these algorithms calls the independent checker.
"""
from fractions import Fraction
import math
import time
from shared import value,frac,digest

LIMITS=dict(dense_cells=100000,dp_transitions=1500000,sparse_states=30000,bb_nodes=30000,
            bb_cells=4096,oracle_cpu=15)


class Cap(Exception):
    def __init__(self,reason,record):super().__init__(reason);self.record=record


def prepare(row,normalize=False):
    result=dict(row);w=list(row['weights']);g=math.gcd(*w) if normalize else 1
    result['weights']=[x//g for x in w];result['capacity']=row['capacity']//g
    return result,dict(gcd=g,gcd_terms=len(w) if normalize else 0,divisions=len(w)+1 if normalize else 0)


def gate(row):
    normalized,features=prepare(row,True)
    c=normalized['capacity'];n=row['n']
    method='dense' if c<=4096 else 'sparse' if n<=16 else 'bb'
    return normalized,method,dict(features,normalized_capacity=c,n=n,comparisons=2)


def solve(row,t,method='dense',side=1,normalize=False,limits=None,domains=None,incumbent=0):
    start=time.process_time();lim=dict(LIMITS,**(limits or {}));t=Fraction(t)
    if method=='gate':data,kernel,features=gate(row)
    else:data,features=prepare(row,normalize);kernel=method
    w,p,v,c=(data[k] for k in ('weights','profits','slopes','capacity'));n=len(w)
    q=[t.denominator*a+t.numerator*b for a,b in zip(p,v)]
    ct=dict(transitions=0,states_peak=0,nodes=0,sorted_terms=0,terminal_peak=0)
    record=dict(time=frac(t),side=side,kernel=kernel,normalization=features,counts=ct,complete=False)
    def guard(reason):
        record['algorithm_cpu']=time.process_time()-start
        raise Cap(reason,record)
    def reserve(key,limit):
        if ct[key]>=lim[limit]:guard(limit+' cap')
        ct[key]+=1
        if ct[key]%2048==0 and time.process_time()-start>=lim['oracle_cpu']:guard('oracle CPU cap')
    if kernel=='dense':
        if c+1>lim['dense_cells']:guard('dense cell allocation cap')
        dp=[(0,0,0)]*(c+1);ct['states_peak']=c+1
        for j,(wi,qi,vi) in enumerate(zip(w,q,v)):
            for r in range(c,wi-1,-1):
                reserve('transitions','dp_transitions');a=dp[r-wi]
                candidate=(a[0]+qi,a[1]+side*vi,a[2]-(1<<j))
                if candidate>dp[r]:dp[r]=candidate
        mask=-dp[c][2]
    elif kernel=='sparse':
        dp={0:(0,0,0)};ct['states_peak']=1
        for j,(wi,qi,vi) in enumerate(zip(w,q,v)):
            nxt=dict(dp)
            for r,a in dp.items():
                reserve('transitions','dp_transitions');rr=r+wi
                if rr>c:continue
                candidate=(a[0]+qi,a[1]+side*vi,a[2]-(1<<j))
                if rr not in nxt:
                    if len(nxt)>=lim['sparse_states']:guard('sparse state allocation cap')
                    nxt[rr]=candidate
                elif candidate>nxt[rr]:nxt[rr]=candidate
            dp=nxt;ct['states_peak']=max(ct['states_peak'],len(dp))
        mask=-max(dp.values())[2]
    elif kernel=='bb':
        # Integer encoding of the lexicographic objective; no floating-point bounds.
        radix=1<<n;primary=(2*sum(abs(x) for x in v)+1)*radix
        scores=[a*primary+side*b*radix-(1<<j) for j,(a,b) in enumerate(zip(q,v))]
        mask=incumbent;best=value(scores,mask);leaves=[];trace=[];full=(1<<n)-1
        def bound(f,u,residual):
            nonlocal best,mask
            reserve('nodes','bb_nodes')
            order=sorted([j for j in range(n) if u>>j&1 and scores[j]>0],key=lambda j:(-Fraction(scores[j],w[j]),j))
            ct['sorted_terms']+=len(order);chosen=f;upper=Fraction(value(scores,f));pivot=None
            for j in order:
                if w[j]<=residual:chosen|=1<<j;residual-=w[j];upper+=scores[j]
                else:
                    if residual:upper+=Fraction(scores[j]*residual,w[j]);pivot=j
                    break
            score=value(scores,chosen)
            if score>best:best=score;mask=chosen
            return upper.numerator//upper.denominator,pivot
        bound(0,full,c)
        stack=list(reversed(domains or [[0,full,c]]))
        while stack:
            f,u,r=stack.pop();upper,pivot=bound(f,u,r)
            if upper<=best:
                if len(leaves)+len(stack)>=lim['bb_cells']:guard('terminal-partition allocation cap')
                leaves.append([f,u,r]);ct['terminal_peak']=max(ct['terminal_peak'],len(leaves)+len(stack))
            else:
                assert pivot is not None;bit=1<<pivot;children=[[f,u^bit,r]]
                if w[pivot]<=r:children.append([f|bit,u^bit,r-w[pivot]])
                if len(stack)+len(leaves)+len(children)>lim['bb_cells']:guard('terminal-partition allocation cap')
                trace.append(dict(domain=[f,u,r],pivot=pivot,children=children));stack.extend(reversed(children))
        record.update(domains=leaves,trace=trace,encoding_primary=primary,encoding_radix=radix,
                      retained_start=bool(domains),start_domains_hash=digest(domains) if domains else None)
    else:raise ValueError(kernel)
    record.update(complete=True,packing=mask,intercept=value(p,mask),slope=value(v,mask),
                  scaled_objective=value(q,mask),algorithm_cpu=time.process_time()-start)
    return record
