# Restore and reproduce experiments 66–75

The compact repository contains code, frozen inputs/protocol, worker summaries and verification receipts. Complete worker traces, proof files, dependency snapshots and the pinned VIPR executable are in the archive identified by [Archive-storage.json](Archive-storage.json). Read [Drive-verification.json](Drive-verification.json) for the completed download and member verification.

Download the `.tar.xz` through the connected Drive account or the receipt's observed Drive URL. Compare its size and SHA-256 with Archive-storage.json, and inspect the archive paths before extracting into an empty directory. It has a single `research66/` prefix. The archive manifest records every other member's size and SHA-256; storage, Drive and replication receipts remain separately in GitHub to avoid self-referential hashes.

Run from the restored directory:

```sh
python3 research66/tools/verify.py --full
python3 research66/tools/replicate.py /tmp/maths-66-75-fresh
```

The first command verifies the seal, member hashes, all 468 workers, every integer observation/interval endpoint, exact work counters, matched scaled answers, continuous real interval coverage, regenerated point proofs, 33 accepted VIPR proofs and 33 rejected false bounds. The second command copies frozen sources/dependencies into a previously absent directory, recreates the inputs and reruns all comparisons. It compares every status and logical worker signature plus proof summary counts; timings are separate validation and are not pooled into the original batch.

For a compact checkout, `python3 research66/tools/verify.py` checks the compact seal and summary consistency without requesting missing detailed evidence. Full verification requires restoring the archive.

Python 3.12, standard-library exact fractions and integer arithmetic were used. VIPR is pinned to official scipopt/vipr commit `30f2951d1e90e47afa821bdd1b12b82246656c42`; source and the Linux executable are archived. Rebuild on a compatible host with GMP development libraries if needed, from the archived `viprchk.cpp` and `CMakeConfig.hpp`:

```sh
g++ -O2 -std=c++14 research66/dependencies/vipr/viprchk.cpp -lgmpxx -lgmp -o research66/dependencies/vipr/viprchk
```

Keep assertions enabled. A rebuilt executable will not match the archived binary's SHA-256; record that environmental deviation separately rather than rewriting the original freeze. SCIP/PySCIPOpt is not part of this batch. The stage35 native source and research51 VIPR adapter are included unchanged as dependencies. No older campaign archive is needed to execute this restored batch.
