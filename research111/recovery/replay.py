"""Replay the disclosed auditor against an extracted original campaign."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def main():
    original=Path(sys.argv[1]).resolve()
    setup=json.loads((ROOT/'Checker-setup.json').read_text())
    source=Path(setup['source']);freeze=json.loads((ROOT/'Replay-freeze.json').read_text())
    for name,digest in freeze['official_python_sources'].items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
    for name,digest in setup['binaries'].items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
    auditor=ROOT/'portable_audit.py'
    assert hashlib.sha256(auditor.read_bytes()).hexdigest()==freeze['files']['portable_audit.py']
    target=original/'code/portable_audit.py';target.write_bytes(auditor.read_bytes())
    env=dict(os.environ,PYTHONPATH=str(source),PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([setup['python'],str(target)],cwd=original,env=env,timeout=300,check=True)


if __name__=='__main__':main()
