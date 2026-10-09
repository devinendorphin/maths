# Verification, recovery and reruns

From the repository, run `PYTHONDONTWRITEBYTECODE=1 python3 research121/code/verify_publication.py`. This needs only the standard library. It verifies compact file identities, archive size/SHA-256, every archived member's size/hash and executable mode, and safe member names. It does not rerun experiments. Archive-storage.json and Archive-manifest.json identify the compressed evidence under `archives/`.

After verification, extract into a **new** directory outside the checkout with Python `tarfile.extractall(..., filter='data')`. The archive roots are `headline/`, `replication/`, `development/` and `reports/`. The first two contain original full results, proofs, source/dependency freezes, smaller executable dependencies, audit controls and measurement receipts. The development root preserves pre-freeze gates. Reports are post-run products. Large external SDK installations are deliberately absent.

Independent mathematical/proof replay in each run root is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_v3.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_selector.py
```

These require the external SDK identified by SDK.json, Python 3.12 and the retained inherited VIPR executable with GMP libraries. The auditor imports no producer/cache/policy implementation. It separately enumerates original feasible subsets, binds original proof/formula headers, checks all budget traces and queries, replays distinct proofs and constructs strictly false original objective bounds. `audit.py` has the recorded count error; `audit_v2.py` has the ineffective unused-tail VIPR mutation. Neither is the successful final audit. Do not silently replace those historical freezes or report that they passed.

Toolchain identities and recovery sources are explicit:

- CP 2024 official supplement commit `9b915e8e959e07ed2c096582c3dcb605ce0269e7`. The unchanged recovered ≤16-item adapted source and executable are included under each run's `external/cp2024/`. Original upstream, patch and adaptation receipts remain in the [original-300 archive](../research101-original-300/REPRODUCE.md).
- Official VeriPB v2 commit `5c485722194cbd9422d3eb169c8e621ca82aeb17`; source archive SHA-256 `6c44310b4284129dbecb49ac07180b857d61c21b4f35caaf8b5f046f37b5f0cc`. The deployment compiles only its unchanged optimized core; checking-rule modules remain unchanged Python. See [Checker-setup.json](../research111/recovery/Checker-setup.json), [setup_checker.py](../research111/recovery/setup_checker.py) and [Recovery-followup.md](../research111/Recovery-followup.md). This is not the historical fifteen-extension checker deployment. Python path/source/core hashes are in SDK.json.
- Exact SCIP v10.0.0 commit `0c80fdd8e91d7d9f23c0c7a55b68884209d5f27c` and SoPlex v8.0.0 commit `2207cfb274dbce5c2644911dd621438535733607`. Official VIPR completion commit `30f2951d1e90e47afa821bdd1b12b82246656c42`. Consult [earlier recovery instructions](../research111/REPRODUCE.md), Exact-setup.json, Completion-setup.json and their archived setup sources. Respect verified package signatures/TLS/source hashes; do not bypass missing prerequisites. The `vipr_fork` checker binary used by the explicit native dependency-change control comes from the prior repair source.

The retained `/workspace/maths-toolchains/` installation satisfies these SDK paths in this environment. This campaign does not measure installation or claim a clean independent SDK rebuild. Compiler/path/platform changes may change binary identities. In another environment, preserve historical expected hashes and record a new deployment separately; a new checker can validate mathematical proofs without making it the original timing deployment.

To rerun the scientific campaign with the same installation, create a new run directory from the source/input/dependency files in Freeze.json plus the three correction/supplement freezes and their source files. Preserve executable bits. For a new full fit, run `code/campaign.py train`, which writes a policy freeze before evaluation, then `code/campaign.py run`. For the published fresh replication, instead copy the original Policy.json, Policy-freeze.json, Training.json, Training-execution.json and only the 28 training proof files listed in replication/Replication-start.json. Training/policy evidence is shared, explicitly not counted as newly executed; no held-out/control outputs or proofs are copied.

Then execute:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 code/campaign.py run
PYTHONDONTWRITEBYTECODE=1 python3 code/cap_repair.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_v3.py
PYTHONDONTWRITEBYTECODE=1 timeout 60s python3 code/policy_repair.py
PYTHONDONTWRITEBYTECODE=1 python3 code/audit_selector.py
```

Comparisons run serially to avoid competing checker workloads. Each main directory is bounded to 900 wall seconds and 256 MiB of evidence, with separate per-producer/checker caps and proof-byte limits in Protocol.json. The selector repair has a 60-second outer cap. Exact SCIP completion work and fork child CPU are fully charged. Separate memory workers require Linux `/proc/*/status`; sampling remains partial for short native children.

Use `code/replicate_v4.py FIRST SECOND OUT.json` to compare **all** logical records and raw/final proof identities across main and supplement results. It excludes only `measurements`, explaining why; all timing/memory differences are retained by `code/summarize.py FIRST SECOND OUT.json`. The latter is post-run descriptive analysis, not policy fitting. The expected comparison is 451 main + six cap + sixty selector records = 517, not 551. Shared training contributes 72 separate original records. Preserve any meaningful disagreement rather than editing expected fields to hide it.
