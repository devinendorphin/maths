"""Independent retained-flow/remaining-imbalance arithmetic, no native dependencies."""
from checker import feasible


def check(m,rec,previous,route,step):
    trace=rec['native']
    if route not in ('generic-cold','generic-warm','guard-generic'):assert trace is None;return
    patched=trace['patched'];after=trace['after'];before=trace['before']
    assert patched['identity_stable'] and after['identity_stable']
    if before is None:
        expected_constructions=step+1 if route=='generic-cold' else (1 if previous is None else previous['native']['constructions']+1)
        assert trace['constructions']==expected_constructions
        if route!='generic-cold' and step:assert previous['stats']['native_failure']
        expected=[0]*len(m['edges']);assert patched['updates']==1 and patched['solves']==0
    else:
        assert previous is not None and route!='generic-cold'
        assert before==previous['native']['after'] and before['identity_stable']
        assert trace['constructions']==previous['native']['constructions'] and patched['updates']==before['updates']+1 and patched['solves']==before['solves']
        expected=[min(y,e['u']-e['l']) for y,e in zip(before['y'],m['edges'])]
    assert patched['y']==expected
    excess=m['b'].copy()
    for e,y in zip(m['edges'],patched['y']):
        assert 0<=y<=e['u']-e['l'];x=e['l']+y;excess[e['a']]-=x;excess[e['z']]+=x
    assert excess==patched['excess'] and sum(excess)==0
    assert after['updates']==patched['updates']
    if rec['stats']['native_failure']:
        assert rec['action']=='charged-native-fallback' and trace['solve_status']!=0 and trace['failure_after']==after
        assert feasible(m,trace['feasible_witness'])
        assert after['solves']==patched['solves']+int(trace['solve_called'])
    elif trace['solve_called']:
        assert feasible(m,trace['feasible_witness']) and trace['solve_status']==0
        assert after['solves']==patched['solves']+1 and not any(after['excess'])
        assert rec['proof']['kind']=='optimal' and rec['proof']['flow']==[e['l']+y for e,y in zip(m['edges'],after['y'])]
    else:
        assert trace['solve_status'] is None and trace['feasible_witness'] is None and after==patched
        assert rec['action'] in ('certificate-admission','generic-shortage')
