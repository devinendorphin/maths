"""Real-parameter and integer-grid exact divide-and-conquer with charged fallback."""
from fractions import Fraction
import time
from shared import frac
import oracles as O


def run(row,kind='real',kernel='dense',normalize=False,forced=None):
    start=time.process_time();queries=[];attempts=[];cache={};intervals=[];lines=set();status='complete';reason=None
    def oracle(t,side=1):
        t=Fraction(t);key=(t,side)
        if key not in cache:
            if len(cache)>=2048 or time.process_time()-start>=30:
                raise O.Cap('curve work/CPU cap',dict(time=frac(t),side=side,kernel=kernel,complete=False,
                            counts=dict(transitions=0,nodes=0,sorted_terms=0,states_peak=0,terminal_peak=0)))
            if forced is not None:
                limit={'dp_transitions':1} if kernel in ('dense','sparse') else {'bb_nodes':1}
                try:r=O.solve(row,t,kernel,side,normalize,limit)
                except O.Cap as exc:
                    attempts.append(dict(exc.record,reason=str(exc),active=False))
                    r=O.solve(row,t,'dense',side,True)
                else:raise AssertionError('forced primary query unexpectedly completed')
            else:r=O.solve(row,t,kernel,side,normalize)
            cache[key]=r;queries.append(r)
        r=cache[key];line=(r['intercept'],r['slope'],r['packing']);lines.add(line);return line
    try:
        if kind=='points':
            packings=[oracle(t)[2] for t in range(row['end']+1)]
        elif kind in ('integer','cross'):
            l=0;h=row['end'];a=oracle(l,1);b=oracle(h,1);stack=[(l,h,a,b)];assigned={}
            while stack:
                l,h,a,b=stack.pop()
                if a==b:
                    intervals.append(dict(left=l,right=h,line=list(a),reason='same extreme endpoint packing'))
                    for t in range(l,h+1):assigned[t]=a[2]
                elif h-l<=1:
                    assigned[l]=a[2];assigned[h]=b[2]
                    intervals.extend([dict(left=l,right=l,line=list(a),reason='single observation'),dict(left=h,right=h,line=list(b),reason='single observation')])
                else:
                    mid=(l+h)//2
                    if kind=='cross' and a[1]!=b[1]:
                        x=Fraction(a[0]-b[0],b[1]-a[1]);mid=max(l+1,min(h-1,x.numerator//x.denominator))
                    m=oracle(mid,1);stack.extend([(mid,h,m,b),(l,mid,a,m)])
            packings=[assigned[t] for t in range(row['end']+1)]
        else:
            lo=Fraction(0);hi=Fraction(row['end']);left=oracle(lo,1);right=oracle(hi,-1);stack=[(left,right,lo,hi)]
            while stack:
                a,b,l,h=stack.pop()
                if a[:2]==b[:2]:continue
                assert a[1]<b[1];x=Fraction(a[0]-b[0],b[1]-a[1]);assert l<=x<=h
                m=oracle(x,1);target=a[0]+x*a[1];best=m[0]+x*m[1];assert best>=target
                if best>target:
                    assert a[1]<m[1]<b[1];stack.extend([(m,b,x,h),(a,m,l,x)])
            ordered=sorted(lines,key=lambda x:x[1])
            for i,line in enumerate(ordered):
                l=lo if i==0 else Fraction(ordered[i-1][0]-line[0],line[1]-ordered[i-1][1])
                h=hi if i==len(ordered)-1 else Fraction(line[0]-ordered[i+1][0],ordered[i+1][1]-line[1])
                assert lo<=l<=h<=hi
                if l<h:intervals.append(dict(left=frac(l),right=frac(h),line=list(line)))
            packings=[max(ordered,key=lambda x:(x[0]+t*x[1],x[1],-x[2]))[2] for t in range(row['end']+1)]
    except O.Cap as exc:
        status='capped';reason=str(exc);attempts.append(dict(exc.record,reason=reason,active=False));packings=[];intervals=[]
    counts={k:sum(q['counts'][k] for q in queries+attempts) for k in ('transitions','nodes','sorted_terms')}
    counts.update(states_peak=max((q['counts']['states_peak'] for q in queries+attempts),default=0),
                  terminal_peak=max((q['counts']['terminal_peak'] for q in queries+attempts),default=0))
    return dict(status=status,reason=reason,kind=kind,kernel=kernel,normalize=normalize,queries=queries,
                incomplete_attempts=attempts,packings=packings,intervals=intervals,lines=[list(x) for x in sorted(lines)],
                counts=counts,oracle_calls=len(queries),aborted_calls=len(attempts),algorithm_cpu=time.process_time()-start)


def sequence(row,mode='cold',force_cells=None):
    start=time.process_time();queries=[];attempts=[];domains=None;packing=0;status='complete';reason=None
    for t in range(row['end']+1):
        lim={'bb_cells':force_cells} if force_cells is not None and mode=='tree' and t==1 else None
        try:r=O.solve(row,t,'bb',1,False,lim,domains if mode in ('tree','small_tree') else None,packing if mode!='cold' else 0)
        except O.Cap as exc:
            attempts.append(dict(exc.record,reason=str(exc),active=False))
            try:r=O.solve(row,t,'bb')
            except O.Cap as fallback:
                attempts.append(dict(fallback.record,reason=str(fallback),active=False));status='capped';reason=str(fallback);break
        queries.append(r);domains=r['domains'] if mode!='small_tree' or len(r['domains'])<=8 else None;packing=r['packing']
    return dict(status=status,reason=reason,kind='warm_'+mode,queries=queries,incomplete_attempts=attempts,
                packings=[q['packing'] for q in queries],intervals=[],lines=[],oracle_calls=len(queries),aborted_calls=len(attempts),
                counts={k:sum(q['counts'][k] for q in queries+attempts) for k in ('transitions','nodes','sorted_terms')},
                algorithm_cpu=time.process_time()-start)
