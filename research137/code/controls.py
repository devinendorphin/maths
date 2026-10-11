"""Transaction, replay and non-cost controls; run on a separate designed model."""
import copy
import hashlib
import json
from checker import encode, verify
from delta import Captured, Refused
from suite import model
from worker import solve


def run(context):
    m=model(4,False,72); p=solve(m,context)
    s=Captured(m,p,context,budget=4096)
    off=next(i for i,e in enumerate(m['edges']) if e['a']+4!=e['z'])
    msg={'version':0,'context':context,'changes':[{'edge':off,'old':m['edges'][off]['c'],'new':m['edges'][off]['c']+1}]}
    bad=[]
    def add(name,mutate):
        q=copy.deepcopy(msg); mutate(q); bad.append((name,q))
    add('stale',lambda q:q.update(version=1))
    add('wrong-context',lambda q:q.update(context='other'))
    add('wrong-old',lambda q:q['changes'][0].update(old=100))
    add('duplicate',lambda q:q['changes'].append(copy.deepcopy(q['changes'][0])))
    add('out-of-range',lambda q:q['changes'][0].update(edge=999999))
    add('noninteger',lambda q:q['changes'][0].update(new=True))
    add('cost-limit',lambda q:q['changes'][0].update(new=1000001))
    add('capacity-message',lambda q:q['changes'][0].update(u=0))
    add('malformed',lambda q:q.update(changes=None))
    add('extra-field',lambda q:q.update(hidden='field'))
    controls=[]
    for name,q in bad:
        before=encode(s.checkpoint())
        try:s.patch(q); raise AssertionError(name)
        except Refused:pass
        assert encode(s.checkpoint())==before
        controls.append({'name':name,'rejected':True,'unchanged':True})
    # A late invalid entry cannot partially commit the first valid entry.
    q=copy.deepcopy(msg);q['changes'].append({'edge':off+1,'old':99999,'new':0})
    before=encode(s.checkpoint())
    try:s.patch(q);raise AssertionError('partial commit')
    except Refused:pass
    assert encode(s.checkpoint())==before
    controls.append({'name':'late-invalid-atomicity','rejected':True,'unchanged':True})
    diag=next(i for i,e in enumerate(m['edges']) if e['a']+4==e['z'])
    fail={'version':0,'context':context,'changes':[{'edge':diag,'old':-5,'new':30}]}
    before=encode(s.checkpoint());r=s.patch(fail)
    assert not r['accepted'] and encode(s.checkpoint())==before
    controls.append({'name':'failed-sign-atomicity','rejected':True,'unchanged':True})
    for version in range(3):
        q=copy.deepcopy(msg);q['version']=version
        q['changes'][0]['old']+=version;q['changes'][0]['new']+=version
        assert s.patch(q)['accepted']
    bundle=s.checkpoint();restored=Captured.restore(bundle,context)
    assert restored.export()==s.export()
    recovery=[]
    mutations=[('edited-cost',lambda b:b['events'][0]['message']['changes'][0].update(new=99)),
               ('deleted-event',lambda b:b['events'].pop()),
               ('reordered',lambda b:b['events'].reverse()),
               ('false-value',lambda b:b['events'][0].update(cost_units=999)),
               ('wrong-head',lambda b:b.update(head='0'*64)),
               ('wrong-version',lambda b:b.update(version=99)),
               ('bad-base',lambda b:b['base']['proof'].update(cost_units=99))]
    for name,mutate in mutations:
        b=copy.deepcopy(bundle);mutate(b)
        try:Captured.restore(b,context);raise AssertionError(name)
        except Refused:pass
        recovery.append({'name':name,'rejected':True})
    try:Captured.restore(bundle,'other');raise AssertionError('restore context')
    except Refused:pass
    recovery.append({'name':'restore-context','rejected':True})
    prefix=copy.deepcopy(bundle);prefix['events'].pop()
    prefix['head']=prefix['events'][-1]['head'];prefix['version']-=1
    assert Captured.restore(prefix,context).version==2
    try:Captured.restore(prefix,context,(s.version,s.head));raise AssertionError('rollback')
    except Refused:pass
    recovery.append({'name':'valid-prefix-rollback-with-trusted-anchor','rejected':True})
    truncated=encode(bundle)[:-7]
    try:json.loads(truncated);raise AssertionError('truncated bytes')
    except json.JSONDecodeError:pass
    recovery.append({'name':'truncated-checkpoint-bytes','rejected':True})
    # Full-domain changes require fresh certification, never a cost-only patch.
    cases=[]
    capacity=copy.deepcopy(m);capacity['edges'][diag]['u']=0
    balance=copy.deepcopy(m);balance['b'][0]+=1;balance['b'][4]-=1
    shortage=copy.deepcopy(m)
    for e in shortage['edges']:
        if e['a']==0:e['u']=0
    for name,mm in [('capacity',capacity),('balance',balance),('shortage',shortage)]:
        pp=solve(mm,context)
        assert verify(mm,pp,context)
        cases.append({'name':name,'model':mm,'proof':pp})
    # Owned admission survives subsequent mutation of caller-owned originals.
    own=Captured(m,p,context);mm,pp=own.export();m['edges'][0]['c']+=100;p['flow'][0]=999
    assert own.export()==(mm,pp)
    # Omission cannot be inferred from a k-sized message. Demonstrate the limit.
    authoritative=copy.deepcopy(mm);authoritative['edges'][diag]['c']=30
    rebound=copy.deepcopy(pp)
    from checker import digest
    rebound['model']=digest(authoritative)
    rebound['cost_units']=sum(e['c']*x for e,x in zip(authoritative['edges'],pp['flow']))
    assert not verify(authoritative,rebound,context)
    # Instrument the sparse noncompacting path to forbid hidden full scans.
    import delta
    original_digest,original_verify=delta.digest,delta.verify
    def forbidden(*args):raise AssertionError('full scan in accepted sparse patch')
    probe=Captured(mm,pp,context,budget=4096)
    delta.digest=delta.verify=forbidden
    try:
        sparse={'version':0,'context':context,'changes':[{'edge':off,'old':mm['edges'][off]['c'],'new':mm['edges'][off]['c']+1}]}
        assert probe.patch(sparse)['accepted']
    finally:delta.digest,delta.verify=original_digest,original_verify
    return {'transaction_controls':controls,'recovery_controls':recovery,
            'noncost_cases':cases,'ownership_control':True,
            'recovery_bundle':bundle,'valid_recovery':True,'no_full_scan_control':True,
            'omitted_delta_limit':{'unanchored_valid_prefix_accepted':True,
                                   'owned_model_unchanged':True,'authoritative_rebind_rejected':True}}
