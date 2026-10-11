# Closing the recovery-storage question: experiments 141–144

The predecessor is the verified 137–140 tree at 103457dbc99f79f4c01d512017cc3d53c392a903.
Its files, measurements and source freeze remain untouched. This continuation uses
the same network schema and pinned NetworkX 3.4.2 optimizer, with fresh generated
seeds and separately inspected development/control inputs.

| Stage | Frozen question | Evidence |
|---|---|---|
| 141 | Can immutable topology/bounds/balances be stored once, with exact cost-vector images and proof-change records? | Full and compact formats share solve/admission logic, concrete model binding, version/hash-chain and terminal anchor. Exact proof changes receive full admission; compact decoding reconstructs the original concrete model. |
| 142 | What are the complete write, restart and active-disk costs under fixed budgets? | Six 16/48/128-node networks with 32–4,096 edges, 48 updates, policies (1 KiB,8 queries), (8 KiB,8), (64 KiB,24), two repetitions of both formats. Active footprint includes the immutable base, snapshot, journal, anchor and temporary snapshot during replacement. |
| 143 | Does compression preserve rejection and recovery? | Fourteen designed refusal controls, including mathematically false proof changes after rehashing, trusted-anchor rollback and a valid-prefix limitation. Every checkpoint and every historical raw event is replayed. |
| 144 | What survives fresh-directory replication, and can the small question be closed? | 72 workers / 3,528 observations per directory. All meaningful fields, bytes and identities compare; both timing/resource sets remain visible. Larger inquiry proceeds after this bounded audit, without treating finite results as a general storage theorem. |

All six headline base networks are new seeds, with fixed supplies, capacities and
eligibility. Cost updates have k in {1,4,8}. The separate development network has
six suppliers; the control network has four. These are synthetic cases, not real
stakeholder policies. This phase does not repeat the old measurements under a new
experiment number and does not extend its cost-only schema to changing needs.

The online contract is the predecessor's persistent admitted plan handle plus
complete trusted cost deltas. Failed residual tests trigger a charged cold
NetworkX solve, exact potential completion and full certificate admission. The
full format records the full changed model/proof at recertification and in each
snapshot. Compact format records changed flow/potential entries on recertification
and a full cost vector/proof in each snapshot, referencing one admitted base.
Neither format changes or relaxes the mathematical checker.

Checkpoint on live serialized journal overflow or cadence; oversized events go
directly into a checked image. Atomic snapshot replacement and journal truncation
are charged. A separate historical evidence file retains every event and image;
it is excluded from the active-recovery budget and counted separately. The live
journal budget is not a bound on whole active disk or Python heap. Real active
disk/temporary-image footprints are measured separately. Complete fresh-session
wall/kernel CPU/RSS include startup, source hashing, imports, solver/proof work,
failed probes, all writes, checkpoint recovery and result reporting.

Both formats flush writes but do not request fsync. No power-loss correctness,
atomic multi-file transaction, hostile source authentication or externally hosted
anchor service is claimed. Recovery logically binds an externally supplied
terminal anchor; storing a co-located anchor.json alone cannot protect against
an attacker rewriting every file or rolling back an entire directory. The final
process has a trusted in-memory anchor and the audit has frozen original inputs.

Workers have 90-second/512 MiB guards. The copied producer retains its prior
guards. Failed/timed-out workers stop the campaign and are retained. Primary and
replica share the pinned environment; they are separate empty directories, not
independent installations. The audit reconstructs inputs and residual arithmetic
separately and re-encodes NetworkX reference models. No second independent
optimizer, human review or formal proof assistant is implied.

This is a comparison of complete storage/recovery formats under stated assurance,
not a new flow algorithm, a universal compression bound or a novelty-priority
claim. It finishes a bounded question so the larger changing-allocation inquiry
can start with measured costs rather than an untested storage promise.
