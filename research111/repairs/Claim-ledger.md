# Claims and remaining trust

| Claim | Supporting evidence | Limits |
|---|---|---|
| Nine native SCIP certificates prove the original point optima | Native `.vipr` files and six completion outputs in archive; independent original header/model/objective binding; original-model enumeration; external checker and false-bound controls | Presolve/separation disabled; three existing base fixtures; no exact reoptimization |
| Ordinary SCIP cold/reoptimized candidates are optimal | Full duplicate native exact/VIPR certification, primal checks and independent enumeration | Certificates produced by the native repository adapter, not ordinary SCIP |
| One packing is optimal throughout a fixed rational interval | Independently checked identical optimal endpoint packings; prior Lean conditional affine theorem | Fixed feasible set and affine functions; Python admission/cache not formally verified |
| A captured immutable fact remains usable | Frozen Fact and model/epoch keys, independent result audit | No continuous external-file or arbitrary-code monitoring |
| Explicit context changes invalidate live caches | Actual capacity/weight/objective/domain/nonlinear/checker change trace; independent LRU and binary-epoch audit | Changed checker is semantically equivalent source in a different deployment; arbitrary undisclosed changes not detected |
| Fork checking decisions match direct checking | Alternating valid/false/malformed controls, each independently replayed | Pristine-parent fork/exec-startup comparison, not logical incremental proof checking |
| Complete maintenance cost is charged | Parent plus waited-child CPU totals, disjoint phases, failed endpoint probes and fallback, completion work, residual | Imports/setup/audits separate; native optimization/witness inseparable |
| Controlled checker-plus-runner resident memory was measured | Separately frozen PPid observer and held successful checker checkpoint | Does not establish an unmodified live-cache process-tree peak; initial tree sampler invalid |
| Replication agrees mathematically | Exact logical fields and raw/final proof identities; named measurement exclusions | Shared SDK; no independent toolchain installation |

Hashes are consistency identities, not authentication against a hostile process. Python, compiler/runtime, model adapter and VIPR checker remain trusted implementation components. Independent enumeration is feasible only because these instances are small.
