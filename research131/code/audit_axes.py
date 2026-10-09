from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import oracle as A
ROOT=Path(__file__).resolve().parents[1]
for name,sha in json.loads((ROOT/'Axes-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
record=json.loads((ROOT/'Axes-results.json').read_text());d=record['logical'];row=d['row'];proofs={}
assert row['weights']==[1,1,1] and row['capacity']==1 and row['profits']==[3,0,0] and row['v']==[0,2,0] and row['u']==[0,0,2]
# Two independent coefficient columns, affecting separately feasible packings.
assert row['v'][1]*row['u'][2]-row['v'][2]*row['u'][1]==4
for f in d['facts']:
    t,s=Q(*f['parameter'][0]),Q(*f['parameter'][1]);scale=math.lcm(t.denominator,s.denominator)
    expected=dict(n=3,weights=[1,1,1],capacity=1,profits=[3*scale,int(2*t*scale),int(2*s*scale)],slopes=[0,0,0],end=1)
    assert f['encoded_row']==expected and f['scale']==scale
    fact=f['fact'];p=ROOT/fact['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==fact['proof_sha256'];A.answer(expected,0,fact['packing'],fact['objective']);A.header_binding(p,expected,0);proofs[fact['proof_sha256']]=p
for o in d['outputs']:
    t,s=Q(*o['parameter'][0]),Q(*o['parameter'][1]);v=[0,Q(3),2*t,2*s]
    assert o['packing'] in [0,1,2,4] and Q(*o['value'])==v[[0,1,2,4].index(o['packing'])]==max(v)
    assert o['reused']==(t>=0 and s>=0 and t+s<=Q(3,2))
inner=next(o for o in d['outputs'] if o['parameter']==[[1,1],[1,1]])
assert not inner['reused'] and Q(*inner['value'])==3 # same optimal candidate beyond admitted triangle
controls=ROOT/'evidence/axes-false';controls.mkdir(parents=True,exist_ok=True)
for sha,p in proofs.items():
    good=subprocess.run([str(A.CHECKER),str(p)],capture_output=True,text=True,timeout=30);assert good.returncode==0 and 'Successfully verified optimal value range' in good.stdout
    text=p.read_text();match=re.search(r'RTP\s+range\s+(\S+)\s+(\S+)',text);assert match[1]==match[2];bad=controls/(sha+'.vipr');target=Q(match[1])-1;bad.write_text(text[:match.start()]+f'RTP range {target} {target}'+text[match.end():])
    rejected=subprocess.run([str(A.CHECKER),str(bad)],capture_output=True,text=True,timeout=30);assert rejected.returncode!=0
report=dict(passed=True,rank_two_objective=True,original_query_checks=len(d['outputs']),encoded_answer_checks=A.COUNTS['answers'],bindings=A.COUNTS['proof_bindings'],distinct_valid_proofs=len(proofs),false_bounds_rejected=len(proofs),supplement=True)
(ROOT/'Axes-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
