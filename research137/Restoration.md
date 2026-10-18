# Publication restoration and provenance

The preceding conversation completed this continuation and recorded local commit
0d94be2, but public upload was blocked pending explicit approval. The user then
approved publishing the branch and evidence archive. Before that approval was
processed, the temporary workspace was reset. The original local Git object and
38,452-byte archive were unavailable; they are not claimed to have been recovered.

The sources were reconstructed from the actual code and proof text preserved in
that conversation, then frozen and executed again from a new checkout. The full
Results.json reproduces the previously recorded 567,235 bytes and SHA-256:

`f2373b658182d5287e51b163efa7448a39741fafc75c1af396452165746562f6`

This matches the full logical records, certificates, paths, bounds, queries,
controls and all-optima supplement, not merely the headline counts. A further
fresh-directory replication and standalone serialized replay are included. Both
restored formal builds compile against the same hash-verified official Lean
4.24.0 binary; successful proofs contain no sorryAx.

The restored source tree/archive have their own new identities. This is a
verified re-execution, not a claim of byte-identical source-tree or archive
recovery. The new archive contains the full restored results and formal logs;
it does not contain the lost development/preliminary records.

The formal harness now explicitly runs Lean from the copied checkout root and
requires two diagnostic errors from the two deliberately false statements.
The mathematical statements and final result encoding are unchanged. The
compatibility shim handles this host's numeric /proc PID mismatch only; it changes
no Lean proof/kernel logic. The earlier failed Lean 4.28.0 smoke attempt is not
part of the proof claim; 4.24.0 is the successful, pinned toolchain.

Earlier development included rational-string normalization and explicit Rat
annotations in arithmetic examples. The restored run starts from the final forms,
not the invalid development inputs. No data were selected based on restored
outcomes. Input construction is deterministic from seed 13720261018 and the
published research133 inputs.
