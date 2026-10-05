# Experiment 33

# Continue temporal-proof research: experiments 31–35 in one continuous run

## Launch prompt

Follow this handoff using the attached `Temporal-proof-five-experiment-campaign.zip`. Inspect and verify the checkpoint, then implement, verify, execute, audit and save experiments 31–35 in one continuous run. Begin with the explicitly authorized resource extension of the five capped stage-30 paths; preserve completed cases and phases. Use fresh development and held-out data for every new experiment. Do not stop after planning or after experiment 31, and do not require another “Continue” between experiments. Negative results are completed experiments; capped computations remain incomplete and must be labeled. Save a reproducible archive, a concise synthesis and precise resume cursors for anything unfinished.

## What is attached and how to start

The required checkpoint is `Temporal-proof-five-experiment-campaign.zip`, SHA256:

`bb2469796172764663afa5e081c2de5b42607c8b30bae8e1333c8cbe93428ad8`

It contains 1,305 files, including the complete stage-26–30 source/evidence, the unchanged supplied stage-25 checkpoint, and the previous handoff. Its byte length is 42,064,456. Unpack it into your own workspace. Do not assume any previous instance's absolute paths exist. Preserve all supplied files unchanged; put new work in separate directories.

Read these relative paths before implementation:

- `Synthesis.md`, `README.md`, `Campaign-status.json`, `Checkpoint-verification.json`, `Final-audit.json`, `Branch-choice-audit.json`.
- Every stage's `Protocol.md`, `Frozen.json`, `Report.md`, development/held summaries and resource logs.
- `stages/29/Freeze-amendment.json` and its retained previous wrapper.
- `stages/30/Freeze-amendment.json`, `Audit-amendment-verification.json`, `Interrupted-attempt.json`, `Resume-cursors.json`, `Paired-completed-accounting.json`, and both `Resource-log-reconciled.json` files.
- The actual APIs in `code/engine.py`, `code/source_clean.py`, `code/campaign.py`, `code/horizon.py`, `code/renewal.py`, `code/refine.py`, `code/audit_new.py`, and the saved-trace validators.

Verify the archive checksum, every `Manifest.json` entry, and each stage's current frozen hashes. The amended stage-29/30 hashes are authoritative for their final implementations; verify the retained prior source against the amendment's prior hash separately. Do not treat an intentionally superseded initial freeze as unexplained corruption. Do not rerun any completed stage or campaign. Read-only audits of saved evidence are permitted, but avoid redundant full audits when already-verified evidence suffices.

Do not launch `replay.py` or the old top-level campaign runner as a way to continue capped trajectories. Replay restarts campaigns; the old runner skips stage markers and has no cursor-based resource-extension entry point. Implement a dedicated continuation driver.

This handoff requests research execution, not merely suggestions, pseudocode or a proposed plan. Work through all five stages autonomously within the declared bounds. If a hard environment limit intervenes, preserve completed work and an exact cursor, state the interruption, and do not claim completion.

## Current model and guarantees to preserve

There are positive integer weights `w_i`, integer capacity `c`, signed integer intercept profits `p_i`, and signed integer slopes `v_i`. Modeled integer time is explicit:

`q_i(t) = p_i + t v_i`, for `t >= 0`.

The empty packing is feasible. For a feasible item mask M, define

`P_M = sum(p_i for i in M)`, `S_M = sum(v_i for i in M)`,

so `V_M(t) = P_M + t S_M`. Ties count as optimal. Retain the incumbent until it is strictly beaten. Modeled time, program CPU, audit CPU and counted proof work are different quantities.

The existing scalar-price cell is `(fixed, free, residual, a, b, num)`, with `a >= 0`, `b > 0`, and `residual = c - weight(fixed)`. At integer profits q,

`Z = b profit_q(fixed) + a residual + sum_free max(0, b q_i - a w_i)`.

The rational upper bound is `Z/b`. A complete disjoint feasible cover certifies incumbent M if every cell satisfies `floor(Z/b) <= V_M(q)`. A price failure is not proof of suboptimality. A feasible improving witness is. The minimum scalar-price bound is attained at zero or a positive free-item profit/weight ratio, evaluated exactly. Do not confuse this fractional relaxation with the integer optimum.

