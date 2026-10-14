"""Transport pieces reconstruct the previously approved archive byte for byte."""
import hashlib
import json
from pathlib import Path


def read_parts(repo, manifest):
    chunks = []
    names = set()
    for index, part in enumerate(manifest['parts'], 1):
        name = part['path']
        assert name == manifest['archive']['path'] + f'.part{index:03d}' and name not in names
        names.add(name)
        data = (Path(repo) / name).read_bytes()
        assert len(data) == part['bytes'] and hashlib.sha256(data).hexdigest() == part['sha256'], name
        chunks.append(data)
    data = b''.join(chunks)
    expected = manifest['archive']
    assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256']
    return data


def read_archive(root, expected):
    root = Path(root)
    part_file = root / 'Archive-parts.json'
    if part_file.exists():
        manifest = json.loads(part_file.read_text())
        assert manifest['archive'] == expected
        return read_parts(root.parent, manifest)
    data = (root.parent / expected['path']).read_bytes()
    assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256']
    return data


if __name__ == '__main__':
    import sys
    root = Path(__file__).resolve().parents[1]
    expected = json.loads((root / 'Archive-storage.json').read_text())
    data = read_archive(root, expected)
    destination = Path(sys.argv[1])
    assert not destination.exists(), 'Refuse to overwrite an existing reconstruction'
    destination.write_bytes(data)
    print('Reconstructed', len(data), 'approved bytes; SHA-256', hashlib.sha256(data).hexdigest())
