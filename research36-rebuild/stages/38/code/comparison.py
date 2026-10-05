"""Final integrity coverage, reporting and comparison with unavailable prior work."""
import hashlib
import json
from pathlib import Path
import tarfile
import zipfile
from common import ROOT, read, save, sha

OLD={36:dict(unpruned_rows=122000,same_rows=57581,same_checks=57509),
     37:dict(naive_comparisons=1369626,index_visits_reported=200961,matched_retained_cases=96),
     38:dict(held_cases=240,held_unpruned_caps=18,held_same_caps=12),
     39:dict(selected_method='same',selected_threshold=50000,accepted_non_normalized=72,normalized=24),
     40:dict(rolling_rows=81056,unpruned_rows=116145,rolling_first_window_rows=38948,later_rebuilds=216,rolling_cpu_harmed_pairs=70)}


def equivalence37():
    matches=0; cases=[]; out=ROOT/'stages/37'
    for row in read(out/'held/Inputs.json'):
        if row['profits']==row['slopes']: matches+=1; cases.append(dict(case=row['case_id'],normalized=True,matched=True)); continue
        pair=[]
        for method in ('naive','indexed'):
            result=read(out/'held/policies'/row['case_id']/method/'Path-result.json.gz')
            record=result['constructions'][0]
            if record['status']!='complete': pair=[]; break
            cert=read(ROOT/record['record']['file']); pair.append([layer['retained'] for layer in cert['layers']])
        matched=len(pair)==2 and pair[0]==pair[1]
        matches+=matched; cases.append(dict(case=row['case_id'],normalized=False,matched=matched))
    save(out/'Indexed-naive-equivalence.json',dict(passed=all(x['matched'] for x in cases),held_cases=96,matched_cases=matches,cases=cases))
    return matches


