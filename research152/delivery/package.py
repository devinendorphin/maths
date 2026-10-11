"""Complete deterministic custody package; missing roots cannot replace an archive."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
ANCESTORS=('research111/repairs','research121','research131','research133','research137','research141','research145','research148')


def info(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def seal():
    files={str(p.relative_to(REPO)):info(p.read_bytes()) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='Publication-seal.json' and '__pycache__' not in p.parts}
    for name in ['README.md','.github/workflows/verify-research152.yml']+[r+'/Publication-seal'+s+'.json' for r in ANCESTORS for s in ('','-df734ad')]:
        files[name]=info((REPO/name).read_bytes())
    receipt=json.loads((ROOT/'Archive-storage.json').read_text())
    (ROOT/'Publication-seal.json').write_text(json.dumps({'archive':receipt,'files':files},sort_keys=True,indent=2)+'\n')


def run(primary,replica):
    roots=[('primary',Path(primary)),('replica',Path(replica))]
    # Fully validate custody inputs before opening or writing any existing artifact.
    for label,path in roots:
        if not path.is_dir():raise ValueError('missing evidence root: '+str(path))
        for name in ('Freeze.json','Inputs.json','Sessions.json','Logical.json','Controls.json','Audit.json'):
            if not (path/name).is_file():raise ValueError('missing '+name+': '+label)
        sessions=json.loads((path/'Sessions.json').read_text());audit=json.loads((path/'Audit.json').read_text())
        if len(sessions)!=72 or not audit['passed'] or audit['queries']!=3528:raise ValueError('incomplete evidence: '+label)
        if len({s['name'] for s in sessions})!=72 or any(s['exit_code'] or s['timed_out'] for s in sessions):raise ValueError('invalid sessions: '+label)
        for session in sessions:
            out=path/'outputs'/session['name']
            if not (out/'Worker.json').is_file() or not (out/'Evidence.jsonl').is_file():raise ValueError('missing worker evidence: '+str(out))
            w=json.loads((out/'Worker.json').read_text());raw=(out/'Evidence.jsonl').read_bytes()
            if len(w['records'])!=49 or len(raw)!=w['evidence_bytes'] or list(map(json.loads,raw.splitlines()))!=w['records']:raise ValueError('invalid worker: '+str(out))
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):
        if (roots[0][1]/name).read_bytes()!=(roots[1][1]/name).read_bytes():raise ValueError('replication mismatch: '+name)
    payloads={}
    for label,path in roots:
        for file in sorted(path.rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts and file.name!='Sessions-progress.json':
                payloads[label+'/'+str(file.relative_to(path))]=file.read_bytes()
    excluded={'Archive-manifest.json','Archive-storage.json','Publication-seal.json'}
    for file in sorted(ROOT.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.name not in excluded:
            payloads['reports/'+str(file.relative_to(ROOT))]=file.read_bytes()
    manifest={name:dict(info(data),mode=0o644) for name,data in payloads.items()}
    archive=REPO/'archives/experiments-152-155-specialist-incremental.tar.xz'
    temporary=archive.with_suffix('.pending')
    with tarfile.open(temporary,'w:xz',preset=6) as tar:
        for name,data in sorted(payloads.items()):
            member=tarfile.TarInfo(name);member.size=len(data);member.mode=0o644;member.mtime=0
            tar.addfile(member,io.BytesIO(data))
    temporary.replace(archive)
    receipt=dict(info(archive.read_bytes()),path=str(archive.relative_to(REPO)),members=len(manifest),uncompressed_bytes=sum(map(len,payloads.values())),
                 roots=['primary','replica','reports'],excluded=['external virtualenv and wheels; pinned requirements/native module hashes/upstream sources retained','Python bytecode','redundant Sessions-progress.json'])
    (ROOT/'Archive-manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    (ROOT/'Archive-storage.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');seal()
    print('Packaged',receipt['bytes'],'bytes;',receipt['members'],'members')


if __name__=='__main__':
    if sys.argv[1:]==['--seal-only']:seal()
    else:run(*sys.argv[1:])
