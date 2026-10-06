# Maths experiments

This repository keeps a compact working collection of the temporal-proof experiments. Complete evidence is preserved in [verified Google Drive archives](https://drive.google.com/drive/folders/1xbG-aDtuDe8cRzVX_jyGT7JF5bv6CbqJ).

The latest batch is [experiments 76–85](research76/Synthesis.md): ten bounded comparisons, 58 input records and 508 audited workers. 461 trajectories completed; 47 runs stopped at declared limits, including ten deliberately all-failed controls. Every input has complete answers from at least one method. Lean B&B removed terminal-storage limits; a fixed solver portfolio completed every fresh transfer input. Complete evidence is in a verified 2.5 MB [Drive archive](https://drive.google.com/file/d/1STxr-EpbCkH9c-w1ZudidKEDmYscOFzG/view?usp=drivesdk).

The preceding batch is [experiments 66–75](research66/Synthesis.md): ten bounded comparisons, 58 input records and 468 audited workers. 455 trajectories completed; 13 method runs reached declared storage limits, and every input has complete answers from at least one method. A simpler solver gate and crossing-guided integer queries helped selected cases; unrestricted partition reuse remained costly. Complete evidence is in a verified 1.7 MB [Drive archive](https://drive.google.com/file/d/1pgRigD7Sanz2mS6oSSYcTrmhmKApqdzy/view?usp=drivesdk).

The earlier batch is [experiments 56–65](research56/Synthesis.md): ten completed comparisons, 70 input records and 420 audited workers. 402 trajectories completed; 18 method runs reached declared allocation limits, and every input has complete answers from at least one method. Normalizing weights and choosing the exact oracle mattered; integer-only querying and accumulated search partitions did not consistently help. Complete evidence is in a verified 1.1 MB [Drive archive](https://drive.google.com/file/d/1-GmLjCjz8VMGC4KZc6lBjU5M8NPjW8Hl/view?usp=drivesdk).

The earlier batch is [experiments 51–55](research51/Synthesis.md): 422 audited workers and 21,942 integer-observation checks. An established exact parametric baseline reduced repeated solves, and cached certificate scheduling reduced horizon work. The production SCIP comparison remains outstanding. Complete evidence and pinned dependencies are in a verified 1.9 MB [Drive archive](https://drive.google.com/file/d/17iUMVbYRiHrfIgIpQ3Oj7DBgyM-ufQfi/view?usp=drivesdk).

The earlier batch is [experiments 46–50](research46/Synthesis.md), following the [frozen roadmap](research46/Roadmap.md): 110 input records and 261,852 independently checked integer-time answers. Wider gates helped on one held set, but repeated proof rebuilding did not repay its cost; all 54 later forced failures recovered safely. Detailed evidence is in one verified 15.5 MB [Drive archive](https://drive.google.com/file/d/1JxXvlbXUz6YikNEj-xAUHKCD-uLYdBy3/view?usp=drivesdk).

The earlier batch is [experiments 41–45](research41/Synthesis.md): 105 inputs, five completed experiments, and 121,746 independently checked integer-time answers. Detailed evidence occupies one verified 16 MB [Drive archive](https://drive.google.com/file/d/1Ux66N1gnn2gcUCYrImgbtTGcDR_Tecy4/view).

For the preceding batch, start with the [36–40 synthesis](research36-rebuild/Synthesis.md), [comparison with the retained prior reports](research36-rebuild/Comparison.md), and [interpretation](analyses/experiments-36-40-rebuild/Interpretation.md). For the full proof records, read [storage and recovery instructions](STORAGE.md).

The recovered 31–35 campaign is the baseline. The rebuilt 36–40 campaign completed 832 unique trajectories, 3,328 headline policy paths, 1,152 timing workers and 216 selector-tuning workers. All headline observation windows completed; 40 capped frontier constructions remain incomplete. [Final audit](research36-rebuild/Final-audit.json).

The rebuilt 36–40 results broadly agree with the retained prior summaries: indexed pruning reduced proof work and avoided the declared frontier caps, while rolling rebuilds reduced proof size but added CPU work on the repeated subsets. Some aggregates and the timing-selected threshold differ. The old 36–40 detailed archive is still unavailable; its surviving reports do not establish proof-by-proof agreement. These are finite experimental results.

A [literature review dated 5 October 2026](research-notes/Literature-review-2026-10-05.md) identifies established parametric methods, reoptimization and proof-checking tools that should guide the next comparisons. The [original proposal for experiments 51–55](research-notes/Roadmap-after-literature.md) is followed by the completed bounded comparisons linked above.

## Working files

- `research76/`: frozen experiments 76–85, lean search, query-depth controls, capped solver fallback and scoped proof-cache checks. [Findings](research76/Synthesis.md).
- `research66/`: frozen experiments 66–75, exact solver/query comparisons, resource-limit findings and verified recovery. [Findings](research66/Synthesis.md).
- `research56/`: frozen experiments 56–65, exact comparisons, resource-limit results and recovery instructions. [Findings](research56/Synthesis.md).
- `research51/`: literature-informed comparisons, frozen inputs, exact audits and recovery instructions. [Findings](research51/Synthesis.md).
- `research-notes/`: sourced literature review and proposed future comparisons.
- `research46/`: roadmap, frozen inputs and audited experiments 46–50. [Findings](research46/Synthesis.md) and [recovery receipt](research46/Archive-storage.json).
- `research41/`: new bounded experiments, frozen inputs, reproducible code and compact results. [Recovery receipt](research41/Archive-storage.json).
- `research36-rebuild/`: unchanged mathematical sources, frozen stage snapshots, protocols, inputs and reports.
- `campaigns/experiments-31-35/`: selected original sources and readable reports; restore the baseline archive before executing the campaign.
- `analyses/experiments-36-40-rebuild/`: compact summaries, retrospective diagnoses and the separately counted supplemental fixture.
- `results/experiments-36-40/`: the three retained reports of the lost prior campaign.
- [Archive-storage.json](Archive-storage.json): Drive locations and every recovery-piece checksum.
- [Drive-archive-verification.json](Drive-archive-verification.json): completed download/reassembly/member verification.
- [REPRODUCE-36-40.md](REPRODUCE-36-40.md): recovery and fresh-run instructions.

The [423 KB review kit](analyses/experiments-36-40-rebuild/Maths-36-40-review-kit.tar.xz) is convenient for reading code, inputs and findings. It excludes the detailed proof and checkpoint history; keep access to the complete archives.

For a small checkout that omits older Git versions:

```sh
git clone --depth 1 https://github.com/devinendorphin/maths.git
cd maths
python3 scripts/verify_compact.py
```

Git history starts from the verified compact collection. Complete experiment evidence remains in the checked Drive archives. Read [STORAGE.md](STORAGE.md) before accessing detailed evidence or reproducing the experiments.
