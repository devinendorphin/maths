# Remaining imbalance and admitted optimizer state

For each arc let physical flow be x = lower + y, where 0 <= y <= upper-lower.
GenericMinCostFlow stores y through forward/reverse residual capacities. When
bounds change, SetArcCapacity clips that y if the new upper-lower is smaller.
The resulting physical hint uses the **new** lower bound. Thus retaining y
does not mean retaining an identical physical allocation when a floor changes.

The supplies passed to a warm Generic setter must be the remaining imbalance:

$$e_v=b_v-\sum_{a\text{ leaves }v}(l_a+y_a)
                 +\sum_{a\text{ enters }v}(l_a+y_a).$$

Self-loop contributions cancel. The sum of e is zero because b is balanced.
Setting new absolute b as this excess would double-count flow already sent.
The source also assigns its initial-excess array in this setter, so its cold
forward-capacity feasibility check cannot be assumed to be a warm residual
feasibility test. This adapter recomputes all remaining imbalances after bounds
are patched, and uses an independently checked full-model feasible witness
before calling Solve with that internal check disabled. A bounded current hint
and a feasible witness imply a residual path/circulation difference connecting
them, including reverse arcs. A witness is not treated as an optimum.

An infeasible model is admitted only with the established shortage inequality:
supply on a node set exceeds its outgoing upper capacity minus incoming lower
bounds. In that case the native hint is patched but not optimized, and remains
uncertified state for later recovery. Neither its old price nor an old cut is
silently reused as a certificate for the changed model.

Generic Solve uses the credited cost-scaling implementation and resets prices.
Successful output is translated back to physical flow and certified with exact
residual potentials: c + pi(tail) - pi(head) >= 0 on every forward residual arc
and <= 0 on every backward residual arc. Feasibility, exact integer objective,
context/model binding and all residual signs are checked. Potential terms
cancel for any feasible flow difference, proving no cheaper feasible allocation
under the declared costs. This covers finite negative costs, parallel arcs and
self-loops, but not the meaning or social validity of those costs.

Full guard admission can retain an old physical plan/potential while the native
hint has changed under a new lower-bound transformation. The guard's certificate
is the allocation admitted; the unsolved hint is not. The audit keeps both
objects explicit. If guard admission fails, its time remains charged and the
subsequent native solve starts from actual retained y/excess, not an assumed
copy of the certificate's flow.

The audit reconstructs capacity clipping and remaining imbalance without
calling native code, verifies literal before/patched/after snapshots, counts
constructions/updates/solves and checks every preflight feasible witness. The
compiled adapter checks graph and optimizer pointer stability internally; this
is execution evidence under a pinned implementation, not hardware attestation.
Cold Generic uses the same bridge and preflight with a new object each query.
Retained-price, spanning-tree and arbitrary-topology reuse are not established.

Transactions remain the frozen fixed-topology 148 interface with caller-owned
values copied and invalid changes rejected before model/version mutation.
Native arithmetic is bounded explicitly to this stage's integer domain. Every
producer status remains subordinate to certificate admission. The completed
finite streams do not prove universal completion or a worst-case speed bound;
worker/algorithm guards and charged fallback are explicit.
