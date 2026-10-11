"""Standard-library custody and full concrete certificate/event replay."""
import copy
import hashlib
import json
from pathlib import Path
import tarfile
from checker import digest,encode,verify
from recovery import apply_proof,hashed,replay
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
    observations=0;images=0
    for label in ('primary','replica'):
        f=json.loads(payloads[label+'/Freeze.json']);ctx=f['context']
        for path,h in f['files'].items():assert hashlib.sha256(payloads[label+'/'+path]).hexdigest()==h
        for name in ('checker.py','delta.py','recovery.py'):assert payloads[label+'/code/'+name]==(ROOT/'code'/name).read_bytes()
        inputs=json.loads(payloads[label+'/Inputs.json']);sessions=json.loads(payloads[label+'/Sessions.json']);logical=json.loads(payloads[label+'/Logical.json'])
        assert len(sessions)==72 and len({s['name'] for s in sessions})==72
        assert {(s['index'],s['format'],s['policy'],s['repetition']) for s in sessions}=={(i,f,p,r) for i in range(6) for f in ('full','compact') for p in range(3) for r in range(2)}
        assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
        for session in sessions:
            prefix=label+'/outputs/'+session['name'];w=json.loads(payloads[prefix+'/Worker.json']);entry=inputs['heldout'][w['index']];base=entry['model'];m=copy.deepcopy(base);p=None;version=0;head=None
            raw=payloads[prefix+'/Evidence.jsonl'];assert len(raw)==w['raw_evidence_bytes']
            assert hashlib.sha256(raw).hexdigest()==logical[session['name']]['evidence_sha256']
            for frame in map(json.loads,raw.splitlines()):
                if 'snapshot' in frame:
                    snap=frame['snapshot'];assert snap['version']==version
                    mm,pp=replay(base,snap,[],ctx,[version,snap['head']]);assert mm==m
                    if p is not None:assert pp==p and snap['head']==head
                    else:p=pp;head=snap['head']
                    images+=1;continue
                event=frame['event'];content=event['payload'];msg=content['message']
                assert msg=={'context':ctx,'version':version,'changes':entry['changes'][version]}
                assert event['previous']==head and event['head']==hashed(head,content)
                for z in msg['changes']:assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                if content['action']=='recertify':
                    p=apply_proof(p,content['difference']) if 'difference' in content else copy.deepcopy(content['proof'])
                    if 'model' in content:assert content['model']==m
                else:p['model']=digest(m);p['cost_units']=content['cost_units']
                assert verify(m,p,ctx);version+=1;head=event['head']
            assert version==48
            m=copy.deepcopy(base);p=None;assert len(w['records'])==49
            for step,rec in enumerate(w['records']):
                if step:
                    for z in entry['changes'][step-1]:assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                if 'proof' in rec:p=copy.deepcopy(rec['proof'])
                else:p['model']=digest(m);p['cost_units']=rec['value']
                assert verify(m,p,ctx) and p['cost_units']==rec['value']
                expected=logical[session['name']]['records'][step]
                assert expected=={'record':rec,'model':digest(m),'proof':hashlib.sha256(encode(p)).hexdigest()}
                assert rec['live_bytes']<=inputs['policies'][w['policy']]['budget']
                bad=copy.deepcopy(p);bad['cost_units']+=1;assert not verify(m,bad,ctx);observations+=1
            active=prefix+'/active/'
            assert replay(json.loads(payloads[active+'base.json']),json.loads(payloads[active+'snapshot.json']),[],ctx,json.loads(payloads[active+'anchor.json']))==(m,p)
            assert payloads[active+'journal.jsonl']==b''
            hashes={name:hashlib.sha256(payloads[active+name]).hexdigest() for name in logical[session['name']]['active_hashes']}
            assert hashes==logical[session['name']]['active_hashes']
            assert sum(len(payloads[active+name]) for name in hashes)==w['active_final_bytes']
            assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        controls=json.loads(payloads[label+'/Controls.json']);assert len(controls['controls'])==14 and all(c['rejected'] for c in controls['controls'])
        fixture=controls['fixture'];base=fixture['base'];snap=fixture['snapshot'];events=fixture['events'];anchor=fixture['anchor']
        replay(base,snap,events,ctx,anchor);replay(base,snap,events[:1],ctx,[1,events[0]['head']])
        from delta import Refused
        for name,mutate in [('cost',lambda d:d.update(cost_units=999)),('duplicate',lambda d:d['pi'].extend([[0,1],[0,2]])),('boolean',lambda d:d['flow'].append([0,True]))]:
            ev=copy.deepcopy(events);mutate(ev[1]['payload']['difference']);ev[1]['head']=hashed(ev[1]['previous'],ev[1]['payload'])
            try:replay(base,snap,ev,ctx,[2,ev[1]['head']])
            except Refused:pass
            else:raise AssertionError(name)
        try:replay(base,snap,events[:1],ctx,anchor)
        except Refused:pass
        else:raise AssertionError('rollback')
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):assert payloads['primary/'+name]==payloads['replica/'+name]
    assert observations==7056 and images==1652
    print('Verified recovery:',len(members),'members,',observations,'certified observations,',images,'images')


if __name__=='__main__':run()
