"""Exact endpoint/intersection recursion; no audit oracle imports."""
from fractions import Fraction
import time
from shared import value, encode_fraction


def solve(row, t, side=1):
    """Capacity DP lexicographically maximizes scaled objective, side*slope, -mask."""
    w, p, v, c = (row[k] for k in ('weights','profits','slopes','capacity'))
    t = Fraction(t)
    q = [t.denominator*a+t.numerator*b for a,b in zip(p,v)]
    dp = [(0,0,0)]*(c+1)
    transitions = 0
    for j, (wi,qi,vi) in enumerate(zip(w,q,v)):
        for r in range(c,wi-1,-1):
            old=dp[r-wi]
            candidate=(old[0]+qi,old[1]+side*vi,old[2]-(1<<j))
            transitions+=1
            if candidate>dp[r]: dp[r]=candidate
    mask=-dp[c][2]
    return dict(time=encode_fraction(t),side=side,packing=mask,
                intercept=value(p,mask),slope=value(v,mask),scaled_objective=dp[c][0],
                transitions=transitions,dp_cells=c+1)


def curve(row):
    start=time.process_time(); queries=[]; cache={}; visited=[]
    def oracle(t,side):
        key=(t,side)
        if key not in cache:
            if len(cache)>=4096: raise RuntimeError('parametric oracle-call cap')
            r=solve(row,t,side); cache[key]=r; queries.append(r)
        r=cache[key]
        return (r['intercept'],r['slope'],r['packing'])
    lo=Fraction(0); hi=Fraction(row['end'])
    left=oracle(lo,1); right=oracle(hi,-1)
    lines={left,right}; stack=[(left,right,lo,hi)]
    while stack:
        a,b,l,h=stack.pop()
        if a[:2]==b[:2]: continue
        assert a[1]<b[1]
        x=Fraction(a[0]-b[0],b[1]-a[1]); assert l<=x<=h
        middle=oracle(x,1); base=a[0]+x*a[1]; best=middle[0]+x*middle[1]
        visited.append(dict(left=list(a),right=list(b),interval=[encode_fraction(l),encode_fraction(h)],
                            query=encode_fraction(x),value=encode_fraction(best),stop=best==base))
        assert best>=base
        if best==base: continue
        assert a[1]<middle[1]<b[1]
        lines.add(middle)
        stack.extend([(middle,b,x,h),(a,middle,l,x)])
    ordered=sorted(lines,key=lambda x:x[1]); pieces=[]
    for i,line in enumerate(ordered):
        l=lo if i==0 else Fraction(ordered[i-1][0]-line[0],line[1]-ordered[i-1][1])
        h=hi if i==len(ordered)-1 else Fraction(line[0]-ordered[i+1][0],ordered[i+1][1]-line[1])
        assert lo<=l<=h<=hi
        if l<h: pieces.append(dict(line=list(line),left=encode_fraction(l),right=encode_fraction(h)))
    # Reporting integer observations is charged, including tie selection.
    packings=[max(ordered,key=lambda x:(x[0]+t*x[1],x[1],-x[2]))[2] for t in range(row['end']+1)]
    return dict(method='parametric_dp',algorithm_cpu=time.process_time()-start,queries=queries,
                recursion=visited,lines=[list(x) for x in ordered],pieces=pieces,packings=packings,
                oracle_calls=len(queries),transitions=sum(x['transitions'] for x in queries),
                peak_dp_cells=row['capacity']+1,line_records=len(ordered))


def points(row):
    start=time.process_time()
    queries=[solve(row,Fraction(t)) for t in range(row['end']+1)]
    return dict(method='point_dp',algorithm_cpu=time.process_time()-start,queries=queries,
                packings=[x['packing'] for x in queries],oracle_calls=len(queries),
                transitions=sum(x['transitions'] for x in queries),peak_dp_cells=row['capacity']+1)
