"""Dependency-free exact custody, transcript, proofs, update contract and replicas."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
sys.path.insert(0,str(ROOT/'code'))
from checker import digest, encode, verify
from transaction import Transaction
ROUTES=('networkx-cold','ortools-cold','flow-repair','guard-repair')


def run():
    seal=json.loads((ROOT/'Publication-seal.json').read_text())
    for path,item in seal['files'].items():
        data=(REPO/path).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],path
    amendment=json.loads((ROOT/'Navigation-amendment.json').read_text())
    for entry in amendment['amendments']:
        old=(REPO/entry['preserved']).read_bytes();current=(REPO/entry['path']).read_bytes()
        # Later sealed navigation retains the exact earlier receipt endpoint.
        if hashlib.sha256(current).hexdigest()!=entry['after']['sha256']:
            path=Path(entry['path'])
            matches=[(REPO/name).read_bytes() for name in seal['files']
                     if Path(name).parent==path.parent and Path(name).name.startswith('Publication-seal-')
                     and hashlib.sha256((REPO/name).read_bytes()).hexdigest()==entry['after']['sha256']]
            assert len(matches)==1;current=matches[0]
        assert hashlib.sha256(old).hexdigest()==entry['before']['sha256'] and hashlib.sha256(current).hexdigest()==entry['after']['sha256']
        previous=json.loads(old);expected=copy.deepcopy(previous)
        for name,change in entry['changed_entries'].items():
            assert previous['files'][name]==change['old'];expected['files'][name]=change['new']
            assert name=='README.md' or name.endswith('/Publication-seal.json')
        assert expected==json.loads(current)
    receipt=seal['archive'];data=(REPO/receipt['path']).read_bytes()
    assert len(data)==receipt['bytes'] and hashlib.sha256(data).hexdigest()==receipt['sha256']
    manifest=json.loads((ROOT/'Archive-manifest.json').read_text());payloads={}
    with tarfile.open(REPO/receipt['path'],'r:xz') as tar:
        members=tar.getmembers();assert len(members)==len(manifest)==receipt['members'] and len({m.name for m in members})==len(members)
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            data=tar.extractfile(member).read();item=manifest[member.name]
            assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'] and member.mode==item['mode'],member.name
            payloads[member.name]=data
    observations=0;cuts=0
    for label in ('primary','replica'):
        f=json.loads(payloads[label+'/Freeze.json']);ctx=f['context'];body=copy.deepcopy(f);body.pop('context')
        assert hashlib.sha256(encode(body)).hexdigest()==ctx and f['headline_not_executed_at_freeze']
        for path,h in f['files'].items():
            assert hashlib.sha256(payloads[label+'/'+path]).hexdigest()==h
            assert payloads[label+'/'+path]==(ROOT/path).read_bytes(),path
        inputs=json.loads(payloads[label+'/Inputs.json']);sessions=json.loads(payloads[label+'/Sessions.json']);logical=json.loads(payloads[label+'/Logical.json'])
        assert len(sessions)==48 and len({s['name'] for s in sessions})==48
        assert {(s['index'],s['route'],s['repetition']) for s in sessions}=={(i,r,k) for i in range(6) for r in ROUTES for k in range(2)}
        assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
        for session in sessions:
            prefix=label+'/outputs/'+session['name'];w=json.loads(payloads[prefix+'/Worker.json']);entry=inputs['heldout'][w['index']];state=Transaction(entry['model'],ctx);previous=None
            raw=payloads[prefix+'/Evidence.jsonl'];assert len(raw)==w['evidence_bytes'] and len(w['query_wall_s'])==25
            assert hashlib.sha256(raw).hexdigest()==logical[session['name']]['evidence_sha256']
            assert list(map(json.loads,raw.splitlines()))==w['records'] and len(w['records'])==25
            assert all(w[k]==session[k] for k in ('index','route','repetition')) and w['context']==ctx
            for step,rec in enumerate(w['records']):
                if step:state.apply(dict(copy.deepcopy(entry['updates'][step-1]['message']),context=ctx))
                m=state.model;p=rec['proof'];assert rec['step']==step and rec['version']==step and rec['model']==digest(m) and verify(m,p,ctx)
                assert logical[session['name']]['records'][step]=={'record':rec,'proof':hashlib.sha256(encode(p)).hexdigest()}
                if rec['stats']['guard_attempt']:
                    assert w['route']=='guard-repair' and previous['kind']=='optimal'
                    candidate=copy.deepcopy(previous);candidate['model']=digest(m);candidate['cost_units']=sum(e['c']*x for e,x in zip(m['edges'],candidate['flow']))
                    assert verify(m,candidate,ctx)==rec['stats']['guard_accepted']
                if rec['stats']['guard_accepted']:assert rec['action']=='certificate-admission'
                bad=copy.deepcopy(p);bad['dependency']='wrong';assert not verify(m,bad,ctx)
                bad=copy.deepcopy(p)
                if p['kind']=='optimal':bad['cost_units']+=1
                else:bad['set']=[];cuts+=1
                assert not verify(m,bad,ctx);observations+=1;previous=copy.deepcopy(p)
            assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
            assert logical[session['name']]['worker']=={k:v for k,v in w.items() if k not in ('records','query_wall_s','worker_wall_s','worker_cpu_s','worker_maxrss_kib')}
        c=json.loads(payloads[label+'/Controls.json']);assert c['passed'] and len(c['controls'])==len(set(c['controls']))==30
        assert verify(c['model'],c['initial_proof'],ctx) and verify(c['model'],c['fallback_proof'],ctx) and verify(c['shortage_model'],c['shortage_proof'],ctx)
        audit=json.loads(payloads[label+'/Audit.json']);assert audit['passed'] and audit['queries']==1200 and audit['cut_queries']==240 and audit['invalid_certificate_controls']==478
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):assert payloads['primary/'+name]==payloads['replica/'+name]
    assert observations==2400 and cuts==480
    print('Verified capacity/need inquiry:',len(members),'members,',observations,'certified observations including',cuts,'cuts; exact logical replication')


if __name__=='__main__':run()