The existing repair kernel reprices old cells and splits failing cells on the fractional relaxed item. It omits infeasible include branches, has deterministic ratio ties, and never consults audit DP or exhaustive enumeration to select a branch. Preserve this kernel for baseline maintenance/rebuilding and for all fallbacks. Charge successful and failed probes, repairs and loss detection. Reuse a successful probe's priced cell instead of repricing it.

Exact positive-factor normalization for `v=p` is already established. For `g(t)=1+t>0`, scaling each initial price gives `B(t)=g(t)B(0)`. Every feasible value lies on the g-times-integer lattice, so `floor(B(t)/g(t)) <= V_M(p)` certifies the same packing for all integer t>=0. Recognition inspects vectors, not generator labels. This is known representation work, not a novelty claim. Do not extend that positive-factor certificate to zero/negative factors or feed fractional normalized slopes to the existing integer-floor horizon routine.

The new experiments deliberately introduce recurrence certificates and exact families of affine value lines. A DP table is not a scalar-price cell, and its operations are not candidate-bound evaluations. Define the new format explicitly. Its include/exclude recurrence must account for the complete disjoint feasible domain; terminal grouping by cardinality, count vector or total slope must be complete. Dominance deletions require independently checked witnesses. Do not silently relabel a value-only optimizer result as a complete proof.

## Findings the next instance must not overwrite or reinterpret

Stages 26–29 completed 48 development and 144 held-out trajectories each. Stage 30 attempted 32 development and 96 held-out trajectories, but five held-out policy paths capped. Across the previous campaign there were 896 unique trajectories and 3,840 policy paths, with 3,835 paths complete.

| Stage | Held-out findings in candidate-bound evaluations | Qualification |
|---|---|---|
| 26 | Maintenance 62,340; root probing at K>1 70,556; root probing at K>=n+1 66,152 | 144 completed pairs per probe policy. Broad root probing had 840 probes and two hits. Only one trajectory benefited; removing it increases the aggregate excess cost. |
| 27 | Maintenance 85,421; gated root 90,212; local ancestor probing 90,373 | 144 completed pairs; 741 local probes and no hits. Fixtures showed a sound local merge when the root fails, but held-out data did not supply one. |
| 28 | Maintenance 83,173; ordinary local 86,567; skip3 84,140; skip15 83,578 | 144 completed pairs per schedule; no hit. Development selected skip15 only as the least-cost probe hypothesis. Maintenance remained the reference. |
| 29 | Raw maintenance 80,589; normalized maintenance 18,044; normalized skip15 18,339 | 144 completed pairs. Normalization avoided 62,545 evaluations; all 120 nonproportional kernel paths were unchanged. Selected probing still cost 295 extra evaluations after normalization. |
| 30 | On selected pairs: maintenance 1,355,897; selected 1,358,790. On rebuild pairs: maintenance 887,074; rebuild 2,111,858 | 95/96 selected pairs and 93/96 rebuild pairs complete. These are different cohorts; raw totals include capped prefixes and are not paired totals. |

Stage 30's saved prefixes contain 188 strict incumbent changes per policy, with every replacement optimum audited. Maintenance/selected reached 534 proof cells, and selected reached 1,055 forest nodes. Five candidate-budget caps occurred in negative-profit/harm trajectories. The hypothesis that simplification probes are generally profitable was not supported. This does not prove that coarsening is impossible or maintenance always wins.

Two interruptions were disclosed. The stage-29 wrapper was corrected after development but before held-out, without any policy change. In stage 30 an audit hit its 45-second guard; an audit-only convex-slope tie check and cache reduced duplicate work. Completed cases were preserved. One uncheckpointed, unverified attempt was repeated; its first algorithm counters and abandoned audit CPU were not retained. The abandoned audit consumed at least its 45-second wall allowance. Headline results describe saved logical executions, not total infrastructure consumption. Do not invent those missing resource measurements.

## Five capped paths: exact resource-extension inputs

