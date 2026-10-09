"""Independent rational subset, explicit polygon, original binding and replay audit."""
from fractions import Fraction as Q
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import oracle as A
ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pb_check(formula,proof):
    sdk=json.loads((ROOT/'SDK.json').read_text())
    p=subprocess.run([sdk['pb_python'],'-m','veripb',str(formula),str(proof)],env=dict(os.environ,PYTHONPATH=sdk['pb_source'],PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=30)
    return p.returncode==0 and 'Verification succeeded' in p.stdout
def vipr_check(proof):
    p=subprocess.run([str(A.CHECKER),str(proof)],capture_output=True,text=True,timeout=30)
    return p.returncode==0 and 'Successfully verified optimal value range' in p.stdout


def point_value(row,mask,q):
    t,s=Q(*q[0]),Q(*q[1])
    return sum(p+t*v+s*u for j,(p,v,u) in enumerate(zip(row['profits'],row['v'],row['u'])) if mask>>j&1)
def best(row,q):
    return max(point_value(row,m,q) for m in range(1<<row['n']) if sum(w for j,w in enumerate(row['weights']) if m>>j&1)<=row['capacity'])
def membership(row,q,partial=False):
    t,s=Q(*q[0]),Q(*q[1])
    if row['case_id']=='crossing':return t>=0 and s>=0 and 2*t+s<=3
    if row['case_id']=='stable' or partial:return t>=0 and s>=0 and t+s<=2
    return 0<=t<=2 and 0<=s<=2


def run():
    for name,digest in json.loads((ROOT/'Freeze.json').read_text())['files'].items():assert sha(ROOT/name)==digest,name
    fixtures=json.loads((ROOT/'Fixtures.json').read_text());proofs={};answers=0
    for f in fixtures:
        row=f['row'];p=ROOT/f['proof'];assert sha(p)==f['proof_sha256'];A.answer(row,0,f['packing'],f['objective'])
        if f['producer']=='cp':
            formula=ROOT/f['formula'];assert sha(formula)==f['formula_sha256']
            expected='min:'+''.join(f' {-v} x{j}' for j,v in enumerate(row['profits']))+' ;\n'+''.join(f'-{w} x{j} ' for j,w in enumerate(row['weights']))+f'>= -{row["capacity"]} ;\n'
            assert formula.read_text()==expected
            bounds=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',p.read_text());assert int(bounds[1])==int(bounds[2])==-f['objective']
            proofs[('cp',f['formula_sha256'],f['proof_sha256'])]=(p,formula)
        else:A.header_binding(p,row,0);proofs[('native',f['proof_sha256'])]=(p,None)
    results=json.loads((ROOT/'Results.json').read_text());assert len(results)==27 and sum(x['stage']==131 for x in results)==24
    memory=[];geometries=[]
    for item in results:
        d=item['logical'];m=item['measurements']
        if item['stage']==131:
            f=fixtures[d['fixture']];assert d['accepted'] and d['proof_sha256']==f['proof_sha256'] and d['formula_sha256']==f.get('formula_sha256')
            usage=m['kernel_child'];assert usage['exit']==0 and usage['child_maxrss_kib']>=0 and usage['launcher_maxrss_kib']>=0 and usage['child_cpu']>=0
            assert m['total']['child_cpu']+0.002>=usage['child_cpu'] and m['parent_lifetime_maxrss_kib']>0
            assert (m['sampling'] is not None)==d['observer']
            if d['observer']:assert m['sampling']['samples']>0
            memory.append(dict(fixture=d['fixture'],observer=d['observer'],repeat=item['repeat'],kernel_child_peak_positive=usage['child_maxrss_kib']>0,sampled_child_or_launcher_seen=m['sampling']['max_positive_processes']>=2 if d['observer'] else None))
            continue
        row=d['row'];expected_admission=all(point_value(row,row['candidate'],q)==best(row,q) for q in row['vertices']);assert d['admitted']==expected_admission
        assert d['partial_admitted']==all(point_value(row,row['candidate'],q)==best(row,q) for q in row['vertices'][:3])
        for item in d['facts']:
            q=item['parameter'];t,s=Q(*q[0]),Q(*q[1]);scale=math.lcm(t.denominator,s.denominator);assert item['scale']==scale
            expected=dict(n=row['n'],weights=row['weights'],capacity=row['capacity'],profits=[int(scale*(p+t*v+s*u)) for p,v,u in zip(row['profits'],row['v'],row['u'])],slopes=[0]*row['n'],end=1)
            assert item['encoded_row']==expected
            f=item['fact'];p=ROOT/f['path'];assert sha(p)==f['proof_sha256'] and f['time']==[0,1]
            A.answer(expected,0,f['packing'],f['objective']);A.header_binding(p,expected,0);proofs[('native',f['proof_sha256'])]=(p,None)
            assert Q(f['objective'],scale)==best(row,q)
        for o in d['outputs']:
            assert sum(w for j,w in enumerate(row['weights']) if o['packing']>>j&1)<=row['capacity']
            assert Q(*o['value'])==point_value(row,o['packing'],o['parameter'])==best(row,o['parameter']);answers+=1
            assert o['reused']==(expected_admission and membership(row,o['parameter']))
            assert o['partial_hull_applicable']==(d['partial_admitted'] and membership(row,o['parameter'],True))
        assert d['old_point_binding_at_1_0'] is False and d['old_point_proof_valid_for_original'] and d['candidate_stable_at_1_0']
        # Exercise the actual independent header binder on the old bytes under
        # the new objective. It must reject, despite continued answer stability.
        first=d['facts'][0];changed=dict(first['encoded_row']);changed['profits']=[p+v for p,v in zip(row['profits'],row['v'])]
        rejected=False
        try:A.header_binding(ROOT/first['fact']['path'],changed,0)
        except AssertionError:rejected=True
        assert rejected
        if row['case_id']=='corner-trap':
            assert not d['admitted'] and d['partial_admitted']
            corner=next(o for o in d['outputs'] if o['parameter']==[[2,1],[2,1]])
            assert corner['packing']!=row['candidate'] and not corner['partial_hull_applicable']
            interior=next(o for o in d['outputs'] if o['parameter']==[[3,2],[3,2]])
            assert not interior['partial_hull_applicable'] and point_value(row,row['candidate'],interior['parameter'])==best(row,interior['parameter'])
        geometries.append(dict(case=row['case_id'],admitted=d['admitted'],partial_admitted=d['partial_admitted'],reused_queries=sum(o['reused'] for o in d['outputs']),all_old_point_bindings_rejected=True))
    controls=ROOT/'evidence/audit-false';controls.mkdir(parents=True,exist_ok=True)
    for identity,(p,formula) in proofs.items():
        assert pb_check(formula,p) if formula else vipr_check(p)
        text=p.read_text()
        if formula:
            match=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);target=int(match[1])-1;text=text[:match.start()]+f'conclusion BOUNDS {target} {target}'+text[match.end():]
        else:
            match=re.search(r'RTP\s+range\s+(\S+)\s+(\S+)',text);assert match[1]==match[2];sense=re.search(r'OBJ\s+(max|min)',text)[1];target=Q(match[1])+(1 if sense=='min' else -1);text=text[:match.start()]+f'RTP range {target} {target}'+text[match.end():]
        bad=controls/(hashlib.sha256(json.dumps(identity).encode()).hexdigest()+p.suffix);bad.write_text(text)
        assert not (pb_check(formula,bad) if formula else vipr_check(bad))
    report=dict(passed=True,records=27,original_answer_checks=answers,encoded_point_answer_checks=A.COUNTS['answers'],proof_bindings=A.COUNTS['proof_bindings'],distinct_proofs=len(proofs),valid_replayed=len(proofs),false_bound_rejected=len(proofs),base_models=dict(archived_memory_fixtures=2,new_two_parameter_models=3),memory_coverage=memory,geometry=geometries,limitations=['Individual process lifetime high-water, not simultaneous process-tree peak','Includes fork/exec lifetime; launcher inherited pages bounded by small launcher footprint','Three explicit tiny geometry models, not a scalability or originality result','Shared external SDK'])
    (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':run()
