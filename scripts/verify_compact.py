#!/usr/bin/env python3
"""Check retained files against the previous Git tree and archived evidence receipts."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'Compact-source-manifest.json').read_text())
for record in manifest['files']:
    data = (root / record['path']).read_bytes()
    digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert digest == record['git_blob_sha'], record['path']
storage = json.loads((root / 'Archive-storage.json').read_text())
verification = json.loads((root / 'Drive-archive-verification.json').read_text())
assert verification['passed'] and verification['all_77_drive_part_hashes_verified']
assert verification['baseline_manifest_members_verified'] == 8275
assert verification['rebuild_manifest_members_verified'] == 566956
assert verification['review_kit_manifest_members_verified'] == 199
assert not verification['experiments_rerun']
for kind, count in [('baseline', 8), ('rebuild', 69)]:
    backup = storage['archives'][kind]
    assert len(backup['parts']) == count
    assert all(row['roundtrip_verified'] for row in backup['parts'])
    expected = next(row for row in verification['archives'] if row['filename'] == backup['filename'])
    assert expected['bytes'] == backup['bytes'] and expected['sha256'] == backup['sha256']
    assert sum(row['payload_bytes'] for row in backup['parts']) == backup['bytes']
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).split(b'\0')
files = [root / name.decode() for name in tracked if name]
print(json.dumps({'passed': True, 'unchanged_files_checked': len(manifest['files']), 'tracked_files': len(files), 'tracked_bytes': sum(p.stat().st_size for p in files), 'math_experiments_rerun': False}, indent=2))
