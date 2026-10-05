"""Independent audits, compact records, and cached audit-only integer oracles."""
import hashlib
import json
import math
import time
from collections import defaultdict
from audit import Checker, optimum, rational_horizon
from common import value

CERTS=set()
ORACLES={}

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def check_cert(row,cert):
    key=digest([row['weights'],row['profits'],row['slopes'],row['capacity'],cert])
    if key in CERTS: return key
    ch=Checker(row)
    for j in range(len(cert['layers'])):
        ch.deadline=time.perf_counter()+45; ch.layer(cert,j)
    if cert.get('current'):
        ch.deadline=time.perf_counter()+45
        ch.layer(cert,cert['current']['prefix'],partial=True)
    if cert['complete']:
        ch.deadline=time.perf_counter()+45; ch.terminal(cert)
    CERTS.add(key)
    return key

def audit_path(row,result):
    start=time.process_time(); ch=Checker(row)
    cert_hashes=[check_cert(row,r['proof']) for r in result['constructions']]
    for n in result['native']:
        ch.deadline=time.perf_counter()+45
        assert n['empty']
        if n['status']!='complete': continue
        t=n['time']; q=[P+t*S for P,S in zip(ch.p,ch.v)]
        assert value(ch.w,n['packing'])<=ch.c
        assert n['objective']==value(q,n['packing'])==optimum(ch.w,q,ch.c)
        ch.cover(n['proof']); ch.prices(n['proof'],t,n['packing'])
    for e in result['events']:
        ch.deadline=time.perf_counter()+45
        if e['kind'] in ('scalar_expiry','fallback_reprice'): ch.repair(e)
    for segment in result['segments']:
        ch.deadline=time.perf_counter()+45
        t=segment['anchor']; m=segment['packing']
        if segment['kind']=='scalar':
            ch.cover(segment['proof']); ch.prices(segment['proof'],t,m)
            q=[P+t*S for P,S in zip(ch.p,ch.v)]
            hs=[rational_horizon(cell,ch.w,q,ch.v,m) for cell in segment['proof']]
            assert hs==segment['certificate']['cell_horizons']
            assert segment['certificate']['first_failure']==min((h for h in hs if h is not None),default=None)
        elif segment['kind']=='normalized':
            assert ch.p==ch.v
            assert segment['certificate']['factor']==dict(intercept=1,slope=1,interval=[0,None])
            ch.cover(segment['base_proof']); ch.prices(segment['base_proof'],0,m)
        else:
            cert=result['constructions'][segment['construction']]['proof']
            assert cert['complete']
            a,b=cert['interval']; assert a<=t and (b is None or segment['until']<=b)
            target=value(ch.p,m)+t*value(ch.v,m)
            assert max(P+t*S for P,S,M in cert['lines'])==target
            candidates=[t+(target-P-t*S)//(S-value(ch.v,m))+1 for P,S,M in cert['lines'] if S>value(ch.v,m)]
            assert segment['loss']==min(candidates,default=None)
    if result.get('gate'):
        features=result['gate']['features']; bounds=[]
        for j in range(ch.n+1):
            xs=ch.v[:j]; g=math.gcd(*[abs(x) for x in xs]) if xs else 0
            bins=1 if not g else 1+sum(abs(x) for x in xs)//g
            bounds.append((ch.c+1)*bins)
        assert bounds==features['prefix_bounds']
        assert sum(bounds)==features['E_bound'] and 2*sum(bounds[:-1])==features['T_bound']
    # The dense capacity DP is audit-only; policy.py cannot import it.
    key=digest([ch.w,ch.p,ch.v,ch.c,row['end']])
    if key not in ORACLES:
        ORACLES[key]=[optimum(ch.w,[P+t*S for P,S in zip(ch.p,ch.v)],ch.c) for t in range(row['end']+1)]
    oracle=ORACLES[key]
    native=[n for n in result['native'] if n['status']=='complete']
    end=row['end'] if result['status']=='window_complete' else max(0,result['final_time']-1)
    for t in range(end+1):
        m=next(n['packing'] for n in reversed(native) if n['time']<=t)
        assert value(ch.p,m)+t*value(ch.v,m)==oracle[t], (row['case_id'],result['policy'],t)
        for s in result['segments']:
            if s['kind']=='frontier' and s['anchor']<=t<=s['until']:
                cert=result['constructions'][s['construction']]['proof']
                assert max(P+t*S for P,S,M in cert['lines'])==oracle[t]
    expected=defaultdict(int)
    for e in result['ledger']:
        assert 0<=e['time']<=row['end']
        for k,v in e['counters'].items():
            if isinstance(v,(int,float)) and not k.endswith('cpu'):
                expected[k]=max(expected[k],v) if k.endswith('_peak') else expected[k]+v
    assert all(expected[k]==v for k,v in result['totals'].items())
    assert abs(result['cpu_reconciliation_error'])<0.001
    return dict(passed=True,integer_time_checks=end+1,certificate_hashes=cert_hashes,
                oracle_hash=digest(oracle),checks=dict(ch.checks),audit_cpu=time.process_time()-start)
