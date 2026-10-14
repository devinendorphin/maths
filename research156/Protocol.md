# Frozen accounting contract, 156–159

156 establishes the interval contract and adversarial controls; 157 compares
the observed and unobserved harness; 158 accounts for query and full-worker costs;
159 independently checks exact answers, native state, interval closure and replication.
This is measurement of the known 152–155 workload, not a fresh held-out speed test.
Inputs.json is byte-identical to 152. The unchanged Python engine/checker/transaction,
public C++ adapter and exact compiled adapter bytes are retained in vendor/ and
bridge.so. Runtime wrappers instrument named call boundaries; no algorithm changes.

Two fresh directories each execute 144 fresh processes: six networks, six routes,
two repetitions and two observer modes. Each process has 49 certified queries.
Observer order alternates by network, route and repetition. One thread; 2 GiB
address-space limit; 90-second process guard; failures retained and not silently
rerun. All full proof/native/witness records, journal bytes and process outputs
are preserved. Every mathematical query and recorded state must be identical
across observer modes and repetitions; native addresses are not published.
Disjoint development uses the six smaller existing development networks, both
modes, all routes and one repetition: 72 excluded workers and 3,528 observations.

The accounted mode records consecutive exclusive wall-clock intervals, starting
after the initial import of time and ending after Worker.json has been encoded
and written. Source-level phase boundaries are declared in meter.py and
account_worker.py. Nested phases replace their parent's category; child time
is never counted twice. Each interval endpoint is the next interval's start.
All worker intervals must sum exactly to end minus origin, and their intersections
with each query's enclosing boundaries must sum exactly to that query duration.
This exact partition is an accounting invariant, not evidence that a clock is
perfect or that categorization makes measurement causally neutral.

Categories separately retain imports, provenance hashing, input, engine setup,
transaction work/copy, validation, model digest, canonical encoding, native
marshalling, native C API calls, Python/native snapshots, feasible-witness
production/admission, potential/certificate production, certificate admission,
repair, query copies/control, record preparation/encoding/writing/ownership,
cleanup and final output. query.control and session.bookkeeping explicitly
retain branch/counter/local control and scope machinery between named calls;
they are measured broad categories, never silently assigned to proof or solver.
native.solve_with_witness includes the C++ witness-validation loop and Solve;
it is not a measurement of a bare optimization kernel. native.simple includes
construction, solving and native result conversion. Python snapshot conversion
is separate from the snapshot C API call. Transaction.apply retains its local
patch loops; transaction.copy, validation, digest and encode are nested separately.

The observer category records sampled enter/leave bookkeeping intervals. Clock
reads, context-manager/wrapper entry and trailing append instructions can land
in adjacent intervals; this category is not the complete causal observer cost.
Ten thousand paired clock reads and matched observer-off sessions quantify
resolution/measurement footprint. No calibration or observer time is subtracted
to invent unobserved component timings. Report observer-on/off totals and ratios;
two repetitions cannot support significance claims for small gaps.

The initial 144-worker primary execution is rejected because the independent
audit found two incomplete visible raw journals, despite complete Worker.json
records and successful worker exits. Its full root and the original source and
development evidence are retained, with the old freeze context. Cause remains
unestablished. No raw journal is reconstructed or admitted after the fact.
The repaired recording path streams each query into an anonymous TemporaryFile,
then verifies every byte/record and atomically publishes the closed complete
journal. Publication, readback and ownership checks are charged as record.publish.
Worker/Accounting JSON also use complete temporary writes and rename with readback.
Both development and both headline directories rerun under a new source freeze.
The parent checks journal custody after every worker. This changes the recording
implementation and its measured costs in both observer modes, not the algorithms
or mathematical queries; it does not establish crash/power-loss durability.

Unobserved mode does not install the call wrappers or interval ledger. The same
worker-level phase contexts, enclosing query timestamps and legacy engine timers
remain, so this is a matched harness comparison, not a claim of zero instrumentation.
The legacy 152 phase fields are retained as a reference, not added to the ledger.

Accounting.json cannot recursively record its own final serialization. The parent
measures launch through wait4 completion, including receipt writing, interpreter
bootstrap before origin, shutdown, scheduling and up to 1 ms polling delay.
Parent time minus ledger time is explicitly process_envelope_gap, not assigned
to startup alone. Parent counters and both endpoints are preserved. No fsync or
power-loss durability is claimed. Every phase cost includes required proof and
evidence work; compact records and sparse native patches are future experiments.

Freeze source, protocol, byte-identical inputs, development audit and controls
before headline runs. Verify native library hashes actually mapped by each worker.
An independent arithmetic checker admits flow/cut proofs, compares model answers
with NetworkX and SimpleMinCostFlow, replays native state transitions and rejects
12 corrupted ledgers. Publish only after full custody, logical replication and
clean downloaded-source checks. Existing scientific artifacts remain unchanged.
