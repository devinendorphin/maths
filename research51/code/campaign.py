"""Frozen, bounded experiments 51–55, sequential timings and exact audits."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import resource
import statistics
import subprocess
import time
from shared import ROOT,REPO,KERNEL,SG,read,save,digest,value
import parametric
import reopt
import events
import audit_batch as A
import vipr_adapter
import cost_model
import policy as previous_policy

VIPR=Path('/workspace/maths-tools/vipr/viprchk')


def inputs():
    rows=[]
    for n in (8,12,16):
        for k,regime in enumerate(('bounded','wide','normalized')):
            for seed in (0,1):
                rng=random.Random(851000+n*100+k*10+seed)
                w=[rng.randint(2,18) for _ in range(n)]; p=[rng.randint(-12,36) for _ in range(n)]
                v=p.copy() if regime=='normalized' else [rng.randint(-3 if k==0 else -24,3 if k==0 else 24) for _ in range(n)]
                rows.append(dict(case_id=f'51-n{n}-{regime}-{seed}',n=n,regime=regime,split='fresh_held',
                                 weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=64,
                                 solve_times=list(range(0,65,4)),stage=51))
    prior=read(REPO/'research46/Inputs.json')
    names=['47-n12-bounded-seed1','47-n16-wide-seed1','50-n16-bounded-seed1','50-n20-wide-seed1']
    for name in names:
        row=next(x for x in prior if x['case_id']==name)
        rows.append(dict(row,case_id='retrospective-'+name,split='retrospective',end=64,
                         solve_times=list(range(0,65,4)),stage=51))
    rows.extend([
        dict(case_id='fixture-chain',n=4,regime='boundary',weights=[1]*4,profits=[48,41,26,3],slopes=[0,1,2,3],capacity=1),
        dict(case_id='fixture-simultaneous',n=8,regime='boundary',weights=[1]*8,profits=[48,41,26,3]*2,slopes=[0,1,2,3]*2,capacity=2),
        dict(case_id='fixture-empty',n=3,regime='empty',weights=[2,3,7],profits=[-1,-2,-3],slopes=[0,-1,-2],capacity=1),
        dict(case_id='fixture-zero',n=4,regime='ties',weights=[1]*4,profits=[0]*4,slopes=[0]*4,capacity=2),
        dict(case_id='fixture-endpoint-tie',n=2,regime='ties',weights=[1,1],profits=[4,4],slopes=[0,1],capacity=1),
    ])
    for row in rows:
        row.setdefault('end',64);row.setdefault('split','boundary_held');row.setdefault('stage',51)
        row.setdefault('solve_times',list(range(0,65,4)))
    return rows


def protocol():
    return dict(version=1,previous_commit='022a59194c9e817518507bd56aaa9d597d19970b',repeats=3,
        inputs='18 fresh held draws, four retrospective objective trajectories truncated to H64, five declared boundary fixtures; no threshold training',
        stages={51:'Exact endpoint/intersection DP vs point DP, original scalar maintenance and indexed frontier.',
                52:'Controlled rational B&B: cold vs incumbent-only vs retained terminal partition; not SCIP.',
                53:'Selective scalar repairs: full rescan vs cached queue; original whole-partition maintenance separately.',
                54:'VIPR 1.0 adapter for native scalar point certificates and same-packing two-endpoint interval bundles.',
                55:'Classical fixed-price theorem/grid and explicit variable-price counterexample; bounded real construction probe comparison.'},
        headline_51='All 27 rows x four methods. Native point solves on the five fixtures only; avoids conflating oracle kernels.',
        headline_52='18 fresh rows and five boundary fixtures, 17 fixed observation solves per trajectory, all three modes.',
        headline_53='All 27 rows, selective scan and queue. Two capped-inactive constructions on chain fixtures.',
        timing='Three full sequential repeats on six fresh non-normalized seed-1 rows for 51,52,53. Rotate method order. Algorithm CPU includes input preparation, solves, decisions, bound work, cleanup, output-answer selection, retained-state copies and evidence assembly; excludes JSON encoding, persistence and independent audits. CPU is machine-local.',
        memory='State-count proxies and serialized proof bytes; no isolated peak-RSS or byte-memory claim.',
        exactness='Signed integer profits and rational intersection oracles. Independent dense capacity DP, separate tie-state audit, cover/split checks, rational horizon and endpoint checks.',
        limits=dict(end=64,oracle_calls=4096,reopt_nodes_per_solve=120000,reopt_terminal_cells=4096,event_cpu_seconds=60,wall_batch_seconds=900),
        freeze='Source, input, protocol, VIPR source/build and prior-kernel hashes sealed after disjoint smoke fixtures, before headline or held timings.',
        unavailable='SCIP/PySCIPOpt/VeriPB/CakePB absent. Shell HTTP proxy refused connection. VIPR source fetched via authorized GitHub connector and compiled without changing source.',
        vipr=dict(repository='scipopt/vipr',commit='30f2951d1e90e47afa821bdd1b12b82246656c42',
                  source_git_blob='1019746a35d6d168e6c4820a28847ac92b6518ec',
                  build='g++ -O2 -std=c++14 viprchk.cpp -lgmpxx -lgmp -o viprchk; generated header sets version 1.1; no SoPlex'),
        proof_scope='Original binary knapsack, explicit bounds, no presolve. VIPR is independently executed, not claimed formally verified. Interval connector uses fixed feasibility, affine objectives and identical feasible packing at both endpoints.',
        cost_scope='2-competitive proof only for fixed known buy price, unit daily rent, free permanent service after buying, unknown horizon. Real capped construction has no transferred competitive CPU guarantee.',
        cap55='One indexed full-horizon probe, caps 256 transitions and 256 total index visits/updates; incomplete proof stays inactive then scalar maintenance starts cold. Initial probe overhead and fallback are charged.',
        proof54='Five point times 0/8/16/32/64 for first fresh 12-item bounded row; first three curve pieces of first fresh eight-item bounded row and all chain pieces; each endpoint verified externally; each generated certificate also tested with a strictly false final bound.')


def freeze():
    save(ROOT/'Inputs.json',inputs());save(ROOT/'Protocol.json',protocol())
    paths=list((ROOT/'code').glob('*.py'))+[ROOT/'Inputs.json',ROOT/'Protocol.json',ROOT/'Roadmap.md']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    kernels={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in KERNEL.glob('*.py')}
    previous={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (REPO/'research46/code').glob('*.py')}
    save(ROOT/'Freeze.json',dict(files=hashes,kernels=kernels,previous=previous,capability=read(ROOT/'Capabilities.json')))
    print('FROZEN',len(inputs()),digest(hashes),flush=True)


def check_freeze():
    seal=read(ROOT/'Freeze.json')
    for name,h in seal['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,h in seal['kernels'].items():assert hashlib.sha256((KERNEL/name).read_bytes()).hexdigest()==h,name
    for name,h in seal['previous'].items():assert hashlib.sha256((REPO/'research46/code'/name).read_bytes()).hexdigest()==h,name
    for name,h in seal['capability']['vipr_files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name


def execute(row,stage,method):
    if stage==51:
        if method=='parametric_dp':return parametric.curve(row)
        if method=='point_dp':return parametric.points(row)
        return previous_policy.run(row,method)
    if stage==52:return reopt.sequence(row,method)
    if stage==53:return events.run(row,method.replace('_cap',''),method.endswith('_cap'))
    if stage==55:
        start=time.process_time(); proof=None; ct=None
        try:
            proof,ct=events.C.build(row['weights'],row['profits'],row['slopes'],row['capacity'],'indexed',
                                   (0,row['end']),time.perf_counter()+30,events.common.counters(),{'transitions':256,'index':256})
            complete=True
        except events.C.BuildCap as exc:
            proof=exc.partial; ct=proof['counters'];complete=False
        probe_cpu=time.process_time()-start
        if complete:
            packings=[max(proof['lines'],key=lambda line:(line[0]+t*line[1],line[1],-line[2]))[2] for t in range(row['end']+1)]
            result=dict(method='bounded_probe',packings=packings,certificate=proof,complete=True,
                        algorithm_cpu=time.process_time()-start,probe_cpu=probe_cpu,construction_counts=ct)
        else:
            fallback=events.run(row,'queue')
            result=dict(method='bounded_probe',packings=fallback['packings'],certificate=proof,complete=False,
                        algorithm_cpu=time.process_time()-start,probe_cpu=probe_cpu,construction_counts=ct,fallback=fallback)
        return result
    raise ValueError(stage)


def audit(row,stage,r):
    start=time.process_time()
    if stage==51:
        if r.get('method') in ('parametric_dp','point_dp'):out=A.parametric(row,r)
        else:
            a=A.audit_path(row,r);out=dict(passed=True,integer_checks=a['integer_time_checks'],rational_checks=0,details=a)
    elif stage==52:out=A.reoptimization(row,r)
    elif stage==53:out=A.event_path(row,r)
    else:
        assert r['construction_counts']['dp_transitions']<=256
        assert r['construction_counts']['index_visits']+r['construction_counts']['index_updates']<=256
        A.check_cert(row,r['certificate']);out=dict(passed=True,integer_checks=A.packings(row,r),rational_checks=0)
        if not r['complete']:out['fallback']=A.event_path(row,r['fallback'])
    out['audit_cpu']=time.process_time()-start
    return out


def worker(row,stage,method,phase,repeat=0):
    path=ROOT/'evidence'/f'{stage}-{row["case_id"]}-{method}-{phase}-{repeat}.json.gz'
    if path.exists():return read(path)['summary']
    r=execute(row,stage,method);a=audit(row,stage,r)
    logical={k:v for k,v in r.items() if k not in ('algorithm_cpu','probe_cpu')}
    def clean(obj):
        if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items() if not k.endswith('cpu') and k not in ('wall','component_cpu','ledger','cpu_reconciliation_error')}
        if isinstance(obj,list):return [clean(v) for v in obj]
        return obj
    summary=dict(stage=stage,case_id=row['case_id'],split=row['split'],regime=row['regime'],n=row['n'],method=method,
                 phase=phase,repeat=repeat,algorithm_cpu=r['algorithm_cpu'],audit=a,signature=digest(clean(logical)))
    for k in ('oracle_calls','transitions','peak_dp_cells','line_records','nodes','sort_terms','peak_terminal_cells','counts','complete','probe_cpu','construction_counts'):
        if k in r:summary[k]=r[k]
    if 'pieces' in r:summary['pieces']=len(r['pieces'])
    if 'constructions' in r:summary['construction_statuses']=[x['status'] for x in r['constructions']]
    save(path,dict(input=row,result=r,audit=a,summary=summary))
    print('PATH',stage,row['case_id'],method,phase,repeat,f'cpu={r["algorithm_cpu"]:.6f}',flush=True)
    return summary


def proof_experiment(rows):
    records=[]; intervals=[]; folder=ROOT/'evidence/vipr';folder.mkdir(exist_ok=True)
    def endpoint(row,t,m=None,label='point'):
        t=Fraction(t); q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
        before=time.process_time(); native=SG.solve(row['weights'],q,row['capacity'],deadline=time.perf_counter()+30)
        source_cpu=time.process_time()-before
        packing=native['packing'] if m is None else m
        assert value(q,packing)==native['objective']==A.optimum(row['weights'],q,row['capacity'])
        before=time.process_time(); text,meta=vipr_adapter.certificate(row,t,packing,native['proof']); adapter_cpu=time.process_time()-before
        name=f'{len(records):03}-{label}';path=folder/(name+'.vipr');path.write_text(text)
        child_before=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.perf_counter()
        run=subprocess.run([str(VIPR),str(path)],capture_output=True,text=True,timeout=30)
        child_after=resource.getrusage(resource.RUSAGE_CHILDREN)
        checker_cpu=(child_after.ru_utime+child_after.ru_stime)-(child_before.ru_utime+child_before.ru_stime)
        checker_wall=time.perf_counter()-wall
        assert run.returncode==0 and 'Successfully verified optimal value range' in run.stdout,(name,run.stdout,run.stderr)
        # Mutate only the final claimed bound; every original constraint stays unchanged.
        lines=text.splitlines(); fields=lines[-1].split();fields[2]=str(meta['scaled_objective']-1);lines[-1]=' '.join(fields)
        corrupted=folder/(name+'-invalid.vipr');corrupted.write_text('\n'.join(lines)+'\n')
        bad=subprocess.run([str(VIPR),str(corrupted)],capture_output=True,text=True,timeout=30)
        assert bad.returncode!=0
        rec=dict(case_id=row['case_id'],time=[t.numerator,t.denominator],packing=packing,kind=label,
                 bytes=len(text.encode()),source_cpu=source_cpu,adapter_cpu=adapter_cpu,checker_cpu=checker_cpu,
                 checker_wall=checker_wall,meta=meta,valid_returncode=run.returncode,invalid_returncode=bad.returncode,
                 stdout=run.stdout,invalid_stdout=bad.stdout,source=native,file=str(path.relative_to(ROOT)))
        records.append(rec);return len(records)-1
    row=next(x for x in rows if x['case_id']=='51-n12-bounded-0')
    for t in (0,8,16,32,64):endpoint(row,t)
    for name in ('51-n8-bounded-0','fixture-chain'):
        row=next(x for x in rows if x['case_id']==name);curve=parametric.curve(row)
        for piece in (curve['pieces'][:3] if name.startswith('51-') else curve['pieces']):
            p,s,m=piece['line']; l=Fraction(*piece['left']);h=Fraction(*piece['right'])
            pair=[endpoint(row,l,m,'interval-left'),endpoint(row,h,m,'interval-right')]
            assert records[pair[0]]['packing']==records[pair[1]]['packing']==m
            checks=0
            for t in range((l.numerator+l.denominator-1)//l.denominator,h.numerator//h.denominator+1):
                q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
                assert value(q,m)==A.optimum(row['weights'],q,row['capacity']);checks+=1
            intervals.append(dict(case_id=name,left=piece['left'],right=piece['right'],packing=m,
                                  endpoints=pair,integer_checks=checks,
                                  rationale='For each fixed feasible x, q(t)*(m-x) is affine and nonnegative at both endpoints.'))
    save(ROOT/'evidence/VIPR-results.json.gz',dict(records=records,intervals=intervals))
    return dict(certificates=len(records),invalid_rejected=len(records),intervals=len(intervals),
                integer_checks=sum(x['integer_checks'] for x in intervals),bytes=sum(x['bytes'] for x in records),
                derivations=sum(x['meta']['derivations'] for x in records),
                source_cpu=sum(x['source_cpu'] for x in records),adapter_cpu=sum(x['adapter_cpu'] for x in records),
                checker_cpu=sum(x['checker_cpu'] for x in records),checker_wall=sum(x['checker_wall'] for x in records),
                scope='VIPR original-problem point certificates plus a small, non-formally-verified affine interval connector')


def run():
    check_freeze();start=time.perf_counter();rows=read(ROOT/'Inputs.json');summaries=[]
    stage_methods={51:['parametric_dp','point_dp','maintain','indexed_full'],52:['cold','incumbent','tree'],53:['scan','queue']}
    for stage,methods in stage_methods.items():
        subset=rows if stage!=52 else [x for x in rows if x['split']!='retrospective']
        for row in subset:
            for method in methods:summaries.append(worker(row,stage,method,'headline'))
        timing=[x for x in rows if x['split']=='fresh_held' and x['case_id'].endswith('-1') and x['regime']!='normalized']
        for repeat in range(3):
            for row in timing:
                for j in range(len(methods)):
                    method=methods[(j+repeat)%len(methods)];summaries.append(worker(row,stage,method,'timing',repeat))
    for row in rows:
        if row['case_id'] in ('fixture-chain','fixture-simultaneous'):summaries.append(worker(row,53,'queue_cap','headline'))
    vipr=proof_experiment(rows)
    model=cost_model.run();save(ROOT/'evidence/Cost-model.json.gz',model)
    for row in rows:summaries.append(worker(row,55,'bounded_probe','headline'))
    # A native point-solve control on all fixtures, without mixing its timings into the DP-oracle ratio.
    native_points=[]
    for row in rows:
        if row['split']!='boundary_held':continue
        before=time.process_time();records=[]
        for t in range(row['end']+1):
            q=[p+t*v for p,v in zip(row['profits'],row['slopes'])]
            r=SG.solve(row['weights'],q,row['capacity'],deadline=time.perf_counter()+30);r['time']=t;records.append(r)
        cpu=time.process_time()-before
        for r in records:
            q=[p+r['time']*v for p,v in zip(row['profits'],row['slopes'])]
            assert r['empty'] and r['objective']==A.optimum(row['weights'],q,row['capacity'])
            checker=A.Checker(row);checker.cover(r['proof']);checker.prices(r['proof'],r['time'],r['packing'])
        native_points.append(dict(case_id=row['case_id'],algorithm_cpu=cpu,solves=len(records)))
        save(ROOT/'evidence'/f'native-point-{row["case_id"]}.json.gz',dict(input=row,records=records,algorithm_cpu=cpu))
    grouped={}
    for s in summaries:
        key=(s['stage'],s['case_id'],s['method']);grouped.setdefault(key,[]).append(s['signature'])
    assert all(len(set(sig))==1 for sig in grouped.values()),'logical repeat mismatch'
    metrics=[]
    for stage,methods in stage_methods.items():
        for method in methods:
            totals=[sum(s['algorithm_cpu'] for s in summaries if s['stage']==stage and s['method']==method and s['phase']=='timing' and s['repeat']==r) for r in range(3)]
            metrics.append(dict(stage=stage,method=method,repeated_sums=totals,median=statistics.median(totals)))
    save(ROOT/'Path-results.json',summaries)
    out=dict(workers=len(summaries),inputs=len(rows),integer_checks=sum(s['audit']['integer_checks'] for s in summaries)+vipr['integer_checks']+sum(x['solves'] for x in native_points),
             rational_checks=sum(s['audit']['rational_checks'] for s in summaries),all_audits_passed=True,logical_repeats_match=True,
             timing=metrics,vipr=vipr,native_point_controls=native_points,
             cost_model=dict(grid_cases=len(model['grid']),counterexamples=len(model['counterexamples']),theorem=model['theorem'],scope=model['scope']),
             elapsed_wall=time.perf_counter()-start)
    assert out['elapsed_wall']<900
    save(ROOT/'Summary.json',out);check_freeze();print('COMPLETED',json.dumps(out),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','run'])
    args=parser.parse_args();freeze() if args.action=='freeze' else run()
