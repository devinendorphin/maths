"""Ten sealed experiments: sequential timed workers and independent audits."""
from collections import defaultdict
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from shared import ROOT,DEPS,KERNEL,ADAPTER,read,save,digest,logical
import design
import oracles as O
import curves
import audit
import proofs


def protocol():
    rows=design.inputs()
    timings=[(r['case_id'],m) for r in rows if r['timing'] for m in design.timing_methods(r['stage'])]
    return dict(version=1,previous_commit='1364047d8fee8fb095fbb30721766e4c33e72d81',input_records=len(rows),
                headline_workers=sum(len(design.METHODS[r['stage']]) for r in rows)+2,
                timing_workers=3*len(timings),repeats=3,methods=design.METHODS,timing_subset=timings,
                limits=O.LIMITS,curve_limits=dict(query_calls=2048,cpu_seconds=30),batch_wall_seconds=900,
                gate='Normalize weights by their gcd and floor capacity. Dense if normalized C<=4096, otherwise sparse for n<=16, otherwise exact B&B. Recompute and charge features at each oracle call; no learned thresholds.',
                ties='Every oracle maximizes integer-scaled profit, then side*slope, then smallest mask. B&B encodes these exactly in integers. Curve outputs need only be primary-optimal at endpoint ties.',
                audit='Independent meet-in-the-middle enumeration for n<=24; immutable exact-weight layers for larger n with C<=4096. Audit all queries, integer observations, interval endpoints, exact normalization, completed work counters and B&B partition recurrence.',
                caps='Reserve before DP transitions, sparse state or B&B node/partition output. Partial queries cannot certify intervals. Capped curve drops all trajectory/interval claims; complete earlier query answers are still audited. Warm sequences may retain only a checked prefix.',
                recovery62='Force each primary query to stop at one transition/node; retain its counts and inactive status; retry normalized dense oracle. Both attempted and fallback work are charged.',
                recovery63='Two extra tree trajectories force a zero terminal-partition output cap at t=1, then retry cold. Standard node/partition caps can also fall back cold.',
                timing='Three sequential repeats with method order rotated over fixed input subsets. Total algorithm CPU includes normalization/gate arithmetic, abandoned attempts, cleanup, query caching, trace/hash construction and output packing selection. Excludes JSON writing, input decoding and independent auditing. Incomplete/capped runs cannot win a speed comparison against complete runs.',
                memory='Retained state/output-cell count proxies only; not peak RSS or total simultaneous allocation bytes.',
                group_dependencies='56/59 common weight scaling pairs, 58 common horizon pairs, 63 H64/H256 pairs share underlying draws. They are not independent random samples.',
                proof64='Four 12-item large-weight trajectories; first two positive-length curve pieces plus two point controls each. Official pinned VIPR checks exact original problems and deliberately false final bounds. Connector rejects explicit varying feasibility, nonlinear objective, mismatched domain or packing.',
                production_solver='SCIP/PySCIPOpt still absent; proxy connection refused. 63 remains a controlled exact reference implementation, not a SCIP benchmark.',
                interpretation='Known methods and finite evaluations. No novel algorithm/theorem, universal speedup, or application result claimed. All caps/censored comparisons reported.')


