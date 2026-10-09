# Fresh replication of experiments 96–100

Run on 2026-10-09 in the published cloud environment. All 116 workers completed on 28 inputs. The independent audit passed 2,400 answer checks, 655 endpoint checks and 521,882 feasible coverage checks. All 93 valid VIPR proofs passed; all 93 weakened-bound controls were rejected. Endpoint and Spec compiled with Lean 4.24.0 without sorryAx. The invalid RejectedStatement was rejected as intended.

The JSON files retain the fresh results and validation receipts. `complete-run.tar.xz` preserves the complete run, including frozen sources, dependencies, inputs and generated evidence; reproducible Python caches and Lean object files are excluded. `Replication-receipt.json` records the source commit, archive checksum and member checksums. Archive members were read back and compared byte for byte with the run directory.

To independently re-audit, verify the archive SHA-256, extract it into a new directory, and run `PYTHONDONTWRITEBYTECODE=1 python3 code/audit.py` from its `research96/` directory. This writes a new Audit.json in the extracted copy. To repeat the campaign, follow ../../REPRODUCE.md and create a fresh copy from Freeze.json. Lean is an external dependency at the path recorded in Lean-setup.json.

This is a replication of the existing experiments, not a new experimental batch. No comparison of runtime performance or equality with the original results is claimed here. Original repository evidence is preserved.
