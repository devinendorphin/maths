"""Thirty inherited admission/transaction controls plus native-state adversaries."""
import copy
from checker import digest, encode, verify
from engine import Engine
from native import Native
from predecessor_controls import run as predecessor
from state_audit import check
from transaction import Rejected


def packet(m,version,ctx,edges=(),balances=()):
    return {'version':version,'context':ctx,'old_model':digest(m),'edges':list(edges),'balances':list(balances)}


def stripped(rec):
    result=copy.deepcopy(rec);result.pop('query_wall_s');result.pop('timing');return result


def run(ctx):
    base=predecessor(ctx);names=base['controls'];evidence=[]
    m={'id':'native-controls','n':2,'b':[2,-2],'denominator':1,'edges':[{'a':0,'z':1,'l':0,'u':3,'c':1}]}
    e=Engine(m,ctx,'generic-warm');first=e.query();check(e.state.model,first,None,e.route,0)
    q=packet(m,0,ctx,balances=[{'node':0,'old':2,'new':1},{'node':1,'old':-2,'new':-1}])
    reduced=e.query(q);assert reduced['native']['patched']['excess']==[-1,1] and reduced['proof']['flow']==[1]
    check(e.state.model,reduced,first,e.route,1);names.append('remaining-imbalance-needs-decrease')
    bad=copy.deepcopy(reduced);bad['native']['patched']['excess']=e.state.model['b'].copy()
    try:check(e.state.model,bad,first,e.route,1)
    except AssertionError:pass
    else:raise AssertionError('absolute supplies accepted as remaining imbalance')
    names.append('reject-false-absolute-supply-trace')
    before=e.native.snapshot();assert e.native.solve([0])==-2 and e.native.snapshot()==before
    names.append('reject-infeasible-preflight-witness')
    malformed=packet(e.state.model,1,ctx,edges=[{'edge':0,'field':'u','old':3,'new':-1}]);saved=encode(e.state.model)
    try:e.query(malformed)
    except Rejected:pass
    else:raise AssertionError('invalid update accepted')
    assert e.native.snapshot()==before and encode(e.state.model)==saved;names.append('transaction-rejection-preserves-native-state')
    short=packet(e.state.model,1,ctx,balances=[{'node':0,'old':1,'new':10},{'node':1,'old':-1,'new':-10}])
    cut=e.query(short);short_model=copy.deepcopy(e.state.model);check(short_model,cut,reduced,e.route,2)
    assert cut['proof']['kind']=='cut' and cut['native']['after']['solves']==1+1
    names.append('infeasible-model-skips-native-solve')
    restored=e.query(packet(e.state.model,2,ctx,balances=[{'node':0,'old':10,'new':2},{'node':1,'old':-10,'new':-2}]))
    check(e.state.model,restored,cut,e.route,3);assert restored['proof']['flow']==[2] and restored['native']['constructions']==1
    names.append('retain-object-through-shortage-recovery');e.close()
    evidence.append({'initial':stripped(first),'decreased':stripped(reduced),'cut':stripped(cut),'shortage_model':short_model,'restored':stripped(restored)})
    e=Engine(m,ctx,'guard-generic');first=e.query();floor=e.query(packet(m,0,ctx,edges=[{'edge':0,'field':'l','old':0,'new':1}]))
    assert floor['stats']['guard_accepted'] and floor['native']['after']['y']==[2] and floor['proof']['flow']==[2]
    assert floor['native']['after']['excess']==[-1,1] and floor['native']['after']['solves']==1
    check(e.state.model,floor,first,e.route,1);names.append('guarded-proof-distinct-from-unsolved-native-hint')
    updated=e.query(packet(e.state.model,1,ctx,balances=[{'node':0,'old':2,'new':3},{'node':1,'old':-2,'new':-3}]))
    check(e.state.model,updated,floor,e.route,2);assert updated['proof']['flow']==[3] and not any(updated['native']['after']['excess'])
    names.append('solve-after-guarded-lower-transform');e.close()
    e=Engine(m,ctx,'generic-warm');initial=e.query()
    cap=e.query(packet(m,0,ctx,edges=[{'edge':0,'field':'u','old':3,'new':1}]))
    assert cap['native']['patched']['y']==[1] and cap['proof']['kind']=='cut'
    names.append('capacity-clamp-below-retained-flow');e.close()
    e=Engine(m,ctx,'generic-warm');failure=e.query(force_native_failure=True)
    assert failure['stats']['native_failure'] and failure['action']=='charged-native-fallback' and failure['native']['status_forced_control']
    check(e.state.model,failure,None,e.route,0);names.append('simulated-status-charged-native-fallback')
    again=e.query();check(e.state.model,again,failure,e.route,1);assert again['native']['constructions']==2
    names.append('rebuild-after-native-status-fallback');e.close()
    names.append('native-topology-guard')
    s=Native(m);changed=copy.deepcopy(m);changed['edges'][0]['z']=0
    try:s.patch(changed)
    except AssertionError:pass
    else:raise AssertionError('topology mutation accepted')
    s.close()
    base['native_evidence']=evidence+[{'floor':stripped(floor),'updated':stripped(updated),'fallback':stripped(failure),'rebuilt':stripped(again)}]
    assert len(names)==42 and len(set(names))==42
    return base
