"""Build concise reports from audited saved data."""
import json,hashlib,statistics,platform
from pathlib import Path
from runner import ROOT,read,save
assert read(ROOT/'Final-audit.json')['passed']
stats={s:read(ROOT/'stages'/str(s)/'held/Summary.json') for s in range(31,36)}
lines=['# Temporal-proof experiments 31–35','', 'All five old stage-30 capped paths reached modeled time 256 under the authorized extension. Experiments 31–35 completed 32 development and 96 held-out trajectories each: 640 new unique trajectories and 1,920 policy paths. Every held-out comparison has 96 completed pairs. No new trajectory or frontier construction capped; no cases or audit ranges remain unstarted. The exact resume file therefore has empty pending lists.','', '| Experiment | Held-out finding | Decisive limitation |','|---|---|---|',
'| 31: scalar tail replication | Maintenance 1,198,568; skip15 1,201,556; rebuild 2,666,372 candidate evaluations. Skip15 found no successful probe. | More resource completed these finite tails; it gives no cheapness or worst-case bound. |',
'| 32: cardinality | Uniform-frontier policy avoided 2,827,592 candidate evaluations and constructed 520,032 DP entries. | Zero-slope controls pay preparation even when renewal was already unnecessary; near-uniform vectors fall back. |',
'| 33: affine factor | Maintenance / max-only / max-min used 1,105,203 / 656,133 / 435,262 candidate evaluations. Max/min built 468,372 DP entries. | Maximum-only lines have a positive-factor domain; minima are required after a sign reversal. |',
'| 34: count vectors | Two-class used 78,470 candidate evaluations and 599,242 DP entries, versus 752,819 maintenance evaluations. | More than two actual slope classes fall back; count-domain preparation can be expensive. |',
'| 35: exact slopes and pruning | Both frontiers used zero scalar renewal evaluations. Unpruned / pruned stored 123,846 / 41,536 recurrence entries; pruning made 1,716,097 dominance comparisons. | Sparse width can be exponential; endpoint pruning is valid only on [0,256]. |','',
'Candidate evaluations, DP entries/transitions, dominance comparisons, horizons and native search steps are distinct units. They are never summed into a synthetic work total. Initial/native optimizer construction, cleanup and disposal are fully charged to every policy even when solves are physically shared. All policies retain ties and use the same native replacement packing; each stage has equal strict-switch counts across its policies. Full recurrence witnesses, scalar covers, branch traces, original-time line crossings, bounded audit records, cumulative ledgers and cap logs are included. Shared weights/profits among directions make these descriptive paired trajectories rather than independent trials.','']
selection=read(ROOT/'stages/34/Selection.json');lines+=['Two-class was sealed as stage 35’s structural candidate using only the declared eight-case development timing subset. Its median aggregate CPU across three repetitions was %.6f s, versus %.6f for affine max/min and %.6f for maintenance. No held-out outcome selected a policy.'%(selection['scores']['two_class'],selection['scores']['affine_pair'],selection['scores']['maintain']),'', '| Stage-35 declared eight-case timing subset | Maintenance | Two-class | Unpruned slope | Endpoint-pruned |','|---|---:|---:|---:|---:|']
for split in ('development','held'):
 d=read(ROOT/f'stages/35/Timing-{split}.json');m=d['median_aggregate_cpu'];lines.append('| '+split+' | '+' | '.join(f'{m[n]:.6f} s' for n in ('maintain','two_class','slope','pruned'))+' |')
