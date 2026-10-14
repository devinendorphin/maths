"""Validate complete roots before replacing the deterministic evidence archive."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / 'code'))
from ledger import check as ledger_check


def info(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def seal():
    files = {str(p.relative_to(REPO)): info(p.read_bytes()) for p in sorted(ROOT.rglob('*'))
             if p.is_file() and p.name != 'Publication-seal.json' and '__pycache__' not in p.parts
             and 'development-outputs' not in p.parts and not p.name.endswith('progress.json')}
    files['.github/workflows/verify-research156.yml'] = info((REPO / '.github/workflows/verify-research156.yml').read_bytes())
    receipt = json.loads((ROOT / 'Archive-storage.json').read_text())
    parts_file = ROOT / 'Archive-parts.json'
    if parts_file.exists():
        for part in json.loads(parts_file.read_text())['parts']:
            files[part['path']] = info((REPO / part['path']).read_bytes())
    (ROOT / 'Publication-seal.json').write_text(json.dumps({'archive': receipt, 'files': files}, sort_keys=True, indent=2) + '\n')


def run(primary, replica, rejected):
    if (ROOT / 'Archive-parts.json').exists():
        raise ValueError('Approved archive has sealed transport pieces; do not repack or replace its bytes')
    roots = [('primary', Path(primary)), ('replica', Path(replica))]
    for label, root in roots:
        if not root.is_dir():
            raise ValueError('Missing evidence root: ' + label)
        for name in ('Freeze.json', 'Inputs.json', 'Sessions.json', 'Audit.json', 'Logical.json', 'Accounting-summary.json'):
            if not (root / name).is_file():
                raise ValueError('Missing evidence ' + name + ': ' + label)
        sessions = json.loads((root / 'Sessions.json').read_text())
        audit = json.loads((root / 'Audit.json').read_text())
        if len(sessions) != 144 or not audit['passed'] or audit['observations'] != 7056:
            raise ValueError('Incomplete execution: ' + label)
        if any(s['exit_code'] or s['timed_out'] for s in sessions) or len({s['name'] for s in sessions}) != 144:
            raise ValueError('Invalid sessions: ' + label)
        for session in sessions:
            out = root / 'outputs' / session['name']
            if not all((out / name).is_file() for name in ('Worker.json', 'Evidence.jsonl', 'Accounting.json')):
                raise ValueError('Missing full worker evidence: ' + str(out))
            worker = json.loads((out / 'Worker.json').read_text())
            raw = (out / 'Evidence.jsonl').read_bytes()
            if len(worker['records']) != 49 or len(raw) != worker['evidence_bytes'] or list(map(json.loads, raw.splitlines())) != worker['records']:
                raise ValueError('Incomplete worker journal: ' + str(out))
            ledger_check(json.loads((out / 'Accounting.json').read_text()), session['wall_ns'])
    for name in ('Inputs.json', 'Freeze.json', 'Logical.json'):
        if (roots[0][1] / name).read_bytes() != (roots[1][1] / name).read_bytes():
            raise ValueError('Logical replication mismatch: ' + name)
    payloads = {}
    rejected = Path(rejected)
    if not (rejected / 'primary-1/Freeze.json').is_file() or not (rejected / 'development-source-1/Freeze.json').is_file():
        raise ValueError('Missing rejected execution custody')
    for label, root in roots + [('reports', ROOT), ('rejected', rejected)]:
        for path in sorted(root.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and not path.name.endswith('progress.json'):
                if label == 'reports' and path.name in ('Archive-manifest.json', 'Archive-storage.json', 'Publication-seal.json'):
                    continue
                payloads[label + '/' + str(path.relative_to(root))] = path.read_bytes()
    manifest = {name: dict(info(data), mode=0o644) for name, data in payloads.items()}
    archive = REPO / 'archives/experiments-156-159-cost-accounting.tar.xz'
    pending = archive.with_suffix('.pending')
    with tarfile.open(pending, 'w:xz', preset=6) as tar:
        for name, data in sorted(payloads.items()):
            entry = tarfile.TarInfo(name)
            entry.size, entry.mode, entry.mtime = len(data), 0o644, 0
            tar.addfile(entry, io.BytesIO(data))
    pending.replace(archive)
    receipt = dict(info(archive.read_bytes()), path=str(archive.relative_to(REPO)), members=len(manifest),
                   uncompressed_bytes=sum(map(len, payloads.values())),
                   excluded=['SDK libraries and virtualenv', 'bytecode', 'redundant progress files'])
    (ROOT / 'Archive-manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    (ROOT / 'Archive-storage.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    seal()
    print('Packaged', receipt['bytes'], 'bytes;', receipt['members'], 'members', flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['--seal-only']:
        seal()
    else:
        run(*sys.argv[1:])
