"""Recover the supplied 31–35 archive without executing research code."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import runpy
import stat
import zipfile

EXPECTED_SHA = "656930b55f767e811089a8b345abb1cbf228559dd13afaf4be770d4c7c4f7b9f"
EXPECTED_BYTES = 176127453
KIT_SHA = "2a70b0fcfb5796a8f4ed8c25e03776b5ae267049c1f3008fcdbdfee5b4181d02"
DEST = Path("campaigns/experiments-31-35")


def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def safe_path(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or not p.parts:
        raise ValueError(f"Unsafe archive path: {name}")
    return p


def manifest_records(manifest):
    rows = manifest
    if isinstance(manifest, dict):
        for key in ("files", "members", "entries"):
            if key in manifest:
                rows = manifest[key]
                break
    result = {}
    iterable = rows.items() if isinstance(rows, dict) else ((None, r) for r in rows)
    for name, row in iterable:
        if isinstance(row, str) and name is not None:
            checksum, size = row, None
        elif isinstance(row, dict):
            name = name or row.get("path") or row.get("file") or row.get("name")
            checksum = row.get("sha256")
            size = row.get("bytes", row.get("size_bytes", row.get("size")))
        else:
            raise ValueError("Unsupported manifest entry")
        if not isinstance(name, str) or not isinstance(checksum, str) or len(checksum) != 64:
            print("Manifest schema preview:", str(manifest)[:2500])
            raise ValueError("Unsupported manifest schema")
        safe_path(name)
        if name in result:
            raise ValueError(f"Duplicate manifest path: {name}")
        result[name] = (checksum, size)
    return result


def main():
    if DEST.exists():
        verify_imported()
        return
    kit_path = Path("handoffs/Campaign-31-35-reassembly-kit.zip")
    with kit_path.open("rb") as stream:
        assert digest(stream) == KIT_SHA, "Reassembly kit differs from inspected version"
    work = Path(".recovery-work")
    work.mkdir(exist_ok=True)
    kit = work / "kit"
    kit.mkdir(exist_ok=True)
    with zipfile.ZipFile(kit_path) as z:
        assert set(z.namelist()) == {"README.md", "reassemble.py", "Parts-manifest.json", "SHA256SUMS.txt", "Verification.json"}
        z.extractall(kit)
    namespace = runpy.run_path(str(kit / "reassemble.py"))
    # Use the inspected reassembly function and its original manifest.
    (Path("handoffs") / "Parts-manifest.json").write_bytes((kit / "Parts-manifest.json").read_bytes())
    archive = work / "Temporal-proof-experiments-31-35-campaign.zip"
    namespace["reassemble"](Path("handoffs"), archive)
    assert archive.stat().st_size == EXPECTED_BYTES
    with archive.open("rb") as stream:
        assert digest(stream) == EXPECTED_SHA
    if DEST.exists():
        raise ValueError(f"Refusing to overwrite an existing campaign: {DEST}")
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos if not i.is_dir()]
        assert len(names) == len(set(names)), "Duplicate archive names"
        assert len(names) == 8276, f"Unexpected member count: {len(names)}"
        for info in infos:
            safe_path(info.filename)
            assert not stat.S_ISLNK(info.external_attr >> 16), "Symlink archive member"
        manifest = json.loads(z.read("Manifest.json"))
        print("Manifest shape:", list(manifest)[:10] if isinstance(manifest, dict) else type(manifest).__name__)
        records = manifest_records(manifest)
        assert len(records) == 8275
        assert set(records) == set(names) - {"Manifest.json"}, "Manifest/archive member mismatch"
        for name, (expected, size) in records.items():
            with z.open(name) as stream:
                assert digest(stream) == expected, f"Hash mismatch: {name}"
            if size is not None:
                assert z.getinfo(name).file_size == size, f"Size mismatch: {name}"
        print(f"Verified {len(records)} manifest member hashes")
        skipped = []
        for info in infos:
            if info.is_dir():
                continue
            # Large nested archives remain exactly recoverable from the preserved parts.
            if info.file_size > 90 * 1024 * 1024:
                skipped.append({"path": info.filename, "bytes": info.file_size, "sha256": records[info.filename][0]})
                continue
            target = DEST.joinpath(*safe_path(info.filename).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as source, target.open("xb") as output:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    output.write(chunk)
        report = {
            "archive": archive.name, "archive_bytes": EXPECTED_BYTES,
            "archive_sha256": EXPECTED_SHA, "part_count": 8,
            "archive_file_members": len(names), "manifest_members_verified": len(records),
            "all_member_hashes_verified": True, "imported_files": len(names) - len(skipped),
            "large_members_preserved_in_parts": skipped, "failures": [],
            "scope": "Byte-integrity recovery only; no experiments rerun or mathematical audits executed.",
        }
    Path("RECOVERY-31-35.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print("Top-level recovered paths:", sorted(p.name for p in DEST.iterdir()))


def verify_imported():
    manifest = manifest_records(json.loads((DEST / "Manifest.json").read_text()))
    assert len(manifest) == 8275
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob("*") if p.is_file()}
    assert actual == set(manifest) | {"Manifest.json"}, "Imported file set differs"
    for name, (expected, size) in manifest.items():
        path = DEST.joinpath(*safe_path(name).parts)
        with path.open("rb") as stream:
            assert digest(stream) == expected, f"Imported hash mismatch: {name}"
        if size is not None:
            assert path.stat().st_size == size
    frozen_counts = {}
    for stage in range(31, 36):
        root = DEST / "research" / "stages" / str(stage)
        frozen = json.loads((root / "Frozen.json").read_text())
        for name, expected in frozen.items():
            with root.joinpath(*safe_path(name).parts).open("rb") as stream:
                assert digest(stream) == expected, f"Frozen source mismatch: stage {stage}, {name}"
        frozen_counts[str(stage)] = len(frozen)
    stage34 = DEST / "research" / "stages" / "34"
    amendment = json.loads((stage34 / "Freeze-amendment.json").read_text())
    initial = json.loads((stage34 / "Frozen-initial.json").read_text())
    current = json.loads((stage34 / "Frozen.json").read_text())
    for name, change in amendment["changes"].items():
        assert initial[name] == change["before"]
        assert current[name] == change["after"]
        with stage34.joinpath(*safe_path(change["prior_source"]).parts).open("rb") as stream:
            assert digest(stream) == change["before"], f"Prior amendment source mismatch: {name}"
    nested = DEST / "supplied" / "Temporal-proof-five-experiment-campaign.zip"
    with nested.open("rb") as stream:
        nested_sha = digest(stream)
    assert nested_sha == "bb2469796172764663afa5e081c2de5b42607c8b30bae8e1333c8cbe93428ad8"
    resume = json.loads((DEST / "research" / "Resume-cursors.json").read_text())
    assert all(isinstance(v, list) and not v for v in resume.values()), "Unexpected pending work"
    path = Path("RECOVERY-31-35.json")
    report = json.loads(path.read_text())
    report.update({
        "imported_member_hashes_verified": len(manifest),
        "frozen_members_verified_by_stage": frozen_counts,
        "prior_stage34_sources_verified": len(amendment["changes"]),
        "nested_checkpoint_sha256_verified": nested_sha,
        "resume_pending_lists_empty": True,
    })
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
