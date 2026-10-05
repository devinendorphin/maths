# Recovery and replication

The compact repository contains source, input and result summaries. [Archive-storage.json](Archive-storage.json) records the complete Drive archive, its byte count and SHA-256. The archive contains every worker proof, the original run log, VIPR certificates and checker outputs, dependency sources, and the pinned VIPR source/header/binary. No earlier archive needs to be rebuilt to inspect this batch's evidence.

1. Download the archive from the observed Drive URL in `Archive-storage.json` and verify its SHA-256.
2. Extract it into a separate directory. It has a `research51/` top-level folder.
3. Run `python3 research51/tools/verify_archive.py` to check every declared member. Add `--full` to independently re-audit all 422 mathematical workers. This requires Python 3.12-compatible standard-library behavior; the mathematical audits do not need a new solver installation.
4. Run `python3 research51/tools/verify_compact.py` to check the compact source seal, corrected repeat signatures and summary receipts.

`Archive-members.json` records member hashes and lengths; the archive's own hash is stored outside it to avoid a circular checksum. The Drive receipt, publication notes and later download-verification receipt are also outside the archive. Stored native temporary-store disposal checks remain in each worker record.

## Fresh replication

For the original Linux/x86_64/GMP environment, the archived executable can be used. On another platform, rebuild VIPR from the included unchanged source:

```sh
g++ -O2 -std=c++14 research51/dependencies/vipr/viprchk.cpp -lgmpxx -lgmp -o research51/dependencies/vipr/viprchk
```

The header records version 1.1; certificates use supported format 1.0. Compilation preserves the assertion-enabled build used here. The archived executable is a platform-specific convenience, not a portable binary guarantee.

Create a new output directory with the helper; do not overwrite the completed campaign:

```sh
python3 research51/tools/replicate.py /workspace/maths-51-55-replication
```

The helper copies pinned dependencies into that isolated directory, creates a new capability/source seal, verifies that the input list matches this campaign, and runs the frozen algorithms with the selected VIPR binary. New machine timings are separate evidence. `--vipr /absolute/path/to/viprchk` selects another build with its source and generated header beside it.

The original campaign has a post-run fingerprint bug: elapsed `algorithm_wall` entered older-policy repeat hashes. The original run stopped after all mathematical work had completed. The helper uses the preserved `tools/finalize.py` for this specific failure; it does not accept other errors. Finalization compares clock-free complete logical results and requires all 422 workers, VIPR interval evidence and native fixture controls. Sources and original timings are retained unchanged.

The SCIP production baseline was not available. Installing it for a future comparison would constitute a separate experiment and requires checking exact/reoptimization support rather than claiming this archive contains that benchmark.