def finish():
    from campaign import POLICIES
    statuses={str(stage):read(ROOT/'stages'/str(stage)/'Complete.json') for stage in range(36,41)}
    cursors=dict(unfinished_paths=[],incomplete_frontier_constructions=[],pending_audit_ranges=[],initialization_failures=[],unstarted_cases=[])
    for stage in range(36,41):
        data=read(ROOT/'stages'/str(stage)/'Resume-cursors.json')
        for key in cursors: cursors[key]+=data[key]
    save(ROOT/'Campaign-status.json',statuses)
    save(ROOT/'Resume-cursors.json',cursors)
    cases=sum(x['unique_trajectories'] for x in statuses.values()); paths=sum(x['policy_paths'] for x in statuses.values())
    assert cases==832 and paths==3328
    matches=equivalence37(); observed={}; pairs=[]
    for stage in range(36,41):
        held=read(ROOT/'stages'/str(stage)/'held/Summary.json')['modes']
        if stage==36: new=dict(unpruned_rows=held['unpruned']['counters']['dp_entries'],same_rows=held['same']['counters']['dp_entries'],same_checks=held['same']['counters']['same_slope_checks'])
        elif stage==37: new=dict(naive_comparisons=held['naive']['counters']['dominance_comparisons'],index_query_visits=held['indexed']['counters']['index_visits'],index_update_visits=held['indexed']['counters']['index_updates'],matched_retained_cases=matches)
        elif stage==38: new=dict(held_cases=240,held_unpruned_caps=held['unpruned']['construction_caps'],held_same_caps=held['same']['construction_caps'],held_indexed_caps=held['indexed']['construction_caps'])
        elif stage==39:
            choice=read(ROOT/'stages/39/Selection.json'); new=dict(selected_method=choice['method'],selected_threshold=choice['threshold'],accepted_non_normalized=held['selected']['gate_accepted'],normalized=held['selected']['normalized'])
        else:
            new=dict(rolling_rows=held['rolling']['counters']['dp_entries'],unpruned_rows=held['unpruned']['counters']['dp_entries'],later_rebuilds=held['rolling']['counters']['interval_rebuilds'])
            first=0; harmed=0
            for row in read(ROOT/'stages/40/held/Inputs.json'):
                folder=ROOT/'stages/40/held/policies'/row['case_id']
                rolling=read(folder/'rolling/Path-result.json.gz'); unpruned=read(folder/'unpruned/Path-result.json.gz')
                first+=rolling['constructions'][0]['counters']['dp_entries'] if rolling['constructions'] else 0
                harmed+=rolling['algorithm_cpu']>unpruned['algorithm_cpu']
            new.update(rolling_first_window_rows=first,rolling_cpu_harmed_pairs=harmed)
        observed[stage]=new
        for key,old in OLD[stage].items():
            if key in new: pairs.append(dict(stage=stage,measure=key,reported_prior=old,rebuild=new[key],equal=old==new[key]))
    save(ROOT/'Comparison.json',dict(prior_status='Reported aggregates only; lost code/evidence unavailable',prior_reports_sha256={p.name:sha(p) for p in (ROOT/'Prior-reports').glob('*')},reported_prior=OLD,observed_rebuild=observed,comparisons=pairs,
                                    index_counter_note='New query-node visits and update-node visits are separate. The old report does not define whether its index visits combines them.'))
    lines=['# Convergences and divergences with the retained 36–40 reports','',
           'The prior campaign could not be recovered. This comparison uses its preserved synthesis and cursors as reported aggregates, not independently verified prior evidence. The rebuild uses the prescribed seeds and vectors from the recovered 31–35 kernels, so it is a reconstruction on the same declared cohorts, not an independent statistical replication. No prior CPU result or held-out outcome selected a new policy.','',
           '| Stage | Measure | Reported prior | Rebuild | Agreement |','|---|---|---:|---:|---|']
    for p in pairs: lines.append(f"| {p['stage']} | {p['measure']} | {p['reported_prior']} | {p['rebuild']} | {'equal' if p['equal'] else 'differs'} |")
    lines += ['','Raw recurrence counts and exact retained sets are useful deterministic comparisons. Different dominance witnesses can still certify the same retained states. Query-node visits and update-node visits are reported separately here; the prior combined definition cannot be recovered. Construction cap counts can differ because complete index/query/order evidence and conservative auxiliary reservations change when the same 500,000-record ceiling fires. No cap was raised.',
              '', 'Stage-39 thresholds can receive different measured CPU scores even when they accept the same inputs and do identical logical work. A different selected threshold in that situation does not establish a different functional gate or a uniquely useful cutoff. CPU differences also reflect hardware, interpreter, instrumentation, fresh-worker native costs and bookkeeping scopes. Unique-case CPU benefited/harmed counts are descriptive; runtime findings rest on the exact predeclared repeated subsets.',
              '', 'All-time same-slope and finite-interval endpoint arguments converge at the mathematical level. They remain elementary optimization arguments. Missing prior proof files prevent proof-by-proof cross-validation, and neither aggregate agreement nor a smaller finite proof establishes a generally efficient optimizer or new arithmetic.']
    (ROOT/'Comparison.md').write_text('\n'.join(lines)+'\n')
    synthesis=['# Rebuilt temporal-proof experiments 36–40','',f'{cases} declared unique trajectories and {paths} headline policy paths were attempted. This consists of 640 core trajectories and 192 separate stress trajectories. Timing and selector tuning are separate from unique-case counts.',
               '',f"Incomplete trajectories: {len(cursors['unfinished_paths'])}. Incomplete abandoned frontier constructions: {len(cursors['incomplete_frontier_constructions'])}. Completed scalar fallback never completes the abandoned proof.",'',
               '| Stage | Held trajectories | Policy | Complete windows | Candidate evaluations | Raw proof rows | Incomplete builds |','|---|---:|---|---:|---:|---:|---:|']
    for stage in range(36,41):
        held=read(ROOT/'stages'/str(stage)/'held/Summary.json')
        for policy,m in held['modes'].items(): synthesis.append(f"| {stage} | {held['cases']} | {policy} | {m['complete']} | {m['counters']['bound_evaluations']} | {m['counters']['dp_entries']} | {m['construction_caps']} |")
    synthesis += ['','| Stage/subset | Median aggregate full algorithm CPU, seconds |','|---|---|']
    for stage in range(36,41):
        for split in ('development','held'):
            timing=read(ROOT/'stages'/str(stage)/f'Timing-{split}.json')
            synthesis.append(f"| {stage}/{split} | "+', '.join(f'{m}: {cpu:.6f}' if cpu is not None else f'{m}: ineligible/capped' for m,cpu in timing['median_aggregate_cpu'].items())+' |')
    synthesis += ['','The 1,152 declared timing workers and 216 stage-39 tuning workers are archived separately. Each timing worker is isolated and pays for its own cold native initial/replacement solves. The held timing subset uses only the first held seeds. Results sharing weights/profits/directions/capacities are dependent paired observations.',
                  '', 'Modeled time is the integer parameter of p+t*v. CPU is execution cost. Strict optimality loss means a feasible packing beats the incumbent; scalar certificate expiry can happen sooner without any switch. Proof width counts saved recurrence and auxiliary records. Preparation and rolling reconstruction must repay their debt separately in each counter and CPU; unlike counts are never added into a synthetic speedup.',
                  '', '[Comparison with the retained prior reports](Comparison.md) records both matching and differing aggregates. The prior detailed 36–40 evidence remains unavailable. New sources, immutable inputs/policy/construction/event records, independent range audits, timings, counters and exact cursors are retained here. The original 31–35 checkpoint remains unchanged as an explicit byte-identical repository reference.',
                  '', 'These are exact parametric integer-knapsack experiments motivated by questions about Allen Brooks’ “numbers with time built in.” They do not reconstruct unpublished mathematics or authenticate a breakthrough. No new arithmetic is claimed.']
    (ROOT/'Synthesis.md').write_text('\n'.join(synthesis)+'\n')
    save(ROOT/'Baseline-reference.json',dict(repository='devinendorphin/maths',path='campaigns/experiments-31-35',archive_bytes=176127453,archive_sha256='656930b55f767e811089a8b345abb1cbf228559dd13afaf4be770d4c7c4f7b9f',reassembly_parts_path='handoffs',unchanged_checkpoint=True))
    # Reconcile hashes and all required independent coverage, beyond a passed flag.
    checked_paths=0; coverage_count=0
    for stage in range(36,41):
        out=ROOT/'stages'/str(stage)
        assert all(sha(out/p)==h for p,h in read(out/'Frozen.json').items())
        for split in ('development','held'):
            for row in read(out/split/'Inputs.json'):
                for policy in POLICIES[stage]:
                    folder=out/split/'policies'/row['case_id']/policy; result=read(folder/'Path-result.json.gz'); audit=read(folder/'Audit.json')
                    assert audit['passed']; assert all((folder/p).exists() and read(folder/p)['passed'] for p in audit['coverage_files'])
                    for i,build in enumerate(result['constructions']):
                        record=read(folder/f'construction-audit-{i:03}.json'); assert not record['pending'] and {r['key'] for r in record['records']}==set(record['required'])
                        assert sha(ROOT/build['record']['file'])==build['record']['sha256']
                    expected_times=row['end']+1 if result['status']=='window_complete' else max(1,result['final_time'])
                    assert sum(len(read(p)['values']) for p in folder.glob('objective-audit-*.json'))==expected_times
                    checked_paths+=1; coverage_count+=len(audit['coverage_files'])
    assert checked_paths==3328
    final=dict(passed=True,unique_trajectories=cases,headline_policy_paths=paths,all_cases_attempted=True,
               all_policy_paths_complete=not cursors['unfinished_paths'],incomplete_constructions=len(cursors['incomplete_frontier_constructions']),
               pending_audit_ranges=[],independent_coverage_files=coverage_count,baseline_unchanged=True,
               timing_workers=1152,selector_tuning_workers=216,no_unique_policy_replays=True)
    save(ROOT/'Final-audit.json',final); save(ROOT/'Complete.json',final)
    archive=ROOT/'Temporal-proof-experiments-36-40-rebuild.tar.xz'
    excluded={'Manifest.json','Archive-verification.json',archive.name}
    files=[p for p in ROOT.rglob('*') if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts and 'archive-parts' not in p.parts]
    manifest={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)}
    save(ROOT/'Manifest.json',dict(files=manifest))
    with tarfile.open(archive,'w:xz',preset=3) as tf:
        for p in sorted(files)+[ROOT/'Manifest.json']: tf.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
    verified=0
    with tarfile.open(archive,'r|xz') as tf:
        for member in tf:
            if member.name=='Manifest.json': continue
            record=manifest[member.name]; stream=tf.extractfile(member); h=hashlib.sha256()
            for b in iter(lambda:stream.read(1<<20),b''): h.update(b)
            assert h.hexdigest()==record['sha256'] and member.size==record['bytes']; verified+=1
    assert verified==len(manifest)
    archive_sha=sha(archive); archive_bytes=archive.stat().st_size
    parts=[]
    if archive_bytes>90*(1<<20):
        directory=ROOT/'archive-parts'; directory.mkdir(exist_ok=True)
        with archive.open('rb') as f:
            i=0
            for data in iter(lambda:f.read(24000000),b''):
                i+=1; payload=f'campaign.part{i:03}'; target=directory/f'Rebuild-36-40-part-{i:03}.zip'
                with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_STORED) as z: z.writestr(payload,data)
                parts.append(dict(file=target.name,file_bytes=target.stat().st_size,file_sha256=sha(target),payload=payload,payload_bytes=len(data),payload_sha256=hashlib.sha256(data).hexdigest()))
        save(directory/'Parts-manifest.json',dict(original=dict(filename=archive.name,bytes=archive_bytes,sha256=archive_sha),parts=parts))
        with zipfile.ZipFile(ROOT.parent/'handoffs/Campaign-31-35-reassembly-kit.zip') as z:
            script=z.read('reassemble.py').decode()
        script=script.replace("directory / 'Temporal-proof-experiments-31-35-campaign.zip'", "directory / json.loads((directory / 'Parts-manifest.json').read_text())['original']['filename']")
        (directory/'reassemble.py').write_text(script)
        archive.unlink()
    save(ROOT/'Archive-verification.json',dict(archive=archive.name,archive_bytes=archive_bytes,archive_sha256=archive_sha,manifest_members=verified,all_member_hashes_verified=True,failures=[],archive_in_parts=bool(parts),parts=len(parts)))
    print('CAMPAIGN_COMPLETE',json.dumps(final),flush=True)
