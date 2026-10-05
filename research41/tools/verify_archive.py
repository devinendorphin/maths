"""Verify a downloaded campaign tar.xz, including every manifest member."""
import argparse
import hashlib
import json
import tarfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('--sha256');args=p.parse_args()
    h=hashlib.sha256(Path(args.archive).read_bytes()).hexdigest()
    if args.sha256: assert h==args.sha256,'archive hash mismatch'
    with tarfile.open(args.archive,'r:xz') as tar:
        files={m.name:m for m in tar if m.isfile()}
        manifest=json.load(tar.extractfile(files['Archive-manifest.json']))
        assert set(files)==set(manifest['members'])|{'Archive-manifest.json'}
        for name,record in manifest['members'].items():
            b=tar.extractfile(files[name]).read()
            assert len(b)==record['bytes'] and hashlib.sha256(b).hexdigest()==record['sha256'],name
    print(json.dumps(dict(passed=True,archive_sha256=h,members=len(manifest['members']))))

if __name__=='__main__': main()
