"""Independent checks: dense capacity DP, scalar covers, rational intervals, splits."""
from fractions import Fraction
import time
from shared import value
from audit import Checker,optimum
from verify import audit_path,check_cert
from audit_horizon import rational_horizon


def packings(row,result):
    for t,m in enumerate(result['packings']):
        q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
        assert value(row['weights'],m)<=row['capacity']
        assert value(q,m)==optimum(row['weights'],q,row['capacity'])
    return len(result['packings'])


def parametric(row,result):
    checks=packings(row,result); rational=0
    for query in result.get('queries',[]):
        t=Fraction(*query['time']); q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
        assert query['scaled_objective']==value(q,query['packing'])==optimum(row['weights'],q,row['capacity'])
        # Independent tie audit: small exact-weight DP holds a set of slopes/masks
        # only for primary-optimal states, rather than the production tuple DP.
        states={0:(0,{(0,0)})}
        for j,(wi,qi,vi) in enumerate(zip(row['weights'],q,row['slopes'])):
            nxt={r:(val,set(options)) for r,(val,options) in states.items()}
            for r,(val,options) in states.items():
                rr=r+wi
                if rr>row['capacity']:continue
                candidate=val+qi; opts={(s+vi,m|1<<j) for s,m in options}
                if rr not in nxt or candidate>nxt[rr][0]:nxt[rr]=(candidate,opts)
                elif candidate==nxt[rr][0]:nxt[rr][1].update(opts)
            states=nxt
        best=max(x[0] for x in states.values()); opts=set().union(*(x[1] for x in states.values() if x[0]==best))
        extreme=max(opts,key=lambda x:(query['side']*x[0],-x[1]))
        assert extreme==(query['slope'],query['packing'])
        rational+=1
    for piece in result.get('pieces',[]):
        p,s,m=piece['line']; assert p==value(row['profits'],m) and s==value(row['slopes'],m)
        for t in (Fraction(*piece['left']),Fraction(*piece['right'])):
            q=[t.denominator*a+t.numerator*b for a,b in zip(row['profits'],row['slopes'])]
            assert value(q,m)==optimum(row['weights'],q,row['capacity']); rational+=1
    return dict(passed=True,integer_checks=checks,rational_checks=rational)


def reoptimization(row,result):
    checker=Checker(row); previous=None
    for solve in result['solves']:
        checker.deadline=time.perf_counter()+45; t=solve['time']; m=solve['packing']
        q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
        assert solve['objective']==value(q,m)==optimum(row['weights'],q,row['capacity'])
        checker.cover([x+[0,1,0] for x in solve['domains']])
        for branch in solve['split_trace']:
            f,u,r=branch['domain']; j=branch['pivot']; assert u>>j&1
            children=[[f,u^(1<<j),r]]
            if row['weights'][j]<=r:children.append([f|1<<j,u^(1<<j),r-row['weights'][j]])
            assert branch['children']==children
        if previous is not None and result['method']=='reopt_tree':
            for f,u,r in solve['domains']:
                assert any(a&f==a and not (f|u)&~(a|b) for a,b,_ in previous)
        previous=solve['domains']
    return dict(passed=True,integer_checks=len(result['solves']),rational_checks=0)


def event_path(row,result):
    checker=Checker(row); checks=packings(row,result); horizons=0
    for source in result['sources']:
        assert source['empty']; checker.cover(source['proof']); checker.prices(source['proof'],source['time'],source['packing'])
    for segment in result['segments']:
        checker.deadline=time.perf_counter()+45; proof=segment['proof']; m=segment['packing']
        checker.cover(proof); start=segment['anchor']; end=segment['until']
        q=[a+start*b for a,b in zip(row['profits'],row['slopes'])]
        failures=[]
        for cell in proof:
            f,u,r,a,b,_=cell
            def num(t):
                qt=[p+t*v for p,v in zip(row['profits'],row['slopes'])]
                return b*value(qt,f)+a*r+sum(max(0,b*qt[j]-a*row['weights'][j]) for j in range(row['n']) if u>>j&1)
            adjusted=cell[:5]+[num(start)]
            dt=rational_horizon(adjusted,row['weights'],q,row['slopes'],m); horizons+=1
            failures.append(None if dt is None else start+dt)
            for t in (start,end):
                qt=[p+t*v for p,v in zip(row['profits'],row['slopes'])]
                assert num(t)//b<=value(qt,m)
        loss=min((x for x in failures if x is not None),default=None)
        assert end==row['end'] if loss is None else end==min(row['end'],loss-1)
    for repair in result['repairs']:
        q=[p+repair['time']*v for p,v in zip(row['profits'],row['slopes'])]
        for call in repair['calls']:
            f,u,r=call['domain']; candidates={Fraction(0)}|{Fraction(q[j],row['weights'][j]) for j in range(row['n']) if u>>j&1 and q[j]>0}
            scores=[]
            for lam in candidates:
                a,b=lam.numerator,lam.denominator
                z=b*value(q,f)+a*r+sum(max(0,b*q[j]-a*row['weights'][j]) for j in range(row['n']) if u>>j&1)
                scores.append((Fraction(z,b),lam,z))
            _,lam,z=min(scores)
            assert call['priced']==[f,u,r,lam.numerator,lam.denominator,z]
        rr=repair['result']
        if not rr['success']:assert value(q,rr['witness'])>value(q,repair['packing'])
    if result['capped_construction'] is not None:
        assert not result['capped_active']; check_cert(row,result['capped_construction'])
    return dict(passed=True,integer_checks=checks,rational_checks=horizons)