All have consumed exactly 500,000 candidate evaluations, are in phase index 4, and have completed four earlier incumbent phases. Their full original inputs, histories and optimizer cache are in the case JSON files under `stages/30/held/cases/`.

| Case | Policy | Current packing mask | Last verified modeled time | First unfinished attempt | Cooldown before that attempt |
|---|---|---:|---:|---:|---:|
| 16-145500-negative-harm | rebuild | 19997 | 203 | 204 | 0 |
| 16-145501-negative-harm | maintain | 50484 | 193 | 194 | 0 |
| 16-145501-negative-harm | selected | 50484 | 193 | 194 | 3 |
| 16-145501-negative-harm | rebuild | 50484 | 110 | 111 | 0 |
| 16-145502-negative-harm | rebuild | 53787 | 211 | 212 | 0 |

Resolve paths by policy name, not an assumed array index. Restore the last phase's `final_proof`, `final_forest`, packing and certificate anchor. For selected, restore the forest's node IDs, child links, active IDs and next ID, plus the cooldown before the interrupted attempt. `engine.run` currently initializes a new forest/cooldown; calling it with a later start time alone is not a valid resume.

The last failed attempt's partial work remains charged. Its partial repair cover is not a certificate. No complete continuation stack was saved for that attempt, so restart that one attempt from the last verified proof and charge the repeated work. Keep the original capped ledger intact and add a separate extension ledger. Do not claim this is identical to a single uninterrupted run with a higher cap. Existing complete phases, source solves and other cases must not be repeated.

## Common protocol for experiments 31–35

### Fresh data and declared matrices

Every new stage uses n=12/16, the same positive-weight/capacity and four-profit-family construction as stage 30, integer time 0–256, one development seed and three held-out seeds. There are 32 development and 96 held-out trajectories per stage: two sizes × four profit families × four directions × seeds. Sharing weights/profits among directions makes trajectories dependent.

| Stage | Development seed | Held-out seeds | Directions |
|---|---:|---|---|
| 31 | 146000 | 146500 / 146501 / 146502 | frozen sparse / signed / scale / harm |
| 32 | 147000 | 147500 / 147501 / 147502 | uniform +1 / uniform -1 / zero / near-uniform |
| 33 | 148000 | 148500 / 148501 / 148502 | p / p+1 / -p+1 / near-affine |
| 34 | 149000 | 149500 / 149501 / 149502 | frozen sparse / signed / scale / harm |
| 35 | 150000 | 150500 / 150501 / 150502 | frozen sparse / signed / scale / harm |

Weights: draw n values uniformly from 2–20; capacity is floor(sum(weights)/3). Profit families, generated in the old order before directions, are random 5–50; proportional `w_i+15+randint(-2,2)`; mixed -15–40; negative `-randint(1,10)`. Read the old generator rather than guessing RNG advancement.

For stages 31/34/35 preserve stage-30 direction generation exactly, including RNG draws for unused directions before filtering to the four active directions. For stage 32 use vectors `[1]*n`, `[-1]*n`, `[0]*n`, and `[1]*n` with one seeded item changed to 2. For stage 33 use `p`, `p+[1]*n`, `-p+[1]*n`, and `p+[1]*n` with one seeded component increased by one. Draw all four profit-family vectors first, in the old family order; then draw one control index for each family, in that same order, and record the generated vectors. A control may accidentally satisfy a structural identity in a degenerate instance; recognize the actual vectors and disclose such cases, rather than forcing a label to mean rejection.

### Limits and resumability

This handoff explicitly authorizes a new, prospective resource budget for stage 31's old-path extension and for the new stages. It does not alter any old frozen result.

