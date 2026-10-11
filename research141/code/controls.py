"""Designed compact replay refusals, ownership and valid-prefix boundary."""
import copy
import hashlib
from checker import digest,encode
from delta import Refused
from predecessor_suite import model
from predecessor_worker import solve
from recovery import hashed,image,proof_change,replay


def run(context):
    base=model(4,False,914141);m=copy.deepcopy(base);p=solve(m,context)
    head=hashlib.sha256(encode({'base':digest(base),'context':context})).hexdigest()
    snap=image(base,m,p,0,head,'compact',context);events=[]
    off=next(i for i,e in enumerate(m['edges']) if e['a']+4!=e['z'])
    diag=next(i for i,e in enumerate(m['edges']) if e['a']+4==e['z'])
    for step,(i,new) in enumerate(((off,m['edges'][off]['c']+1),(diag,30))):
        msg={'version':step,'context':context,'changes':[{'edge':i,'old':m['edges'][i]['c'],'new':new}]}
        m['edges'][i]['c']=new;newp=solve(m,context)
        payload={'message':msg,'action':'patch' if step==0 else 'recertify','cost_units':newp['cost_units']}
        if step:payload['difference']=proof_change(p,newp)
        event={'payload':payload,'previous':head,'head':hashed(head,payload)}
        head=event['head'];events.append(event);p=newp
    anchor=[2,head];assert replay(base,snap,events,context,anchor)==(m,p)
    tests=[]
    def test(name,change):
        b,s,e,a=copy.deepcopy((base,snap,events,anchor));change(b,s,e,a)
        try:replay(b,s,e,context,a);raise AssertionError(name)
        except Refused:pass
        tests.append({'name':name,'rejected':True})
    test('wrong-base',lambda b,s,e,a:b['edges'][0].update(u=0))
    test('wrong-context',lambda b,s,e,a:s.update(context='other'))
    test('missing-cost',lambda b,s,e,a:s['costs'].pop())
    test('false-snapshot-value',lambda b,s,e,a:s['proof'].update(cost_units=999))
    test('edited-event',lambda b,s,e,a:e[0]['payload']['message']['changes'][0].update(new=99))
    test('delete-event',lambda b,s,e,a:e.pop())
    test('reorder',lambda b,s,e,a:e.reverse())
    test('wrong-anchor',lambda b,s,e,a:a.__setitem__(1,'bad'))
    test('false-proof-flow',lambda b,s,e,a:e[1]['payload']['difference']['flow'].append([0,999]))
    test('false-proof-value',lambda b,s,e,a:e[1]['payload']['difference'].update(cost_units=999))
    # Rehashing invalid proof changes still fails mathematical admission.
    for name,mutate in [('rehash-false-proof',lambda d:d.update(cost_units=999)),
                        ('rehash-duplicate-index',lambda d:d['pi'].extend([[0,1],[0,2]])),
                        ('rehash-cost-domain',lambda d:d['flow'].append([0,True]))]:
        ev=copy.deepcopy(events);mutate(ev[1]['payload']['difference']);ev[1]['head']=hashed(ev[1]['previous'],ev[1]['payload'])
        try:replay(base,snap,ev,context,[2,ev[1]['head']]);raise AssertionError(name)
        except Refused:pass
        tests.append({'name':name,'rejected':True})
    # A mathematically valid prefix needs an external anchor to reject rollback.
    prefix=replay(base,snap,events[:1],context,[1,events[0]['head']])
    assert prefix[0]['edges'][diag]['c']==-5
    try:replay(base,snap,events[:1],context,anchor);raise AssertionError('rollback')
    except Refused:pass
    tests.append({'name':'trusted-anchor-rollback','rejected':True})
    return {'controls':tests,'valid_compact_replay':True,'unanchored_valid_prefix_possible':True,
            'fixture':{'base':base,'snapshot':snap,'events':events,'anchor':anchor}}
