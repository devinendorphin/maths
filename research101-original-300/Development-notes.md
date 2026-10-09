# Pre-freeze dependency and adapter development

PySCIPOpt 6.0.0, Cython 0.29.37, pybind11 2.13.6 and CMake 3.31.6 were installed outside Git. The small standalone CP knapsack program does not need CMake. Downloads, source commits and setup outcomes are retained.

The old GitHub VeriPB mirror compiled but supports proof format 1; CP 2024 emits format 2. The pinned official GitLab version2 source was obtained. Its complete extension build hit the declared 180-second parent-command cap. Completed native extensions were recovered and the remaining unchanged Python modules are interpreted. No verification rules were edited or disabled. Package metadata was generated separately. This mixed deployment successfully checks the adapted CP smoke proof; runtime file identities are frozen.

An initial SCIP exact probe used an incorrect argument signature and was corrected during development. The proper `enableExactSolving(True)` invocation reports that this wheel was built without exact support. Objective reoptimization and continuation after a zero-node cap were exercised successfully. These smoke checks are not headline workers.

The published CP program generates random positive-profit data. The adapter supplies deterministic items, uses absolute profits for a valid signed-profit big-M, and prints negated coefficients as signed integers rather than double minus signs. Explicit auxiliary threshold/conjunction truth values are added to its solution line, then checked by VeriPB. The independent audit separately reconstructs the original point model and enumerates all feasible subsets.

The checker wrapper must propagate the checker return code and require its explicit success output. A prototype wrapper failed to propagate the return code; this was corrected before freezing. Malformed signed serialization and incomplete auxiliary assignments were rejected during development. No failed development proof is counted as an accepted result.

The immutable snapshot holds model tuples and candidate intervals admitted from accepted endpoint facts. It does not repeatedly load disk witnesses. Its trust boundary is a fixed admitted model and a dependency epoch supplied at stream start; a change in external disk copies need not revoke unchanged captured facts. Model/epoch changes require new admission. This is ordinary trusted Python code, not a new formal verification result.
