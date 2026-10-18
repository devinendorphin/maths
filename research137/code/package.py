"""Package restored verified evidence; never overwrite an earlier publication."""
import argparse,hashlib,io,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'research137'
def main(primary,replica,formal_primary,formal_replica):
    f=json.loads((HERE/'Freeze.json').read_text());payload={}
    for name in [*f['files'],'research137/Freeze.json']:payload['snapshot/'+name]=(ROOT/name).read_bytes()
    for prefix,directory,names in [('primary',primary,['Results.json','Replay.json']),('replica',replica,['Results.json','Replay.json']),('formal-primary',formal_primary,['Formal-check.json']),('formal-replica',formal_replica,['Formal-check.json'])]:
        for name in names:payload[prefix+'/'+name]=(directory/name).read_bytes()
    for p in HERE.glob('*'):
        if p.is_file() and p.name not in ('Freeze.json','Inputs.json'):
            payload['reports/'+p.name]=p.read_bytes()
    for p in HERE.joinpath('code').glob('*.py'):payload.setdefault('snapshot/research137/code/'+p.name,p.read_bytes())
    archive=ROOT/'archives/experiments-137-139-complete.tar.xz';assert not archive.exists()
    members={}
    with tarfile.open(archive,'w:xz',preset=6) as tar:
        for name,data in sorted(payload.items()):
            info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(data))
            members[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'mode':info.mode}
    (HERE/'Archive-manifest.json').write_text(json.dumps({'members':members},indent=2)+'\n')
    data=archive.read_bytes();receipt={'path':str(archive.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (HERE/'Archive-storage.json').write_text(json.dumps(receipt,indent=2)+'\n')
    files={}
    for p in sorted(HERE.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name=='Publication-manifest.json':continue
        data=p.read_bytes();files[str(p.relative_to(ROOT))]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (HERE/'Publication-manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('primary','replica','formal_primary','formal_replica'):p.add_argument(n,type=Path)
    a=p.parse_args();main(a.primary,a.replica,a.formal_primary,a.formal_replica)
