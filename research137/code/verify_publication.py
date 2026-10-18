"""Verify publication bytes and full evidence; execute no archived code."""
import hashlib,io,json,tarfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'research137'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    freeze=json.loads((HERE/'Freeze.json').read_text())
    for name,digest in freeze['files'].items():assert sha((ROOT/name).read_bytes())==digest,name
    publication=json.loads((HERE/'Publication-manifest.json').read_text())
    for name,e in publication['files'].items():
        data=(ROOT/name).read_bytes();assert len(data)==e['bytes'] and sha(data)==e['sha256'],name
    receipt=json.loads((HERE/'Archive-storage.json').read_text());data=(ROOT/receipt['path']).read_bytes()
    assert len(data)==receipt['bytes'] and sha(data)==receipt['sha256']
    manifest=json.loads((HERE/'Archive-manifest.json').read_text())['members'];content={}
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as tar:
        for m in tar:
            path=PurePosixPath(m.name)
            assert not path.is_absolute() and '..' not in path.parts and m.isfile() and m.name not in content
            e=manifest[m.name];payload=tar.extractfile(m).read()
            assert len(payload)==e['bytes'] and m.mode==e['mode'] and sha(payload)==e['sha256'],m.name
            content[m.name]=payload
    assert set(content)==set(manifest)
    primary=content['primary/Results.json'];assert primary==content['replica/Results.json']
    assert len(primary)==567235 and sha(primary)=='f2373b658182d5287e51b163efa7448a39741fafc75c1af396452165746562f6'
    for name in ('primary/Replay.json','replica/Replay.json'):
        a=json.loads(content[name]);assert a['passed'] and a['results_sha256']==sha(primary)
    for name in ('formal-primary/Formal-check.json','formal-replica/Formal-check.json'):
        a=json.loads(content[name]);assert a['passed'] and a['no_sorryAx_in_successful_proofs']
        assert [c['returncode']==0 for c in a['checks']]==[True,True,False]
        for c in a['checks'][:2]:assert 'sorryAx' not in c['stdout']+c['stderr']
        assert a['checks'][2]['stdout'].count('error:')>=2
    for name,digest in freeze['files'].items():assert sha(content['snapshot/'+name])==digest,name
    assert content['snapshot/research137/Freeze.json']==(HERE/'Freeze.json').read_bytes()
    assert json.loads((HERE/'Formal-check.json').read_text())==json.loads((HERE/'Replica-Formal-check.json').read_text())
    print(json.dumps({'passed':True,'archive_members':len(content),'frozen_files':len(freeze['files']),
                      'byte_identical_results':True,'matches_pre_reset_results':True,'counts':json.loads(primary)['counts']}))
if __name__=='__main__':main()