- Scalar-price work: at most 2,000,000 cumulative candidate evaluations per policy trajectory, and 4,096 returned/pending scalar proof cells. For an old capped path the 500,000 already spent counts toward the 2,000,000 total.
- Native optimizer: at most 500,000 generator steps, 4,096 live/returned cells and 30 seconds per solve; at most 2,000,000 cumulative search steps per policy trajectory. Check limits inside the construction loop and dispose every native store even after errors/cancellation.
- Frontier proof construction: at most 500,000 retained DP proof entries across layers, 2,000,000 DP transitions, and, in stage 35, 5,000,000 dominance comparisons per policy trajectory. Bound allocations and retain proof predecessors needed by the independent checker. A rolling value array without a verifiable recurrence proof is insufficient.
- Algorithm execution: at most 120 cumulative seconds per fresh policy trajectory; at most 120 additional seconds per old capped-path continuation. Check guards within pricing, DP updates and pruning, not only after a trajectory finishes.
- Audit: bounded streaming batches of at most 45 seconds, with checkpoints between batches. Split a large case by phase/event range or DP-layer range; do not reset a deadline in an unbounded loop. Preserve verified audit prefixes and resume the pending range without recomputing policies.
- Aim for roughly ten minutes per stage. Checkpoint and report progress at least once a minute. Use a predeclared 900-second algorithm/audit batch budget; if exhausted, mark pending work and continue another explicitly bounded batch if the environment permits. Do not silently omit cases or repeatedly restart completed prefixes.

Freeze implementations, directions, dispatch precedence, construction/fallback rules, caps and selection rules after meaningful verification and before held-out execution. Development may guide later stages; held-out outcomes must not tune policies or caps. If a smaller matrix is necessary, declare it before its outcomes are inspected. Preserve null results, capped attempts and counterexamples.

Save computed case/phase results atomically before auditing. A top-level `Complete.json` marker must distinguish completed from capped, and “all cases attempted” from “all policy paths complete.” Save unstarted cases, current audit range, pending optimizer/proof construction and cumulative counters. Resource logs must reconcile all saved capped cases on resume, not just caps seen in the current invocation.

### Fair comparisons and accounting

All policies share the initial instance, packing and scalar proof. They hold that packing until strict optimality loss. To avoid a tie-selection confound, use the same existing exact native optimizer to select each replacement incumbent and scalar proof for every policy, including frontier policies that already know the optimum value. Physically share identical phase solves if useful, but charge their full recorded construction/search/cleanup/disposal work consistently. Frontiers persist across phases when their original-time proof remains valid; do not rebuild them merely because the incumbent changed. Phase-local cooldowns/forests reset as before.

A new frontier DP is explicitly part of the algorithm under test. It may construct its own exact certificate and loss-detection witness. It is not the audit oracle. Independent audit DP/enumeration must use separate implementations and must not supply missing algorithm states, branch choices, dispatch decisions or free future-optimum answers.

At a declared frontier-construction guard, save the incomplete frontier separately and charge all work. A fixed policy may discard it and fall back to the last full scalar proof; that fallback rule must be frozen before held-out and both failed construction and subsequent maintenance must be charged. Never use a partial DP as a certificate. If the overall trajectory budget is exhausted, the path is incomplete even if an audit knows the answer.

Report distinct counters: candidate bounds, hinge terms, pricing calls, splits, probes, horizons; DP entries/transitions, backpointer work, frontier lines, envelope evaluations/intersections, recognition, sorting/dominance comparisons; source generator/search steps; returned and peak active proof/frontier sizes; switches and phase lengths. Do not add these unlike counts into one invented total or declare a DP winner because it has zero scalar-price evaluations.

Measure clean end-to-end algorithm CPU including recognition, construction, all policy/horizon/lineage work, allocation, frontiers and charged native solves; exclude audit oracles. Keep initialization, certificate maintenance, optimizer search, serialization and audits separately visible. Pure pricing/DP kernel CPU is secondary. Do not hide the cost of solving all cardinalities/slopes or of an unsuccessful construction.

For any timing-based selection or runtime performance claim, predeclare three timing repetitions on the eight development trajectories with n=12, families random/negative and all four stage directions. Also repeat that eight-trajectory subset from the first held-out seed if reporting held-out runtime advantages; those measurements may validate timing variability but must not influence selection. Use fresh algorithm state for each repetition, identical logical work, and fully charged shared native solves/frontier builds. The selection score is the median across repetitions of aggregate end-to-end CPU over those eight cases; disclose capped repetitions and do not assign them a fictitious full-window runtime. If any candidate cannot finish the selection subset under the declared limits, it is ineligible for a CPU-based preferred-policy claim. Do not rerun entire held-out campaigns for timing; keep predeclared subset repetitions separate from unique-case headline counters. Single-run CPU remains descriptive if no performance claim is made.

