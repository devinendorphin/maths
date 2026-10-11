"""Standard-library archive/custody and complete mathematical replay."""
import copy
import hashlib
import json
from pathlib import Path
import tarfile
from checker import digest, encode, verify
from delta import Captured

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def run():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for path,info in seal['files'].items():
        data=(REPO/path).read_bytes()
        assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],path
    receipt=seal['archive'];data=(REPO/receipt['path']).read_bytes()
    assert len(data)==receipt['bytes'] and hashlib.sha256(data).hexdigest()==receipt['sha256']
    manifest=json.loads((ROOT/'Archive-manifest.json').read_text());payloads={}
    with tarfile.open(REPO/receipt['path'],'r:xz') as archive:
        members=archive.getmembers();assert len(members)==len(manifest) and len({m.name for m in members})==len(members)
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            content=archive.extractfile(member).read();info=manifest[member.name]
            assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'] and member.mode==info['mode']
            payloads[member.name]=content
    total=0
    for label in ('primary','replica'):
        freeze=json.loads(payloads[label+'/Freeze.json']);context=freeze['context']
        for path,h in freeze['files'].items():assert hashlib.sha256(payloads[label+'/'+path]).hexdigest()==h
        for name in ('checker.py','delta.py'):
            assert payloads[label+'/code/'+name]==(ROOT/'code'/name).read_bytes()
        inputs=json.loads(payloads[label+'/Inputs.json'])['heldout'];sessions=json.loads(payloads[label+'/Sessions.json'])
        assert len(sessions)==78 and all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
        expected={(i,r,j,4096) for i in range(6) for r in ('cold','full-recheck','delta-buffered','delta-fsync') for j in range(3)}|{(i,'delta-buffered',0,64) for i in range(6)}
        assert len({s['name'] for s in sessions})==78
        assert {(s['index'],s['route'],s['repetition'],s['budget']) for s in sessions}==expected
        mathematical=json.loads(payloads[label+'/Mathematical-records.json'])
        for session in sessions:
            prefix=label+'/outputs/'+session['name']
            w=json.loads(payloads[prefix+'/Worker.json']);m=copy.deepcopy(inputs[w['index']]['model']);p=None
            log=payloads[prefix+'/Journal.jsonl'];checkpoint=payloads[prefix+'/Checkpoint.json']
            assert hashlib.sha256(log).hexdigest()==mathematical[session['name']]['journal_sha256']
            assert hashlib.sha256(checkpoint).hexdigest()==mathematical[session['name']]['checkpoint_sha256']
            assert len(log)==w['journal_write_bytes'] and len(checkpoint)==w['checkpoint_bytes']
            for j,rec in enumerate(w['records']):
                if j:
                    for z in inputs[w['index']]['changes'][j-1]:
                        assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                if 'proof' in rec:p=copy.deepcopy(rec['proof'])
                else:p['model']=digest(m);p['cost_units']=rec['cost_units']
                assert verify(m,p,context) and p['cost_units']==rec['cost_units']
                identity=mathematical[session['name']]['records'][j]
                assert identity['record']==rec and identity['model_digest']==digest(m)
                assert identity['proof_digest']==hashlib.sha256(encode(p)).hexdigest()
                if 'journal_bytes' in rec:assert rec['journal_bytes']<=w['budget']
                bad=copy.deepcopy(p);bad['cost_units']+=1;assert not verify(m,bad,context)
                total+=1
            rm,rp=Captured.restore(json.loads(checkpoint),context).export()
            assert rm==m and rp==p
            assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        controls=json.loads(payloads[label+'/Controls.json'])
        assert all(c['rejected'] for c in controls['transaction_controls']+controls['recovery_controls'])
        for case in controls['noncost_cases']:assert verify(case['model'],case['proof'],context)
    for name in ('Mathematical-records.json','Controls.json','Freeze.json'):
        assert payloads['primary/'+name]==payloads['replica/'+name]
    print('Verified',len(members),'archive members and',total,'certified observations across two matching runs')


if __name__=='__main__':run()
