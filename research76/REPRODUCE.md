# Restore and reproduce experiments 76–85

The compact repository contains frozen sources, inputs/protocol, worker and mathematical summaries, split/storage/cache metrics and verification receipts. Complete worker traces, proof files, dependency snapshots and the pinned VIPR executable are in the archive identified by [Archive-storage.json](Archive-storage.json). [Drive-verification.json](Drive-verification.json) records completed download and member verification.

Download the `.tar.xz` through the intended connected Drive account or the receipt's observed URL. Check size and SHA-256 against Archive-storage.json, inspect archive paths and extract into an empty directory. It has a single `research76/` prefix. Archive-members.json records every other archived file's length and SHA-256. Storage, Drive and replication receipts stay separately in GitHub to avoid circular archive checksums.

Run from the restored directory:

```sh
python3 research76/tools/verify.py --full
python3 research76/tools/replicate.py /tmp/maths-76-85-fresh
```

Full verification checks the seal, all archived members, all 508 worker answers/signatures, integer observations, interval endpoints, dense/sparse work, stored B&B partition recurrence, lean B&B work by separate traversal replay, every integer split rule, every non-reused VIPR certificate regenerated from the native source proof, 82 accepted and 82 rejected external proofs, alias packing feasibility/value and continuous interval coverage. It repeats the 24 explicit cache rejections and four valid model hits.

Replication copies source/dependency snapshots into a previously absent directory, recreates identical inputs and runs every comparison. It compares every completed and capped status/logical signature, proof summary counts, and cache controls. Replication CPU data is validation only and is not pooled into the original timing findings.

For a compact checkout, `python3 research76/tools/verify.py` checks compact seal/summary consistency without missing detailed evidence. Full verification and execution require the restored dependencies and evidence.

Python 3.12 and standard-library exact fractions/integers were used. Source/dependencies include the unchanged stage35 native proof generator, research51 VIPR adapter, and the four disclosed experiment73 input controls. No old campaign archive is required after restoring this archive.

VIPR is official scipopt/vipr commit `30f2951d1e90e47afa821bdd1b12b82246656c42`. Source and Linux executable are archived. To rebuild on a compatible host with GMP development libraries:

```sh
g++ -O2 -std=c++14 research76/dependencies/vipr/viprchk.cpp -lgmpxx -lgmp -o research76/dependencies/vipr/viprchk
```

Keep assertions enabled. A rebuilt executable changes the archived binary checksum; record that environmental deviation separately rather than rewriting the original seal. This is not a production SCIP experiment. Lean point answers receive independent mathematical checking but carry no stored terminal-partition certificate for reuse.
