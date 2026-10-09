"""Independent original-model audit of the selector-inclusive supplement."""
import collections
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import time
import audit_v3 as A
ROOT=Path(__file__).resolve().parents[1]
for name,sha in json.loads((ROOT/'Selector-freeze.json').read_text())['files'].items():assert A.digest(ROOT/name)==sha,name
policy=json.loads((ROOT/'Policy.json').read_text());records=json.loads((ROOT/'Selector-results.json').read_text());proofs={};start=time.perf_counter()
assert len(records)==60 and collections.Counter(x['stage'] for x in records)=={126:36,130:24}
for item in records:
    d=item['logical'];m=item['measurements'];row=d['row'];obs=[Q(*t) for t in d['observations']];forecast=d['forecast_count'];alpha=None;factor=True
    for p,v in zip(row['profits'],row['slopes']):
        if p:
            a=Q(v,p)
            if alpha is not None and a!=alpha:factor=False
            alpha=a
        elif v:factor=False
    alpha=alpha or Q(0)
    count=len(obs) if forecast is None else forecast
    bucket='repeated' if forecast is None and len(set(obs))<=4 and count>4 else ('dense' if count>4 else 'sparse')
    expected='factor' if factor and min(1,1+alpha*row['end'])>0 else policy['choices'][bucket]
    assert d['selected_method']==expected
    assert m['total']['cpu']>=m['method_total']['cpu'] and m['phases']['policy_selection']>=0
    assert abs(m['phase_sum']+m['residual_cpu']-m['total']['cpu'])<1e-8 and m['residual_cpu']>=-0.002
    for o in d['outputs']:A.answer(row,Q(*o['time']),o['packing'],o['objective'])
    for item in d['facts']:
        f=item['fact'];assert f['producer']=='native' and f['model']==A.model(row)
        p=ROOT/f['proof'];assert A.digest(p)==f['proof_sha256'];A.answer(row,Q(*f['time']),f['packing'],f['objective']);A.header_binding(p,row,Q(*f['time']));proofs[f['proof_sha256']]=p
    for b in d['blocks']:
        for t in [Q(*b['lo']),Q(*b['hi'])]:
            objective=sum(t.denominator*p+t.numerator*v for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])) if b['packing']>>j&1);A.answer(row,t,b['packing'],objective)
        if b['rule']=='factor':assert all(Q(v)==Q(*b['alpha'])*p for p,v in zip(row['profits'],row['slopes']))
controls=ROOT/'evidence/selector-false';controls.mkdir(parents=True,exist_ok=True)
for sha,p in proofs.items():
    assert A.check_vipr(p);text=p.read_text();match=re.search(r'RTP\s+range\s+(\S+)\s+(\S+)',text);assert match[1]==match[2];sense=re.search(r'OBJ\s+(max|min)',text)[1];target=Q(match[1])+(1 if sense=='min' else -1)
    bad=controls/(sha+'.vipr');bad.write_text(text[:match.start()]+f'RTP range {target} {target}'+text[match.end():]);assert not A.check_vipr(bad)
report=dict(passed=True,records=60,counts=A.COUNTS,distinct_native_proofs=len(proofs),valid_replayed=len(proofs),false_bound_rejected=len(proofs),wall=time.perf_counter()-start)
(ROOT/'Selector-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
