"""Fixed adapter refusal checks; development graphs are separately excluded."""
import copy
from basis import Basis
from checker import digest,encode,verify
from predecessor_suite import model
from worker import proof


def run(ctx):
    m=model(4,False,914145);s=Basis(m);x=s.optimize();p=proof(m,x,ctx);checks=[]
    mutations={
        'capacity':lambda z:z['edges'][0].update(u=1),
        'lower-bound':lambda z:z['edges'][0].update(l=1),
        'balance':lambda z:z['b'].__setitem__(0,z['b'][0]+1),
        'topology':lambda z:z['edges'].pop(),
        'identity':lambda z:z.update(id='different'),
        'denomination':lambda z:z.update(denominator=7)}
    for name,edit in mutations.items():
        bad=copy.deepcopy(m);edit(bad)
        try:s.require_fixed(bad)
        except ValueError:checks.append(name)
        else:raise AssertionError(name)
    old=m['edges'][0]['c'];good={'edge':0,'old':old,'new':old+1}
    cases={
        'stale-cost':[dict(good,old=old-1)],'duplicate':[good,good],
        'boolean-index':[dict(good,edge=True)],'boolean-cost':[dict(good,new=True)],
        'out-of-range':[dict(good,edge=len(m['edges']))],
        'outside-domain':[dict(good,new=1000001)],
        'extra-field':[dict(good,unexpected=1)],
        'late-error-atomicity':[good,dict(good,edge=1,old=100000)]}
    for name,changes in cases.items():
        before=(encode(s.m),s.d.edge_weights.copy(),s.d.edge_flow.copy(),s.d.parent.copy())
        try:s.change_costs(changes)
        except ValueError:pass
        else:raise AssertionError(name)
        assert before==(encode(s.m),s.d.edge_weights,s.d.edge_flow,s.d.parent);checks.append(name)
    s.change_costs([good]);s.optimize();assert verify(s.m,proof(s.m,s.optimize(),ctx),ctx)
    loop=copy.deepcopy(m);loop['edges'][0]['z']=loop['edges'][0]['a']
    try:Basis(loop)
    except ValueError:checks.append('loop-refusal')
    else:raise AssertionError('loop')
    bad=copy.deepcopy(p);bad['cost_units']+=1;assert not verify(m,bad,ctx);checks.append('false-cost')
    return {'model':m,'initial_proof':p,'controls':checks,'passed':True,'scope':'loop-free cost-only basis; noncost updates require reset'}
