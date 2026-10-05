"""Close out frozen batch; repair ONLY the post-run logical fingerprint.

The original run included algorithm_wall in its repeat hash. Original sources,
worker records and timings remain unchanged. This utility excludes clock fields,
compares complete logical results, and records the correction explicitly.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from shared import read,save,digest,value
import campaign
import audit_batch as A


def logical(obj):
    if isinstance(obj,dict):
        return {k:logical(v) for k,v in obj.items() if not k.endswith(('_cpu','_wall')) and k not in
                ('cpu','wall','component_cpu','ledger','cpu_reconciliation_error')}
    if isinstance(obj,list):return [logical(v) for v in obj]
    return obj


def finish():
    campaign.check_freeze();start=time.perf_counter();summaries=[];groups=defaultdict(list);old_mismatches=0
    paths=sorted((ROOT/'evidence').glob('[0-9]*.json.gz'))
    assert len(paths)==422
    for path in paths:
        record=read(path);r=record['result'];s=dict(record['summary']);assert record['audit']['passed']
        s['original_signature']=s['signature'];s['signature']=digest(logical(r))
        groups[(s['stage'],s['case_id'],s['method'])].append(s)
        summaries.append(s)
    for key,rows in groups.items():
        assert len({x['signature'] for x in rows})==1,key
        old_mismatches+=len({x['original_signature'] for x in rows})>1
    metrics=[]
    for stage,methods in {51:['parametric_dp','point_dp','maintain','indexed_full'],52:['cold','incumbent','tree'],53:['scan','queue']}.items():
        for method in methods:
            totals=[sum(s['algorithm_cpu'] for s in summaries if s['stage']==stage and s['method']==method and s['phase']=='timing' and s['repeat']==r) for r in range(3)]
            per=defaultdict(list)
            for s in summaries:
                if s['stage']==stage and s['method']==method and s['phase']=='timing':per[s['case_id']].append(s['algorithm_cpu'])
            metrics.append(dict(stage=stage,method=method,repeated_sums=totals,median=statistics.median(totals),
                                per_case_medians={k:statistics.median(v) for k,v in per.items()}))
    vipr=read(ROOT/'evidence/VIPR-results.json.gz');records=vipr['records']
    assert all(x['valid_returncode']==0 and x['invalid_returncode']!=0 for x in records)
    rows={x['case_id']:x for x in read(ROOT/'Inputs.json')}
    for interval in vipr['intervals']:
        row=rows[interval['case_id']];left,right=[records[i] for i in interval['endpoints']]
        assert left['packing']==right['packing']==interval['packing']
        assert left['time']==interval['left'] and right['time']==interval['right']
        for endpoint in (left,right):
            a,b=endpoint['time'];q=[b*p+a*v for p,v in zip(row['profits'],row['slopes'])]
            assert value(q,interval['packing'])==A.optimum(row['weights'],q,row['capacity'])
    native=[]
    for path in sorted((ROOT/'evidence').glob('native-point-*.json.gz')):
        r=read(path);native.append(dict(case_id=r['input']['case_id'],solves=len(r['records']),algorithm_cpu=r['algorithm_cpu']))
    probe=[s for s in summaries if s['stage']==55];model=read(ROOT/'evidence/Cost-model.json.gz')
    assert all(r['online']<=2*r['offline'] and r['offline']==min(r['price'],r['horizon']) for r in model['grid'])
    vipr_summary=dict(certificates=len(records),invalid_rejected=len(records),intervals=len(vipr['intervals']),
        integer_checks=sum(x['integer_checks'] for x in vipr['intervals']),bytes=sum(x['bytes'] for x in records),
        derivations=sum(x['meta']['derivations'] for x in records),
        **{key:sum(x[key] for x in records) for key in ('source_cpu','adapter_cpu','checker_cpu','checker_wall')})
    out=dict(workers=len(summaries),inputs=len(rows),
        integer_checks=sum(s['audit']['integer_checks'] for s in summaries)+vipr_summary['integer_checks']+sum(x['solves'] for x in native),
        rational_checks=sum(s['audit']['rational_checks'] for s in summaries),all_audits_passed=True,logical_repeats_match=True,
        timing=metrics,vipr=vipr_summary,native_point_controls=native,
        cost_model=dict(grid_cases=len(model['grid']),counterexamples=len(model['counterexamples']),theorem=model['theorem'],scope=model['scope']),
        probe=dict(complete=sum(s['complete'] for s in probe),inactive_partial=sum(not s['complete'] for s in probe),
                   transitions=sum(s['construction_counts']['dp_transitions'] for s in probe),
                   index_work=sum(s['construction_counts']['index_visits']+s['construction_counts']['index_updates'] for s in probe)),
        correction=dict(reason='Original post-run hash included algorithm_wall.',affected_logical_groups=old_mismatches,
                        experiment_changes=False,timing_changes=False,original_evidence_preserved=True,
                        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    save(ROOT/'Path-results.json',summaries);save(ROOT/'Summary.json',out)
    save(ROOT/'Final-audit.json',dict(passed=True,workers=422,expected_worker_files=422,corrected_logical_groups=len(groups),
                                    logical_repeats_match=True,freeze_intact=True,all_stored_mathematical_audits_passed=True,
                                    finalization_wall=time.perf_counter()-start,summary_sha256=hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()))
    print(json.dumps(out,indent=2))


if __name__=='__main__':finish()
