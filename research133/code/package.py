"""Deterministic compact evidence archive, member manifest and publication seal."""
import hashlib
import io
import json
from pathlib import Path
import stat
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def run(primary,replica):
    paths={}
    for prefix,root in [('primary',primary),('replica',replica)]:
        for p in sorted(root.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.name!='Sessions-progress.json':paths[f'{prefix}/{p.relative_to(root)}']=p
    exclude={'Publication-seal.json','Archive-storage.json','Archive-manifest.json'}
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.name not in exclude:paths[f'reports/{p.relative_to(ROOT)}']=p
    archive=REPO/'archives/experiments-133-136-allocation.tar.xz';manifest={}
    with tarfile.open(archive,'w:xz',preset=9) as tar:
        for name,p in paths.items():
            data=p.read_bytes();mode=stat.S_IMODE(p.stat().st_mode)
            m=tarfile.TarInfo(name);m.size=len(data);m.mode=mode;m.mtime=0;tar.addfile(m,io.BytesIO(data));manifest[name]=dict(info(data),mode=mode)
    save('Archive-manifest.json',{'files':manifest})
    receipt=dict(info(archive.read_bytes()),path=str(archive.relative_to(REPO)),members=len(manifest),uncompressed_bytes=sum(v['bytes'] for v in manifest.values()),roots=['primary','replica','reports'],excluded=['external venv/wheel; identities and recovery retained','Python bytecode','Sessions-progress.json: exact redundant rolling copy of final sessions'])
    save('Archive-storage.json',receipt)
    files={str(p.relative_to(REPO)):info(p.read_bytes()) for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='Publication-seal.json'}
    for name in ['README.md','.github/workflows/verify-research133.yml']:files[name]=info((REPO/name).read_bytes())
    save('Publication-seal.json',{'files':files,'archive':receipt})
    print(json.dumps(receipt))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]))
