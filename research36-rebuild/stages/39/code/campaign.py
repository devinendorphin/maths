"""Checkpointed orchestration for the complete declared 36–40 matrices."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import shutil
import statistics
import subprocess
import sys
import tarfile
import time
import zipfile
from common import ROOT, REPO, BASELINE, SG, limits, read, save, sha, value

POLICIES={36:['maintain','unpruned','same'],37:['maintain','unpruned','same','naive','indexed'],
          38:['maintain','unpruned','same','indexed'],39:['maintain','unpruned','conservative','selected'],
          40:['maintain','unpruned','selected','rolling']}
CAPS={stage:limits(stage) for stage in POLICIES}


def source_record(w,p,c,path):
    if path.exists(): return read(path)
    try: record=SG.solve(w,p,c)
    except SG.SourceCap as exc:
        record=dict(status='initialization_incomplete',reason=str(exc),cost=exc.cost)
    save(path,record,immutable=True); return record


def core(stage,split,directory):
    seed=151000+(stage-36)*1000; seeds=[seed] if split=='development' else [seed+500,seed+501,seed+502]
    rows=[]
    for n in (12,16):
        for seed in seeds:
            rng=random.Random(seed); w=[rng.randint(2,20) for _ in range(n)]; c=sum(w)//3
            families=dict(random=[rng.randint(5,50) for _ in w],proportional=[wi+15+rng.randint(-2,2) for wi in w],
                          mixed=[rng.randint(-15,40) for _ in w],negative=[-rng.randint(1,10) for _ in w])
            for family,p in families.items():
                source=source_record(w,p,c,directory/'generation-sources'/f'{n}-{seed}-{family}.json')
                if source.get('status')=='initialization_incomplete':
                    save(directory/'initialization-failures'/f'{n}-{seed}-{family}.json',dict(n=n,seed=seed,family=family,weights=w,profits=p,capacity=c,source=source,rng_state=rng.getstate()))
                    # No packing-dependent directions are invented. All four paths stay blocked.
                    from experiment import directions
                    directions(p,0,rng)
                    continue
                state_before=rng.getstate()
                # Frozen generator advancement includes zero/reinforce before filtering.
                from experiment import directions
                vectors=directions(p,source['packing'],rng)
                for regime in ('sparse','signed','scale','harm'):
                    rows.append(dict(stage=stage,split=split,case_id=f'{n}-{seed}-{family}-{regime}',matrix='core',
                                     n=n,seed=seed,family=family,regime=regime,weights=w,profits=p,slopes=vectors[regime],capacity=c,
                                     end=1024 if stage==40 else 256,generation_source=source,
                                     rng_state_before=state_before,rng_state_after=rng.getstate()))
    return rows


def stress(split,directory):
    seeds=[253000] if split=='development' else [253500,253501,253502]; rows=[]
    for n in (12,16,20):
        for seed in seeds:
            rng=random.Random(seed); w=[rng.randint(2,20) for _ in range(n)]
            families=dict(random=[rng.randint(5,50) for _ in w],proportional=[wi+15+rng.randint(-2,2) for wi in w],
                          mixed=[rng.randint(-15,40) for _ in w],negative=[-rng.randint(1,10) for _ in w])
            for family in ('random','negative'):
                p=families[family]; state_before=rng.getstate()
                bounded=[rng.randint(-3,3) for _ in w]; wide=[rng.randint(-256,256) for _ in w]
                powers=[rng.choice((-1,1))*(1<<i) for i in range(n)]
                signs=[rng.choice((-1,1)) for _ in range((n+2)//3)]
                blocks=[signs[i//3]*(1<<(i//3)) for i in range(n)]
                vectors=dict(bounded=bounded,wide=wide,powers=powers,blocks=blocks)
                for ratio in (3,2):
                    c=sum(w)//ratio
                    source=source_record(w,p,c,directory/'generation-sources'/f'stress-{n}-{seed}-{family}-c{ratio}.json')
                    if source.get('status')=='initialization_incomplete':
                        save(directory/'initialization-failures'/f'stress-{n}-{seed}-{family}-c{ratio}.json',dict(weights=w,profits=p,capacity=c,source=source,slopes=vectors,rng_state=rng.getstate()))
                        continue
                    for regime,v in vectors.items():
                        rows.append(dict(stage=38,split=split,case_id=f'stress-{n}-{seed}-{family}-c{ratio}-{regime}',matrix='stress',
                                         n=n,seed=seed,family=family,regime=regime,weights=w,profits=p,slopes=v,capacity=c,capacity_ratio=ratio,end=256,
                                         generation_source=source,blocks=[i//3 for i in range(n)],
                                         rng_state_before=state_before,rng_state_after=rng.getstate()))
    return rows


def verify_inputs(stage,split,rows):
    """Separate RNG reconstruction without calling the algorithm generator."""
    expected={}; seeds=sorted({r['seed'] for r in rows if r['matrix']=='core'})
    for n in (12,16):
        for seed in seeds:
            g=random.Random(seed); w=[g.randint(2,20) for i in range(n)]
            families=[('random',[g.randint(5,50) for i in range(n)]),('proportional',[x+15+g.randint(-2,2) for x in w]),
                      ('mixed',[g.randint(-15,40) for i in range(n)]),('negative',[-g.randint(1,10) for i in range(n)])]
            for family,p in families:
                group=[r for r in rows if r['matrix']=='core' and r['n']==n and r['seed']==seed and r['family']==family]
                if not group: continue
                mask=group[0]['generation_source']['packing']; one=[0]*n; one[g.randrange(n)]=g.choice((-1,1))
                signed=[g.randint(-3,3) for i in range(n)]
                vectors=dict(sparse=one,signed=signed,scale=p,harm=[-1 if mask>>i&1 else 1 for i in range(n)])
                for r in group:
                    assert (r['weights'],r['profits'],r['capacity'],r['slopes'])==(w,p,sum(w)//3,vectors[r['regime']])
                    expected[r['case_id']]=True
    if stage==38:
        seeds=sorted({r['seed'] for r in rows if r['matrix']=='stress'})
        for n in (12,16,20):
            for seed in seeds:
                g=random.Random(seed); w=[g.randint(2,20) for i in range(n)]
                profits=[ [g.randint(5,50) for i in range(n)], [x+15+g.randint(-2,2) for x in w],
                          [g.randint(-15,40) for i in range(n)], [-g.randint(1,10) for i in range(n)] ]
                for family,p in [('random',profits[0]),('negative',profits[3])]:
                    bounded=[g.randint(-3,3) for i in range(n)]; wide=[g.randint(-256,256) for i in range(n)]
                    powers=[g.choice((-1,1))*2**i for i in range(n)]
                    signs=[g.choice((-1,1)) for i in range((n+2)//3)]; blocks=[signs[i//3]*2**(i//3) for i in range(n)]
                    vectors=dict(bounded=bounded,wide=wide,powers=powers,blocks=blocks)
                    for r in rows:
                        if r['matrix']=='stress' and r['n']==n and r['seed']==seed and r['family']==family:
                            assert (r['weights'],r['profits'],r['slopes'],r['capacity'])==(w,p,vectors[r['regime']],sum(w)//r['capacity_ratio'])
                            expected[r['case_id']]=True
    assert len(expected)==len(rows)
    return dict(passed=True,cases=len(rows),case_ids=sorted(expected),independent_rng_reconstruction=True)


def inputs(stage,split):
    directory=ROOT/'stages'/str(stage)/split; target=directory/'Inputs.json'
    if target.exists(): return read(target)
    rows=core(stage,split,directory)
    if stage==38: rows+=stress(split,directory)
    save(target,rows,immutable=True)
    for row in rows: save(directory/'inputs'/(row['case_id']+'.json'),row,immutable=True)
    save(directory/'Input-verification.json',verify_inputs(stage,split,rows),immutable=True)
    expected=(80 if split=='development' else 240) if stage==38 else (32 if split=='development' else 96)
    assert len(rows)==expected, 'Initialization failures must be resolved without inventing packings'
    return rows


def freeze(stage):
    out=ROOT/'stages'/str(stage); frozen=out/'Frozen.json'
    if frozen.exists():
        assert all(sha(out/p)==s for p,s in read(frozen).items()); return
    assert read(ROOT/'Verification-fixtures.json')['passed']
    shutil.copytree(ROOT/'code',out/'code',ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
    handoff=(ROOT/'Handoff.md').read_text()
    protocol=f'# Rebuilt experiment {stage}\n\n'+handoff+'\n\n## Rebuild implementation declaration\n\n'+json.dumps(dict(policies=POLICIES[stage],caps=CAPS[stage]),indent=2)+'''

Original unpruned recurrence and first-transition tie behavior are fixture-compared with stage 35. Same-slope order is (S,W,-P,M,raw-ID). Endpoint order is (W,-value(a),-value(b),S,M). Indexed queries use descending endpoint-a ranks and prefix maxima of (endpoint-b value,-canonical position,witness-ID); unreachable values are explicit nulls. Raw rows, predecessor IDs, every deletion, coordinates, query outcomes and terminal tree aggregates are retained. The independent checker reconstructs every generation domain, index range and deletion. Auxiliary memory guards conservatively reserve sorter/order/map/tree/query records before allocation; these guard details may differ from the unavailable prior implementation.

All policy workers are isolated fresh Python processes. Each pays for its own cold native initial and replacement solves, recognition, construction, horizons, scalar repair, driver bookkeeping and certificate handling. Model time is independent of CPU. Native stores are disposed even on failure. Retained output-proof disposal is outside the CPU boundary for every method. Interpreter/import/input decoding, logical fingerprinting, serialization and audits are separate infrastructure costs. Operation ledgers place horizons at their anchors and construction at its actual build time. CPU bookkeeping is tracked within its operation blocks; final accounting overhead is disclosed as a separate component. Timing uses median aggregate full CPU over the exact three declared repetitions and never the fastest trial. Capped repetitions are ineligible. No held-out tuning.

Construction caps preserve partial proof/cursor, abandon it as active evidence and use a complete scalar partition, repricing stale numerators before its horizon. A later rolling build failure permanently hands that policy to scalar maintenance. All failed preparation is charged. Incomplete constructions remain incomplete even when fallback finishes the window. Each complete rolling window rebuild starts from the original items. At a strict loss on a boundary, native replacement precedes the new build. No fifth build at 1024.

Same-slope correctness: at any prefix a lighter state with equal S and no smaller P admits every identical remaining completion and has a constant nonnegative value difference. Induction through the complete include/exclude recurrence therefore preserves global optima for all nonnegative times. Endpoint correctness: a lighter state's affine value difference nonnegative at both a and b is nonnegative throughout [a,b], so the same completion argument preserves the global optimum only there. Discarded states can be necessary later. These elementary arguments and exponential worst-case widths are separate from checked finite proofs and empirical CPU observations. No new arithmetic is claimed.
'''
    (out/'Protocol.md').write_text(protocol)
    shutil.copy2(ROOT/'Verification-fixtures.json',out/'Verification.json')
    save(out/'Base-kernel-hashes.json',{p.name:sha(p) for p in BASELINE.glob('*.py')})
    files=list((out/'code').glob('*.py'))+[out/'Protocol.md',out/'Verification.json',out/'Base-kernel-hashes.json']
    save(frozen,{str(p.relative_to(out)):sha(p) for p in files},immutable=True)


def worker(stage,row,method,folder,selection=None):
    if (folder/'Path-result.json.gz').exists(): return read(folder/'Path-result.json.gz')
    if list(folder.glob('state-*.json.gz')) or list(folder.glob('native-*.json.gz')):
        raise RuntimeError(f'Interrupted policy has saved prefixes requiring exact continuation: {folder}')
    command=[sys.executable,str(ROOT/'stages'/str(stage)/'code/policy.py'),str(ROOT/'stages'/str(stage)/row['split']/'inputs'/(row['case_id']+'.json')),method,str(folder)]
    if selection: command.append(str(selection))
    folder.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    with (folder/'Worker.log').open('a') as log:
        subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=450,env=dict(os.environ,MATHS_RESEARCH_ROOT=str(ROOT)))
    result=read(folder/'Path-result.json.gz')
    save(folder/'Infrastructure.json',dict(child_wall=time.perf_counter()-start,algorithm_wall=result['algorithm_wall'],input_decoding_cpu=result['input_decoding_cpu'],worker_log='Worker.log'),immutable=True)
    return result


def audit_worker(stage,row,folder):
    if (folder/'Audit.json').exists() and read(folder/'Audit.json')['passed']: return
    command=[sys.executable,str(ROOT/'stages'/str(stage)/'code/campaign.py'),'audit-worker','--row',str(ROOT/'stages'/str(stage)/row['split']/'inputs'/(row['case_id']+'.json')),'--folder',str(folder)]
    with (folder/'Audit-worker.log').open('a') as log:
        subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=900,env=dict(os.environ,MATHS_RESEARCH_ROOT=str(ROOT)))


def timing_subset(rows):
    first=min(r['seed'] for r in rows if r['matrix']=='core')
    subset=[r for r in rows if r['matrix']=='core' and r['n']==12 and r['seed']==first and r['family'] in ('random','negative')]
    if rows[0]['stage']==38:
        seed=min(r['seed'] for r in rows if r['matrix']=='stress')
        subset += [r for r in rows if r['matrix']=='stress' and r['n']==12 and r['seed']==seed and r['family'] in ('random','negative') and r['capacity_ratio']==2]
    assert len(subset)==(16 if rows[0]['stage']==38 else 8)
    return subset


def committed(message):
    if not (REPO/'.git').is_dir() or os.environ.get('MATHS_PERSIST_GIT')!='1': return
    subprocess.run(['git','add','research36-rebuild'],cwd=REPO,check=True,stdout=subprocess.DEVNULL)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode==0: return
    subprocess.run(['git','commit','-m',message],cwd=REPO,check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['git','push'],cwd=REPO,check=True,stdout=subprocess.DEVNULL)


class BatchEnd(Exception): pass


def execute(seconds):
    deadline=time.perf_counter()+seconds
    def guard(stage,task):
        save(ROOT/'Resume-controller.json',dict(stage=stage,next_task=task,batch_deadline_remaining=deadline-time.perf_counter()))
        if deadline-time.perf_counter()<450: raise BatchEnd()
    try:
        for stage in range(36,41):
            out=ROOT/'stages'/str(stage)
            if (out/'Complete.json').exists(): continue
            freeze(stage); dev=inputs(stage,'development')
            selection=out/'Selection.json' if stage==39 else ROOT/'stages/39/Selection.json' if stage==40 else None
            if stage==39 and not selection.exists():
                scores={}; tuning=[]
                candidates=[dict(method=m,threshold=t) for m in ('unpruned','same') for t in (50000,125000,250000,500000)]
                for candidate in candidates+[dict(method='maintain',threshold=0)]:
                    name=candidate['method']+'-'+str(candidate['threshold']); sp=out/'tuning'/(name+'.json')
                    if not sp.exists(): save(sp,candidate,immutable=True)
                    aggregates=[]; caps=[]
                    for rep in range(3):
                        total=0
                        for row in timing_subset(dev):
                            folder=out/'tuning'/name/f'rep{rep}'/row['case_id']; guard(stage,dict(kind='tuning',candidate=name,repetition=rep,case=row['case_id']))
                            result=worker(stage,row,'maintain' if candidate['method']=='maintain' else 'gate_'+candidate['method'],folder,sp)
                            audit_worker(stage,row,folder)
                            total+=result['algorithm_cpu']
                            if result['status']!='window_complete' or any(x['status']!='complete' for x in result['constructions']): caps.append(dict(rep=rep,case=row['case_id']))
                        aggregates.append(total); committed(f'Checkpoint experiment 39 tuning {name} repetition {rep}')
                    score=None if caps else statistics.median(aggregates)
                    scores[name]=score; tuning.append(dict(candidate=candidate,repetitions=aggregates,median_cpu=score,caps=caps))
                eligible=[x for x in tuning if x['candidate']['method']!='maintain' and x['median_cpu'] is not None]
                winner=min(eligible,key=lambda x:(x['median_cpu'],x['candidate']['threshold'],x['candidate']['method']!='unpruned')) if eligible else None
                chosen=winner['candidate'] if winner else dict(method='maintain',threshold=0)
                reference=chosen['method'] if winner and scores['maintain-0'] is not None and winner['median_cpu']<scores['maintain-0'] else 'maintain'
                save(out/'Tuning.json',dict(grid=tuning,subset=[r['case_id'] for r in timing_subset(dev)],workers=216),immutable=True)
                save(selection,dict(**chosen,reference=reference,median_scores=scores,basis='median aggregate full CPU of three declared development repetitions',sealed_before_held=True),immutable=True)
                save(out/'Selection-seal.json',dict(sha256=sha(selection)),immutable=True); committed('Seal experiment 39 development-only selector')
            if stage==40 and not (out/'Selection.json').exists():
                shutil.copy2(selection,out/'Selection.json'); assert sha(out/'Selection.json')==sha(selection)
                save(out/'Selection-seal.json',dict(sha256=sha(selection)),immutable=True)
            for split in ('development','held'):
                rows=dev if split=='development' else inputs(stage,split)
                for index,row in enumerate(rows):
                    if all((out/split/'policies'/row['case_id']/m/'Path-result.json.gz').exists() and (out/split/'policies'/row['case_id']/m/'Audit.json').exists() for m in POLICIES[stage]):
                        continue
                    for method in POLICIES[stage]:
                        folder=out/split/'policies'/row['case_id']/method
                        guard(stage,dict(kind='unique_policy',split=split,case=row['case_id'],policy=method))
                        result=worker(stage,row,method,folder,selection)
                        audit_worker(stage,row,folder)
                    from audit import stream_domain
                    stream_domain(row,out/split/'domain-audits'/(row['case_id']+'.json'))
                    save(out/split/'Cursor.json',dict(completed_cases=index+1,total_cases=len(rows),next_case=rows[index+1]['case_id'] if index+1<len(rows) else None))
                    committed(f'Checkpoint experiment {stage} {split} case {index+1} of {len(rows)}')
                    if (index+1)%8==0: print('PROGRESS',stage,split,index+1,len(rows),flush=True)
                for rep in range(3):
                    for row in timing_subset(rows):
                        for method in POLICIES[stage]:
                            folder=out/f'timing-{split}'/f'rep{rep}'/row['case_id']/method
                            guard(stage,dict(kind='timing',split=split,rep=rep,case=row['case_id'],policy=method))
                            result=worker(stage,row,method,folder,selection)
                            expected=read(out/split/'policies'/row['case_id']/method/'Path-result.json.gz')
                            if result['status']=='window_complete' and expected['status']=='window_complete':
                                assert result['logical_signature']==expected['logical_signature'], 'Timing logical work differs from unique case'
                            audit_worker(stage,row,folder)
                        committed(f'Checkpoint experiment {stage} {split} timing repetition {rep} case {row["case_id"]}')
                summarize_split(stage,split,rows)
                summarize_timing(stage,split,rows)
                committed(f'Save experiment {stage} {split} summary and repeated timings')
            finalize_stage(stage); committed(f'Complete rebuilt experiment {stage}')
        finalize_campaign(); committed('Package rebuilt experiments 36–40 and comparison with retained reports')
    except BatchEnd:
        committed('Preserve bounded experiment batch and exact next task')
        print('BATCH_CHECKPOINT',flush=True)
        return


def cumulative(result,t,key):
    if key=='algorithm_cpu': return sum(x['cpu'] for x in result['ledger'] if x['time']<=t)
    return sum(x['counters'].get(key,0) for x in result['ledger'] if x['time']<=t)


def summarize_split(stage,split,rows):
    out=ROOT/'stages'/str(stage); modes={}; comparisons=[]
    for row in rows:
        results={m:read(out/split/'policies'/row['case_id']/m/'Path-result.json.gz') for m in POLICIES[stage]}
        times=set([0,64,128,256]+([512,768,1024] if stage==40 else []))
        for r in results.values(): times.update(x['time'] for x in r['ledger']); times.update(r['switch_times'])
        base=results['maintain']
        for name,r in results.items():
            if name not in modes: modes[name]=dict(cases=0,complete=0,capped=0,construction_caps=0,counters={},algorithm_cpu=0,switches=0,normalized=0,gate_accepted=0,gate_rejected=0,core={},stress={})
            m=modes[name]; m['cases']+=1; m['complete']+=r['status']=='window_complete'; m['capped']+=r['status']!='window_complete'
            m['construction_caps']+=sum(x['status']!='complete' for x in r['constructions']); m['algorithm_cpu']+=r['algorithm_cpu']; m['switches']+=len(r['switch_times']); m['normalized']+=r['normalized']
            if r['gate']: m['gate_accepted']+=r['gate']['accepted']; m['gate_rejected']+=not r['gate']['accepted']
            for k,v in r['totals'].items(): m['counters'][k]=max(m['counters'].get(k,0),v) if k.endswith('_peak') else m['counters'].get(k,0)+v
            group=m[row['matrix']]; group['cases']=group.get('cases',0)+1; group['construction_caps']=group.get('construction_caps',0)+sum(x['status']!='complete' for x in r['constructions'])
            group['complete']=group.get('complete',0)+(r['status']=='window_complete')
            if name=='maintain': continue
            paired=base['status']=='window_complete' and r['status']=='window_complete'; measures={}
            for key in ('bound_evaluations','dp_entries','dp_transitions','same_slope_checks','dominance_comparisons','index_visits','index_updates','algorithm_cpu'):
                ledger=[[t,cumulative(base,t,key),cumulative(r,t,key)] for t in sorted(times)]
                savings=[b-a for t,b,a in ledger]; end_saving=savings[-1]
                first=next((t for (t,b,a),s in zip(ledger,savings) if s>0),None)
                lastbad=max((i for i,s in enumerate(savings) if s<=0),default=-1)
                persistent=ledger[lastbad+1][0] if end_saving>0 and lastbad+1<len(ledger) else None
                measures[key]=dict(saving=end_saving,preparation_debt=max(0,-savings[0]),first_advantage=first,persistent_advantage=persistent,common_time_ledger=ledger)
            comparisons.append(dict(case_id=row['case_id'],matrix=row['matrix'],capacity_ratio=row.get('capacity_ratio'),policy=name,paired=paired,normalized=r['normalized'],measures=measures))
    for name,m in modes.items():
        if name=='maintain': continue
        m['comparisons']={}
        for key in comparisons[0]['measures']:
            cs=[c for c in comparisons if c['policy']==name and c['paired']]; xs=[c['measures'][key]['saving'] for c in cs]
            largest=max(xs,default=0)
            m['comparisons'][key]=dict(pairs=len(xs),saving=sum(xs),benefited=sum(x>0 for x in xs),harmed=sum(x<0 for x in xs),tied=sum(x==0 for x in xs),without_largest=sum(xs)-largest,
                                       excluding_normalized=sum(c['measures'][key]['saving'] for c in cs if not c['normalized']),distribution=sorted(xs))
    save(out/split/'Summary.json',dict(cases=len(rows),modes=modes,comparisons=comparisons))


def summarize_timing(stage,split,rows):
    out=ROOT/'stages'/str(stage); subset=timing_subset(rows); repetitions=[]
    for rep in range(3):
        aggregate={m:0 for m in POLICIES[stage]}; capped=[]
        for row in subset:
            for method in POLICIES[stage]:
                r=read(out/f'timing-{split}'/f'rep{rep}'/row['case_id']/method/'Path-result.json.gz')
                aggregate[method]+=r['algorithm_cpu']
                if r['status']!='window_complete' or any(x['status']!='complete' for x in r['constructions']): capped.append(dict(case=row['case_id'],method=method))
        repetitions.append(dict(rep=rep,aggregate_cpu=aggregate,capped=capped))
    medians={m:None if any(any(c['method']==m for c in r['capped']) for r in repetitions) else statistics.median(r['aggregate_cpu'][m] for r in repetitions) for m in POLICIES[stage]}
    save(out/f'Timing-{split}.json',dict(subset=[r['case_id'] for r in subset],repetitions=repetitions,median_aggregate_cpu=medians,logical_work_identical=True,selection=False))


def finalize_stage(stage):
    out=ROOT/'stages'/str(stage); dev=read(out/'development/Summary.json'); held=read(out/'held/Summary.json'); records=[]; incomplete=[]
    for split in ('development','held'):
        for row in read(out/split/'Inputs.json'):
            for method in POLICIES[stage]:
                folder=out/split/'policies'/row['case_id']/method; path=folder/'Path-result.json.gz'; r=read(path)
                assert read(folder/'Audit.json')['passed']
                assert r['totals']['bound_evaluations']<=CAPS[stage]['scalar_evaluations'] and r['totals']['native_generator_steps']<=CAPS[stage]['cumulative_native']
                records.append(dict(case=row['case_id'],split=split,method=method,status=r['status'],result_file=str(path.relative_to(ROOT)),sha256=sha(path)))
                for build in r['constructions']:
                    if build['status']!='complete': incomplete.append(dict(stage=stage,split=split,case=row['case_id'],policy=method,record=build['record'],cursor=build['cursor'],reason=build['reason'],trajectory_status=r['status'],active_certificate=False,fallback_complete=r['status']=='window_complete',frozen_cap_exhausted=True))
    freeze(stage)
    save(out/'Complete.json',dict(all_cases_attempted=True,unique_trajectories=dev['cases']+held['cases'],policy_paths=len(records),all_policy_paths_complete=all(r['status']=='window_complete' for r in records),incomplete_constructions=len(incomplete),audit_passed=True),immutable=True)
    save(out/'Resume-cursors.json',dict(unfinished_paths=[r for r in records if r['status']!='window_complete'],incomplete_frontier_constructions=incomplete,pending_audit_ranges=[],initialization_failures=[],unstarted_cases=[]),immutable=True)
    save(out/'Result-reconciliation.json',dict(passed=True,records=records,no_unique_policy_replays=True),immutable=True)
    lines=[f'# Rebuilt experiment {stage}', '',f"{dev['cases']} development and {held['cases']} held-out trajectories.",'','| Policy | Held windows complete | Candidate evaluations | Raw proof rows | Index visits | Incomplete builds |','|---|---:|---:|---:|---:|---:|']
    for name,m in held['modes'].items(): lines.append(f"| {name} | {m['complete']} | {m['counters']['bound_evaluations']} | {m['counters']['dp_entries']} | {m['counters']['index_visits']} | {m['construction_caps']} |")
    lines += ['','Unlike counters are separate units. Completed fallback does not complete an abandoned frontier. Independent audits cover every saved DP layer, index/deletion evidence, scalar events, native objectives and all integer times in completed observation windows. Timings use the three predeclared isolated repetitions; original shared-data dependencies remain. No worst-case efficiency or new arithmetic claim is made.']
    (out/'Report.md').write_text('\n'.join(lines)+'\n')
    print('STAGE_COMPLETE',stage,read(out/'Complete.json'),flush=True)


def prepare():
    ROOT.mkdir(exist_ok=True)
    if not (ROOT/'Handoff.md').exists(): shutil.copy2(REPO/'handoffs/Temporal-proof-experiments-36-40-handoff.md',ROOT/'Handoff.md')
    # Recheck the preserved baseline on this runner without replaying research.
    subprocess.run([sys.executable,str(REPO/'scripts/recover_campaign_31_35.py')],cwd=REPO,check=True)
    save(ROOT/'Checkpoint-verification.json',read(REPO/'RECOVERY-31-35.json'))
    prior=ROOT/'Prior-reports'; prior.mkdir(exist_ok=True)
    for p in (REPO/'results/experiments-36-40').glob('*'): shutil.copy2(p,prior/p.name)
    save(ROOT/'Environment.json',dict(python=platform.python_version(),platform=platform.platform(),standard_library_only=True,runner=os.environ.get('RUNNER_OS','local')))
    if not (ROOT/'fixture-evidence').exists():
        from fixtures_new import run
        run()
    committed('Prepare rebuilt campaign and verify meaningful proof fixtures')


def finalize_campaign():
    from comparison import finish
    finish()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=['prepare','run','audit-worker']); parser.add_argument('--batch-seconds',type=int,default=900); parser.add_argument('--row'); parser.add_argument('--folder'); args=parser.parse_args()
    if args.mode=='prepare': prepare()
    elif args.mode=='run': execute(args.batch_seconds)
    else:
        from audit import path_audit
        folder=Path(args.folder); path_audit(read(args.row),read(folder/'Path-result.json.gz'),folder)


if __name__=='__main__': main()
