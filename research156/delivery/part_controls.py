"""A missing, corrupt or reordered transport piece must be rejected."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from archive_parts import read_parts


def run():
    names = []
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        prefix = 'evidence.tar.xz'
        chunks = [b'first-raw-bytes', b'second-raw-bytes']
        manifest = {'archive': {'path': prefix, 'bytes': sum(map(len, chunks)),
                    'sha256': hashlib.sha256(b''.join(chunks)).hexdigest()}, 'parts': []}
        for i, data in enumerate(chunks, 1):
            path = prefix + f'.part{i:03d}'
            (repo / path).write_bytes(data)
            manifest['parts'].append({'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        assert read_parts(repo, manifest) == b''.join(chunks)
        def reject(name, value):
            try:
                read_parts(repo, value)
            except (AssertionError, FileNotFoundError):
                names.append(name)
            else:
                raise AssertionError('Invalid parts accepted: ' + name)
        reordered = copy.deepcopy(manifest)
        reordered['parts'].reverse()
        reject('reject-reordered-pieces', reordered)
        (repo / manifest['parts'][1]['path']).unlink()
        reject('reject-missing-piece', manifest)
        (repo / manifest['parts'][1]['path']).write_bytes(b'corrupt')
        reject('reject-corrupt-piece', manifest)
        (repo / manifest['parts'][1]['path']).write_bytes(chunks[1])
        wrong = copy.deepcopy(manifest)
        wrong['archive']['sha256'] = '0' * 64
        reject('reject-wrong-whole-archive', wrong)
    report = {'passed': True, 'excluded_from_headline': True, 'controls': names}
    root = Path(__file__).resolve().parents[1]
    (root / 'Part-controls.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Passed four transport corruption/refusal controls')


if __name__ == '__main__':
    run()