At common modeled times 0,64,128,256 and at every switch/expiry, compare cumulative ledgers. Include the unsuccessful detection that ends a phase. For successful new proof construction, record initial debt, first strict cumulative advantage and first advantage that persists to the observation end, using each work measure separately. Report paired-completed denominators, benefited/harmed/tied distributions and largest-contributor sensitivity; show results excluding recognized structural trajectories as a descriptive ablation. Never pick the best method separately per held-out case.

For a current incumbent M at phase anchor tau, compare each certified line A+s*t at that anchor. If d=s-S_M>0 and margin=V_M(tau)-(A+s*tau)>=0, its first strict loss is tau+floor(margin/d)+1. Lines with d<=0 cannot cause future loss while M is optimal at tau. Take the minimum eligible crossing, keep ties, and also obey any finite certificate interval. Keep all frontier lines on the original time axis. The old optimality-horizon API assumes validity at its time zero; offset profits/lines explicitly before reusing it in a later phase.

Independently verify original-profit DP answers, feasible improving witnesses, scalar covers/prices/numerators/exact expiry calendars, every recurrence base case and transition, predecessor masks, complete grouping, pruning witnesses and exact integer line crossings. For n<=16 enumerate feasible packings once per source when helpful; use that to audit new grouped frontiers, not to build them. An all-time claim needs a mathematical argument plus a complete checked finite certificate, not extrapolation from time samples.

## Experiment 31 — What is behind the capped proof growth?

### 31A: resource extension, separate from new evidence

Implement and verify the dedicated continuation described above. Resume only the five listed stage-30 paths to time 256 under the 2,000,000 total-evaluation budget. Restore proofs, forests, cooldowns, current packing, original p/v, the optimizer cache and cumulative costs. Save results under a new `stage30-extension/` directory. Keep original stage-30 capped results and paired summaries unchanged. If a continuation still caps, preserve its next verified cursor and proceed to the fresh stage-31 matrix.

Compare original cap times and extension work with the completed time-256 outcome when available. Identify whether remaining cost is repricing an unchanged partition, splitting to refine bounds, failed probing, source search or actual incumbent changes. Recognize the actual direction: for these negative-profit/harm inputs the initial packing is empty and the slope vector is all ones. This suggests cardinality structure; it does not itself prove that any new algorithm is fast.

### 31B: fresh budget-controlled replication

On the new stage-31 matrix compare maintain-only, the frozen local skip15 hypothesis and reconstruct-every-expiry, all with the established v=p normalization. Use the same kernel and new declared caps for all three. This is fresh evidence, not a completion of stage 30.

Report paired results at time 64/128/256, cap rates, price calls on retained cells, growth of partitions/ancestry, strict switches, charged optimizer work and cumulative costs. Separate the old extension from these 32/96 new trajectories. Classify hard cases by vectors/packing structure rather than generator labels alone. Do not pool the five selected hard tails into a new independent held-out sample.

Question: did the old caps conceal a bounded but expensive tail, or continuing growth, and how much of that cost is associated with a uniform change in item profits?

## Experiment 32 — Can cardinality certificates remove uniform-offset renewal?

Recognize a uniform slope `v_i = gamma` by inspecting every entry. Define the feasible cardinality classes

`D_k = {M feasible : |M|=k}`,

and the exact intercept frontier

`A_k = max_{M in D_k} P_M`.

Represent infeasible classes as unreachable, not as a large negative integer. Empty cardinality has `A_0=0`.

For uniform slopes every packing in D_k has value `P_M + gamma k t`, so the optimal value is exactly

`max_k (A_k + gamma k t)`.

Build an exact cardinality DP certificate once, with signed profits, valid predecessor witnesses and a complete recurrence proof. A suitable capacity-state recurrence is

`D(j,r,k) = max(D(j-1,r,k), p_j + D(j-1,r-w_j,k-1))`,

