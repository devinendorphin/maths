# Reproduce the rebuilt experiments 36–40

Use Python 3.12 and the standard library. This compact repository retains the unchanged mathematical sources and all declared 36–40 inputs. Detailed archived records must be restored when needed.

## Restore the baseline first

Clone a small current checkout:

```sh
git clone --depth 1 https://github.com/devinendorphin/maths.git
cd maths
export PYTHONDONTWRITEBYTECODE=1
```

Download all eight baseline ZIP pieces plus `Parts-manifest.json` and `reassemble.py` from the [Drive baseline folder](https://drive.google.com/drive/folders/1lS6VPt5pFe8qAUaZSHm-zHpqR1NUFx_f). Keep them together and run `python3 reassemble.py` there. Then:

```sh
python3 scripts/restore_archives.py --baseline /path/to/Temporal-proof-experiments-31-35-campaign.zip
python3 scripts/recover_campaign_31_35.py
```

Restoration verifies the original size and SHA256 and restores the entire checkpoint, including its manifest and older nested archive. The second command checks imported checkpoint integrity without replaying old experiments. Disabling bytecode caches prevents Python from adding files that would invalidate the baseline's file-set check.

For inspection of the rebuilt campaign's complete proofs and saved states, download its 69 pieces plus reassembly files from the [Drive rebuild folder](https://drive.google.com/drive/folders/1v3tgJO938AVY6dOvppsCFH9MYqPXEsOk), run its reassembly script, and restore:

```sh
python3 scripts/restore_archives.py --rebuild /path/to/Temporal-proof-experiments-36-40-rebuild.tar.xz
```

This is optional for a fresh run after the complete baseline has been restored. See [STORAGE.md](STORAGE.md) and [Archive-storage.json](Archive-storage.json) for all file locations and checksums.

## Start a fresh campaign

Preserve the saved campaign. Copy its unchanged source and handoff to a new output directory:

```sh
mkdir research36-reproduction
cp -a research36-rebuild/code research36-reproduction/code
cp research36-rebuild/Handoff.md research36-reproduction/Handoff.md
export MATHS_RESEARCH_ROOT="$PWD/research36-reproduction"
python3 "$MATHS_RESEARCH_ROOT/code/campaign.py" prepare
python3 "$MATHS_RESEARCH_ROOT/code/campaign.py" run --batch-seconds 900
```

Repeat the bounded final command until the new directory contains `Archive-verification.json`. Keep `PYTHONDONTWRITEBYTECODE=1` throughout. The controller reuses completed policy results and audit ranges. It refuses to replay a policy interrupted inside an unfinished action; such a case requires exact continuation from its evidence. A frontier stopped by its frozen guard remains incomplete even if scalar fallback completes its observation window. Do not raise a cap to relabel a stopped construction complete.

The declared matrix has 832 unique trajectories and 3,328 headline paths. The 1,152 timing workers and 216 selector-tuning workers are separate. Stage 39 seals selection before held-out execution; stage 40 carries that selection byte-identically. CPU and timing-selected thresholds can vary by environment.

The mathematical source has not been modified to optimize recordkeeping. A fresh full campaign will still generate substantial detailed evidence; choose a separate output/storage location. Older archived instructions and the immutable review kit describe the original expanded repository. This document and [STORAGE.md](STORAGE.md) describe its compact replacement.

The original lost 36–40 campaign cannot be reproduced or cross-validated proof by proof from its three retained aggregate reports. Supplemental diagnoses and the later-window failure fixture did not supply algorithm or selector decisions. No worst-case efficiency or new arithmetic claim follows from these finite experiments.

