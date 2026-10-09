"""Compact archive with a manifest and complete read-back verification."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
RUNS=[Path('/workspace/maths-onboarding')/name for name in ['repair-headline','repair-replication']]


def main():
    archive=REPO/'archives/experiments-111-120-repairs.tar.xz'
    assert not archive.exists(), 'Preserve existing archives; use a different name for a revision.'
    entries={};executable=set()
    for label,run in zip(['headline','replication'],RUNS):
        for p in sorted(run.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                name=label+'/'+p.relative_to(run).as_posix();entries[name]=p.read_bytes()
                if p.stat().st_mode & 0o111:executable.add(name)
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and not set(p.relative_to(ROOT).parts)&{'__pycache__','dependencies','development'} and p.name not in ['Archive-storage.json','Publication-seal.json']:
            entries['reports/repairs/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
    for name in ['REVIEW.md','Alignment.md','README.md','REPRODUCE.md']:
        entries['reports/'+name]=(ROOT.parent/name).read_bytes()
    manifest=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in sorted(entries.items())]
    entries['Archive-members.json']=(json.dumps(dict(files=manifest),indent=2)+'\n').encode()
    with tarfile.open(archive,'w:xz',preset=6) as t:
        for name,data in sorted(entries.items()):
            info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o755 if name in executable else 0o644
            t.addfile(info,io.BytesIO(data))
    with tarfile.open(archive) as t:
        observed={};observed_exec=set()
        for m in t:
            if m.isfile():
                observed[m.name]=t.extractfile(m).read()
                if m.mode & 0o111:observed_exec.add(m.name)
    assert observed==entries
    assert observed_exec==executable
    receipt=dict(path=archive.relative_to(REPO).as_posix(),bytes=archive.stat().st_size,
                 sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=len(entries),
                 individually_hashed_files=len(manifest),members_manifest=manifest,executable_members=sorted(executable),
                 verification='Every member read back and matched exactly; SDK installations excluded. Includes both runs, invalid controls, original/final auditors and post-run reports.')
    (ROOT/'Archive-storage.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='members_manifest'}))


if __name__=='__main__':
    main()
