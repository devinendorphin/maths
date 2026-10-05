# Literature review: temporal proof reuse and parametric knapsack

Reviewed 5 October 2026. This is a research review and a proposed change of direction; no new experiment was run for it. Completed campaign sources, protocols and results remain frozen.

## Conclusion

Substantial relevant work already exists. Parametric knapsack, sensitivity analysis, event-driven certificate maintenance, search-tree reuse and independently checked optimization proofs are established research areas. Our experiments should be described as implementations and finite evaluations of particular combinations, rather than evidence that these general principles are new.

The most useful immediate shortcut is to compare with an established exact parametric method that discovers changes in the optimal solution through ordinary optimization calls. The second is to compare with solvers that retain their search across related problems. These are stronger comparisons than adding another threshold to our existing policies.

This does not make the completed work pointless: its explicit accounting of incomplete constructions, repairs and verification gives us a useful test bed. It changes what we should investigate next. See the [proposed next five experiments](Roadmap-after-literature.md).

## What our current model actually covers

The implemented problem is exact 0–1 knapsack with fixed integer weights and capacity. Each item's profit is an affine function `q_i(t) = p_i + t*v_i`, with signed integer coefficients. The campaigns observe nonnegative integer times through a finite horizon. Feasibility stays fixed while the objective changes.

Our scalar certificates use rational upper bounds on partitions of the feasible space. Their expiration is the first time that their bounds cease to certify the current answer. An expiration can occur before the best packing changes. Our reusable frontiers retain weight/slope/intercept states, prune dominated states, and form an envelope of affine profit functions. Native solves currently start cold at the driver level.

The code examined includes [frontier construction and envelopes](../research46/code/certificates.py), [policy decisions and native solve calls](../research46/code/policy.py), and [the earlier scalar horizon implementation](../campaigns/experiments-31-35/research/stages/35/code/horizon.py). Exactness here means the declared finite answers agree with a separate exact checker. It does not mean the Python checker itself has been formally verified.

## Direct matches and what to reuse

| Our component | Established connection | Consequence for this project |
|---|---|---|
| Affine item profits and changing optimal packings | Linear-parametric knapsack [1–3] | Introduce an established exact parametric baseline before further gate tuning. |
| Sparse frontier and dominance pruning | Dynamic programming and capital-allocation/knapsack methods [2, 10] | Treat the general method as prior art; investigate only clearly specified implementation or guarantee differences. |
| Reuse while a bound remains valid | Sensitivity/tolerance analysis [4] | Reuse specialized results where their perturbation assumptions match. |
| Certificate horizons and repair events | Kinetic data structures [5] | Cache failure times and schedule local repairs; distinguish proof failures from answer changes. |
| Solving again after objective changes | MIP reoptimization [6] | Compare retained search trees and incumbents with our cold native solve path. |
| Independent exact proof checking | SCIP exact mode, VIPR and VeriPB/CakePB [7–9] | Evaluate an existing proof format/checker before building a broader custom infrastructure. |
| Pay now to reduce future work | Rent-or-buy and costly prediction models [11–13] | Charge feature computation and construction, and state assumptions before claiming a policy guarantee. |

### Exact parametric optimization: the strongest missing comparison

