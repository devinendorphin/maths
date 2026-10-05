# Reproduce temporal-proof experiments 31–35

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
