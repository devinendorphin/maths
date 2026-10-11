"""Standard-library complete custody, certificates and rejected-run preservation."""
import copy
import hashlib
import json
from pathlib import Path
import tarfile
from checker import digest,encode,verify
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent


def run():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for path,item in seal['files'].items():
        data=(REPO/path).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],path
    receipt=seal['archive'];data=(REPO/receipt['path']).read_bytes()
    assert len(data)==receipt['bytes'] and hashlib.sha256(data).hexdigest()==receipt['sha256']
    manifest=json.loads((ROOT/'Archive-manifest.json').read_text());payloads={}
    with tarfile.open(REPO/receipt['path'],'r:xz') as tar:
        members=tar.getmembers();assert len(members)==len(manifest) and len({m.name for m in members})==len(members)
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            data=tar.extractfile(member).read();item=manifest[member.name]
            assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'] and member.mode==item['mode'],member.name
            payloads[member.name]=data
    observations=0;cuts=0
    for label in ('primary','replica'):
        f=json.loads(payloads[label+'/Freeze.json']);ctx=f['context']
        for path,h in f['files'].items():assert hashlib.sha256(payloads[label+'/'+path]).hexdigest()==h
        for name in ('checker.py','delta.py','basis.py','worker.py'):assert payloads[label+'/code/'+name]==(ROOT/'code'/name).read_bytes()
        inputs=json.loads(payloads[label+'/Inputs.json']);sessions=json.loads(payloads[label+'/Sessions.json']);logical=json.loads(payloads[label+'/Logical.json'])
        assert len(sessions)==54 and len({s['name'] for s in sessions})==54
        assert {(s['index'],s['route'],s['repetition']) for s in sessions}=={(i,r,k) for i in range(9) for r in ('cold','basis','guard') for k in range(2)}
        assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
        for session in sessions:
            prefix=label+'/outputs/'+session['name'];w=json.loads(payloads[prefix+'/Worker.json']);entry=inputs['heldout'][w['index']];m=copy.deepcopy(entry['model']);p=None
            raw=payloads[prefix+'/Evidence.jsonl'];assert len(raw)==w['evidence_bytes']
            assert hashlib.sha256(raw).hexdigest()==logical[session['name']]['evidence_sha256']
            assert list(map(json.loads,raw.splitlines()))==w['records'] and len(w['records'])==25
            for step,rec in enumerate(w['records']):
                if step:
                    update=entry['updates'][step-1];assert digest(m)==update['old_model']
                    if update['kind']=='cost':
                        for z in update['changes']:assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                    else:m=copy.deepcopy(update['model']);assert rec['action']=='model-reset'
                if 'proof' in rec:p=copy.deepcopy(rec['proof'])
                else:
                    assert rec['action']=='certificate-patch' and w['route']=='guard' and p['kind']=='optimal'
                    p['model']=digest(m);p['cost_units']=rec['cost_units']
                    assert rec['edge_checks']==len(entry['updates'][step-1]['changes'])
                assert rec['step']==step and rec['model']==digest(m) and verify(m,p,ctx)
                expected=logical[session['name']]['records'][step]
                assert expected=={'record':rec,'proof':hashlib.sha256(encode(p)).hexdigest()}
                bad=copy.deepcopy(p);bad['dependency']='wrong';assert not verify(m,bad,ctx)
                bad=copy.deepcopy(p)
                if p['kind']=='optimal':bad['cost_units']+=1
                else:bad['set']=[];cuts+=1
                assert not verify(m,bad,ctx);observations+=1
            assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        c=json.loads(payloads[label+'/Controls.json']);assert c['passed'] and len(c['controls'])==len(set(c['controls']))==16
        assert verify(c['model'],c['initial_proof'],ctx)
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):assert payloads['primary/'+name]==payloads['replica/'+name]
    rejected=json.loads((ROOT/'Rejected-execution.json').read_text())
    for label in ('primary','replica'):
        prefix='rejected-record-ownership/'+label+'/';f=json.loads(payloads[prefix+'Freeze.json'])
        assert hashlib.sha256(payloads[prefix+'Freeze.json']).hexdigest()==rejected['runs'][label]['source_freeze_sha256']
        for path,h in f['files'].items():assert hashlib.sha256(payloads[prefix+path]).hexdigest()==h
        sessions=json.loads(payloads[prefix+'Sessions.json']);assert len(sessions)==54;bad=[]
        for s in sessions:
            p=prefix+'outputs/'+s['name']+'/';w=json.loads(payloads[p+'Worker.json']);raw=list(map(json.loads,payloads[p+'Evidence.jsonl'].splitlines()))
            if raw!=w['records']:bad.append(s['name'])
        assert bad==rejected['runs'][label]['mismatched_workers']
    assert observations==2700 and cuts==72
    print('Verified larger inquiry:',len(members),'members,',observations,'certified observations including',cuts,'cuts; rejected runs retained')


if __name__=='__main__':run()
