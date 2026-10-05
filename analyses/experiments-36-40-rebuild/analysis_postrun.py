"""Read-only campaign diagnostics and separately counted supplemental fixtures."""
import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tarfile

REPO=Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name=='scripts' else Path(__file__).resolve().parent
PRIMARY=REPO/'research36-rebuild'
OUT=REPO/'analyses/experiments-36-40-rebuild'
METRICS=('bound_evaluations','dp_entries','dp_transitions','dominance_comparisons','same_slope_checks','index_visits','index_updates')

def read(path):
    path=Path(path)
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as stream: return json.load(stream)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(data,indent=2,sort_keys=True).encode()
    if path.suffix=='.gz': payload=gzip.compress(payload,mtime=0)
    path.write_bytes(payload)

def bounds(row):
    slopes=row['slopes']; widths=[]
    for j in range(len(slopes)+1):
        prefix=slopes[:j]; gcd=math.gcd(*[abs(x) for x in prefix]) if prefix else 0
        lower=sum(min(0,x) for x in prefix); upper=sum(max(0,x) for x in prefix)
        widths.append((row['capacity']+1)*(1 if not gcd else 1+(upper-lower)//gcd))
    return dict(prefix_bounds=widths,E_bound=sum(widths),T_bound=2*sum(widths[:-1]))

def diagnose():
    assert read(PRIMARY/'Complete.json')['passed']
    archive=read(PRIMARY/'Archive-verification.json')
    write(OUT/'Primary-reference.json',dict(path='research36-rebuild',archive=archive,manifest_sha256=digest(PRIMARY/'Manifest.json'),scope='Retrospective diagnostics only; no declared policy executions replayed'))
    cohorts=[]; gate_rows=[]; maxima=dict(native_generator_steps=0,native_returned_cells=0,native_wall=0)
    paths=0
    for stage in range(36,41):
        directory=PRIMARY/'stages'/str(stage)
        modes=list(read(directory/'held/Summary.json')['modes'])
        for split in ('development','held'):
            summary=read(directory/split/'Summary.json')
            write(OUT/'compact-summaries'/f'{stage}-{split}.json',dict(stage=stage,split=split,cases=summary['cases'],modes=summary['modes'],scope='Aggregate modes only; full per-case common-time ledgers remain in the primary campaign'))
            del summary
            groups={}
            for row in read(directory/split/'Inputs.json'):
                results={mode:read(directory/split/'policies'/row['case_id']/mode/'Path-result.json.gz') for mode in modes}
                features=bounds(row)
                for mode,result in results.items():
                    paths+=1
                    key=(row['matrix'],row['n'],row['family'],row['regime'],row.get('capacity_ratio'),mode)
                    if key not in groups:
                        groups[key]=dict(matrix=key[0],n=key[1],family=key[2],regime=key[3],capacity_ratio=key[4],policy=mode,cases=0,complete=0,construction_caps=0,algorithm_cpu=0,counters={metric:0 for metric in METRICS},paired=0,cpu_benefited=0,cpu_harmed=0,normalized=0)
                    group=groups[key]; group['cases']+=1; group['complete']+=result['status']=='window_complete'; group['construction_caps']+=sum(build['status']!='complete' for build in result['constructions']); group['algorithm_cpu']+=result['algorithm_cpu']; group['normalized']+=result['normalized']
                    for metric in METRICS: group['counters'][metric]+=result['totals'][metric]
                    if results['maintain']['status']=='window_complete' and result['status']=='window_complete':
                        group['paired']+=1
                        delta=results['maintain']['algorithm_cpu']-result['algorithm_cpu']
                        group['cpu_benefited']+=delta>0; group['cpu_harmed']+=delta<0
                    for native in result['native']:
                        assert native['construction_steps']<=500000 and native['empty']
                        maxima['native_generator_steps']=max(maxima['native_generator_steps'],native['construction_steps'])
                        maxima['native_wall']=max(maxima['native_wall'],native['wall'])
                        if native['status']=='complete':
                            assert len(native['proof'])<=4096
                            maxima['native_returned_cells']=max(maxima['native_returned_cells'],len(native['proof']))
                if stage in (39,40):
                    for mode in ('conservative','selected') if stage==39 else ('selected',):
                        result=results[mode]; gate=result['gate']; normalized=result['normalized']
                        if gate:
                            assert all(gate['features'][name]==features[name] for name in features)
                            choice=gate['selection']; expected=choice['method']!='maintain' and features['E_bound']<=choice['threshold'] and features['T_bound']<=2000000
                            assert gate['accepted']==expected
                        reference=results['unpruned']; complete=bool(reference['constructions']) and all(b['status']=='complete' for b in reference['constructions'])
                        entries=reference['totals']['dp_entries'] if complete else None
                        if entries is not None: assert entries<=features['E_bound']
                        gate_rows.append(dict(stage=stage,split=split,case_id=row['case_id'],policy=mode,normalized=normalized,features=features,accepted=None if gate is None else gate['accepted'],selection=None if gate is None else gate['selection'],complete_observed_unpruned_rows=entries,bound_to_rows_ratio=None if not entries else features['E_bound']/entries,retrospective_could_have_completed_unpruned=complete,retrospective_only=True))
            cohorts.append(dict(stage=stage,split=split,groups=list(groups.values())))
    assert paths==3328
    write(OUT/'Cohort-diagnostics.json',dict(groups=cohorts,unique_policy_paths=paths,cpu_counts='Descriptive unique executions, not repeated timing estimates; observations share source data',operation_units='Counters stay separate'))
    write(OUT/'Gate-diagnostics.json',dict(passed=True,rows=gate_rows,retrospective_only=True,not_used_by_algorithm_or_selector=True))
    write(OUT/'Native-limit-verification.json',dict(passed=True,headline_paths=paths,maxima=maxima,source_kernel_guard='steps >= min(max_steps,500000); returned cells <=4096; 30-second construction guard; disposed native store'))
    tuning=read(PRIMARY/'stages/39/Tuning.json')
    equalities=[]
    for method in ('unpruned','same'):
        for rep in range(3):
            for case in tuning['subset']:
                signatures=[read(PRIMARY/f'stages/39/tuning/{method}-{threshold}/rep{rep}/{case}/Path-result.json.gz')['logical_signature'] for threshold in (50000,125000,250000,500000)]
                equalities.append(dict(method=method,rep=rep,case_id=case,identical=len(set(signatures))==1))
    write(OUT/'Threshold-equivalence.json',dict(passed=all(x['identical'] for x in equalities),comparisons=equalities,interpretation='If identical, different timing scores do not establish a functionally different or uniquely useful threshold'))
    ceilings=[]
    for n in (12,16):
        max_capacity=(20*n)//3
        e=(max_capacity+1)*sum(1+3*j for j in range(n+1))
        t=2*(max_capacity+1)*sum(1+3*j for j in range(n))
        assert e<=50000 and t<=2000000
        ceilings.append(dict(n=n,max_capacity=max_capacity,E_ceiling=e,T_ceiling=t))
    write(OUT/'Core-gate-bound.json',dict(passed=True,ceilings=ceilings,argument='For every non-normalized core direction, absolute item slopes are at most 3. At prefix j, U-L is at most 3*j, and either gcd is zero (one bin) or it is at least one, so bins are at most 1+3*j. Capacity is at most floor(20*n/3). All four fixed thresholds therefore accept every possible non-normalized core input, regardless of seed. Scale directions are recognized first and skip the gate.',scope='This declared core generator only; excludes stress, other capacities, larger n and larger slopes'))
    prior=read(PRIMARY/'Comparison.json')
    note=['# Supplemental interpretation and diagnostics','',
          'These analyses read the completed campaign. They do not replay declared cases or select any policy. The primary archive remains unchanged.','',
          'The rebuilt inputs independently satisfy the handoff’s seeded protocol. The lost campaign’s actual vectors and initial packing masks cannot be compared. In particular, harm directions depend on the initial optimal packing; seeds alone cannot establish byte-identical prior inputs. Differences in deterministic counts are genuine reported divergences, but their cause cannot be identified from aggregate documents.','',
          'Cohort-diagnostics.json separates core/stress, size, family, direction, capacity and policy, with explicit paired denominators. CPU benefited/harmed counts there describe unique executions. Use the primary campaign’s prescribed repeated timing subsets for runtime findings.','',
          'Gate-diagnostics.json records exact independently recomputed bounds, acceptance decisions, observed complete unpruned widths and retrospective could-have-completed descriptions. The latter are audit-only observations and never supplied algorithm features. Threshold-equivalence.json checks identical logical work across thresholds within each method and development repetition.','',
          'Core-gate-bound.json gives an elementary bound stronger than a retrospective count: with the declared core generator, every non-normalized direction has absolute item slopes at most 3 and capacity at most floor(20*n/3). The largest possible E bound is 45,475 at n=16, and the T bound is at most 80,464. Even the smallest threshold of 50,000 must accept every non-normalized core input. The grid cannot distinguish acceptance decisions on this generator; a timing-selected threshold does not demonstrate failed-build avoidance. This does not extend to the stress generator or broader inputs.','',
          'The supplemental later-window guard fixture exercises abandonment, stale scalar repricing and the strict loss at 257. It is outside the 832/3,328 unique counts and the timing/tuning counts. Its full result and audit ranges are saved separately.','',
          'Missing prior proofs prevent proof-by-proof validation. Matching reported aggregates does not authenticate the old evidence. No worst-case efficiency or new arithmetic claim follows.']
    (OUT/'Interpretation.md').write_text('\n'.join(note)+'\n')

def validate_later():
    os.environ['MATHS_RESEARCH_ROOT']=str(PRIMARY)
    sys.path.insert(0,str(PRIMARY/'stages/40/code'))
    import certificates as C
    from policy import run
    from audit import path_audit
    row=dict(case_id='supplemental-later-window-cap',stage=40,weights=[1,1],profits=[10,-246],slopes=[0,1],capacity=1,end=1024)
    original=C.build; calls=0
    def bounded(*args,**kwargs):
        nonlocal calls
        calls+=1
        if calls==2:
            args=list(args); args[8]=dict(args[8],auxiliary=3)
        return original(*args,**kwargs)
    C.build=bounded
    try: result=run(row,'rolling')
    finally: C.build=original
    assert result['status']=='window_complete' and len(result['constructions'])==2
    assert result['constructions'][0]['status']=='complete' and result['constructions'][1]['status']!='complete'
    assert result['constructions'][1]['anchor']==256 and result['switch_times']==[257]
    assert any(event['kind']=='fallback_reprice' and event['time']==256 for event in result['events'])
    folder=OUT/'later-window-cap'
    write(folder/'Input.json',row); write(folder/'Result.json.gz',result)
    audit=path_audit(row,result,folder)
    assert audit['passed']
    write(folder/'Validation.json',dict(passed=True,not_a_declared_experiment=True,forced_auxiliary_guard_on_second_build=3,frozen_policy_sha256=digest(PRIMARY/'stages/40/code/policy.py'),frozen_builder_sha256=digest(PRIMARY/'stages/40/code/certificates.py')))

def package():
    shutil.copy2(Path(__file__),OUT/'analysis_postrun.py')
    archive=OUT/'Supplemental-analysis.tar.xz'
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name not in ('Manifest.json','Archive-verification.json',archive.name)]
    manifest={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in files}
    write(OUT/'Manifest.json',manifest)
    with tarfile.open(archive,'w:xz') as stream:
        for p in files+[OUT/'Manifest.json']: stream.add(p,arcname=str(p.relative_to(OUT)),recursive=False)
    checked=0
    with tarfile.open(archive,'r|xz') as stream:
        for member in stream:
            if member.name=='Manifest.json': continue
            data=stream.extractfile(member).read(); expected=manifest[member.name]
            assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']; checked+=1
    assert checked==len(manifest)
    write(OUT/'Archive-verification.json',dict(passed=True,archive=archive.name,bytes=archive.stat().st_size,sha256=digest(archive),verified_members=checked))

def review_kit():
    archive=OUT/'Maths-36-40-review-kit.tar.xz'
    mapping={}
    root_names=['Handoff.md','Synthesis.md','Comparison.md','Comparison.json','Complete.json','Final-audit.json','Archive-verification.json','Baseline-reference.json','Verification-fixtures.json','Environment.json','Resume-cursors.json']
    for name in root_names:
        p=PRIMARY/name
        if p.exists(): mapping['research36-rebuild/'+name]=p
    for p in (PRIMARY/'code').glob('*.py'): mapping['research36-rebuild/code/'+p.name]=p
    for stage in range(36,41):
        directory=PRIMARY/'stages'/str(stage)
        for p in (directory/'code').glob('*.py'): mapping[str(p.relative_to(REPO))]=p
        for name in ['Protocol.md','Report.md','Frozen.json','Base-kernel-hashes.json','Complete.json','Selection.json','Selection-seal.json','Tuning.json','Timing-development.json','Timing-held.json','Resume-cursors.json']:
            p=directory/name
            if p.exists(): mapping[str(p.relative_to(REPO))]=p
        for split in ('development','held'):
            for name in ('Inputs.json','Input-verification.json'):
                p=directory/split/name
                if p.exists(): mapping[str(p.relative_to(REPO))]=p
    baseline=REPO/'campaigns/experiments-31-35/research/stages/35/code'
    for p in baseline.glob('*.py'): mapping[str(p.relative_to(REPO))]=p
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix not in ('.xz',) and p.name not in ('Manifest.json','Archive-verification.json'):
            mapping[str(p.relative_to(REPO))]=p
    mapping['REPRODUCE-36-40.md']=REPO/'REPRODUCE-36-40.md'
    scope=OUT/'Review-kit-scope.md'
    scope.write_text('# Small review kit\n\nThis contains the new sources and frozen snapshots, original stage-35 kernel modules, all declared inputs, protocols, reports, timing/selection records, aggregate summaries, and supplemental diagnostics/fixture. It excludes the full checkpoint history, detailed unique policy records, construction/event proofs and their hundreds of thousands of audit/checkpoint files. This is a reading/source kit, not the complete evidence archive. Full evidence and the checked primary 69-part archive remain at https://github.com/devinendorphin/maths/tree/main/research36-rebuild . Follow REPRODUCE-36-40.md with the full repository for a fresh complete reproduction.\n')
    mapping[str(scope.relative_to(REPO))]=scope
    manifest={name:dict(bytes=p.stat().st_size,sha256=digest(p)) for name,p in mapping.items()}
    manifest_file=OUT/'Review-kit-manifest.json'; write(manifest_file,manifest)
    with tarfile.open(archive,'w:xz',preset=3) as stream:
        for name,p in sorted(mapping.items()): stream.add(p,arcname=name,recursive=False)
        stream.add(manifest_file,arcname='Review-kit-manifest.json',recursive=False)
    checked=0
    with tarfile.open(archive,'r|xz') as stream:
        for member in stream:
            if member.name=='Review-kit-manifest.json': continue
            data=stream.extractfile(member).read(); expected=manifest[member.name]
            assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']; checked+=1
    assert checked==len(manifest) and archive.stat().st_size<32*(1<<20)
    write(OUT/'Review-kit-verification.json',dict(passed=True,archive=archive.name,bytes=archive.stat().st_size,sha256=digest(archive),verified_members=checked,full_evidence_included=False))

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    diagnose(); validate_later(); package(); review_kit()
    print('Supplemental cohort/gate diagnostics, native limits, later-window fixture and archive verified')
