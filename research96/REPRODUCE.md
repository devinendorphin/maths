# Reproduce experiments 96–100

The compact checkout contains reports and own source. Restore the full evidence/dependency archive before executing the campaign. Keep the original records separate from a fresh run.

1. Read `Archive-storage.json` beside this file. Obtain `archives/experiments-96-100-complete.tar.xz` at the recorded repository commit and check its SHA-256 and length.
2. Extract into an empty working directory. The archive has a `research96/` root. Check every file listed in `research96/Archive-members.json` against its recorded length and SHA-256. The member manifest itself is covered by the archive digest, not by a self-referential entry.
3. Use Python 3.12 or newer and a platform able to execute the included x86-64 VIPR binary with its GMP/C++ runtime libraries. Its frozen source is included. If rebuilding it, record the new binary identity and treat that as a new dependency version.
4. Lean 4.24.0 is a separate dependency. The official release URL, archive digest and recorded binary identity are in `Lean-setup.json`. Install that release outside the repo and verify its digest. The session setup script is tied to `/workspace`; on a different host, adapt its destination and the recorded `binary` path while preserving the pinned release. Such deployment-path changes are outside the frozen source snapshot and must be disclosed.
5. For a fresh replication, copy only files named by `Freeze.json` and the freeze manifest into another empty directory. Do not overwrite retained `Results.json`, `Original-run.log` or the evidence folder. Make the Lean binary available at the recorded path or explicitly document the path override in your replication receipt. The campaign checks all frozen file hashes before starting.

From the fresh copy:

```sh
python3 code/campaign.py
python3 code/audit.py
```

The campaign compiles the formal theorem and independent contract, then runs the bounded comparisons. It writes `Formal-check.json`, `Results.json`, `Execution.json` and evidence. The auditor independently enumerates small feasible subsets, validates proof coverage and partial bounds, and reruns all distinct VIPR proofs plus weakened-bound controls.

For direct mathematical checking, from `formal/` with the pinned Lean binary on `PATH`:

```sh
lean -o Endpoint.olean Endpoint.lean
LEAN_PATH=. lean Spec.lean
```

No Mathlib is needed. Successful proofs report only the declared standard Lean axioms; no `sorryAx` is accepted. `RejectedStatement.lean` is deliberately invalid and must not be treated as a failed headline proof or imported into the successful library. No Comparator run is claimed.

`Freeze.json` describes the source/input snapshot before the headline run; its `headline_started: false` records that moment, not the later completion status. Development smoke checks and corrections are described separately. Full raw results are canonical; `evidence/Results-progress.json` is only a duplicate evolving output and is excluded from the archive. Python caches and reproducible Lean `.olean` build files are also excluded.

The fresh replication receipt excludes timing fields and checksum seals containing source timing diagnostics when comparing logical results. It does not exclude objective values, masks, proof bytes, statuses or dependency identities. Timing is compared separately in `Replication-timing.json`.

The outer archive storage/verification receipts are repository sidecars created after packaging. They are not inside the archive, because an archive cannot contain its own final checksum. This archive preserves complete experiment records and the frozen prior solver/checker sources; it does not bundle the 459-MB Lean distribution or the entire OpenAI mathematics collection.