where the include term exists only when `r>=w_j` and its predecessor is reachable. At j=0, only cardinality 0 is reachable with value 0. These are maxima over weight at most r. Validate all reachable and unreachable entries independently. This recurrence is an algorithm/proof under test, not an invocation of `H.F.dp` as an oracle.

Compare normalized maintenance with a policy that constructs this proof for every recognized uniform-slope vector and otherwise falls back to maintenance. Existing exact v=p normalization takes precedence for both policies. Uniform zero slopes are intentionally included: their frontier preparation may cost more than the already-valid static certificate. Do not suppress those unfavorable cases after seeing them.

Use exact affine-line arithmetic to determine loss of the fixed incumbent, keep ties, and call the common native optimizer at each strict loss to select the next common packing. The frontier remains valid for the entire original time axis; its construction should be charged once, not once per phase. Preserve the complete DP proof even if its upper envelope uses fewer than n+1 lines.

Fixtures must include negative profits, capacity zero, infeasible cardinalities, equal intercepts, simultaneous line crossings, negative/zero/positive gamma, a uniform vector that changes the optimum several times, and near-uniform rejection. Verify the envelope at all integer times 0–256 against independent original-profit DP and verify its all-time derivation analytically.

Measure DP preparation debt, number of feasible cardinalities, envelope lines/switches, recurrence proof memory, avoided renewals and total charged CPU. Compare recognized and rejected controls separately. Report a negative amortization result if preparation does not repay within time 256.

Question: can a fixed family of cardinality-value lines certify changing optima more economically than repeatedly refining scalar-price cells?

## Experiment 33 — What happens when an affine factor reaches zero or changes sign?

Recognize exact rational constants alpha,beta satisfying

`v_i = alpha p_i + beta` for all i.

Then for cardinality k,

`V_M(t) = (1+alpha t) P_M + beta k t`.

For nonconstant p, derive alpha from a pair of unequal p entries, derive beta, then verify the identity everywhere with exact rationals. For constant p, use the canonical uniform-slope interpretation alpha=0, beta=the common v if v is uniform; otherwise reject. Near-affine vectors must not be accepted by tolerance or labels.

The maximum-intercept frontier from stage 32 is sufficient only while `g(t)=1+alpha t` is positive. If g<0, maximizing the original value within a cardinality class requires the minimum intercept

`L_k = min_{M in D_k} P_M`.

At g=0, all feasible packings with the same k have equal value, and infeasible cardinalities remain infeasible. Establish this rule explicitly. A max/min pair of recurrence certificates therefore supplies exact candidate value lines for all integer times, with maxima used on the positive side and minima on the negative side. Alternatively, maximizing over all feasible max/min witness lines gives the same global optimum for every sign; prove that equivalence.

Compute each candidate line's slope from the witness's actual sum(v_i), and verify agreement with `alpha*A_k+beta*k` or `alpha*L_k+beta*k`. Although alpha,beta may be rational, original packing slopes must be integers. Do not run the scalar integer-floor horizon routine on fractional normalized coefficients.

Compare three fixed policies: normalized maintenance; a max-frontier policy valid on g>0 that hands back to the scalar kernel/common optimizer at the first integer t with g<=0; and a max/min-frontier policy valid through zero and negative factors. Both frontier policies fall back on non-affine vectors and give the existing v=p shortcut priority. A factor boundary alone must not trigger an incumbent switch. At the max-only handoff, reprice/repair the last complete scalar partition at the boundary's original integer profits; invoke the common optimizer only if a feasible witness proves strict loss. Old cached scalar numerators are anchored at their previous modeled time and must be updated. Charge recognition, maximum/minimum construction, factor-boundary dispatch and native solves. The max/min policy may omit the minimum table only when alpha>=0 makes g positive for all t>=0, according to a rule frozen before held-out.

Fixtures include alpha=0, alpha=1, alpha=-1, rational alpha=-1/2 with integer v, a zero occurring at an integer time, a zero strictly between integers, constant p, negative p, cardinality ties and near-affine rejection. A stage-29 positive-factor certificate must be rejected outside its positive domain; the distinct min-frontier certificate is what handles the negative side.

Measure whether handling the factor boundary avoids a burst of renewed proof work, and whether building the additional minimum table repays its cost. Make no all-time claim for the max-only policy after its handoff unless the scalar fallback itself proves one.

