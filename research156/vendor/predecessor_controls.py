"""Adversarial transaction rollback, ownership, shortage and charged fallback controls."""
import copy
from checker import digest, encode, verify
from engine import Engine, ROUTES
from transaction import Rejected, Transaction


def run(context):
    m={'id':'controls','n':3,'b':[2,0,-2],'denominator':1,'edges':[
        {'a':0,'z':1,'l':0,'u':2,'c':1}, {'a':1,'z':2,'l':0,'u':2,'c':1},
        {'a':0,'z':2,'l':0,'u':2,'c':7}, {'a':1,'z':1,'l':0,'u':2,'c':-1}]}
    good={'version':0,'context':context,'old_model':digest(m),'edges':[{'edge':0,'field':'u','old':2,'new':1}],'balances':[]}
    tests={}
    def change(name, fn):
        msg=copy.deepcopy(good);fn(msg);tests[name]=msg
    change('wrong-context',lambda q:q.update(context='wrong'))
    change('stale-version',lambda q:q.update(version=-1))
    change('boolean-version',lambda q:q.update(version=False))
    change('wrong-old-model',lambda q:q.update(old_model='wrong'))
    change('unknown-message-field',lambda q:q.update(extra=1))
    change('unknown-edge-field',lambda q:q['edges'][0].update(field='a'))
    change('wrong-old-value',lambda q:q['edges'][0].update(old=1))
    change('boolean-edge',lambda q:q['edges'][0].update(edge=True))
    change('noninteger-new',lambda q:q['edges'][0].update(new=0.5))
    change('boolean-new',lambda q:q['edges'][0].update(new=True))
    change('negative-capacity',lambda q:q['edges'][0].update(new=-1))
    change('oversized-capacity',lambda q:q['edges'][0].update(new=10001))
    change('duplicate-edge-field',lambda q:q['edges'].append(copy.deepcopy(q['edges'][0])))
    change('unbalanced-needs',lambda q:q['balances'].append({'node':0,'old':2,'new':3}))
    change('duplicate-balance',lambda q:q['balances'].extend([{'node':0,'old':2,'new':3}]*2))
    change('bad-node',lambda q:q['balances'].append({'node':3,'old':0,'new':1}))
    change('partial-after-valid-prefix',lambda q:q['edges'].append({'edge':99,'field':'u','old':2,'new':1}))
    change('bad-container',lambda q:q.update(edges=None))
    change('empty-update',lambda q:q.update(edges=[],balances=[]))
    change('too-many-changes',lambda q:q.update(edges=[copy.deepcopy(q['edges'][0])]*33))
    tests['malformed-top-level'] = []
    results=[]
    for name,msg in tests.items():
        state=Transaction(m,context);before=encode({'model':state.model,'version':state.version})
        try:state.apply(msg)
        except Rejected:pass
        else:raise AssertionError(name)
        assert encode({'model':state.model,'version':state.version})==before
        results.append(name)
    state=Transaction(m,context);packet=copy.deepcopy(good);returned=state.apply(packet)
    packet['edges'][0]['new']=999;returned['edges'][0]['u']=999
    assert state.model['edges'][0]['u']==1;results.append('caller-ownership')
    try:state.apply(good)
    except Rejected:pass
    else:raise AssertionError('replay')
    results.append('replay-rejection')
    e=Engine(m,context,'guard-repair');initial=e.query();assert initial['proof']['flow'][0]==2
    repaired=e.query(good);assert repaired['proof']['flow'][0]<=1 and not repaired['stats']['guard_accepted']
    results.append('reduction-below-old-flow')
    # Valid simultaneous bounds need only hold at final commit, independent of field order.
    q={'version':1,'context':context,'old_model':digest(e.state.model),'edges':[
        {'edge':0,'field':'l','old':0,'new':3},{'edge':0,'field':'u','old':1,'new':3}],
       'balances':[{'node':0,'old':2,'new':3},{'node':1,'old':0,'new':-1}]}
    rec=e.query(q);assert verify(e.state.model,rec['proof'],context);results.append('atomic-joint-bounds-and-needs')
    short={'version':2,'context':context,'old_model':digest(e.state.model),'edges':[],
           'balances':[{'node':0,'old':3,'new':100},{'node':2,'old':-2,'new':-99}]}
    cut=e.query(short);short_model=copy.deepcopy(e.state.model);assert cut['proof']['kind']=='cut';results.append('checked-shortage')
    restore={'version':3,'context':context,'old_model':digest(e.state.model),'edges':[],
             'balances':[{'node':0,'old':100,'new':3},{'node':2,'old':-99,'new':-2}]}
    recovered=e.query(restore);assert recovered['proof']['kind']=='optimal' and recovered['stats']['flow_hint']
    results.append('repair-after-infeasibility')
    fallback=Engine(m,context,'flow-repair').query(force_budget=True)
    assert fallback['stats']['budget_fallback'] and fallback['action']=='charged-cold-fallback'
    results.append('charged-budget-fallback')
    # Full guard invalidates an old pi when expanding a profitable residual self-loop.
    g=copy.deepcopy(m);g['edges'][3]['u']=0;e=Engine(g,context,'guard-repair');e.query()
    q={'version':0,'context':context,'old_model':digest(g),'balances':[],
       'edges':[{'edge':3,'field':'u','old':0,'new':2}]}
    rec=e.query(q);assert not rec['stats']['guard_accepted'] and rec['proof']['flow'][3]==2
    results.append('new-residual-self-loop')
    # Proof objects returned to callers cannot poison retained state.
    rec['proof']['flow'][0]=999;assert e.query()['proof']['flow'][0]!=999
    results.append('proof-ownership')
    return {'passed':True,'controls':results,'model':m,'initial_proof':initial['proof'],
            'shortage_proof':cut['proof'],'shortage_model':short_model,
            'fallback_proof':fallback['proof']}
