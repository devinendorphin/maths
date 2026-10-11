"""Deterministic archive, every-member manifest and compact publication seal."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def run(primary,replica,rejected):
    payloads={}
    for label,path in [('primary',primary),('replica',replica),('rejected-custody',rejected)]:
        path=Path(path)
        for file in sorted(path.rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts and file.name!='Sessions-progress.json':
                payloads[label+'/'+str(file.relative_to(path))]=file.read_bytes()
    excluded={'Archive-manifest.json','Archive-storage.json','Publication-seal.json'}
    for file in sorted(ROOT.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.name not in excluded:
            payloads['reports/'+str(file.relative_to(ROOT))]=file.read_bytes()
    manifest={name:dict(info(data),mode=0o644) for name,data in payloads.items()}
    archive=REPO/'archives/experiments-137-140-allocation.tar.xz'
    with tarfile.open(archive,'w:xz',preset=6) as tar:
        for name,data in sorted(payloads.items()):
            member=tarfile.TarInfo(name);member.size=len(data);member.mode=0o644;member.mtime=0
            tar.addfile(member,io.BytesIO(data))
    data=archive.read_bytes();receipt=dict(info(data),path=str(archive.relative_to(REPO)),members=len(manifest),
        uncompressed_bytes=sum(len(d) for d in payloads.values()),
        roots=['primary','replica','reports','rejected-custody'],
        excluded=['external venv; exact environment and installed optimizer module identity/source retained',
                  'Python bytecode','redundant Sessions-progress.json'])
    (ROOT/'Archive-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (ROOT/'Archive-storage.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    files={}
    for file in sorted(ROOT.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.name!='Publication-seal.json':
            files[str(file.relative_to(REPO))]=info(file.read_bytes())
    extra=['README.md','.github/workflows/verify-research137.yml']
    extra += [f'{r}/Publication-seal{suffix}.json' for r in ('research121','research131','research133') for suffix in ('','-aff30ba')]
    extra += [f'research111/repairs/Publication-seal{suffix}.json' for suffix in ('','-aff30ba')]
    for name in extra:files[name]=info((REPO/name).read_bytes())
    (ROOT/'Publication-seal.json').write_text(json.dumps({'archive':receipt,'files':files},indent=2,sort_keys=True)+'\n')
    print('Packaged',receipt['bytes'],'bytes,',receipt['members'],'members')


if __name__=='__main__':run(*sys.argv[1:])
