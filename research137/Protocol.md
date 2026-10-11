# Frozen continuation: sparse cost updates and complete recovery costs

The predecessor is commit aff30ba1e7abef9958ec061bae9868e774d08381.
Experiments 133–136 and their schema limits remain unchanged. This is a new,
separately bounded domain: at most 256 nodes, 4,096 finite-capacity edges,
integer balances/bounds/flows, capacities at most 10,000, cost units of magnitude
at most 1,000,000 and a fixed positive objective denominator. The copied exact
producer is unchanged; the new checker changes only these explicit schema guards.

| Stage | Question | Contract |
|---|---|---|
| 137 | Can accepted cost changes avoid full model scans? | Owned admitted state; complete trusted cost delta; strict version/context/old-value checks; atomic commit; changed-edge residual signs; instrumented absence of hash/verify calls on a noncompacting accepted patch. |
| 138 | Do complete costs improve on larger graphs? | Six synthetic held-out networks, sparse/dense families with 8/24/64 suppliers and as many recipients; 24 updates with k in {1,4,8}; cold NetworkX + certificate completion, captured full recheck + cold fallback, buffered delta + cold fallback, fsync delta + cold fallback. Three repetitions per route/network. |
| 139 | What does bounded replay and restart require? | 4 KiB live serialized delta-record budget, six separate 64-byte binding controls. Full snapshot/recapture on budget overflow, retained raw log, independently audited replay, atomic terminal checkpoint, file and directory fsync on durable route, trusted terminal anchor for rollback detection. |
| 140 | What is outside the sparse interface? | Twelve invalid/failed transaction controls, ten recovery controls, caller ownership, omission limitation, separate capacity/balance/shortage recertification. A rejected old proof never establishes shortage. |

The two topology families contain 16/48/128 nodes and 32/96/256 or
64/576/4,096 edges. These are six mathematical base models, not 78 models.
Headline work comprises 72 route/network/repetition workers and six budget
controls, each with 25 observations. Separate transaction/recovery controls use
a designed four-supplier model. Tiny exhaustive enumeration uses a distinct
two-supplier model. Development uses six suppliers and a different seed; only
development/control models were solved before the freeze. Held-out streams are
deterministic generated inputs, not hidden human data or real service priorities.

Every worker has a 60-second wall guard and 512 MiB address-space guard. Native
certificate-completion routines keep the inherited 1,000-cycle/10,000-augmentation
guards. Timeouts/errors preserve partial output and stop the campaign. No cap is
raised during execution. Both primary and fresh-directory replica use a separately
installed pinned NetworkX 3.4.2 environment in this session; they share it with
each other. No API spend or external deployment is needed.

Cost units are exact integers divided by three. The same complete delta is read
by each route; no route derives it by scanning an external authoritative model.
NetworkX is the cold optimizer for every route; its answers receive independently
checked potentials from the inherited completion routine. The separate auditor
reconstructs original models, reimplements residual/cut arithmetic and NetworkX
encoding, and enumerates a tiny regression. It is separate code, not a second
independent optimizer, human review or a formal proof assistant.

The online output contract permits a previously admitted plan handle plus changed
cost/value evidence when the allocation stays fixed. Full allocation/proof export
and terminal checkpoint/replay costs are charged at the end of every session;
full-recheck/cold routes export proofs each observation. Consumers demanding a
complete stateless certificate or whole allocation every observation still incur
linear export costs. This is a deployment comparison under an explicit persistent
state contract, not a universal ranking of flow algorithms.

Complete fresh-process wall and kernel CPU/RSS include interpreter startup, input
loading, hashing frozen code, imports, proof completion, failed patches/fallback,
raw log writes and final Worker.json output. Phase timings are supplemental and
exclude final result serialization; complete process totals are the headline
costs. Log writes are flushed; only delta-fsync calls fsync on every record and
on the terminal atomic checkpoint/directory. A local fsync measurement is not
fault-injection or a guarantee about the storage hardware. Source installation
cost is recorded as outside these repeated sessions.

The budget bounds live serialized delta records, not the admitted base, total
Python heap or retained raw evidence file. Snapshotting replaces the live replay
base and costs O(V+E); the append-only experimental evidence log deliberately
retains all historical records. No bounded total-disk claim is made.

Replay hash chains detect accidental or unanchored inconsistent edits. They do
not authenticate an adversarial source. A valid earlier prefix is distinguishable
from the current state only with a trusted external terminal anchor. The test
explicitly demonstrates that omitting a real change from the trusted delta is
outside the interface's detection ability. Reading/hashing authoritative raw
models remains linear if that stronger contract is needed.

Replication compares all source/model/certificate/journal/checkpoint identities,
control outcomes, decisions, operation counts and bytes. Only measured wall/CPU/
RSS fields are excluded; both raw measurement sets remain retained. No statistical
significance, cryptographic security, new optimization theorem, fairness or
practical stakeholder validation is inferred from these synthetic tests.
