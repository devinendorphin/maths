# Recovery and fresh replication

The compact checkout omits `evidence/` and `dependencies/`; the complete archive contains both. `Archive-storage.json` identifies the complete repository archive and its size/SHA-256. This small archive is a fallback after two stalled Drive uploads; no Drive verification is claimed. Download it to a new directory, check that SHA-256, and inspect the tar member list before extracting. The archive has only regular files beneath `research86/`; do not overwrite completed records.

```sh
python3 research86/tools/verify.py
python3 research86/tools/verify.py --full
python3 research86/tools/replicate.py /tmp/maths86-fresh
```

The first command checks compact seals and present member hashes. The second needs the complete archive, independently re-audits all mathematical workers, regenerates each original-problem proof from its native certificate, and executes the frozen external checker on every unique valid proof and a temporary lowered-bound control. Independent checks are outside the algorithm timings. The third copies frozen sources/dependencies into a nonexistent directory, freezes deterministic inputs, runs every worker from fresh algorithm/proof state, and compares statuses and logical signatures with the original. Clock values are excluded from signatures; original timings are never overwritten or pooled.

Use Linux with Python 3 and the executable checker snapshot. Its pinned source/build material is in `dependencies/vipr/`; if rebuilding for a different platform, preserve the original binary and explain the new checker identity. Ordinary source/audit/connector Python and VIPR are not claimed formally verified.

Algorithm code, input generation and mathematical contracts were frozen before the original headline run. The post-run verification, replication and reporting tools do not select inputs or modify the frozen source. `Archive-members.json` lists all archived member hashes except its own hash to avoid circularity. Storage/readback receipts are outside the archive they describe. The original novelty note is stored in `research-notes/`; an archive snapshot supports offline reading.

The lost original 36–40 detailed archive is still unavailable. This archive is a new 86–95 campaign, not a reconstruction of that run or the original inspiration's unpublished mathematics.
