"""Dependency-free compact seal, archive and mathematical proof replay."""
import hashlib
import json
from pathlib import Path
import tarfile
from checker import verify
from routes import invalid_controls

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def run():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for name,info in seal['files'].items():
        data=(REPO/name).read_bytes()
        assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
    receipt=seal['archive'];archive=REPO/receipt['path'];data=archive.read_bytes()
    assert len(data)==receipt['bytes'] and hashlib.sha256(data).hexdigest()==receipt['sha256']
    manifest=json.loads((ROOT/'Archive-manifest.json').read_text())['files'];payloads={};count=0
    with tarfile.open(archive,'r:xz') as tar:
        members=tar.getmembers();assert len(members)==len(manifest)
        assert len({m.name for m in members})==len(members)
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            info=manifest[member.name];payload=tar.extractfile(member).read()
            assert len(payload)==info['bytes'] and hashlib.sha256(payload).hexdigest()==info['sha256'] and member.mode==info['mode'],member.name
            if member.name in ('primary/Proof-controls.json','replica/Proof-controls.json','primary/Freeze.json','replica/Freeze.json','primary/Mathematical-records.json','replica/Mathematical-records.json','primary/Maintenance-controls.json','replica/Maintenance-controls.json'):
                payloads[member.name]=json.loads(payload)
            count+=1
    for root in ('primary','replica'):
        dep=payloads[root+'/Freeze.json']['dependency'];proofs=payloads[root+'/Proof-controls.json']
        assert len(proofs)==227
        for r in proofs.values():
            assert verify(r['model'],r['proof'],dep)
            assert invalid_controls(r['model'],r['proof'],dep)==r['controls']
    assert payloads['primary/Proof-controls.json']==payloads['replica/Proof-controls.json']
    assert payloads['primary/Mathematical-records.json']==payloads['replica/Mathematical-records.json']
    assert payloads['primary/Maintenance-controls.json']==payloads['replica/Maintenance-controls.json']
    print('Verified',len(seal['files']),'compact files,',count,'archive members and 227 certificates per run; mathematical identities match')


if __name__=='__main__':run()
