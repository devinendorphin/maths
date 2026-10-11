"""Delivery-only controls, excluded from the frozen scientific campaign."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from package import run

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def test(primary,replica):
    archive=REPO/'archives/experiments-148-151-capacity-needs.tar.xz'
    before=hashlib.sha256(archive.read_bytes()).hexdigest();names=[]
    with tempfile.TemporaryDirectory(prefix='maths148-package-') as tmp:
        absent=Path(tmp)/'absent'
        try:run(str(absent),replica)
        except ValueError as error:assert 'missing evidence root' in str(error)
        else:raise AssertionError('missing root accepted')
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==before;names.append('missing-root-preserves-archive')
        incomplete=Path(tmp)/'incomplete';incomplete.mkdir()
        for name in ('Freeze.json','Inputs.json','Sessions.json','Logical.json','Controls.json','Audit.json'):
            shutil.copyfile(Path(primary)/name,incomplete/name)
        try:run(str(incomplete),replica)
        except ValueError as error:assert 'missing worker evidence' in str(error)
        else:raise AssertionError('missing workers accepted')
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==before;names.append('missing-worker-preserves-archive')
    (ROOT/'Delivery-controls.json').write_text(json.dumps({'passed':True,'excluded_from_headline':True,'controls':names,
                                                           'archive_before_after_sha256':before},sort_keys=True,indent=2)+'\n')
    print('Passed',len(names),'delivery custody controls; archive unchanged')


if __name__=='__main__':test(*sys.argv[1:])
