"""Deterministic complete archive, per-member identities and publication seal."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def run(primary,replica,*rejected):
    storage=ROOT.name=='research141';paths=[('primary',primary),('replica',replica)]
    paths += [('rejected-record-ownership/'+name,path) for name,path in zip(('primary','replica'),rejected)]
    if len(rejected)!=(0 if storage else 2):raise ValueError('complete custody roots required')
    for label,path in paths:
        path=Path(path)
        if not path.is_dir() or not (path/'Freeze.json').is_file() or not (path/'Sessions.json').is_file():
            raise ValueError('missing evidence root: '+str(path))
        sessions=json.loads((path/'Sessions.json').read_text())
        if len(sessions)!=(72 if storage else 54):raise ValueError('incomplete session set: '+label)
        for session in sessions:
            out=path/'outputs'/session['name']
            if not (out/'Worker.json').is_file() or not (out/'Evidence.jsonl').is_file():
                raise ValueError('missing worker evidence: '+str(out))
    payloads={}
    for label,path in paths:
        for file in sorted(Path(path).rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts and file.name!='Sessions-progress.json':
                payloads[label+'/'+str(file.relative_to(path))]=file.read_bytes()
    excluded={'Archive-manifest.json','Archive-storage.json','Publication-seal.json'}
    for file in sorted(ROOT.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.name not in excluded:
            payloads['reports/'+str(file.relative_to(ROOT))]=file.read_bytes()
    manifest={name:dict(info(data),mode=0o644) for name,data in payloads.items()}
    archive=REPO/'archives'/('experiments-141-144-recovery.tar.xz' if storage else 'experiments-145-147-dynamic-allocation.tar.xz')
    with tarfile.open(archive,'w:xz',preset=6) as tar:
        for name,data in sorted(payloads.items()):
            member=tarfile.TarInfo(name);member.size=len(data);member.mode=0o644;member.mtime=0
            tar.addfile(member,io.BytesIO(data))
    receipt=dict(info(archive.read_bytes()),path=str(archive.relative_to(REPO)),members=len(manifest),uncompressed_bytes=sum(map(len,payloads.values())),
                 roots=[label for label,_ in paths]+['reports'],excluded=['external virtualenv; pinned source/module version/hash and license retained','Python bytecode','redundant Sessions-progress.json'])
    (ROOT/'Archive-manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    (ROOT/'Archive-storage.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    files={str(p.relative_to(REPO)):info(p.read_bytes()) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='Publication-seal.json' and '__pycache__' not in p.parts}
    extra=['README.md','.github/workflows/verify-research141-147.yml']
    extra += [f'{r}/Publication-seal{suffix}.json' for r in ('research111/repairs','research121','research131','research133','research137') for suffix in ('','-103457d')]
    if not storage:extra+=['research141/Publication-seal.json']
    for name in extra:files[name]=info((REPO/name).read_bytes())
    (ROOT/'Publication-seal.json').write_text(json.dumps({'archive':receipt,'files':files},sort_keys=True,indent=2)+'\n')
    print('Packaged',ROOT.name,receipt['bytes'],'bytes;',receipt['members'],'members')


if __name__=='__main__':run(*sys.argv[1:])
