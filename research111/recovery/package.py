"""Package only the new verification supplement, preserving original evidence."""
from pathlib import Path
import hashlib
import io
import json
import tarfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
archive=REPO/'archives/original-300-recovery-verification.tar.xz'
assert not archive.exists(),'Preserve prior packaging revisions outside the checkout before regeneration.'
entries={p.name:p.read_bytes() for p in sorted(ROOT.iterdir()) if p.is_file() and p.name!='Archive-storage.json'}
entries['frozen/setup_checker.py']=Path('/workspace/maths-onboarding/recovery-frozen-setup_checker.py').read_bytes()
sdk=Path('/workspace/maths-toolchains/veripb2-recovery-source')
for p in sdk.glob('setup-*.log'):entries['setup-logs/'+p.name]=p.read_bytes()
entries['setup-logs/build_core.py']=(sdk/'build_core.py').read_bytes()
entries['Recovery-followup.md']=(ROOT.parent/'Recovery-followup.md').read_bytes()
files=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for name,data in sorted(entries.items())]
entries['Archive-members.json']=(json.dumps({'files':files},indent=2)+'\n').encode()
with tarfile.open(archive,'w:xz') as t:
    for name,data in sorted(entries.items()):
        info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
with tarfile.open(archive) as t:assert {m.name:t.extractfile(m).read() for m in t if m.isfile()}==entries
receipt=dict(path=archive.relative_to(REPO).as_posix(),bytes=archive.stat().st_size,
    sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=len(entries),members_manifest=files,
    verification='All members read back exactly; preserves pre-replay setup adapter, new audit, source/binary identities and setup logs. Large SDK and core extension excluded.')
(ROOT/'Archive-storage.json').write_text(json.dumps(receipt,indent=2)+'\n')
print({k:v for k,v in receipt.items() if k!='members_manifest'})
