# A conditional maintenance result and its limits

Let a fixed graph have fixed balances, lower/upper bounds, feasible flow x and an
admitted valid potential pi. At update i, a complete trusted list changes only
k_i cost coefficients. Keep x and pi fixed. On each changed edge e, check:

```
r'_e = c'_e + pi_tail - pi_head
x_e < u_e implies r'_e >= 0
x_e > l_e implies r'_e <= 0
```

If all checks pass, update the objective numerator by
sum((c'_e-c_e)*x_e). Unchanged residual signs remain valid. For any feasible y,
delta=y-x is conserved at every node, so the potential terms cancel and
cost'(y)-cost'(x)=sum(r'_e*delta_e). A positive delta has a forward residual edge
and nonnegative r'; a negative delta has a reverse residual edge and nonpositive
r'. Every summand is nonnegative. Thus x remains optimal.

Full initial admission needs O(V+E) exact arithmetic operations and stores
O(V+E) numbers. Under the specified complete-delta/version interface, the accepted
sign/value tests over updates need O(sum k_i) additional operations. Coefficient
bit lengths affect arithmetic and storage. With k updated costs of B bits and
flow entries of U bits, the objective updates include multiplication/addition
on those bit lengths; the arithmetic-operation bound is not constant bit cost.

This result does not make discovery or validation of a delta from arbitrary raw
models O(k). Full model hashing, serializing a complete certificate and an
ordinary stateless replay still cost O(V+E) in data length. Maintaining a
versioned delta log can store O(sum k_i) changed values plus the admitted base;
bounding it requires eviction or an O(V+E) snapshot/recapture, which must be
charged. If a sign test fails, x might still be optimal with new potentials.
Potential repair, feasibility changes, code/dependency changes and solver fallback
are not bounded by this accepted-update result.

The actual headline pipeline deliberately exports and fully checks each proof,
so it retains these linear work and I/O costs. Captured.patch in the supplemental
controls also materializes a full model hash on export; it is not a measured
O(k) complete implementation. Its complete delta is supplied by a harness that
scans the raw model. Across 64 cost-only transitions, 25 patches preserve the
captured proof and 39 fail and recapture; every accepted state passes the full
checker. Stale versions and changed dependency contexts are rejected.

For a counterexample to guaranteed answer stability, use two parallel supplier-to-
recipient edges, each capacity one, supply/demand one. Costs are (t,0).
At t=-1 the first edge is uniquely optimal; at t=1 the second is uniquely optimal.
Alternating these values changes one coefficient each time yet changes the
unique optimal plan on every update. Six observations/five updates reproduce and
each old certificate fails at the next step, even after its objective value is
recomputed. This establishes lack of guaranteed plan reuse; it does not prove
that every possible update algorithm has cold-solve cost.

These are applications of established residual optimality and sensitivity,
written with an explicit admission/storage contract. No new mathematical priority
is claimed. The argument is inspectable prose, not formally checked Lean code.
