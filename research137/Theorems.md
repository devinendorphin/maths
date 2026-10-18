# Three concrete proof results

## 1. A potential certificate proves a global optimum (Lean checked)

Fix any finite directed network, allowing parallel edges and self loops. Let
bounds, balances, flows, costs and node potentials be rational. Feasibility means
`l[e] <= x[e] <= u[e]` and outgoing minus incoming flow equals `b[v]` at every
node. If

```
x[e] < u[e]  implies c[e] + pi[tail(e)] - pi[head(e)] >= 0
x[e] > l[e]  implies c[e] + pi[tail(e)] - pi[head(e)] <= 0,
```

then every feasible y with the same bounds and balances has `c·x <= c·y`.
There is no graph-size bound and no integrality assumption in this theorem.

For delta=y-x, summing node balances against potentials gives
`sum (pi_tail-pi_head)*delta = 0`. This identity is derived from the concrete
incidence function, including self-loop cancellation; it is not supplied as an
extra hypothesis. Thus the objective difference is `sum r[e]*delta[e]`.
Each positive delta permits a forward residual move and has nonnegative r;
each negative delta permits a reverse move and has nonpositive r. Every term
is nonnegative, proving the result for all feasible competitors.

`formal/Flow.lean` constructs the finite sums, proves cancellation and proves
`Allocation.certificate_sound`. `formal/Spec.lean` states the full contract again
and proves it using that theorem. It also checks arithmetic counterexamples to
omitting reverse signs or matching balances. Successful compilation reports only
standard Lean axioms (propext, Classical.choice, Quot.sound), with no sorryAx.
This formalizes the mathematical certificate condition; it does not prove that
the Python JSON parser or evaluator implements that condition correctly.

## 2. Complete cost deltas preserve an admitted optimum (Lean checked)

Keep graph, bounds, balances, x and pi fixed. Let S contain every changed cost
coefficient, so `newCost[e]=oldCost[e]` outside S. If the old certificate was valid
and all residual signs hold at the changed edges under newCost, x is optimal
under newCost. `Allocation.delta_signs` proves the new signs and
`Allocation.delta_optimal` derives the new global optimum.

`Allocation.objective_update` also proves the exact identity

```
newCost·x = oldCost·x + sum ((newCost[e]-oldCost[e])*x[e]).
```

Outside S the summands are zero. Following initial full admission, checking a
complete trusted delta of size k and updating this value requires O(k) rational
arithmetic operations and can retain O(V+E) numbers for current state. Over T
accepted updates the sign/value work is O(V+E+sum k_i), with initial admission
included. This operation count is a prose consequence of the interface, not a
Lean complexity theorem. Bit lengths, discovering/validating the delta, reading
full models, full certificate export, log retention, failed attempts, repair and
fallback remain separate costs. No end-to-end runtime improvement is proved.

## 3. Exact single-edge cost-stability interval (written proof + exact witnesses)

Assume x is feasible and optimal for c. Choose an original edge e=(a,z) and
change only its cost from c_e to c_e+t. In x's residual graph, REMOVE BOTH
residual orientations belonging to e; call the resulting graph H. All other
original edges, including parallel edges, stay present.

Let d_H(s,t) be the shortest path cost in H, with +infinity for no path and zero
for the empty path when s=t. H has no negative cycle, since the original x is
optimal. Define extended endpoints

```
L = -c_e - d_H(z,a)   if x_e < u_e and that return path exists; otherwise -infinity
U =  d_H(a,z) - c_e   if x_e > l_e and that return path exists; otherwise +infinity.
```

**The old flow x is optimal after the change if and only if L <= t <= U.**
Endpoints are included. Since t=0 is an optimum, the interval contains zero.
For a fixed edge l_e=u_e there are no residual orientations and both ends are
infinite. Self loops use the empty return path. For a bridge whose flow is
forced by balances, removing both orientations can leave no return path, so
its cost may change arbitrarily while the same flow stays optimal.

### Proof of both directions

Any simple residual cycle using the forward orientation of e consists of that
arc and a return path z→a in H, so its changed cost is at least
`c_e+t+d_H(z,a)`. A cycle using the reverse orientation similarly has changed
cost at least `-c_e-t+d_H(a,z)`. Cycles avoiding e have unchanged nonnegative
cost. A simple cycle using both orientations of the SAME original non-loop edge
is just its two-arc cancellation cycle; its cost is always zero. A simple cycle
cannot otherwise contain both orientations, because it would revisit an endpoint.
For self loops the forward and reverse arcs are separate one-arc cycles.

Consequently all residual cycles are nonnegative when L<=t<=U. Any difference
between feasible flows decomposes into residual cycles with nonnegative amounts,
so no competitor is cheaper. Equivalently, shortest-distance potentials certify
the unchanged x under the new costs.

If t<L at a finite lower endpoint, combine the forward e arc with a shortest
return path attaining d_H(z,a). This cycle has cost strictly below zero. Send
its positive residual bottleneck around it: bounds and balances stay feasible,
and total cost strictly decreases. The upper-endpoint argument reverses e.
At equality the same nonzero augmentation has zero objective change, giving a
distinct tied optimum. Finite graphs without negative cycles have a shortest
simple path whenever the target is reachable, so every finite endpoint is attained.
This proves maximality, not merely a sufficient safe interval.

Removing BOTH orientations matters: retaining e's reverse arc would create a
spurious return path that cancels the very change being assessed. The interior
bridge fixture is a concrete control for that mistake.

### What the executable witnesses establish

For each return direction, the producer exports distance labels and an explicit
path, or a closed reachable set with an unreachable target. The separate evaluator
checks every residual triangle inequality, closure of reachable labels, residual
capacity, exclusion of both e orientations, and path cost equality. Triangle
inequalities lower-bound every possible path; the explicit equal-cost path
attains the bound. An unreachable target plus closure proves there is no return
path. The base optimum certificate is mandatory; a local path witness alone
cannot rule out an unrelated negative cycle elsewhere.

At sampled interior/endpoints the unchanged flow receives a fully rechecked
new potential. At each finite endpoint there is a checked tied alternative;
outside, an explicit feasible flow has strictly smaller rational cost. For tiny
inputs, exhaustive feasible-flow comparisons independently recover the SAME
endpoints by intersecting `(c·(y-x))+t*(y_e-x_e)>=0` for every competitor y.
These finite checks validate the implementation. The general cycle/path theorem
in this section is not yet formalized in Lean.

## Interaction obstruction: separate ranges do not compose

Two parallel edges each have capacity one and carry one unit in total. Start
with costs (0,2) and flow (1,0). Raising the first cost by two alone is safe
(a tie). Lowering the second by two alone is also safe (a tie). Together the costs
become (2,0): the old plan costs two and (0,1) costs zero.

Thus the Cartesian product of separately computed single-edge intervals need
not lie within the true joint stability region. Joint changes must be checked
together, for example by checking or repairing potentials under ALL new costs.
The joint optimality region for a fixed flow is convex (an intersection of linear
competitor inequalities), but generally is not a Cartesian product.

All these are established optimization arguments. The concrete contribution here
is the formalized soundness/maintenance statements plus inspectable exact
sensitivity witnesses and independently replayed finite controls. No new
mathematical priority or solution to the full allocation research problem is claimed.
