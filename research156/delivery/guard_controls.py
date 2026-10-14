"""Missing accepted evidence must not overwrite a complete delivery archive."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from package import run, ROOT, REPO


def test(primary, replica, rejected):
    archive = REPO / 'archives/experiments-156-159-cost-accounting.tar.xz'
    before = hashlib.sha256(archive.read_bytes()).hexdigest()
    names = []
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        try:
            run(root / 'missing-root', replica, rejected)
        except ValueError:
            names.append('missing-root-refuses-before-write')
        else:
            raise AssertionError('Missing root accepted')
        partial = root / 'partial'
        partial.mkdir()
        for name in ('Freeze.json', 'Inputs.json', 'Sessions.json', 'Audit.json', 'Logical.json', 'Accounting-summary.json'):
            shutil.copyfile(Path(primary) / name, partial / name)
        try:
            run(partial, replica, rejected)
        except ValueError:
            names.append('missing-worker-refuses-before-write')
        else:
            raise AssertionError('Missing worker accepted')
    after = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert before == after
    report = {'passed': True, 'excluded_from_headline': True, 'controls': names,
              'tested_candidate_before_and_after_sha256': before}
    (ROOT / 'Delivery-controls.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Passed both delivery refusal controls; existing archive unchanged')


if __name__ == '__main__':
    import sys
    test(*sys.argv[1:])
