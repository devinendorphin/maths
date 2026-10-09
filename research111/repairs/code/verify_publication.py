"""Read-only verification of compact publication and both preserved/new archives."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for name,expected in seal['files'].items():
        assert sha((REPO/name).read_bytes())==expected,name
    counts=[]
    for receipt_file in [REPO/'research111/Archive-storage.json',ROOT/'Archive-storage.json',REPO/'research101-original-300/Archive-storage.json',REPO/'research111/recovery/Archive-storage.json']:
        receipt=json.loads(receipt_file.read_text());p=REPO/receipt['path']
        assert p.stat().st_size==receipt['bytes'] and sha(p.read_bytes())==receipt['sha256']
        with tarfile.open(p) as t:
            members={};executables=set()
            for m in t:
                if m.isfile():
                    members[m.name]=t.extractfile(m).read()
                    if m.mode & 0o111:executables.add(m.name)
        if 'executable_members' in receipt:
            assert executables==set(receipt['executable_members'])
        listed=receipt.get('members_manifest',receipt.get('members'))
        if listed is None and 'archive_root' in receipt:
            prefix=receipt['archive_root']
            manifest_name=prefix+'Archive-members.json'
            manifest=json.loads(members[manifest_name])['files']
            listed=[dict(path=prefix+name,**metadata) for name,metadata in manifest.items()]
            assert set(members)=={m['path'] for m in listed}|{manifest_name}
        if isinstance(listed,dict):
            listed=[dict(path=name,**metadata) for name,metadata in listed.items()]
        if isinstance(listed,list):
            for member in listed:
                assert len(members[member['path']])==member['bytes'] and sha(members[member['path']])==member['sha256'],member['path']
        else:raise AssertionError('missing member manifest')
        if 'Archive-members.json' in members:
            manifest=json.loads(members['Archive-members.json'])['files']
            for member in manifest:
                assert len(members[member['path']])==member['bytes'] and sha(members[member['path']])==member['sha256']
            assert set(members)=={m['path'] for m in manifest}|{'Archive-members.json'}
        counts.append(dict(path=receipt['path'],members=len(members)))
    assert sha((REPO/'archives/experiments-101-110-complete.tar.xz').read_bytes())=='caed8f982a8e57044e8ab1f9c8867947e5f3a474803f6454a831a97836419dc2'
    print(json.dumps(dict(passed=True,compact_files=len(seal['files']),archives=counts,previous_101_110_archive_preserved=True)))


if __name__=='__main__':main()
