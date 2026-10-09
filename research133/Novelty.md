# Attribution and originality assessment

Three versioned primary implementations were retrieved over verified HTTPS,
hashed and inspected. Their complete source snapshots are in each archive run's
upstream/ directory; Primary-source-receipts.json identifies URLs and bytes.

- Official NetworkX 3.4.2 network_simplex: reduced costs, primal pivots, tied
  solutions, integer-data handling and infeasibility. It credits Király/Kovács
  (2012) and Barr/Glover/Klingman (1979), already identified in the charter.
- Boost Graph 1.86.0 cycle_canceling.hpp, by Piotr Wygocki: all-zero initial
  distances, Bellman–Ford negative-cycle reconstruction and residual augmentation.
  It credits Ahuja/Magnanti/Orlin, *Network Flows* (1993). This is the established
  algorithm family used by the independently written native producer.
- OR-Tools 9.11 min_cost_flow.h: reduced costs c+p_tail-p_head, integer
  epsilon-optimality, cost scaling, and an explicit comment that GenericMinCostFlow
  already supports warm start/incrementality while SimpleMinCostFlow's interface
  does not expose that capability. Its references include Goldberg/Tarjan (1990),
  Goldberg (1997), Goldberg/Kharitonov (1993), Bunnagel/Korte/Vygen (1998), and
  Ahuja/Goldberg/Orlin/Tarjan (1992).

Those source implementations were read; the cited full papers were not. This
campaign therefore credits established mechanisms but does not establish
priority against the full dynamic-flow, sensitivity, robust-optimization or
fair-allocation literature. OR-Tools was consulted as prior art, not installed or
benchmarked. This avoids representing the simple warm native comparison as a
comparison with state-of-the-art incremental network solvers.

Mathematical originality: residual signs, lower-bound feasibility reduction,
negative-cycle cancellation, positive scaling and bounded-edge checking are
established. The maintenance result exposes its assurance and export assumptions
but supplies no new general dynamic min-cost-flow theorem. Integral coverage
candidate enumeration is an elementary finite formulation, not a new fairness
principle.

Implementation contribution: an inspectable pipeline composing optimality and
cut proofs, distinct scalar/max-min admission, explicit failed-probe accounting,
resource budgets and full identity replication. This concrete artifact is useful;
any claim that the combination or format is first requires broader comparison.
It is not a formally verified Python implementation.

Empirical contribution: a frozen, replicated finite measurement set comparing
six compatible routes on the same four model/update families, including exact
counts of stable answers with inapplicable captured proofs. The result supports
specific descriptive findings, not a broad speed/scalability claim. Whether this
constitutes a research novelty beyond useful reproducibility remains open.

No blanket ban on novelty is imposed. A future originality claim should identify
its precise mathematical, implementation or empirical contribution and complete
the corresponding primary-paper comparison first. Human questions, policy choices
and interpretation remain credited alongside prior mathematics and AI-assisted
implementation; synthetic policies here are not real stakeholder validation.
