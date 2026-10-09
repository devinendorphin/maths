from fractions import Fraction
import horizon as H
from audit_horizon import verify_case

def fractional_bound(cell,w,q):
    fixed,free,residual,*_=cell
    total=Fraction(H.value(q,fixed));remaining=residual
    items=sorted((i for i in range(len(w)) if free>>i&1 and q[i]>0),key=lambda i:Fraction(q[i],w[i]),reverse=True)
    for i in items:
        take=min(remaining,w[i]);total+=Fraction(take*q[i],w[i]);remaining-=take
        if not remaining:break
    return total

def audit_case(x):
    verify_case(x)
    t=x['certificate']['first_failure']
    if t is None:return dict(cells=0,renewed_time_checks=0)
    q=[p+t*v for p,v in zip(x['profits'],x['slopes'])];r=x['renewal'];value=H.value(q,x['packing'])
    assert r['value']==value
    failed=[]
    for i,(old,new) in enumerate(zip(x['proof'],r['proof'])):
        assert tuple(old[:3])==tuple(new[:3])
        assert new[4]>0 and new[3]>=0
        assert H.numerator(new,x['weights'],q,[0]*len(q),0)==new[5]
        assert Fraction(new[5],new[4])==fractional_bound(new,x['weights'],q)
        if new[5]//new[4]>value:failed.append(i)
    assert failed==r['failed_cells'] and r['success']==(not failed)
    best=H.F.dp(x['weights'],q,x['capacity'])
    assert x['still_optimal']==(value==best)
    assert x['fresh']['objective']==best and x['fresh']['empty']
    checked=0
    if r['success']:
        assert x['still_optimal']
        y=dict(x,profits=q,proof=r['proof'],certificate=r['certificate'],optimum=H.optimum_horizon(H.packing_lines(x['weights'],q,x['slopes'],x['capacity']),q,x['slopes'],x['packing']))
        checked=len(verify_case(y))
        next_time=r['certificate']['first_failure']
        assert next_time is None or next_time>=1
    return dict(cells=len(r['proof']),renewed_time_checks=checked)