Question: can exact cardinality structure be retained across a sign change without an unsound normalization assumption?

## Experiment 34 — Can a small number of slope classes support one persistent frontier?

For the fresh standard directions, group items by their actual integer slope value. Fix the structural gate at at most two distinct slope classes, after the exact v=p shortcut. Do not choose a dimension limit from held-out results.

Let the classes G_j have slopes gamma_j. Every packing with count vector kappa has the same total slope

`S_kappa = sum_j gamma_j kappa_j`.

Define `A_kappa` as the maximum intercept P_M over feasible packings with that vector. An independently certified count-vector DP gives the exact all-time optimum

`max_kappa (A_kappa + t S_kappa)`.

The DP include transition increments precisely the chosen item's class coordinate. Store unreachable vectors explicitly and verify the full feasible count-domain accounting. Recognize classes from v, not from “sparse” or “harm.” Sparse and harm directions often have two classes; scale is already handled by the factor certificate. A signed vector with more classes must use the frozen fallback.

Compare normalized maintenance, the frozen max/min affine-frontier policy from stage 33, and the new at-most-two-class policy. In the two-class policy, dispatch order is v=p shortcut, class-count gate, count-vector construction, scalar fallback. Do not use another method's frontier for free. Charge any rejected/failed construction and retain the last valid scalar certificate for fallback.

Fixtures must include one class, two unequal classes, class slopes of opposite sign, three-class rejection, a class containing negative profits, empty/infeasible count vectors, and different vectors with the same total slope. Enumeration must verify every feasible packing belongs to exactly one vector class and that its affine value is bounded by the correct certified intercept.

Report class cardinalities, complete DP entry counts, number of reachable count vectors, duplicate total slopes, envelope size, preparation debt, memory, switches and fallback/cap rates. Keep construction and per-expiry work distinct.

For stage 35, choose one structural candidate using only the predeclared repeated development CPU subset in the common protocol: affine max/min or two-class. Seal that choice before stage 35 begins. If neither beats maintenance there, keep maintenance as the reference and carry the less costly structural method as a hypothesis. Do not promote a held-out winner to a preferred general policy.

Question: does the low-dimensional structure of sparse/harm slopes explain maintenance cost better than a history of failed coarsening probes?

## Experiment 35 — Can an exact slope frontier generalize, and does pruning repay its cost?

Remove the fixed class-dimension restriction. For every reachable total slope s define

`A_s = max_{M feasible, S_M=s} P_M`.

Then the exact all-time optimum is

`max_s (A_s + t s)`.

Build an exact sparse DP over prefix, weight and total slope. A safe elementary state is the best intercept for a specified prefix j, exact total weight W and slope s. Exclude/include recurrence accounts for every feasible packing, including the empty packing and negative profits/slopes. Terminal aggregation over W<=c gives A_s. Keep witness predecessors and enough proof data for an independent checker; the width of the slope range may be large and the number of states may be exponential. A small observed frontier is not a worst-case bound.

Compare four fixed policies on fresh data: normalized maintenance; the structural candidate sealed after stage-34 development; an unpruned sparse-slope frontier (only the exact same-state max-intercept reduction); and the same sparse frontier with endpoint-dominance pruning valid on the declared observation interval [0,256]. Give all policies the existing v=p shortcut and charge their own recognition/construction work. Use the common native phase optimizer as specified above.

A proposed safe pruning rule is this: at the same prefix j, state X may dominate state Y when

`W_X <= W_Y`, `P_X >= P_Y`, and `P_X + 256 S_X >= P_Y + 256 S_Y`.

Because the value difference is affine, both endpoint inequalities imply domination throughout [0,256]; the lighter prefix permits every identical remaining-item completion that was feasible for Y. Prove the completion argument and audit every discarded state with a feasible dominator and an acyclic witness chain. Define deterministic handling of equality. Do not compare states from different prefixes or require only one endpoint. Charge sorting, queries, comparisons, deletions and witness bookkeeping. Efficient exact data structures are allowed, but their verification cannot be replaced by trust in a library's output.

