# Recovered original 300-worker campaign, experiments 101–110

This is the recovered original campaign, distinct from the published [273-worker campaign](../research101/Synthesis.md). Preserve both evidence sets.

Start with the [recovery report](Recovery-report.md), [recovery audit](Audit.json), [findings](Synthesis.md) and [assurance contract](Assurance-contract.md). The full [archive](../archives/experiments-101-110-original-300-workers.tar.xz) is 687116 bytes, SHA-256 `4a01c756935d8efda38fb7df02b9ad1caeec4cbbf3ccd8f2a568783969f5e758`. See [storage and verification](Archive-storage.json) and [recovery instructions](REPRODUCE.md).

All 403 manifest-listed files were checked from the GitHub blob readback before publication. The recovered audit accepted 21 distinct VeriPB proofs from the disclosed adaptation of the official CP 2024 knapsack implementation and rejected all 21 false-bound controls; 139 distinct native VIPR proofs and their false controls also passed. Original and archived fresh results match under the declared logical comparison.

The complete original archive is unchanged and restores a `research101/` root. Extract it into an empty directory, rather than over the existing repository's newer `research101/` directory. Large external SDKs are outside the archive; the pinned sources, identities and deployment instructions are retained.

`Recorded-Audit.json` is the original audit; `Audit.json` and `Recovery-audit.log` are the recovery replay. `Recovery-verification.json` and `Original-archive-storage.json` preserve the recovery-stage/original publication status; their earlier unconfirmed-publication fields are historical. The current remote archive verification is recorded in `Archive-storage.json`. Old handoff instructions retained inside the unchanged archive are historical documents, not new execution requests.

This recovery establishes access to the original implementation and proof evidence. It does not remeasure the original timings, independently reinstall its SDK, or establish a general DP/SCIP ranking. The newer Python DP baseline and nine native exact-SCIP certificates are separate comparisons. Update missing-evidence assessments using this recovery while retaining earlier reviews as dated records.
