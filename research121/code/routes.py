"""Exact parametric envelopes and distinct guarded/immutable/window/point paths."""
from collections import OrderedDict
from fractions import Fraction as Q
import json
from pathlib import Path
import backend as B
import native as N

ROOT=Path(__file__).resolve().parents[1]


def pair(t):t=Q(t);return [t.numerator,t.denominator]


def envelope(row):
    states=[(0,0,0,0)]
    for j,(w,p,v) in enumerate(zip(row['weights'],row['profits'],row['slopes'])):
        states+= [(a+w,b+p,c+v,m|(1<<j)) for a,b,c,m in states if a+w<=row['capacity']]
    lines={}
    for w,p,v,m in states:
        if v not in lines or (p,-m)>(lines[v][0],-lines[v][1]):lines[v]=(p,m)
    hull=[];begins=[]
    for v,(p,m) in sorted(lines.items()):
        begin=None
        while hull:
            pv,pp,pm=hull[-1];begin=Q(pp-p,v-pv)
            if len(hull)==1 or begin>begins[-1]:break
            hull.pop();begins.pop()
        if not hull:begin=None
        hull.append((v,p,m));begins.append(begin)
    blocks=[]
    for i,(v,p,m) in enumerate(hull):
        lo=Q(0) if begins[i] is None else max(Q(0),begins[i]);hi=Q(row['end']) if i+1==len(hull) else min(Q(row['end']),begins[i+1])
        if lo<hi:blocks.append(dict(lo=pair(lo),hi=pair(hi),packing=m))
    assert blocks and blocks[0]['lo']==[0,1] and blocks[-1]['hi']==[row['end'],1]
    return blocks


def factor(row):
    alpha=None
    for p,v in zip(row['profits'],row['slopes']):
        if not p:
            if v:return None
        else:
            a=Q(v,p)
            if alpha is not None and a!=alpha:return None
            alpha=a
    alpha=alpha or Q(0)
    return alpha if min(Q(1),1+alpha*row['end'])>0 else None


def choose(row,observations,policy,forecast=None):
    if factor(row) is not None:return 'factor'
    count=len(observations) if forecast is None else forecast
    bucket='repeated' if forecast is None and len(set(map(Q,observations)))<=4 and count>4 else ('dense' if count>4 else 'sparse')
    return policy['choices'][bucket]


def stream(row,observations,method='points',route='native',certificate_cap=None):
    begin=N.clock();phases={};facts=[];outputs=[];cache=OrderedDict();blocks=[];failed=0;evictions=0;guard_reads=0;hits=0;capped=False
    start=N.clock();session=B.Session('fork' if route=='cp-fork' else 'process') if route.startswith('cp-') else None
    phases['checker_session_start_parent']=N.elapsed(start)['cpu']
    def add(cost):
        for k,v in cost.items():phases[k]=phases.get(k,0.0)+v
    def point(t,allow_cache=True):
        nonlocal hits,evictions
        t=Q(t)
        if allow_cache and t in cache:
            f=cache.pop(t);cache[t]=f;hits+=1;return f
        f,cost=B.produce(row,t,route,session);add(cost);facts.append(dict(row=row,fact=f));cache[t]=f
        if method=='lru4' and len(cache)>4:cache.popitem(last=False);evictions+=1
        return f
    alpha=factor(row) if method=='factor' else None
    if alpha is not None:
        f=point(0);blocks=[dict(lo=[0,1],hi=[row['end'],1],packing=f['packing'],rule='factor',alpha=pair(alpha),basis=f)]
    elif method in ['snapshot','guarded']:
        start=N.clock();proposed=envelope(row);phases['curve_discovery']=N.elapsed(start)['cpu']
        for block in proposed:
            required={Q(*block[k]) for k in ['lo','hi']}-set(cache)
            if certificate_cap is not None and len(facts)+len(required)>certificate_cap:
                capped=True;failed+=1;blocks=[];break
            a,b=point(Q(*block['lo'])),point(Q(*block['hi']));m=block['packing']
            assert N.value(N.scaled(row,Q(*block['lo'])),m)==a['objective'] and N.value(N.scaled(row,Q(*block['hi'])),m)==b['objective']
            blocks.append(dict(**block,rule='endpoints',left=a,right=b))
    for t0 in observations:
        t=Q(t0);assert 0<=t<=row['end'];start=N.clock();block=next((b for b in blocks if Q(*b['lo'])<=t<=Q(*b['hi'])),None)
        phases['lookup_and_context']=phases.get('lookup_and_context',0.0)+N.elapsed(start)['cpu']
        assert N.scope(row)==(facts[0]['fact']['model'] if facts else N.scope(row))
        if block is not None:
            mask=block['packing']
            if method=='guarded' and block['rule']=='endpoints':
                start=N.clock()
                for f in [block['left'],block['right']]:
                    payload=(ROOT/f['proof']).read_bytes();assert N.sha(payload)==f['proof_sha256'];guard_reads+=1
                    if f['producer']=='native':assert payload.decode().startswith(N.certificates.prefix(row,Q(*f['time']),f['objective']))
                    elif f['producer']=='cp':
                        assert N.sha((ROOT/f['formula']).read_bytes())==f['formula_sha256']
                    assert f['model']==N.scope(row) and N.value(N.scaled(row,Q(*f['time'])),mask)==f['objective']
                phases['guarded_hash_and_endpoint_admission']=phases.get('guarded_hash_and_endpoint_admission',0.0)+N.elapsed(start)['cpu']
        elif method=='window2':
            f=point(t);mask=f['packing'];hi=min(Q(row['end']),t+2)
            if hi>t:
                g=point(hi)
                if N.value(N.scaled(row,hi),mask)==g['objective']:blocks.append(dict(lo=pair(t),hi=pair(hi),packing=mask,rule='endpoints',left=f,right=g))
                else:failed+=1
        else:mask=point(t,allow_cache=method!='points')['packing']
        outputs.append(dict(time=pair(t),packing=mask,objective=N.value(N.scaled(row,t),mask)))
    if session is not None:
        start=N.clock();session.close();phases['resident_parent_import_ipc_shutdown']=N.elapsed(start)['cpu']-session.reported
    start=N.clock();path=ROOT/'evidence/outputs'/N.sha(N.encode([N.scope(row),[pair(t) for t in observations],method,route,certificate_cap]));path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(N.encode(outputs))
    phases['output_io']=N.elapsed(start)['cpu'];total=N.elapsed(begin)
    logical=dict(row=row,method=method,route=route,observations=[pair(t) for t in observations],outputs=outputs,facts=facts,blocks=blocks,
        failed_probes=failed,cache_hits=hits,evictions=evictions,guarded_file_reads=guard_reads,preparation_capped=capped,certificate_cap=certificate_cap)
    measurements=dict(total=total,phases=phases,phase_sum=sum(phases.values()),residual_cpu=total['cpu']-sum(phases.values()))
    return logical,measurements