The unpruned recurrence certificate can support an all-time claim when construction completes. The endpoint-pruned certificate is only for [0,256]; explicitly reject use beyond 256. Do not label it all-time because sampled extrapolation looks correct. If retaining a complete dominance proof costs more memory/work than unpruned DP, report that result.

Fixtures include equal weight/slope with unequal intercept, lighter but worse-intercept states, lines crossing inside the interval, domination at one endpoint only, equal endpoint values, negative slopes, an improving high-slope/low-intercept state, and a request at time 257 that must be rejected by an interval-limited certificate. Compare surviving envelope values against exhaustive feasible lines on small instances and independent original-profit DP on n=12/16.

Report reachable versus retained states, frontier/envelope lines, witness-chain size, dominance work, active memory, construction caps/fallbacks, common-time debt/payback and completed paired CPU distributions. State whether any advantage persists after including proof construction and pruning overhead. Do not describe unlike operation counters as one speedup.

Question: does keeping an exact family of future value lines avoid enough repeated proof maintenance to repay its construction, or merely move the combinatorial burden into a larger initial certificate?

## Required outputs before leaving each stage

Save the stage protocol, development and held-out inputs/results, frozen source and hashes, verification fixtures, independent audit findings, all recurrence/cover/dominance evidence, common-time ledgers, cap/resource logs, atomic status/cursors and a short report. Preserve failed hypotheses and unusual instances. Save each checkpoint through the environment's supported persistent file workflow before moving on. Do not depend on scratch surviving to the next instance.

After all five stages, provide one concise synthesis and one reproducible campaign archive. State which stages/paths completed, which capped or remain unstarted, the paired denominators, whether the five old paths finished, and the decisive limitation of each experiment. Explain the different roles of optimality horizons, certificate expiry, changing proof complexity and amortized preparation work in plain language.

Separate elementary mathematical identities and independently verified certificates from empirical runtime findings. The cardinality/count/slope frontiers are explicit parametric optimization constructions, not evidence of novel arithmetic. This program originated in questions about Allen Brooks' “numbers with time built in”; it is an independent model and does not recover his unpublished mathematics or authenticate a breakthrough.

Begin with checkpoint inspection and the dedicated capped-path continuation, then proceed through experiment 35 without asking the user to restart the inquiry.


Fixed policies: [('maintain', 'maintain'), ('affine_max', 'affine_max'), ('affine_pair', 'affine_pair')]. Construction-cap fallback discards the incomplete frontier and uses the last full scalar partition. Any overall wall cap leaves the trajectory incomplete. Deterministic DP ties keep the first transition; pruning equal endpoints retains the first sorted state. Max/min omits min only when alpha>=0. No per-held-case tuning. CPU descriptive except stage34 development selection; no held-out runtime advantage claim. Stage34 predeclares 3 repeats of 8 n12 random/negative development trajectories; scores are median aggregate full CPU and capped methods ineligible. Audit batches are one layer or at most four scalar events, each <=45 seconds; 900-second outer batches checkpoint then continue.

Complete recurrence induction accounts for exclude and feasible include packings at each prefix, with unreachable classes explicit. A maximum intercept for a fixed cardinality/count/slope bounds all packings in that group, and its predecessor mask attains it. Uniform slopes give A_k+gamma*k*t. Affine slopes give (1+alpha*t)*P+beta*k*t: maximize P when the factor is positive, minimize P when negative, and any feasible intercept when zero. Maximizing over both extrema therefore gives the exact global optimum for every sign; every line is feasible. Count-vector lines have slope sum(gamma_j*k_j); exact slope states group by their actual integer sum(v). These completed unpruned certificates are valid for all t>=0 (max-only only in its positive domain). For endpoint pruning at the same prefix, a lighter state with both endpoint values at least those of the deleted state dominates throughout [0,256] by affinity and permits every identical remaining-item completion. Witness edges point to retained states and are acyclic. This proof has no implication beyond 256 for the pruned format. Tables, masks, grouping, crossings and every dominance witness are independently checked. These are elementary parametric optimization constructions, with potentially exponential slope-state width, and no new arithmetic claim.