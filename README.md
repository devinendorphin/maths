# Maths experiments

This repository keeps a compact working collection of the temporal-proof experiments. Complete evidence is preserved in [verified Google Drive archives](https://drive.google.com/drive/folders/1xbG-aDtuDe8cRzVX_jyGT7JF5bv6CbqJ).

The latest batch is [experiments 46–50](research46/Synthesis.md), following the [frozen roadmap](research46/Roadmap.md): 110 input records and 261,852 independently checked integer-time answers. Wider gates helped on one held set, but repeated proof rebuilding did not repay its cost; all 54 later forced failures recovered safely. Detailed evidence is in one verified 15.5 MB [Drive archive](https://drive.google.com/file/d/1JxXvlbXUz6YikNEj-xAUHKCD-uLYdBy3/view?usp=drivesdk).

The preceding batch is [experiments 41–45](research41/Synthesis.md): 105 inputs, five completed experiments, and 121,746 independently checked integer-time answers. Detailed evidence occupies one verified 16 MB [Drive archive](https://drive.google.com/file/d/1Ux66N1gnn2gcUCYrImgbtTGcDR_Tecy4/view).

For the preceding batch, start with the [36–40 synthesis](research36-rebuild/Synthesis.md), [comparison with the retained prior reports](research36-rebuild/Comparison.md), and [interpretation](analyses/experiments-36-40-rebuild/Interpretation.md). For the full proof records, read [storage and recovery instructions](STORAGE.md).

The recovered 31–35 campaign is the baseline. The rebuilt 36–40 campaign completed 832 unique trajectories, 3,328 headline policy paths, 1,152 timing workers and 216 selector-tuning workers. All headline observation windows completed; 40 capped frontier constructions remain incomplete. [Final audit](research36-rebuild/Final-audit.json).

The rebuilt 36–40 results broadly agree with the retained prior summaries: indexed pruning reduced proof work and avoided the declared frontier caps, while rolling rebuilds reduced proof size but added CPU work on the repeated subsets. Some aggregates and the timing-selected threshold differ. The old 36–40 detailed archive is still unavailable; its surviving reports do not establish proof-by-proof agreement. These are finite experimental results.

## Working files

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

