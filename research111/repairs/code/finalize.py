"""Post-run comparison/reporting; does not execute or change experimental results."""
import collections
import hashlib
import json
from pathlib import Path
import shutil
import statistics

ROOT = Path(__file__).resolve().parents[1]
RUNS = [Path('/workspace/maths-onboarding')/name for name in ['repair-headline','repair-replication']]


def read(root, name):
    return json.loads((root/name).read_text())


def dump(name, value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    a,b = RUNS
    results = [read(p,'Results.json') for p in RUNS]
    assert len(results[0]) == len(results[1]) == 77
    assert [(r['kind'],r['logical']) for r in results[0]] == [(r['kind'],r['logical']) for r in results[1]]
    assert [r['logical'] for r in read(a,'Memory-repair.json')] == [r['logical'] for r in read(b,'Memory-repair.json')]
    assert read(a,'Checker-fixtures.json') == read(b,'Checker-fixtures.json')
    identities=[]
    for p in sorted((a/'evidence').rglob('*.vipr')):
        name=p.relative_to(a).as_posix();q=b/name
        assert q.exists() and p.read_bytes()==q.read_bytes(), name
        identities.append(dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    for filename in ['Audit.json','Integrity-audit.json']:
        assert all(read(p,filename)['passed'] for p in RUNS)
    dump('Replication.json',dict(passed=True,records_per_run=77,memory_supplements_per_run=2,
         mathematical_and_admission_fields_match=True,raw_and_final_proofs_match=True,
         proof_files_compared=len(identities),
         excluded_fields={'Results.json[].measurements':'All timings, CPU phases, resource counters, memory measurements and their arithmetic residuals are observations, not mathematical identities; retained in both raw runs.',
                          'Memory-repair.json[].measurements':'RSS/PSS and timing observations; all logical fields compared exactly.',
                          'Execution.json.wall and Audit.json.wall':'Elapsed measurements; all non-time audit fields compared separately.',
                          'evidence/scip/*.set and *.log':'Absolute fresh-directory file paths and diagnostic timings; raw and completed proof bytes compared separately.'},
         no_logical_fields_excluded=True, shared_sdk_installation=True, independent_sdk_installation=False))
    assert {k:v for k,v in read(a,'Audit.json').items() if k!='wall'} == {k:v for k,v in read(b,'Audit.json').items() if k!='wall'}
    dump('Proof-manifest.json',identities)
    table=[]
    for root,rr in zip(RUNS,results):
        groups=collections.defaultdict(list)
        for r in rr:
            d=r['logical'];m=r['measurements'];key=(r['kind'],d.get('case_id'),d.get('density'),d.get('method'))
            cost=m.get('total',m)
            if 'cpu' in cost:
                groups[key].append(cost['cpu'])
        for key,values in groups.items():
            table.append(dict(run=root.name,kind=key[0],case_id=key[1],density=key[2],method=key[3],
                              total_cpu_seconds=values,median_total_cpu_seconds=statistics.median(values)))
    cache=[]
    for root,rr in zip(RUNS,results):
        for r in rr:
            if r['kind']=='R119-120':
                cache.append(dict(run=root.name,case_id=r['logical']['case_id'],measurements=r['measurements'],
                                  correction='resident_process_tree fields measure runner only in this runtime; invalid as combined process memory. Use Memory-repair.json for controlled live runner+checker checkpoint.'))
    dump('Summary.json',dict(records_per_run=77,base_models=3,additional_model_variants='capacity, weight and affine-objective modifications of two base fixtures; not extra independently sampled models',
         native_scip_certificates_per_run=9,requiring_completion_per_run=6,
         audits=[read(p,'Audit.json') for p in RUNS],timing_table=table,cache_memory=cache,
         memory_checkpoints=[dict(run=p.name,records=read(p,'Memory-repair.json')) for p in RUNS],
         setup_cost_scope='320.28s exact-build setup script plus 93.05s completion-build script; excludes inherited source acquisition, prior development and CMake installation. Not a measured total installation cost.',
         unresolved=['Historical 300-worker archive unrecovered','No recovered CP2024/VeriPB implementation','Density policy remains degenerate','Unmodified execution process-tree peak not established','Optimization and native witness construction inseparable in producer']))
    for name in ['Results.json','Memory-repair.json','Audit.json','Integrity-audit.json','Execution.json','Checker-fixtures.json']:
        shutil.copy2(a/name,ROOT/name)
    shutil.copy2(b/'Audit.json',ROOT/'Fresh-audit.json')
    shutil.copy2(b/'Integrity-audit.json',ROOT/'Fresh-integrity-audit.json')
    print('Exact replication comparison passed; compact reports copied.')


if __name__=='__main__':
    main()
