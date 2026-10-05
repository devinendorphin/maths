"""Five bounded experiments. Development choices are sealed before held cases."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import os
import random
import statistics
import time
from pathlib import Path
from common import ROOT, BASELINE, counters, limits, save, read
import certificates as C
import policy
from verify import audit_path, check_cert, digest

def inputs():
    rows=[]
    for stage in (41,42,43,45):
        regimes=('bounded','wide','powers','blocks') if stage!=45 else ('bounded','wide','powers','normalized')
        for split,seeds in (('development',(0,)),('held',(1,2))):
            for n in (12,16):
                for regime in regimes:
                    for seed in seeds:
                        rng=random.Random(641000+1000*(stage-41)+100*n+10*regimes.index(regime)+seed)
                        w=[rng.randint(2,20) for _ in range(n)]
                        p=[rng.randint(-10,40) for _ in range(n)]
                        if regime=='bounded': v=[rng.randint(-3,3) for _ in range(n)]
                        elif regime=='wide': v=[rng.randint(-32,32) for _ in range(n)]
                        elif regime=='powers': v=[rng.choice((-1,1))*2**i for i in range(n)]
                        elif regime=='blocks': v=[rng.choice((-1,1))*2**(i//4) for i in range(n)]
                        else: v=p.copy()
                        rows.append(dict(stage=stage,case_id=f'{stage}-{split}-{n}-{regime}-{seed}',
                            split=split,n=n,regime=regime,replicate=seed,weights=w,profits=p,slopes=v,
                            capacity=sum(w)//2,end=64 if stage<=42 else 256))
    for join in (32,64,128):
        for offset in (-1,0,1):
            loss=join+offset
            rows.append(dict(stage=44,case_id=f'44-join{join}-offset{offset}',split='held',n=2,
                regime='boundary',replicate=0,weights=[1,1],profits=[10,11-loss],slopes=[0,1],
                capacity=1,end=3*join+16,window=join,expected_first_strict_loss=loss))
    return rows

def freeze():
    rows=inputs()
    protocol=dict(version=1,stages={
        '41':'Broader slope ranges: gate bounds and unpruned/same/indexed construction.',
        '42':'Choose an input-only indexed construction gate on development CPU, then test held cases.',
        '43':'Compare fixed 32-step and doubling rebuild windows against full-window and scalar proofs.',
        '44':'Strict loss just before, at, and after a window join; deliberately cap the second build.',
        '45':'Transfer the development gate to doubling windows on fresh inputs and normalized controls.'},
        cases=105,development_cases=32,held_cases=73,
        construction_workers=72,headline_paths=306,tuning_paths=96,timing_paths=288,
        training_candidates=[dict(method='maintain',threshold=0)]+[dict(method='indexed',threshold=t) for t in (2000,5000,15000)],
        training_repeats=3,held_timing_repeats=3,limits=limits(41),
        timing='Sequential cold native solves; process CPU excludes persistence and independent audits. Input decode is outside CPU. No parallel workers.',
        selection='Lowest median of per-repeat total algorithm CPU over eight stage-42 development cases; ties by candidate order. Seal before any held path.',
        proof_retention='Content-addressed compressed objects. No growing action snapshots. Completed audited workers can resume; an interrupted worker restarts cold.',
        boundaries='Rebuild windows overlap at the join. A strict loss endpoint uses the replacement native packing. An incomplete build is never active.',
        oracle='Independent capacity DP at every integer time; independent recurrence, deletions, index, scalar covers/prices/repairs and horizons.',
        interpretation='Finite deterministic samples, not universal bounds on runtime. Three sequential repeats are machine-local timing evidence.',
        gate_transition_cap=60000,forced_second_build_auxiliary_cap=3)
    save(ROOT/'Inputs.json',rows,immutable=True)
    save(ROOT/'Protocol.json',protocol,immutable=True)
    files=list((ROOT/'code').glob('*.py'))+[ROOT/'Inputs.json',ROOT/'Protocol.json']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    kernels={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASELINE.glob('*.py')}
    save(ROOT/'Freeze.json',dict(files=hashes,kernels=kernels),immutable=True)
    print('FROZEN',digest(hashes),len(rows),flush=True)

def check_freeze():
    seal=read(ROOT/'Freeze.json')
    for name,h in seal['files'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,h in seal['kernels'].items(): assert hashlib.sha256((BASELINE/name).read_bytes()).hexdigest()==h,name

def objectify(data):
    if isinstance(data,list): node=[objectify(x) for x in data]
    elif isinstance(data,dict): node={k:objectify(v) for k,v in data.items()}
    else: return data
    b=json.dumps(node,sort_keys=True,separators=(',',':')).encode()
    if len(b)<2048: return node
    h=hashlib.sha256(b).hexdigest(); p=ROOT/'evidence/objects'/f'{h}.json.gz'
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_suffix('.tmp'); tmp.write_bytes(gzip.compress(b,compresslevel=6,mtime=0)); tmp.replace(p)
    return {'$object':h}

def hydrate(data):
    if isinstance(data,list): return [hydrate(x) for x in data]
    if not isinstance(data,dict): return data
    if set(data)=={'$object'}:
        h=data['$object']; b=gzip.decompress((ROOT/'evidence/objects'/f'{h}.json.gz').read_bytes())
        assert hashlib.sha256(b).hexdigest()==h
        return hydrate(json.loads(b))
    return {k:hydrate(v) for k,v in data.items()}

def compact(row,result,phase,repeat):
    return dict(case_id=row['case_id'],stage=row['stage'],split=row['split'],regime=row['regime'],n=row['n'],
        replicate=row['replicate'],phase=phase,repeat=repeat,policy=result['policy'],status=result['status'],
        algorithm_cpu=result['algorithm_cpu'],component_cpu=result['component_cpu'],totals=result['totals'],
        normalized=result['normalized'],gate=result['gate'],switch_times=result['switch_times'],
        signature=result['logical_signature'],
        builds=[{k:r[k] for k in ('method','interval','status','reason','raw_rows','lines','cpu')} for r in result['constructions']],
        fallback_reprices=sum(e['kind']=='fallback_reprice' for e in result['events']),audit_passed=True)

def worker(row,method,phase,repeat=0,selection=None,forced=None):
    name=f"{row['case_id']}--{phase}--{repeat}--{method}"
    path=ROOT/'evidence/workers'/f'{name}.json.gz'
    if path.exists(): return hydrate(read(path))['summary']
    start=time.perf_counter(); r=policy.run(row,method,selection=selection,forced_caps=forced)
    audit=audit_path(row,r)
    assert r['status']=='window_complete', (name,r['status'],r['pending'])
    if row['stage']==44:
        assert r['switch_times']==[row['expected_first_strict_loss']]
        if forced:
            assert len(r['constructions'])>=2
            assert r['constructions'][1]['status']!='complete'
            assert not r['constructions'][1]['active_certificate']
            assert any(e['kind']=='fallback_reprice' for e in r['events']) or row['expected_first_strict_loss']==row['window']
    summary=compact(row,r,phase,repeat)
    save(path,objectify(dict(input=row,result=r,audit=audit,summary=summary)),immutable=True)
    print('PATH',name,f"cpu={r['algorithm_cpu']:.5f}",f"wall={time.perf_counter()-start:.3f}",flush=True)
    return summary

def build_worker(row,method):
    path=ROOT/'evidence/workers'/f"{row['case_id']}--construction--{method}.json.gz"
    if path.exists(): return hydrate(read(path))['summary']
    ct=counters(); start=time.process_time()
    try:
        cert,cc=C.build(row['weights'],row['profits'],row['slopes'],row['capacity'],method,(0,row['end']),time.perf_counter()+120,ct,limits(41))
        status='complete'; reason=None
    except C.BuildCap as e: cert=e.partial; cc=cert['counters']; status='incomplete'; reason=str(e)
    cpu=time.process_time()-start
    audited=check_cert(row,cert)
    gate=C.gate(row['weights'],row['profits'],row['slopes'],row['capacity'],counters())
    assert cc['dp_entries']<=gate['E_bound'] and cc['dp_transitions']<=gate['T_bound']
    summary=dict(stage=41,case_id=row['case_id'],split=row['split'],regime=row['regime'],n=row['n'],
        method=method,status=status,reason=reason,algorithm_cpu=cpu,counters=cc,gate=gate,audit_passed=True,
        decisions={str(t):gate['E_bound']<=t and gate['T_bound']<=60000 for t in (2000,5000,15000)})
    save(path,objectify(dict(input=row,certificate=cert,audit=dict(passed=True,certificate_hash=audited),summary=summary)),immutable=True)
    print('BUILD',row['case_id'],method,status,f'{cpu:.5f}',flush=True)
    return summary

def run():
    check_freeze(); rows=read(ROOT/'Inputs.json'); records=[]
    # Training is complete before any held-case computation (including stage 41).
    dev=[r for r in rows if r['stage']==42 and r['split']=='development']
    candidates=read(ROOT/'Protocol.json')['training_candidates']; tuning=[]
    for rep in range(3):
        for row in dev:
            for j in range(len(candidates)):
                ix=(j+rep)%len(candidates); choice=candidates[ix]
                method='maintain' if choice['method']=='maintain' else 'selected'
                tuning.append(worker(row,method,f'tuning{ix}',rep,choice))
    scores=[]
    for ix,c in enumerate(candidates):
        totals=[sum(x['algorithm_cpu'] for x in tuning if x['phase']==f'tuning{ix}' and x['repeat']==rep) for rep in range(3)]
        scores.append(dict(candidate=c,repeat_totals=totals,median=statistics.median(totals)))
    selection_path=ROOT/'Selection.json'
    winner=min(range(len(scores)),key=lambda i:(scores[i]['median'],i))
    seal=dict(chosen=scores[winner]['candidate'],scores=scores,training_records_hash=digest(tuning),freeze_hash=digest(read(ROOT/('Freeze-original.json' if (ROOT/'Freeze-original.json').exists() else 'Freeze.json'))))
    if selection_path.exists(): assert read(selection_path)==seal
    else: save(selection_path,seal,immutable=True)
    print('SEALED SELECTION',seal['chosen'],flush=True)
    records.extend(tuning); builds=[]
    for row in rows:
        if row['stage']==41:
            for method in ('unpruned','same','indexed'): builds.append(build_worker(row,method))
            continue
        methods={42:('maintain','same','indexed_full','selected'),43:('maintain','indexed_full','rolling32','adaptive'),
                 44:('rolling32','forced'),45:('maintain','indexed_full','adaptive','gate_adaptive')}[row['stage']]
        for method in methods:
            records.append(worker(row,'rolling32' if method=='forced' else method,'forced' if method=='forced' else 'headline',
                selection=seal['chosen'],forced={'auxiliary':3} if method=='forced' else None))
    for rep in range(3):
        for row in rows:
            if row['stage'] not in (42,43,45) or row['split']!='held' or row['replicate']!=1: continue
            methods={42:('maintain','same','indexed_full','selected'),43:('maintain','indexed_full','rolling32','adaptive'),
                45:('maintain','indexed_full','adaptive','gate_adaptive')}[row['stage']]
            for j in range(4):
                method=methods[(j+rep)%4]
                records.append(worker(row,method,'timing',rep,seal['chosen']))
    assert len(builds)==72 and len(records)==690
    groups=defaultdict(set)
    for x in records: groups[(x['case_id'],x['policy'],x['phase'] if x['phase'].startswith('tuning') else ('forced' if x['phase']=='forced' else 'normal'))].add(x['signature'])
    assert all(len(s)==1 for s in groups.values()), 'logical repeat mismatch'
    def finish(name,data):
        path=ROOT/name
        if path.exists(): assert read(path)==data, name
        else: save(path,data,immutable=True)
    finish('Construction-results.json',builds)
    finish('Path-results.json',records)
    finish('Audit-summary.json',dict(passed=True,construction_workers=len(builds),path_workers=len(records),
        unique_inputs=len(rows),all_policy_paths_complete=True,all_logical_repeats_match=True,
        all_proofs_checked=True,completed_worker_files=len(list((ROOT/'evidence/workers').glob('*.json.gz')))))
    print('COMPLETE',len(builds),len(records),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('freeze','run'))
    args=parser.parse_args(); freeze() if args.action=='freeze' else run()
