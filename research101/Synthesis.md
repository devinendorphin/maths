# Experiments 101–110: an exact DP baseline and checked production candidates

Completed 9 October 2026. A simple capacity-indexed 0/1 dynamic program, with a separately implemented exact recurrence checker, was the fastest implemented checked path on all eight matched dense/sparse records in both executions. This materially strengthens the baseline against which interval reuse should be judged on small-capacity knapsack. It establishes neither a new algorithm nor general competitiveness.

All 273 workers completed across ten experiments and eight mathematical models: six deterministic signed-affine n=8/12/16 fixtures, a tied/sign-changing fixture, and a zero-capacity fixture. Many workers reuse models, times and controls; 273 is not an independent sample size. The headline campaign took 1.95 seconds; its independent audit took 0.75 seconds. A fresh isolated replication completed and matched every Results.json field except top-level CPU/wall times. Both audits passed.

## 101–105: baseline capabilities and limits

**101** produced and admitted 24 exact DP tables: eight models at t=0,4,8. The certificate includes all prefix/capacity values, original weights/capacity/affine coefficients and rational query, plus an optimal feasible packing. The checker validates initialization, every recurrence, model binding and packing/objective agreement using integer arithmetic. It does not import the producer. The final auditor independently enumerates original feasible subsets.

**102** solved those same 24 point inputs with ordinary SCIP 10.0.0 through PySCIPOpt 6.0.0. Every candidate packing matched the independently admitted DP upper certificate. The wheel rejected `enableExactSolving(True)` because it was compiled without exact solve support. This is a successful production candidate path with exact external DP checking, not an exact-mode SCIP result. No presolve certificate, native SCIP proof log or reoptimization result is claimed. Integer coefficient magnitudes are small and exactly representable in the floating API; no arbitrary rational-input guarantee follows.

**103** scaled weights and capacity by 1,4,16 on all eight models. All 24 objectives remained unchanged, as independently verified. Certificate growth exposes the pseudopolynomial dependence on capacity: n16-s1 grew from 969 cells/3,486 JSON bytes to 15,249 cells/49,318 bytes. The zero-capacity case stayed at nine cells. The full-cost comparison uses the unscaled models; these scale measurements do not establish a DP/VIPR crossover.

**104** checked 18 point inputs on the tie and zero-capacity fixtures. Signed/zero objectives selected valid optima, including empty solutions; ties need not select the same packing across solvers. **105** checked 24 rational inputs at 1/3,7/5,15/2 through integer denominator scaling, with exact original-problem enumeration. Both extend implementation coverage rather than prove new mathematical results.

## 106–109: admission, caps and reuse

**106** rejected all 144 corrupted certificates: altered base table, interior cell, final cell, scaled coefficients, out-of-range packing and changed time, on every baseline point. The independent auditor also rejected them. These are deliberate controls, not a claim of comprehensive hostile-input security or formal verification.

**107** recorded eight expected one-cell-cap incompletes, never admitted them, then completed at the exactly sufficient cell budget. The failed preallocation check and fresh fallback are charged. This tests resource gating, not interrupted native solver recovery or partial DP bounds.

**108** rejected old certificates on 15 actual capacity changes and produced fresh valid ones. One restricted-capacity case retained a feasible old optimal packing and transferred its optimum correctly. Expansions never use the subset-transfer rule. The zero-capacity unchanged case is excluded: the first attempted run exposed an incorrect expectation of rejection there, and that driver correction plus the aborted source/log is preserved in the archive.

**109** compared 15 observations per model, fresh DP versus memoized exact point certificates. Memoization built three tables and readmitted them on 12 hits; both returned identical answers and memoization was faster in both runs on all eight models. This is a single execution of each path per campaign, not the three-repetition timing protocol of 110. Model/time applicability and complete recurrence checking are charged; this does not implement an unchecked immutable-cache shortcut.

## 110: full-cost comparison

Median CPU milliseconds over three rotated repetitions, including child checker CPU, proof serialization and file I/O:

| Model / stream | DP + checker | SCIP + DP checker | VIPR points | VIPR intervals |
|---|---:|---:|---:|---:|
| n8-s0 / dense 9 | 1.69 | 19.25 | 27.95 | 13.59 |
| n8-s0 / sparse 3 | 0.62 | 6.68 | 10.52 | 14.69 |
| n12-s0 / dense 9 | 2.94 | 20.33 | 39.63 | 22.69 |
| n12-s0 / sparse 3 | 1.13 | 9.36 | 13.84 | 23.06 |
| n16-s0 / dense 9 | 3.54 | 24.12 | 111.98 | 78.25 |
| n16-s0 / sparse 3 | 1.27 | 7.29 | 33.41 | 77.78 |
| ties / dense 9 | 1.23 | 17.14 | 24.65 | 8.46 |
| ties / sparse 3 | 0.54 | 6.01 | 7.27 | 7.79 |

Fresh-run medians and raw certificate byte counts are retained in Summary.json. DP was fastest in all eight records again. SCIP added cost when DP was already needed to supply the exact certificate. VIPR intervals beat VIPR points on all four dense streams and lost on all four sparse streams in both executions, yet neither beat DP here.

These paths provide different checker implementations and evidence formats. The DP result is a full recurrence transcript checked by Python; VIPR provides an established external original-problem proof checker, and interval reuse inherits the separately Lean-checked conditional theorem. A timing advantage for DP does not imply that these assurance contracts are interchangeable or that one implementation is formally verified. Ordinary SCIP plus DP still incurs DP construction, so this is not a test of native SCIP proof efficiency. Imports, dependency installation, independent audit and packaging are outside per-path timings. Deployment installation was performed but not timed. No statistical significance, broad scalability or novelty claim follows.

## Independent evidence and next direction

Each audit passed 1,716 answer checks and admitted 569 DP certificates, rejected all 144 deliberately corrupted DP tables, and accepted 42 distinct VIPR proofs while rejecting 42 weakened-final-bound controls. There were 115 distinct model/query oracle combinations; verification counts are repeated checks. The auditor imports none of DP, its checker or SCIP, and independently enumerates feasible subsets. Both completed executions and the aborted attempt are in the verified 256,316-byte archive.

The production solver gap is narrowed to a tested candidate path, while exact SCIP and exact/reoptimization compatibility remain open. The CP 2024 certifying-DP implementation, VeriPB interoperability and formally verified DP checking remain unimplemented. The next useful work is a bounded large-capacity crossover study or a properly built exact/proof-logging production baseline, rather than another broad cache-gate sweep. Preserve the strongest DP baseline in future cost comparisons.
