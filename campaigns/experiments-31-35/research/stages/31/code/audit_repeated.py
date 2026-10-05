from fractions import Fraction
import horizon as H
from audit_renewal import fractional_bound
from audit_horizon import rational_horizon

def contains(cell,mask):return mask&cell[0]==cell[0] and mask&~(cell[0]|cell[1])==0
def cover(proof,w,c):
    for m in range(1<<len(w)):
        if H.value(w,m)<=c:assert sum(contains(cell,m) for cell in proof)==1
def check_prices(proof,w,q,c,m):
    for cell in proof:
        f,u,r,a,b,num=cell
        assert f&u==0 and r==c-H.value(w,f) and r>=0 and a>=0 and b>0
        assert num==H.numerator(cell,w,q,[0]*len(w),0) and Fraction(num,b)==fractional_bound(cell,w,q)
        assert num//b<=H.value(q,m)
def horizon_check(proof,w,q,v,m,cert):
    times=[rational_horizon(cell,w,q,v,m) for cell in proof]
    assert times==cert['cell_horizons'];finite=[x for x in times if x is not None]
    assert cert['first_failure']==(min(finite) if finite else None)

def audit_case(x):
    w,p,v,c,m=x['weights'],x['profits'],x['slopes'],x['capacity'],x['packing'];initial=x['initial_proof']
    assert H.value(p,m)==H.F.dp(w,p,c);cover(initial,w,c)
    optimal=H.optimum_horizon(H.packing_lines(w,p,v,c),p,v,m)['first_loss'];events=0;cells=0
    for path in x['paths']:
        old=[list(cell) for cell in initial];previous_time=0;totals=dict(price_calls=0,bound_evaluations=0,free_term_evaluations=0,splits=0)
        for ordinal,event in enumerate(path['events'],1):
            trigger=int(path['mode'].split('_')[1]) if path['mode'].startswith('once_') else None
            expected_action='rebuild' if path['mode']=='rebuild' or ordinal==trigger else 'repair'
            assert event['action']==expected_action and event['ordinal']==ordinal
            t=event['time'];assert event['previous_time']==previous_time
            q0=[a+previous_time*b for a,b in zip(p,v)];horizon_check(old,w,q0,v,m,event['previous_certificate'])
            assert t==previous_time+event['previous_certificate']['first_failure']
            q=[a+t*b for a,b in zip(p,v)];r=event['result'];target=H.value(q,m)
            for key in ('price_calls','bound_evaluations','free_term_evaluations'):totals[key]+=event['counters'][key]
            totals['splits']+=r['splits'];events+=1
            if not r['success']:
                witness=r['witness'];assert H.value(w,witness)<=c and H.value(q,witness)>target
                assert t==optimal and path['status']=='packing_lost';break
            assert target==H.F.dp(w,q,c)
            domain=old if event['action']=='repair' else [[0,(1<<len(w))-1,c,0,1,0]]
            new=r['proof'];assert len(new)==len(r['origins'])
            for cell,o in zip(new,r['origins']):
                root=domain[o];assert cell[0]&root[0]==root[0] and (cell[0]|cell[1])&~(root[0]|root[1])==0
            for trace in r['trace']:
                f,u,res,i=trace['fixed'],trace['free'],trace['residual'],trace['pivot'];bit=1<<i;assert u&bit
                expected=[[f,u^bit,res]]
                if w[i]<=res:expected.append([f|bit,u^bit,res-w[i]])
                assert trace['children']==expected
            # Coverage is also enumerated after each event, independent of trace bookkeeping.
            cover(new,w,c);check_prices(new,w,q,c,m);cells+=len(new)
            old=new;previous_time=t
        assert all(path['totals'][key]==value for key,value in totals.items())
        if path['status']!='packing_lost':
            q=[a+previous_time*b for a,b in zip(p,v)];horizon_check(old,w,q,v,m,path['final_certificate'])
            dt=path['final_certificate']['first_failure']
            if path['status']=='forever_certified':assert dt is None and optimal is None
            else:assert previous_time+dt>x['end'] and (optimal is None or optimal>x['end'])
        cover(path['final_proof'],w,c)
    return dict(passed=True,events=events,cells=cells,first_optimality_loss=optimal)