def freeze():
    save(ROOT/'Inputs.json',design.inputs());save(ROOT/'Protocol.json',protocol())
    paths=list((ROOT/'code').glob('*.py'))+[ROOT/'Inputs.json',ROOT/'Protocol.json',ROOT/'Roadmap.md']
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    dependencies={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    save(ROOT/'Freeze.json',dict(files=files,dependencies=dependencies,capabilities=read(ROOT/'Capabilities.json')))
    print('FROZEN',len(design.inputs()),digest(files),flush=True)


def check_freeze():
    data=read(ROOT/'Freeze.json')
    for p,h in {**data['files'],**data['dependencies']}.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p


def execute(row,method):
    if method.startswith('point_bb_'):
        mode=method.removeprefix('point_bb_');cap=None
        if mode=='tree_cap':mode='tree';cap=0
        return curves.sequence(row,mode,cap)
    if method.startswith('force_'):return curves.run(row,'real',method.removeprefix('force_'),forced=True)
    pieces=method.split('_');kind,kernel=pieces[:2]
    return curves.run(row,kind,kernel,normalize=method.endswith('_gcd'))


def worker(row,method,phase,repeat,checker):
    path=ROOT/'evidence'/f'{row["case_id"]}--{method}--{phase}--{repeat}.json.gz'
    if path.exists():return read(path)['summary']
    r=execute(row,method);checked=checker.check(r)
    if method.startswith('force_'):
        assert r['status']=='complete' and r['aborted_calls']==r['oracle_calls']>0
    if method=='point_bb_tree_cap':assert r['aborted_calls']>=1
    s=dict(stage=row['stage'],case_id=row['case_id'],n=row['n'],capacity=row['capacity'],end=row['end'],regime=row['regime'],
           method=method,phase=phase,repeat=repeat,status=r['status'],reason=r['reason'],algorithm_cpu=r['algorithm_cpu'],
           counts=r['counts'],oracle_calls=r['oracle_calls'],aborted_calls=r['aborted_calls'],
           intervals=len(r['intervals']),integer_packings=len(set(r['packings'])),
           actual_kernels=sorted({q['kernel'] for q in r['queries']}),audit=checked,signature=digest(logical(r)))
    save(path,dict(input=row,result=r,audit=checked,summary=s))
    print('PATH',row['case_id'],method,phase,repeat,r['status'],f'cpu={r["algorithm_cpu"]:.6f}',flush=True)
    return s


def finish():
    expected=protocol();paths=sorted((ROOT/'evidence').glob('*--*.json.gz'))
    assert len(paths)==expected['headline_workers']+expected['timing_workers']
    rows=[read(p)['summary'] for p in paths];by=defaultdict(list)
    for s in rows:assert s['audit']['passed'];by[(s['case_id'],s['method'])].append(s)
    completed_repeat_groups=0;censored_groups=0
    for key,samples in by.items():
        if all(x['status']=='complete' for x in samples):
            assert len({x['signature'] for x in samples})==1,key
            if len(samples)>1:completed_repeat_groups+=1
        else:
            censored_groups+=1
            # Only a completely solved repeat may participate in an eligible timing.
    timing=[]
    for stage in range(56,66):
        for method in design.timing_methods(stage):
            selected=[x for x in rows if x['stage']==stage and x['method']==method and x['phase']=='timing']
            if not selected:continue
            totals=[sum(x['algorithm_cpu'] for x in selected if x['repeat']==r) for r in range(3)]
            cases=defaultdict(list)
            for x in selected:cases[x['case_id']].append(x)
            eligible=all(x['status']=='complete' for x in selected)
            timing.append(dict(stage=stage,method=method,repeated_sums=totals,median=statistics.median(totals),
                               eligible=eligible,complete_runs=sum(x['status']=='complete' for x in selected),runs=len(selected),
                               per_case_medians={case:statistics.median(x['algorithm_cpu'] for x in samples) for case,samples in cases.items()},
                               complete_cases=[case for case,samples in cases.items() if all(x['status']=='complete' for x in samples)]))
    proof_summaries=read(ROOT/'Proof-summary.json')
    summary=dict(workers=len(rows),inputs=len(read(ROOT/'Inputs.json')),complete_workers=sum(x['status']=='complete' for x in rows),
                 capped_workers=sum(x['status']!='complete' for x in rows),
                 integer_checks=sum(x['audit']['integer_checks'] for x in rows)+sum(x['integer_checks'] for x in proof_summaries),
                 rational_checks=sum(x['audit']['rational_checks'] for x in rows),all_stored_audits_passed=True,
                 completed_logical_repeats_match=True,completed_repeat_groups=completed_repeat_groups,censored_groups=censored_groups,
                 timing=timing,proofs=proof_summaries)
    save(ROOT/'Path-results.json',rows);save(ROOT/'Summary.json',summary)
    save(ROOT/'Final-audit.json',dict(passed=True,expected_workers=len(rows),all_stored_audits_passed=True,
                                    freeze_intact=True,summary_sha256=hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()))
    print('COMPLETED',json.dumps(summary),flush=True)


def run():
    check_freeze();start=time.perf_counter();rows=read(ROOT/'Inputs.json');checkers={};proof_summaries=[]
    for stage in range(56,66):
        subset=[x for x in rows if x['stage']==stage]
        for row in subset:
            checker=audit.Auditor(row);checkers[row['case_id']]=checker
            for method in design.METHODS[stage]:worker(row,method,'headline',0,checker)
            if stage==64:
                record=read(ROOT/'evidence'/f'{row["case_id"]}--real_gate--headline--0.json.gz')
                assert record['result']['status']=='complete'
                proof_summaries.append(proofs.run(row,record['result'],checker))
        for repeat in range(3):
            methods=design.timing_methods(stage)
            for row in subset:
                if not row['timing']:continue
                for j in range(len(methods)):
                    worker(row,methods[(j+repeat)%len(methods)],'timing',repeat,checkers[row['case_id']])
                if time.perf_counter()-start>900:raise RuntimeError('batch wall cap')
        if stage==63:
            for row in subset[:2]:worker(row,'point_bb_tree_cap','headline',0,checkers[row['case_id']])
        # Audit-only caches are discarded after each experiment; they never choose methods.
        checkers.clear();check_freeze()
    save(ROOT/'Proof-summary.json',proof_summaries);finish();check_freeze()
    save(ROOT/'Execution.json',dict(completed=True,wall_seconds=time.perf_counter()-start,batch_limit_seconds=900))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','run']);args=parser.parse_args()
    freeze() if args.action=='freeze' else run()
