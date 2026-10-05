# Recovery, verification and fresh replication

The compact repository contains code, frozen inputs, protocols, summaries and receipts. [Archive-storage.json](Archive-storage.json) records the observed Drive archive URL, length and SHA-256. Complete worker evidence, VIPR files, checker outputs, run logs and pinned dependency/checker sources are in that archive. No preceding archive needs to be reconstructed for this batch.

Download the archive, verify its SHA-256, and extract it into a separate directory. It has a `research56/` top-level folder. `Archive-members.json` records every member's length and SHA-256. The archive's own checksum and later publication/download/replication receipts stay outside it to avoid circular checksums.

Run:

```sh
python3 research56/tools/verify.py
python3 research56/tools/verify.py --full
```

The compact check verifies source/summary seals, complete logical repeats and the presence of a complete method for every input. The full check additionally verifies all archived members and dependency hashes, independently re-audits all 420 workers, and executes VIPR on all 24 valid and 24 invalid certificates. Audits of capped runs validate only completed query answers and inactive partial records; they do not certify a missing trajectory.

## Fresh replication

The included VIPR executable targets the original Linux/x86_64/GMP environment. On another platform, rebuild it from the unchanged included source:

```sh
g++ -O2 -std=c++14 research56/dependencies/vipr/viprchk.cpp -lgmpxx -lgmp -o research56/dependencies/vipr/viprchk
```

The generated header sets supported version 1.1; exported certificates use format 1.0. This assertion-enabled build matches the configuration used in the findings. A new binary may have different bytes; fresh replication seals its own dependencies rather than changing the original receipt.

Create a new, empty output directory:

```sh
python3 research56/tools/replicate.py /workspace/maths-56-65-replication
```

The helper copies source and dependencies, creates a fresh capability/source seal, verifies the same inputs, runs the frozen ten comparisons, and compares complete logical worker signatures. Timings from the fresh run are separate validation evidence, not added to original reported medians. All original outputs remain intact.

The main mathematical execution limit is 900 seconds; individual oracles also have declared state, node, transition and CPU caps. Physical time caps can censor runs on a substantially slower environment. Do not compare an incomplete method's short runtime with a complete method as a speedup.

SCIP/PySCIPOpt was absent and the required HTTP proxy refused connection. The archived search-reuse code is a controlled exact reference implementation. A production SCIP benchmark and exact/reoptimization compatibility check would be a separate experiment.
