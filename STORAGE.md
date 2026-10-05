# Evidence storage and recovery

The complete recovered 31–35 archive and rebuilt 36–40 archive are in [Google Drive](https://drive.google.com/drive/folders/1xbG-aDtuDe8cRzVX_jyGT7JF5bv6CbqJ). The repository keeps the working sources, protocols, all declared 36–40 inputs, reports, selection/timing summaries, compact diagnostics and a small review kit.

## Verified backups

| Archive | Bytes | Recovery pieces | Drive location |
|---|---:|---:|---|
| Recovered experiments 31–35 | 176,127,453 | 8 ZIP files | [Baseline folder](https://drive.google.com/drive/folders/1lS6VPt5pFe8qAUaZSHm-zHpqR1NUFx_f) |
| Rebuilt experiments 36–40 | 1,640,269,628 | 69 ZIP files | [Rebuild folder](https://drive.google.com/drive/folders/1v3tgJO938AVY6dOvppsCFH9MYqPXEsOk) |
| Small review kit | 423,340 | 1 tar.xz file | [Review kit](https://drive.google.com/file/d/1-wPROcWMQV940W2N953UUXMux-7gdAXh/view?usp=drivesdk) |

The Drive upload connection accepts files up to 100 MB, and workspace downloads accept files up to 32 MiB. Existing 24 MB recovery pieces fit both limits. These pieces preserve the complete original archives byte for byte; they are not abbreviated results.

Every one of the 77 pieces was downloaded back from Drive and checked against its original size and SHA256. Both archives were reassembled exclusively from those downloads. All 8,275 baseline manifest entries, all 566,956 rebuild manifest entries and all 199 review-kit manifest entries passed their content checks. See [Drive-archive-verification.json](Drive-archive-verification.json).

[Archive-storage.json](Archive-storage.json) records the observed Drive folder/file IDs and URLs, original archive checksums, and checksums for every container and payload. Drive access permissions are unchanged; access to these archives requires access to the owner's Drive.

## Download and reassemble

Download all the files from the appropriate Drive recovery folder. If Drive wraps the folder in a ZIP download, extract that outer ZIP first. Keep the part ZIPs, `Parts-manifest.json` and `reassemble.py` together, then run:

```sh
python3 reassemble.py
```

The script checks every container and payload and verifies the final archive's size and SHA256. It refuses to overwrite an existing output. A missing or changed piece causes an error; never bypass the checks.

To restore the detailed evidence into this checkout:

```sh
python3 scripts/restore_archives.py --baseline /path/to/Temporal-proof-experiments-31-35-campaign.zip --rebuild /path/to/Temporal-proof-experiments-36-40-rebuild.tar.xz
```

The helper checks original archive identities, preserves differing existing files by refusing to overwrite them, and restores the original directory layout. Add `--verify-only` to check the archives without extracting them. See [REPRODUCE-36-40.md](REPRODUCE-36-40.md) for a fresh campaign.

## What changed

The repeated checkpoints, detailed event/construction/audit records, expanded prior checkpoint history and large recovery pieces live in the verified archives. The compact working collection preserves the selected original files byte for byte. [Compact-source-manifest.json](Compact-source-manifest.json) records their original Git blob identifiers; `python3 scripts/verify_compact.py` checks them.

No experiment was rerun and no mathematical result was changed. The original archive and campaign manifests remain inside the complete backups. Forty stopped frontier constructions remain incomplete even though their scalar fallback observation windows completed. The three retained reports of the lost original 36–40 campaign remain reports; the lost original archive was not recovered.

With the repository owner's explicit approval, main was replaced by a new root commit containing the verified compact collection. Temporary branches retaining the previous history were removed. Mathematical sources and complete archived evidence were preserved. GitHub controls when unreachable objects and its reported repository size are reclaimed; old commit URLs are historical identifiers rather than supported recovery locations. See History-cleanup.json.

