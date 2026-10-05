"""Experiments 46–50, sealed development choices and bounded evidence."""
import argparse
import hashlib
import random
import statistics
import time
from collections import defaultdict
from pathlib import Path
from common import ROOT, BASELINE, read, save, limits
from storage import objectify, hydrate
from verify import audit_path, digest
import policy

GATES=[dict(method='maintain',threshold=0),dict(method='indexed',threshold=15000),
       dict(method='indexed',threshold=30000),dict(method='indexed',threshold=30000,pressure_max=40),
       dict(method='indexed',threshold=30000,pressure_min=40)]
BUDGETS=[dict(budget=x) for x in (0,1000,4000,16000)]
METHODS={46:('maintain','indexed_full','legacy_gate'),47:('maintain','indexed_full','legacy_gate','feature_gate'),
         48:('maintain','adaptive','budget_fixed','budget_selected'),
         50:('maintain','indexed_full','feature_gate','composed')}

def inputs():
    rows=[]
    for n in (12,16):
        for seed in range(4):
            rng=random.Random(746000+100*n+seed)
            w=[rng.randint(2,20) for _ in range(n)]; p=[rng.randint(-10,40) for _ in range(n)]
            slopes=[rng.choice((-1,1))*2**(i//4) for i in range(n)]
            for scale in (1,8):
                for end in (64,256):
                    rows.append(dict(stage=46,case_id=f'46-n{n}-seed{seed}-scale{scale}-H{end}',split='held',
                        n=n,regime='blocks',replicate=seed,weights=w,profits=p,slopes=[scale*x for x in slopes],
                        capacity=sum(w)//2,end=end,scale=scale,pair_group=f'46-n{n}-seed{seed}'))
    for stage in (47,48,50):
        ns=(16,20) if stage==50 else (12,16)
        regimes=('bounded','wide','powers','normalized') if stage==50 else ('bounded','wide','powers','blocks')
        for n in ns:
            for k,regime in enumerate(regimes):
                for seed in range(3):
                    rng=random.Random(746000+10000*(stage-46)+100*n+10*k+seed)
                    w=[rng.randint(2,20) for _ in range(n)];p=[rng.randint(-10,40) for _ in range(n)]
                    if regime=='bounded':v=[rng.randint(-3,3) for _ in range(n)]
                    elif regime=='wide':v=[rng.randint(-32,32) for _ in range(n)]
                    elif regime=='powers':v=[rng.choice((-1,1))*2**i for i in range(n)]
                    elif regime=='blocks':v=[rng.choice((-1,1))*2**(i//4) for i in range(n)]
                    else:v=p.copy()
                    end=(64 if k%2==0 else 256) if stage==47 else (512 if stage==50 else 256)
                    rows.append(dict(stage=stage,case_id=f'{stage}-n{n}-{regime}-seed{seed}',
                        split='held' if stage==50 or seed else 'development',n=n,regime=regime,replicate=seed,
                        weights=w,profits=p,slopes=v,capacity=sum(w)//2,end=end))
    for join in (32,64):
        for offset in (-1,0,1):
            losses=[join*j+offset for j in (1,2,3)];p=[120]
            for loss in losses:p.append(p[-1]-(loss-1))
            rows.append(dict(stage=49,case_id=f'49-join{join}-offset{offset}',split='held',n=4,regime='boundary_chain',
                replicate=0,weights=[1]*4,profits=p,slopes=[0,1,2,3],capacity=1,end=4*join+8,
                window=join,expected_switches=losses))
    return rows

def protocol():
    return dict(version=1,unique_inputs=110,matched_stage46_groups=8,development_inputs=16,held_inputs=94,
        headline_paths=444,tuning_paths=216,timing_paths=360,total_workers=1020,
        stages={46:'Matched block-slope inputs: multiply slopes by 1 or 8 and observe through 64 or 256.',
            47:'Input-only gates use horizon times slope L1 divided by profit L1; select on eight development inputs.',
            48:'Stop renewing a doubling-window certificate at a recorded construction-work threshold; select on eight development inputs.',
            49:'Three successive strict losses; force the second/third/fourth build to hit entries, index or auxiliary caps.',
            50:'Transfer sealed gates and renewal thresholds to fresh 16/20-item inputs, H=512 and normalized controls.'},
        gate_candidates=GATES,renewal_candidates=BUDGETS,limits=limits(46),repeats=3,
        selection='Minimum median of per-repeat summed algorithm CPU over eight development inputs, tie by declared candidate order. All development training precedes every held worker.',
        selection_order='Gate training in 47, renewal training in 48, seal both, then headline cases and held repeats.',
        pace_proxy='Exact comparison H*sum(abs(slopes)) with 40*max(1,sum(abs(profits))); no floating point or future oracle.',
        never_build_gate='The never-build gate candidate still pays feature/gate arithmetic; the separate maintenance reference pays no gate arithmetic.',
        renewal_work='Sum of past construction dp_transitions, index_visits and index_updates. Check at a join before building again. Zero means never build.',
        renewal_limit='A stop-renewing threshold, not a hard total-work cap: the initial or last allowed build may exceed it. Mandatory safety caps still apply.',
        forced_variants=[dict(cap=cap,build_index=i) for cap in ('entries','index','auxiliary') for i in (1,2,3)],
        forced_caps=dict(entries=1,index=1,auxiliary=3),
        timing='Sequential cold native solves. CPU includes all algorithm decisions, solve cleanup/disposal and bookkeeping; excludes decoding, persistence and independent audits.',
        timing_subset='Stage 46 seed 0: eight matched inputs; stages 47,48,50 seed 1: eight inputs each. Three repeats with rotated method order.',
        audit='Independent recurrence/index/deletion checks, complete or partial construction cursors, scalar cover/prices/repairs, horizons, gates and renewal decisions; separate capacity DP at every integer time.',
        interpretation='Finite samples. Stage 46 has eight independent seed/item groups, not 32 independent draws. Timing is machine-local. Normalized controls are reported separately.',
        storage='Content-addressed compressed objects and completed worker records only; interrupted workers restart cold, never falsely resume inside an action.')

def freeze():
    save(ROOT/'Inputs.json',inputs(),immutable=True);save(ROOT/'Protocol.json',protocol(),immutable=True)
    files=list((ROOT/'code').glob('*.py'))+[ROOT/'Inputs.json',ROOT/'Protocol.json',ROOT/'Roadmap.md']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    kernels={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASELINE.glob('*.py')}
    save(ROOT/'Freeze.json',dict(files=hashes,kernels=kernels,previous_commit='e3368164abe24d981bf8f173dbda4a1c2dad78f6'),immutable=True)
    print('FROZEN',len(inputs()),digest(hashes),flush=True)

def check_freeze():
    seal=read(ROOT/'Freeze.json')
    for name,h in seal['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,h in seal['kernels'].items():assert hashlib.sha256((BASELINE/name).read_bytes()).hexdigest()==h,name

def summarize(row,r,method,phase,repeat,audit):
    return dict(case_id=row['case_id'],stage=row['stage'],split=row['split'],regime=row['regime'],n=row['n'],
        replicate=row['replicate'],end=row['end'],scale=row.get('scale'),pair_group=row.get('pair_group'),
        phase=phase,repeat=repeat,policy=method,status=r['status'],algorithm_cpu=r['algorithm_cpu'],
        component_cpu=r['component_cpu'],totals={k:v for k,v in r['totals'].items() if v},normalized=r['normalized'],
        gate=r['gate'],switch_times=r['switch_times'],signature=r['logical_signature'],
        builds=[{k:b[k] for k in ('anchor','method','interval','status','reason','raw_rows','lines','cpu')} for b in r['constructions']],
        fallback_reprices=sum(e['kind']=='fallback_reprice' for e in r['events']),
        renewal_decisions=[e for e in r['events'] if e['kind']=='renewal_decision'],
        audit_passed=audit['passed'],integer_time_checks=audit['integer_time_checks'])

def worker(row,method,phase,repeat=0,selection=None):
    name=f"{row['case_id']}--{phase}--{repeat}--{method}";out=ROOT/'evidence/workers'/f'{name}.json.gz'
    if out.exists():return hydrate(read(out))['summary']
    effective=dict(row);forced=None;actual=method
    if method.startswith('forced_'):
        _,cap,ix=method.split('_');effective['forced_build_index']=int(ix)
        forced={cap:protocol()['forced_caps'][cap]};actual='rolling32'
    start=time.perf_counter();result=policy.run(effective,actual,selection=selection,forced_caps=forced)
    audit=audit_path(effective,result)
    assert result['status']=='window_complete',(name,result['status'],result['pending'])
    if row['stage']==49:
        assert result['switch_times']==row['expected_switches']
        if forced:
            i=effective['forced_build_index'];assert len(result['constructions'])>i
            assert result['constructions'][i]['status']!='complete'
            assert not result['constructions'][i]['active_certificate']
            assert sum(b['status']!='complete' for b in result['constructions'])==1
    summary=summarize(row,result,method,phase,repeat,audit)
    save(out,objectify(dict(input=effective,result=result,audit=audit,summary=summary)),immutable=True)
    print('PATH',name,f"cpu={result['algorithm_cpu']:.6f}",f"wall={time.perf_counter()-start:.3f}",flush=True)
    return summary

def finish(name,data):
    p=ROOT/name
    if p.exists():assert read(p)==data,name
    else:save(p,data,immutable=True)

def train(rows,stage,candidates,method):
    records=[]
    for rep in range(3):
        for row in rows:
            if row['stage']!=stage or row['split']!='development':continue
            for j in range(len(candidates)):
                ix=(j+rep)%len(candidates)
                records.append(worker(row,method,f'tuning{stage}_{ix}',rep,candidates[ix]))
    scores=[]
    for ix,c in enumerate(candidates):
        totals=[sum(x['algorithm_cpu'] for x in records if x['phase']==f'tuning{stage}_{ix}' and x['repeat']==rep) for rep in range(3)]
        scores.append(dict(candidate=c,repeat_totals=totals,median=statistics.median(totals)))
    winner=min(range(len(scores)),key=lambda i:(scores[i]['median'],i))
    seal=dict(stage=stage,chosen=scores[winner]['candidate'],scores=scores,training_records_hash=digest(records),freeze_hash=digest(read(ROOT/'Freeze.json')))
    finish(f'Selection-{stage}.json',seal)
    print('SEALED',stage,seal['chosen'],flush=True)
    return seal,records

def run():
    check_freeze();rows=read(ROOT/'Inputs.json')
    gate,records=train(rows,47,GATES,'feature_gate')
    budget,tuning=train(rows,48,BUDGETS,'budget_selected');records+=tuning
    selection=dict(gate=gate['chosen'],budget=budget['chosen']['budget'])
    for row in rows:
        methods=METHODS[row['stage']] if row['stage']!=49 else ('rolling32',)+tuple(f'forced_{cap}_{ix}' for cap in ('entries','index','auxiliary') for ix in (1,2,3))
        for method in methods:records.append(worker(row,method,'headline',selection=selection))
    for rep in range(3):
        for row in rows:
            if row['stage']==49:continue
            if row['replicate']!=(0 if row['stage']==46 else 1):continue
            for j in range(len(METHODS[row['stage']])):
                method=METHODS[row['stage']][(j+rep)%len(METHODS[row['stage']])]
                records.append(worker(row,method,'timing',rep,selection))
    assert len(records)==1020
    groups=defaultdict(set)
    for x in records:
        groups[(x['case_id'],x['policy'],x['phase'] if x['phase'].startswith('tuning') else 'normal')].add(x['signature'])
    assert all(len(s)==1 for s in groups.values()),'Logical repeat mismatch'
    finish('Path-results.json',records)
    finish('Audit-summary.json',dict(passed=True,unique_inputs=len(rows),policy_workers=len(records),headline_paths=444,
        tuning_paths=216,timing_paths=360,all_policy_paths_complete=True,all_logical_repeats_match=True,
        all_proofs_checked=True,integer_time_checks=sum(x['integer_time_checks'] for x in records),
        incomplete_constructions=sum(b['status']!='complete' for x in records for b in x['builds']),
        completed_worker_files=len(list((ROOT/'evidence/workers').glob('*.json.gz')))))
    print('COMPLETE',len(records),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=('freeze','run'));args=ap.parse_args()
    freeze() if args.action=='freeze' else run()