**[1] Nemesch, Ruzika, Thielen and Wittmann (2025), _A survey of exact and approximation algorithms for linear-parametric optimization problems_.** [Publisher](https://link.springer.com/article/10.1007/s10898-025-01512-6), [open text](https://arxiv.org/html/2501.11544v1). Full relevant sections read: exact methods, multiobjective connections and knapsack. Published 28 June 2025; the survey's search covers literature through 2024.

The survey describes the Eisner–Severance approach: solve at interval endpoints, query where their objective lines intersect, and recurse where another solution is needed. Its optimization-call accounting depends on the number of pieces in the optimal value curve. This can avoid explicitly constructing our entire candidate frontier. General parametric problems can still have exponentially many pieces; it is not a universal cheap solution.

**[2] Moshe Eben-Chaime (1996), _Parametric Solution for Linear Bicriteria Knapsack Models_.** [Publisher](https://pubsonline.informs.org/doi/10.1287/mnsc.42.11.1565). Original abstract and metadata read; algorithm context cross-checked in [1]. The original full paper was not available in the material read.

This is a direct precedent for computing parametric knapsack solutions through a network/dynamic-programming representation. Its reported complexity is sensitive to item count, capacity and the number of solution vectors. We should obtain the full paper before claiming to reproduce its precise algorithm or signed-coefficient assumptions. Meanwhile, the general exact-oracle method in [1] provides a concrete baseline we can implement and audit.

**[3] Michael Holzhauser and Sven O. Krumke (2017), _An FPTAS for the parametric knapsack problem_.** [Author preprint](https://arxiv.org/abs/1701.07822), [journal](https://www.sciencedirect.com/science/article/abs/pii/S0020019017301072). Abstract read.

This addresses affine profits with arbitrary signed integer slopes and intercepts, making its problem statement especially close to ours. It approximates the parametric solution with polynomial resources, while exact output can be exponential. It is a useful option for a separately labeled approximation project. An approximation guarantee cannot replace the exact certificates required by the current campaigns.

### Sensitivity and scheduled certificate repair

**[4] David Pisinger and Alima Saidi (2017), _Tolerance analysis for 0–1 knapsack problems_.** [Journal](https://www.sciencedirect.com/science/article/pii/S0377221716309043), [accepted manuscript](https://backend.orbit.dtu.dk/ws/files/128585240/Tolerance_analysis_for_postprint.pdf). Full accepted manuscript read.

The paper determines how far an individual profit or weight can change without invalidating an optimal solution, sharing dynamic-programming work across tolerance calculations. This could replace bespoke analysis on single-item perturbation controls. Our usual trajectory changes many profits together. Separate one-item tolerance intervals cannot simply be combined into a guarantee for that simultaneous trajectory.

**[5] Julien Basch, Leonidas J. Guibas and John Hershberger, _Data Structures for Mobile Data_ (SODA 1997; journal version 1999).** [Journal](https://www.sciencedirect.com/science/article/pii/S0196677498909889), [conference paper](https://www.ime.usp.br/~cris/aulas/19_1_6957/BaschGH-DSforMobileData.pdf). Full conference paper read; journal metadata checked.

Kinetic data structures maintain short certificates, predict their failure times, place failures in a priority queue, and repair the structure when events occur. This is a close conceptual precedent for our horizon/repair driver. Its distinction between internal certificate events and actual changes in the maintained answer suggests a useful measurement: how much repair occurs without a packing change? Geometry-specific efficiency bounds do not automatically apply to knapsack. A heap can reduce repeated event scheduling work without making each optimization repair cheap.

### Reusing optimization search and established proof tools

**[6] Gerald Gamrath, Benjamin Hiller and Jakob Witzig (2015), _Reoptimization Techniques for MIP Solvers_, ZIB report 15-24.** [Publication record](https://optimization-online.org/2015/05/4898/), [full report](https://optimization-online.org/wp-content/uploads/2015/05/4898.pdf). Full report read.

The work reuses a branch-and-bound search structure when objectives change or feasible regions become more restrictive. This is a direct alternative to our cold native solves. Old objective-dependent pruning and dual reductions require care when the objective changes; retaining a tree is not permission to trust every old bound. A fair comparison should distinguish a cold solve, an incumbent-only warm start, and actual tree reuse, charging setup and the complete sequence.

**[7] Hojny et al. (2025), _The SCIP Optimization Suite 10.0_.** [Preprint](https://arxiv.org/abs/2511.18580), [full text](https://arxiv.org/html/2511.18580v1). Relevant exact-solving and certification sections read.

SCIP now offers rational exact MILP solving and certificate infrastructure. This may spare us from writing another generic exact solver. A material limitation in the report is that the described certificate proves the transformed problem after presolving; presolving itself is not certified in that format. End-to-end original-problem claims therefore need a checked transformation or a compatible configuration without those transformations. The report does not establish that exact mode and reoptimization can be combined as required here. Check their compatibility before promising that combined baseline.

**[8] Cheung, Gleixner and Steffy (2017), _Verifying Integer Programming Results_; VIPR implementation and specification.** [Primary software and references](https://github.com/scipopt/vipr), [paper DOI](https://doi.org/10.1007/978-3-319-59250-3_13). Software README/specification read; the original paper was not read in full.

VIPR provides an independently checkable rational proof format for integer programming, with tools for processing proofs. Its current documentation also describes extensions associated with Eifler and Gleixner's 2024 work on verified cuts. This is useful prior infrastructure for a small interoperability experiment. A proof at one time does not certify a whole interval. An incomplete construction record is also distinct from a completed optimality proof.

**[9] Koops, Le Berre, Myreen, Nordström, Oertel, Tan and Vinyals (2025), _Practically Feasible Proof Logging for Pseudo-Boolean Optimization_.** [Publication and full text](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2025.21). Full relevant text read. Published 8 August 2025.

The work connects practical optimization proof logging with VeriPB and a formally verified CakePB checker, including several solver reasoning techniques. Our binary variables and integer linear constraints fit the broad pseudo-Boolean setting. This gives us another possible adapter target and a stronger checker trust story than our current Python audit alone. The paper does not, by itself, provide an adapter for our rational scalar interval certificates or demonstrate their reuse across time.

**[10] George L. Nemhauser and Z. Ullmann (1969), _Discrete Dynamic Programming and Capital Allocation_.** [Publisher](https://pubsonline.informs.org/doi/10.1287/mnsc.15.9.494). Abstract and bibliographic metadata read.

This is an early precedent in the dynamic-programming tradition behind knapsack frontiers. It supports treating the general frontier idea as established. This review does not attribute our particular endpoint-dominance test or Fenwick index implementation to that paper; those narrower details need their own comparison before any novelty assessment.

### Construction cost, prediction and recent adjacent work

**[11] Sreenivas Gollapudi and Debmalya Panigrahi (2019), _Online Algorithms for Rent-Or-Buy with Expert Advice_.** [Primary proceedings](https://proceedings.mlr.press/v97/gollapudi19a.html). Abstract read.

The paper studies rent-or-buy decisions using predictions from multiple experts. The analogy for us is maintaining a proof versus paying for reusable construction. It is an analogy, not an established reduction: our construction costs vary, certificates expire, and maintenance may continue after construction. Classical guarantees must not be attached to our gates without a matching cost model.

**[12] Marina Drygala, Sai Ganesh Nagarajan and Ola Svensson (2023), _Online Algorithms with Costly Predictions_.** [Primary proceedings](https://proceedings.mlr.press/v206/drygala23a.html). Abstract read.

The paper treats the cost of obtaining predictions as part of an online decision. This supports a concrete discipline for our policies: charge probes and feature computation, not just the eventual construction. Our current accounting is useful here, but operation counters are not automatically equivalent to CPU time or a competitive bound.

**[13] Qiming Cui and Michael Dinitz (2026), _Ski Rental with Distributional Predictions of Unknown Quality_.** [ICML 2026 proceedings](https://proceedings.mlr.press/v306/cui26a.html), [preprint](https://arxiv.org/abs/2602.21104). Abstract read; proofs not reviewed.

This recent work studies robustness when prediction quality is unknown. It is a useful guide for designing policies that remain reasonable after transfer, rather than relying on one training set. We have not established that its assumptions or guarantees apply to our construction/renewal problem.

**[14] Diego Cifuentes, Santanu S. Dey and Jingye Xu, _Sensitivity analysis for mixed binary quadratic programming_ (preprint 2023; Mathematical Programming 216, 2026).** [Preprint record](https://arxiv.org/abs/2312.06714), [author-hosted manuscript](https://www2.isye.gatech.edu/~sdey30/SenMBQP.pdf), [author publication list](https://www2.isye.gatech.edu/~sdey30/publications.html). Relevant manuscript introduction and scope read; journal citation checked against the author list.

This examines sensitivity to right-hand-side changes using copositive/completely positive formulations and includes limits on what sensitivity methods can guarantee. It is relevant if we extend to changing capacity or constraints. It does not directly replace our fixed-feasibility, changing-linear-objective method. Applications involving availability or routing changes require such additional models and are not demonstrated by our current knapsack experiments.

## What we should stop reproducing, and what is still worth testing

We do not need another experiment to establish that multiplying every profit by the same positive factor preserves the best packing. That is an elementary invariance; normalized controls remain useful implementation checks. We should likewise avoid presenting affine envelopes, dynamic-programming dominance, certificate failure scheduling or generic proof reuse as new principles.

More threshold searches should wait for stronger baselines. The [46–50 findings](../research46/Synthesis.md) already give a reason: the selected renewal threshold was zero, and the composed transferred policy consequently built no frontiers. Its small timing difference cannot establish a benefit from active composition. Those findings support simplifying the next batch rather than expanding heuristic tuning.

Useful work remains in measuring exactly when interval proofs beat existing methods, preserving soundness under partial construction, and bounding all setup/repair costs. A possible research question is whether compact, independently checkable interval certificates can offer a clear cost guarantee in a specified class of exact integer-parametric problems. This is a hypothesis for further investigation, not a finding of novelty or a claim that no one has studied it.

## Coverage and limits

This was a targeted literature review, not an exhaustive systematic search or a novelty clearance. Searches covered parametric knapsack/optimization, tolerance analysis, kinetic certificates, objective-change reoptimization, exact optimization proof logging, and online construction decisions. Primary papers, author manuscripts, official proceedings and software documentation were preferred. Access levels are stated above to avoid treating abstracts as fully reviewed methods. The 2025 survey was supplemented with direct 2025–2026 sources.

Remaining implementation questions are explicit: signed-coefficient and tie handling in the exact baseline; SCIP exact/reoptimization compatibility; which existing proof format can express our bounds economically; and whether any published cost model truly matches expiring, renewable constructions. These questions should narrow the next experiments, not be assumed solved.
