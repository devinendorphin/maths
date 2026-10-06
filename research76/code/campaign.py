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
import cache_tests


def protocol():
    rows=design.inputs();timings=[(r['case_id'],m) for r in rows if r['timing'] for m in design.timing_methods(r['stage'])]
    return dict(version=1,previous_commit='0425b3f46ab2d210ec872a7262b631fab0c5c011',input_records=len(rows),headline_workers=sum(len(design.METHODS[r['stage']]) for r in rows),timing_workers=3*len(timings),repeats=3,methods=design.METHODS,timing_subset=timings,limits=O.LIMITS,curve_limits=dict(query_calls=2048,cpu_seconds=30),batch_wall_seconds=900,
      lean='Same exact B&B scoring, bounds and traversal; omit completed terminal partitions and split traces. Cap active stack at4096 and nodes at30000. Independent MITM/layer optimality and separate traversal counter replay, not a portable lean proof certificate.',
      portfolio='Normalize on every query. If C<=4096 try dense, then lean B&B, then sparse; otherwise lean B&B, sparse, dense. Lean primary node budget3000; all other standard caps remain. No past performance selection. Charge all failed attempts. Final success alone supplies a certificate interval.',
      forced='forcedportfolio: stop each of the first two attempts at one node/transition. deadportfolio: all three at one. Incomplete attempts inactive; no interval or packing output when all fail.',
      balanced='Floor endpoint line intersection clamped inside interval; replace by midpoint when outside central quarter. Equal slopes midpoint. Width2/3 uses normal strict interior clamping; all queries and rewrite arithmetic charged.',
      ties='Scaled profit, directional slope, smallest mask. Real-curve endpoint outputs require primary optimality only.',
      audit='MITM enumeration n<=24; independent immutable exact-weight layers for n>24/C<=4096. Every completed query, integer observation, interval endpoint. Stored partition recurrences and lean traversal work counters independently replayed.',
      timing='Three sequential rotated repeats on fixed subsets. Includes preprocessing, failed attempts, choices and output construction; excludes JSON I/O and independent audits. Capped aggregates ineligible.',
      dependencies='76 includes four disclosed73 retained inputs. 78 algebraic skew controls, not sampled hard-case search. 79 horizon variants share draws. No tuning on any campaign outcome.',
      proofs='82 two fresh/reuse sweeps per curve;83 reuse sweep and explicit cache invalidation controls. Cache keyed by full feasible-set and affine-coefficient digests plus exact rational time; packing feasibility and equality to trusted accepted bound separately checked. Official VIPR accepts valid and rejects false final bounds. Metadata model assumed truthful.',
      interpretation='Known methods, finite local comparisons. Not SCIP production, formal verification, universal complexity improvement, peak-RSS measurement, statistical significance or application validation.')


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
    kernel={'gatebb':'gate_bb','gatelean':'gate_lean','lean':'bb_lean'}.get(kernel,kernel)
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
    for stage in range(76,86):
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
    print('COMPLETED',json.dumps({k:summary[k] for k in ('workers','inputs','complete_workers','capped_workers','integer_checks','rational_checks')}),flush=True)


def run():
    check_freeze();start=time.perf_counter();rows=read(ROOT/'Inputs.json');checkers={};proof_summaries=[]
    for stage in range(76,86):
        subset=[x for x in rows if x['stage']==stage]
        for row in subset:
            if time.perf_counter()-start>900:raise RuntimeError('batch wall cap')
            checker=audit.Auditor(row);checkers[row['case_id']]=checker
            for method in design.METHODS[stage]:worker(row,method,'headline',0,checker)
            if stage in (82,83):
                record=read(ROOT/'evidence'/f'{row["case_id"]}--real_dense_gcd--headline--0.json.gz')
                assert record['result']['status']=='complete'
                for reuse in ((False,True) if stage==82 else (True,)):proof_summaries.append(proofs.run(row,record['result'],checker,reuse))
                if stage==83:
                    proof=read(ROOT/'evidence'/('proof-'+row['case_id']+'-reuse.json.gz'));cache_tests.run(row,proof,checker)
        for repeat in range(3):
            methods=design.timing_methods(stage)
            for row in subset:
                if not row['timing']:continue
                for j in range(len(methods)):
                    worker(row,methods[(j+repeat)%len(methods)],'timing',repeat,checkers[row['case_id']])
                if time.perf_counter()-start>900:raise RuntimeError('batch wall cap')
        # Audit-only caches are discarded after each experiment; they never choose methods.
        checkers.clear();check_freeze()
    save(ROOT/'Cache-tests.json',[read(p) for p in sorted((ROOT/'evidence').glob('cache-tests-*.json.gz'))])
    save(ROOT/'Proof-summary.json',proof_summaries);finish();check_freeze()
    save(ROOT/'Execution.json',dict(completed=True,wall_seconds=time.perf_counter()-start,batch_limit_seconds=900))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','run']);args=parser.parse_args()
    freeze() if args.action=='freeze' else run()
