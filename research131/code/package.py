"""Post-run compact archive, executable member identities and publication seal."""
import hashlib
import io
import json
from pathlib import Path
import stat
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def info(data):return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def save(name,data):(ROOT/name).write_text(json.dumps(data,indent=2)+'\n')


def run(headline,replica):
    archive=REPO/'archives/experiments-131-132-complete.tar.xz';sources={}
    for prefix,root in [('primary',headline),('replica',replica)]:
        for p in sorted(root.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.name!='Results-progress.json':sources[f'{prefix}/{p.relative_to(root)}']=p
    omitted={'Archive-storage.json','Archive-manifest.json','Publication-seal.json'}
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['dependencies','external','evidence','development','__pycache__']) and p.name not in omitted:
            sources[f'reports/{p.relative_to(ROOT)}']=p
    members={}
    with tarfile.open(archive,'w:xz',preset=9) as tar:
        for name,p in sources.items():
            data=p.read_bytes();mode=stat.S_IMODE(p.stat().st_mode);metadata=tarfile.TarInfo(name);metadata.size=len(data);metadata.mode=mode;metadata.mtime=0;metadata.uid=metadata.gid=0
            tar.addfile(metadata,io.BytesIO(data));members[name]=dict(**info(data),mode=mode)
    save('Archive-manifest.json',dict(files=members))
    receipt=dict(path=str(archive.relative_to(REPO)),**info(archive.read_bytes()),members=len(members),uncompressed_bytes=sum(m['bytes'] for m in members.values()),executable_members=[n for n,m in members.items() if m['mode']&0o111],excluded=['Large external SDK installations','Python bytecode','Results-progress.json (redundant rolling copy of final Results.json)'],roots=['primary','replica','reports'])
    save('Archive-storage.json',receipt)
    files={str(p.relative_to(REPO)):info(p.read_bytes()) for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['dependencies','external','evidence','development','__pycache__']) and p.name!='Publication-seal.json'}
    for name in ['README.md','.github/workflows/verify-research131.yml']:files[name]=info((REPO/name).read_bytes())
    for p in sorted((REPO/'projects/certified-allocation').rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(REPO))]=info(p.read_bytes())
    save('Publication-seal.json',dict(files=files,archive=receipt))
    print(json.dumps({k:v for k,v in receipt.items() if k!='executable_members'}))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]))
