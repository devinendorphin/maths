"""Dependency-free compact publication and full archive member verification."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def run():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for name,info in seal['files'].items():
        p=REPO/name;data=p.read_bytes();assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
    archive=REPO/seal['archive']['path'];data=archive.read_bytes()
    assert len(data)==seal['archive']['bytes'] and hashlib.sha256(data).hexdigest()==seal['archive']['sha256']
    manifest=json.loads((ROOT/'Archive-manifest.json').read_text());count=0
    with tarfile.open(archive,'r:xz') as tar:
        members=tar.getmembers();assert len(members)==len(manifest['files'])
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            info=manifest['files'][member.name];payload=tar.extractfile(member).read();assert len(payload)==info['bytes'] and hashlib.sha256(payload).hexdigest()==info['sha256']
            assert member.mode==info['mode'];count+=1
    print('Publication verified:',len(seal['files']),'compact files and',count,'hashed archive members')


if __name__=='__main__':run()
