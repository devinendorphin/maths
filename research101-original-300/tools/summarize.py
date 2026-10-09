"""Post-run aggregation; not part of the prospectively frozen producer."""
import collections, hashlib, json, pathlib, statistics
ROOT = pathlib.Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def summarize(rows):
    groups = collections.defaultdict(list)
    for w in rows: groups[(w['stage'], w['case_id'], w['method'])].append(w['result'])
    out = []
    for (stage, case, method), rs in sorted(groups.items()):
        first = rs[0]
        item = dict(stage=stage, case_id=case, method=method, repeats=len(rs),
                    median_cpu=statistics.median(r['algorithm_cpu'] for r in rs),
                    min_cpu=min(r['algorithm_cpu'] for r in rs), max_cpu=max(r['algorithm_cpu'] for r in rs),
                    median_parent_cpu=statistics.median(r['parent_cpu'] for r in rs),
                    median_child_cpu=statistics.median(r['child_cpu'] for r in rs),
                    records=len(first['records']), observations=len(first['claims']),
                    certificate_bytes=first.get('certificate_bytes', sum(r['bytes'] for r in first['records'])))
        if 'proposals' in first:
            item['median_scip_solve_only_cpu'] = statistics.median(sum(p['algorithm_cpu'] for p in r['proposals']) for r in rs)
        for k in ['repeat_validations','successful_probes','failed_probes','hits','evictions','peak_entries','initial_gap','initial_status','final_status']:
            if k in first: item[k] = first[k]
        out.append(item)
    return out
NONLOGICAL = {'algorithm_cpu','algorithm_wall','parent_cpu','child_cpu','adapter_cpu',
              'checker_cpu','checker_wall','native_cpu','wall','seal'}
def logical(x):
    if isinstance(x, dict): return {k:logical(v) for k,v in x.items() if k not in NONLOGICAL}
    if isinstance(x, list): return [logical(v) for v in x]
    return x
def main(fresh):
    fresh = pathlib.Path(fresh)
    a = json.loads((ROOT/'Results.json').read_text()); b = json.loads((fresh/'Results.json').read_text())
    assert logical(a)==logical(b)
    for base in [ROOT,fresh]: assert json.loads((base/'Audit.json').read_text())['passed']
    for name in ['Results.json','Audit.json','Execution.json','Fresh-run.log','Fresh-audit.log']:
        dst=ROOT/'replication'/name;dst.parent.mkdir(exist_ok=True);dst.write_bytes((fresh/name).read_bytes())
    summary=dict(original=summarize(a), replication=summarize(b))
    (ROOT/'Summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    receipt=dict(passed=True, workers=300, logical_match=True,
        excluded_fields=sorted(NONLOGICAL),
        exclusion_note='Receipt seals contain timing diagnostics; all proof and witness hashes remain compared. Each run is independently audited.',
        fresh_directory=str(fresh), same_external_sdk=True, independent_sdk_installation=False,
        original_results_sha256=sha(ROOT/'Results.json'), replication_results_sha256=sha(fresh/'Results.json'),
        original_audit=json.loads((ROOT/'Audit.json').read_text()), replication_audit=json.loads((fresh/'Audit.json').read_text()),
        original_execution=json.loads((ROOT/'Execution.json').read_text()), replication_execution=json.loads((fresh/'Execution.json').read_text()))
    (ROOT/'Replication.json').write_text(json.dumps(receipt,indent=2)+'\n')
    lines=['# Complete CPU costs by case', '', 'Median of three timed workers, except mechanism experiments 102, 106 and 108 (one worker). CPU includes required checker children; deployment and independent auditing are separate.', '',
           '| Experiment / case | Method | Original ms | Fresh ms | Proof bytes | Point records |',
           '|---|---|---:|---:|---:|---:|']
    for x,y in zip(summary['original'],summary['replication']):
        assert (x['stage'],x['case_id'],x['method'])==(y['stage'],y['case_id'],y['method'])
        lines.append(f"| {x['case_id']} | {x['method']} | {x['median_cpu']*1000:.3f} | {y['median_cpu']*1000:.3f} | {x['certificate_bytes']} | {x['records']} |")
    (ROOT/'Cost-table.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(logical_match=True, groups=len(summary['original']), original_workers=len(a), fresh_workers=len(b))))
if __name__=='__main__':
    import sys
    main(sys.argv[1])
