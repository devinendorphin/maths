# Development and scope before the frozen run

The Lean toolchain was absent and was obtained through a 300-second/512-MiB download gate. The official Lean 4.24.0 archive matched its release SHA-256. The distribution stays outside the repository and evidence archive. Mathlib is unnecessary for this rational theorem; `Std` is enough.

Before freezing the headline execution, development checked the theorem and independently written interface and tried one compact-witness and one checkpoint fixture. Those trials are not headline workers. Corrections during development included rational simplification, explicit positivity multiplication, list/tuple normalization when comparing reconstructed cells, and a Python import-path collision with the old `campaign` module. Failed Lean development checks were rejected; only the clean frozen compilation is evidence of acceptance.

The formal theorem covers arbitrary fixed feasible predicates and affine rational objectives for rational queries in a rational interval. It does not formalize real-number completion, JSON parsing, the Python witness checker/cache, the native optimizer, or VIPR's implementation. The scalar denominator identity is separately checked. The independently written Lean contract is checked by type ascription; Comparator is not installed or claimed executed.

The compact witness reconstructs the same native scalar certificate and is admitted through the unchanged VIPR compiler/checker. Its small serialization is not a new proof system. CP 2024 DP/VeriPB interoperability remains unimplemented; this batch records that limitation rather than claiming that route was reproduced.

The interrupted-construction test is a small exhaustive branch-tree reference. It demonstrates sound partial bounds and invalidation, not faster native solver resumption. Frozen native production is deliberately capped once, cleaned up, and followed by a freshly checked fallback.
