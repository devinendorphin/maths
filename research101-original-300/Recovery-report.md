# Recovered original CP 2024 comparison and 300-worker campaign

Recovery checked 9 October 2026 (America/New_York). This report records a recovery, not a new headline experiment.

The original archive survived in the preceding session's workspace. The earlier publication operation was interrupted; no branch update for this archive was confirmed. The repository now contains a different 273-worker campaign under the same batch numbers and archive basename. That filename collision must not be treated as evidence identity.

Recovered archive: `/workspace/maths-storage/experiments-101-110-original-300-workers.tar.xz` (a renamed byte-identical copy).

- Bytes: 687116.
- SHA-256: `4a01c756935d8efda38fb7df02b9ad1caeec4cbbf3ccd8f2a568783969f5e758`.
- Members: 404; all 403 individually listed file hashes and lengths verified.
- Published 273-worker archive: 256316 bytes, SHA-256 `caed8f982a8e57044e8ab1f9c8867947e5f3a474803f6454a831a97836419dc2`.

The recovered archive was restored to `/workspace/maths-recovered-101-110/research101`. Its original audit was preserved as `Recorded-Audit.json`; `Audit.json` and `Recovery-audit.log` contain the recovery replay. `Recovery-verification.json` records the new checks. These sidecars are outside the unchanged original archive.

The full recovered auditor was rerun successfully, with all frozen campaign files and 107 external runtime file identities checked. It accepted 139 distinct native VIPR proofs and **21 distinct headline VeriPB proofs**, and rejected all corresponding false-bound controls. It independently enumerated the eight small models and checked 6239 answers. Original and archived fresh results also match after the explicitly listed timing/seal exclusions; underlying proof and witness hashes remain compared. This validates retained evidence, not a new timing measurement or independently installed SDK.

## Which CP implementation this is

Demirović et al.'s CP 2024 paper, *Pseudo-Boolean Reasoning About States and Transitions to Certify Dynamic Programming and Decision Diagram Algorithms*, DOI `10.4230/LIPIcs.CP.2024.9`, supplies the knapsack proof-producing DP used here.

Official supplement: https://github.com/ciaranm/cp2024-dynamic-programming-supplement/tree/CP2024

Pinned commit: `9b915e8e959e07ed2c096582c3dcb605ce0269e7`.

The retained upstream download archive hash matches its original receipt. The adapted C++ code, binary, input files, OPB formulas, original producer proofs, auxiliary-solution-expanded proofs, source patch and build receipts are present. This is distinct from the newer instance's Python DP checker.

Adaptations supply fixed items instead of the random benchmark generator, use absolute signed profits in the big-M, print signed coefficients correctly and explicitly assign auxiliary solution flags before VeriPB checking. No unchanged-paper-benchmark reproduction is claimed. The headline model at each point is independently reconstructed and exhaustively audited. The checker is the frozen official VeriPB v2 source with fifteen completed native extensions and remaining unchanged interpreted modules; the capped build and recovery are disclosed.

## What is now supported, and what remains

The statement that the original adaptation and 21-proof verification have no recovered supporting evidence is now outdated. Their supporting evidence has been recovered, its identity verified, and the actual proofs successfully rechecked.

The original per-worker timing records are also recovered, but the recovery audit does not remeasure their CPU costs. Those comparisons charge point-model adaptation/encoding, producer, proof I/O, solution expansion and checker child CPU within a deployed environment. One-time software adaptation/development and dependency installation were recorded separately, not included in each worker's headline total. Whether another proposed comparison requires amortizing those one-time costs must be specified explicitly.

The original small-instance process-per-proof CP comparison is not the same experiment as the faster newer Python DP baseline. Their timing findings cannot be merged into a single DP claim. Nor do the newer nine native SCIP certificates verify this CP implementation; they address a separate comparison.

For the newer instance: preserve both campaigns; import this recovery under a distinct name, such as `research101-original-300` and `archives/experiments-101-110-original-300-workers.tar.xz`. Do not overwrite the published 273-worker campaign or silently replace its archive. Read the recovered Protocol, adaptation, Assurance-contract and REPRODUCE files before deciding which new matched comparisons remain necessary. Update the evidence inventory and historical missing-evidence statements, retaining the prior review as a dated record.

The archive excludes the large external SDK installations. A different environment must obtain the pinned dependencies and disclose changed paths/build identities; do not bypass freezes silently. Proof validity can be separately assessed under a newly identified checker deployment without pretending it is the original timed environment.
