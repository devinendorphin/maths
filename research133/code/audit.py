"""Independent reference audit plus checker mutation replay of every proof."""
import hashlib
import json
from pathlib import Path
import time
from checker import encode, verify
from reference import check_certificate, enumerate_fair, enumerate_static, network_simplex
from routes import invalid_controls

ROOT=Path(__file__).resolve().parents[1]


def run():
    tick=time.perf_counter();cpu=time.process_time()
    freeze=json.loads((ROOT/'Freeze.json').read_text())
    for name,sha in freeze['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    inputs=json.loads((ROOT/'Inputs.json').read_text())
    sessions=json.loads((ROOT/'Sessions.json').read_text())['sessions']
    assert len(sessions)==232 and all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
    proofs={};answers={};counts={};queries=0;controls=0;enumerated=0
    mathematical={}
    for session in sessions:
        name=session['name'];out=ROOT/'outputs'/name
        w=json.loads((out/'Worker.json').read_text())
        assert w['child_processes']==0 and w['dependency']==freeze['dependency']
        assert w['cache_peak_bytes']<=session['cache_limit']
        if session['mode']=='budget':assert w['evictions']==9 and w['cache_peak_bytes']==0
        for r in w['records']:
            queries+=1;mode=session['mode'];counts[mode]=counts.get(mode,0)+1
            model,proof=r['model'],r['proof'];data=encode(proof)
            assert (out/(r['label']+'.json')).read_bytes()==data
            assert len(data)==r['proof_bytes']<=16384
            assert hashlib.sha256(data).hexdigest()==r['proof_sha256']
            assert verify(model,proof,freeze['dependency']) and check_certificate(model,proof)
            key=hashlib.sha256(encode(model)).hexdigest()
            if key not in answers:answers[key]=network_simplex(model)[0]
            assert proof.get('cost_units')==answers[key],(name,r['label'])
            assert sum(r['timing'].values())<=r['query_wall_s']+1e-6
            if r['proof_sha256'] not in proofs:
                proofs[r['proof_sha256']]={'model':model,'proof':proof,'controls':invalid_controls(model,proof,freeze['dependency'])}
                controls+=len(proofs[r['proof_sha256']]['controls'])
            # All fields except measured timings are meaningful replication data.
            mathematical[name+'/'+r['label']]={k:v for k,v in r.items() if k not in ['timing','query_wall_s','query_cpu_s']}
        if w['mode']=='static':
            assert len(w['records'])==11
            for r in w['records']:
                value,count=enumerate_static(r['model']);enumerated+=count
                assert r['proof'].get('cost_units')==value
        if w['mode']=='fairness':
            reference=enumerate_fair(inputs['fairness'][w['index']]);enumerated+=reference['assignments']
            ex=w['extras']
            assert ex['selected_coverage']==reference['coverage'] and ex['fair_cost_units']==reference['cost_units'] and ex['scalar_cost_units']==reference['scalar_cost_units']
            # Descending exhaustive candidate sweep; every rejected higher floor is certified.
            candidates=[r for r in w['records'] if 'coverage_candidate' in r]
            assert all(r['proof']['kind']=='cut' for r in candidates[:-1])
            if ex['selected_coverage'] is None:assert candidates[-1]['proof']['kind']=='cut'
            else:assert candidates[-1]['proof']['kind']=='optimal'
        if w['mode']=='counterexample':assert w['extras']=={'single_edge_updates':5,'optimal_plan_changes':5}
        mathematical[name+'/session']={k:v for k,v in w.items() if k not in ['records','worker_wall_s','worker_cpu_s','kernel_self_maxrss_kib']}
    report={'passed':True,'workers':len(sessions),'queries':queries,'query_counts':counts,'distinct_models_or_observations':len(answers),'distinct_certificates':len(proofs),'invalid_controls_rejected':controls,'enumerated_assignments':enumerated,'reference':'NetworkX 3.4.2 network_simplex plus independently coded exhaustive enumeration','audit_wall_s':time.perf_counter()-tick,'audit_cpu_s':time.process_time()-cpu}
    (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'Proof-controls.json').write_text(json.dumps(proofs,indent=2,sort_keys=True)+'\n')
    (ROOT/'Mathematical-records.json').write_text(json.dumps(mathematical,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report))


if __name__=='__main__':run()
