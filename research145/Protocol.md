# Beginning the larger allocation inquiry: experiments 145–147

This stage starts the larger question in projects/certified-allocation/Problem.md:
how to maintain checked allocations as costs, capacities and needs change. It is
a first measured step, not completion of that research program. Experiments
141–144 close the separate storage-format question before this headline executes.

| Stage | Question | Evidence |
|---|---|---|
| 145 | Can a retained primal network-simplex tree serve as a genuine cost-update baseline? | Adapter retains the complete NetworkX tree, flow and edge arrays. It updates only the supplied costs, recomputes tree potentials, and reruns the upstream pivot rules. Fresh cold, retained basis, and certificate-guard plus retained-basis fallback are matched. |
| 146 | What happens when capacities and needs also change? | Three mixed streams include a reduced capacity, increased balanced needs, a genuine shortage, cost changes during shortage, and restored capacity. Unsupported fixed-model changes are refused by the old basis and explicitly reset. Every outcome has an exact optimality or infeasibility-cut certificate. |
| 147 | Which findings survive audit and replication, and what is the next larger question? | Two empty directories, 54 workers and 1,350 observations each, original-input reconstruction, separate residual/cut arithmetic, reference solving, adapter refusal controls and retained complete evidence. |

Six fresh cost-only transportation networks have 32/128/256 nodes, with
64/256/512 sparse edges or 256/4,096/16,384 dense edges. Three mixed streams have
16/48/128 nodes and 32/96/256 edges. There are 24 updates, two repetitions per
route per network, and separate development/control seeds. Only this stage's
checker expands the previous 4,096-edge ceiling to 16,384. Its other integer,
capacity, cost and 256-node limits remain unchanged. The carried delta-handle
message ceiling of 4,096 changed edges remains; generated cost updates use 1/4/8.

The adapter uses NetworkX 3.4.2's private _DataEssentialsAndFunctions and the
upstream pivot loop, with a fixed artificial-edge envelope covering all allowed
future costs. It retains the basis rather than destructively exporting it as the
public cold API does. Cost changes invalidate tree potentials, so their complete
tree recomputation is charged at the next optimize call. It does not offer warm
capacity/balance/topology changes or self-loop support. Artificial flow on a fresh
solve indicates infeasibility, which is separately completed into a checked cut.
Every produced feasible plan gets full residual-potential completion and exact
admission; solver internals are not accepted as a certificate.

The guard route uses the previously admitted certificate for k-edge residual
tests. All cost changes also reach the retained solver, even when the guard skips
optimization. The next failed test resumes from that retained primal tree.
Capacity/need changes force a fresh basis; a previously infeasible state also
requires a fresh solve. The cold route uses the unchanged public NetworkX solver
and the same exact proof completion. Tie-equivalent plans need not match between
routes; feasibility status and objective must match. Each route must reproduce
its own meaningful fields and evidence bytes between directories.

Workers have fixed 90-second/512 MiB guards and the adapter has a fixed
100,000-pivot guard per solve. Failure stops the campaign, keeps all evidence and
cannot become a win. Complete fresh-session wall/kernel CPU/RSS include startup,
source hashing, graph construction, proof completion, full certificate admission,
model hashing, guard misses, explicit resets, flushed raw logs and result files.
Logs are buffered with flush, not fsync. No durable/power-loss or persisted-basis
restart claim is made. These sessions share one pinned Python/NetworkX installation.

This is a transparent adapted baseline, not an official NetworkX incremental
API, independent solver implementation or state-of-the-art performance claim.
The complete pinned source and BSD-3-Clause license are retained. General
directed multigraph development checks (including lower bounds, fixed-capacity
edges, parallel/reversed arcs and negative costs) are excluded from headline
measurements; headline networks remain a small synthetic transportation family.

Prior work: Zoltán Király and Péter Kovács, *Efficient implementations of
minimum-cost flow algorithms* (2012), https://arxiv.org/abs/1207.6381, compares
multiple static algorithms and network families. Its broader benchmarks motivate
the later specialist-solver comparison; our adapted Python baseline does not
replace that comparison. Hassan Rashidi, *A dynamic version for the Network
Simplex Algorithm*, Applied Soft Computing 24 (2014), 414–422,
https://www.sciencedirect.com/science/article/pii/S1568494614003482, establishes
prior reoptimization work by title/metadata only here; its full method has not
been inspected in this session. We make no novelty-priority claim.

Costs, needs and eligibility are synthetic explicit policy inputs. Mathematical
minimum cost is not fairness, consent, a stakeholder decision or readiness for
deployment. The participation and credit rules of the project continue to apply.
