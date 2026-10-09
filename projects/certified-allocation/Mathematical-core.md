# A checkable starting lemma

Let `x` and `y` be feasible flows with identical balance requirements and bounds. Set `delta = y - x`. At each node, outgoing minus incoming delta is zero. Hence:

```
sum_e (pi[tail(e)] - pi[head(e)]) * delta[e] = 0
cost(y) - cost(x) = sum_e r[e] * delta[e]
r[e] = c[e] + pi[tail(e)] - pi[head(e)]
```

When `delta[e] > 0`, the edge has forward residual capacity at x and the certificate requires `r[e] >= 0`. When `delta[e] < 0`, it has reverse residual capacity and the certificate requires `r[e] <= 0`. Every term is nonnegative, so `cost(y) >= cost(x)`. This is the standard residual-potential optimality argument, not a new theorem. The illustrative Python checker is not formally verified.

With fixed x, bounds and potentials, and affine costs `c[e](theta)`, each residual sign is a linear inequality in theta. Their intersection is a convex polyhedron certifying that x remains optimal. A different potential can extend the region without changing x. Capacity or balance changes require a fresh feasibility check; the preceding derivation assumes identical feasible sets for x and its competitors.

For the worked two-supplier/two-recipient example, diagonal edges cost 1 each. The other two cost `4-t` and `3-s`. Each supplier provides two units; each recipient needs two. Every feasible flow is parametrized by `k=0,1,2`, where k units from each supplier cross to the other recipient. Its cost is:

```
4 + k * (5 - t - s)
```

Therefore the diagonal plan remains optimal exactly when `t+s <= 5`, including ties. The initial potentials `(0,0,1,1)` certify only `t <= 3` and `s <= 2`. At `(4,0)` the original potentials fail, but new potentials certify the unchanged diagonal plan. At `(4,2)` the diagonal plan loses optimality and the crossed plan costs 2 instead of 4. Reducing the first diagonal capacity to one invalidates the old plan even at the original costs and requires a feasible repair. The example's enumeration, residual checks and corrupted controls are recorded in Worked-example.json.