lines+=['','These measurements use fresh algorithm state and include preparation, recognition, all native solves and maintenance; audit/serialization are excluded. All three repetitions completed with identical logical counters. Held-out timing covers only the first seed’s prescribed subset and cannot change selection. In both subsets pruning was slower than the unpruned frontier in every repetition: fewer retained states did not repay comparisons and witness bookkeeping. Both exact frontiers beat maintenance on these measured subsets after charging construction. This is empirical evidence for these cases, not a general runtime guarantee.','',
'An optimality horizon says when the current packing is first strictly beaten. Certificate expiry says when its particular proof stops certifying it, often earlier. Proof complexity can grow while the packing stays unchanged. A persistent frontier removes repeated certificate renewal by paying for an exact family of future value lines up front; whether that preparation amortizes depends on the trajectory and work measure.','',
'Completed unpruned cardinality/count/slope recurrence certificates give exact value representations for all nonnegative modeled times in their declared structural domains. Affine max/min certificates handle zero and negative factors; the max-only policy needs its checked scalar handoff. Endpoint-dominance certificates certify only 0–256 and reject 257. Mathematical derivations are separated from sampled DP checks and empirical timings in Mathematical-guarantees.md. No novel arithmetic, recovered unpublished mathematics, or breakthrough claim is made.','',
'Evidence interruptions are disclosed. Three missing policy-result records (one in stage 31, two in stage 32) retained earlier partial file versions; only those records were regenerated from frozen code, independently audited, and their repeated work recorded separately. Original aggregate summaries and every surviving path were preserved. Later stages retain separate immutable policy results; read-only reconciliation completed pending saved audit ranges without replaying policies. Stage 34’s first timing attempt failed at a checkpoint pathname after computing a policy result; that uncheckpointed timing attempt was repeated. Its CPU was not retained and is not invented. The corrected wrapper and prior hashes are retained; the correction preceded held-out and changed no policy or selection rule. Headline counters describe the saved unique logical executions, not all infrastructure consumption.','',
'CPU scopes remain explicit. Stages 31–34 unique-case timings are descriptive except the stage-34 development selection. Conservative intermediate CPU ledgers include unallocated driver bookkeeping at the observation end; exact operation ledgers place horizon evaluations at their original anchors and compare every switch/expiry and times 0/64/128/256. Timing-based findings use only the declared repetitions. Memory accounting reconstructs retained proof objects, not process RSS. Serialization is excluded from algorithm CPU; prospective per-save CPU records exist from stage 33 onward, while earlier serialization CPU was not retained.']
(ROOT/'Synthesis.md').write_text('\n'.join(lines)+'\n')
# Append stage-specific limitations/results to the short stage reports.
limitations={31:'An unchanged packing can still require extensive repricing or repeated root splitting. Completing a selected hard tail is not fresh independent evidence.',32:'The zero-slope frontier has no renewal work to repay its positive preparation debt. Uniform recognition does not cover near-uniform inputs.',33:'Positive-factor normalization is invalid at zero or negative factors. A separate independently checked minimum recurrence supplies the missing negative-side proof.',34:'The two-class gate is fixed; general signed vectors usually reject it. Development-only timing selects the hypothesis, not a general held-out winner.',35:'Endpoint pruning reduces recurrence width but adds dominance and witness work and loses all-time validity; sparse slope width has no polynomial worst-case guarantee.'}
for s in range(31,36):
 p=ROOT/'stages'/str(s)/'Report.md';text=p.read_text();text+='\nDecisive limitation: '+limitations[s]+'\n\nEvery held-out comparison has 96 completed pairs. Complete-work-ledgers.json supplies every operation counter separately, payback times, benefited/harmed/tied counts, largest-beneficiary deletion, and the actual-vector structural ablation. Additional-accounting.json supplies cardinalities, reachable/unreachable entries, raw/retained states, envelope sizes, duplicate slopes, proof memory, phase lengths and source costs. No trajectory or construction caps occurred.\n';p.write_text(text)
 if s==35:p.write_text(p.read_text()+'\nPruning made 1,716,097 dominance comparisons while reducing held-out raw recurrence entries from 123,846 to 41,536. The predeclared repeated timing subsets show an unpruned advantage after charging all construction; no worst-case or general-policy claim follows.\n')
status={str(s):read(ROOT/'stages'/str(s)/'Complete.json') for s in range(31,36)};status['stage30_extension']=read(ROOT/'stage30-extension/Complete.json');save(ROOT/'Campaign-status.json',status)
save(ROOT/'Environment.json',dict(python=platform.python_version(),platform=platform.platform(),standard_library_only=True,modeled_time_end=256))
(ROOT/'README.md').write_text('''# Reproduce temporal-proof experiments 31–35

Python 3, standard library only. Read Synthesis.md, Mathematical-guarantees.md, Final-audit.json, Campaign-status.json and Resume-cursors.json first. Every fresh comparison has 96 completed held-out pairs. The old extension and repeated timing/evidence-recovery executions remain separate.

The campaign archive contains research/ plus the byte-identical original campaign archive under supplied/. To materialize the old evidence for checksum/extension inspections:

```sh
python3 -m zipfile -e supplied/Temporal-proof-five-experiment-campaign.zip campaign
```

Validate the new saved evidence without executing policies:

```sh
python3 research/code/reconcile.py 31 32 33 34 35
python3 research/code/diagnostics.py 31 32 33 34 35
python3 research/code/audit_inputs.py 31 32 33 34 35
python3 research/code/final_check.py
```

reconcile continues only missing bounded audit ranges, using saved policy results. Completed markers and immutable per-policy records are authoritative. No pending path or audit remains in this deliverable; Resume-cursors.json has empty lists. Do not rerun the old runner or replay script to extend stage 30.

To reproduce a new stage in a fresh empty directory:

```sh
python3 research/code/reproduce.py 35 --destination reproduced-stage35
```

Replace 35 with 31–34 as desired. Reproduction uses each stage's frozen code, original seed matrices and prospective caps. Stage 35 copies the sealed original stage-34 structural selection; stage-34 timing scores may vary on another machine. Timings, recovery repeats and unique cases are stored separately. The stage-34 wrapper/audit amendment retains its original source and prior hashes. The three regenerated evidence paths are disclosed in Evidence-recovery.json with original aggregate counters and additional repeated work; original summaries were not retroactively changed.

Independent certificate checks run per DP layer and bounded scalar-event batch. Full inputs, native solve/disposal costs, recurrence masks and predecessors, domain covers, lineage, pruning witnesses, line crossings, common-time ledgers and source hashes are retained. The archive's Manifest.json hashes all included research files; the nested original archive's expected SHA256 is bb2469796172764663afa5e081c2de5b42607c8b30bae8e1333c8cbe93428ad8.

Do not sum unlike operation counts, infer general runtime advantages from unique-case CPU, or extrapolate the pruned certificate past time 256. The model is explicit parametric integer knapsack, not new arithmetic.
''')
print('SYNTHESIS WRITTEN')
