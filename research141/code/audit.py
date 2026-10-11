"""Original-input reconstruction and separate residual/cut arithmetic."""
import copy
import hashlib
import json
from pathlib import Path
import time
import networkx as nx
from checker import digest,encode,verify
from controls import run as controls
from recovery import apply_proof,hashed,replay

ROOT=Path(__file__).resolve().parents[1]


def independent(m,p,context):
    assert p['model']==digest(m) and p['dependency']==context and p['kind']=='optimal'
    balance=[0]*m['n'];cost=0
    for e,x in zip(m['edges'],p['flow']):
        assert type(x) is int and e['l']<=x<=e['u'];balance[e['a']]+=x;balance[e['z']]-=x;cost+=e['c']*x
        r=e['c']+p['pi'][e['a']]-p['pi'][e['z']]
        if x<e['u']:assert r>=0
        if x>e['l']:assert r<=0
    assert balance==m['b'] and cost==p['cost_units']


def reference(m):
    g=nx.MultiDiGraph();balance=m['b'].copy();constant=0
    for v in range(m['n']):g.add_node(v)
    for i,e in enumerate(m['edges']):
        balance[e['a']]-=e['l'];balance[e['z']]+=e['l'];constant+=e['l']*e['c']
        g.add_edge(e['a'],e['z'],key=i,capacity=e['u']-e['l'],weight=e['c'])
    for v,b in enumerate(balance):g.nodes[v]['demand']=-b
    return nx.network_simplex(g)[0]+constant


def run():
    tick=time.perf_counter();freeze=json.loads((ROOT/'Freeze.json').read_text());ctx=freeze['context']
    for path,h in freeze['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
    import networkx.algorithms.flow.networksimplex as mod
    assert nx.__version__==freeze['environment']['networkx'] and hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()==freeze['environment']['networksimplex_sha256']
    inputs=json.loads((ROOT/'Inputs.json').read_text());sessions=json.loads((ROOT/'Sessions.json').read_text())
    expected={(i,f,p,r) for i in range(6) for f in ('full','compact') for p in range(3) for r in range(2)}
    assert len(sessions)==72 and {(s['index'],s['format'],s['policy'],s['repetition']) for s in sessions}==expected
    assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
    answers={};unique={};logical={};queries=0;checks=0;snaps=0
    for session in sessions:
        out=ROOT/'outputs'/session['name'];w=json.loads((out/'Worker.json').read_text());base=inputs['heldout'][w['index']]['model'];m=copy.deepcopy(base);p=None
        assert len(w['records'])==49 and all(w[k]==session[k] for k in ('index','format','policy','repetition'))
        assert w['raw_evidence_bytes']==(out/'Evidence.jsonl').stat().st_size
        evidence=[json.loads(line) for line in (out/'Evidence.jsonl').read_bytes().splitlines()];position=0;version=0;head=None
        per=[]
        for frame in evidence:
            if 'snapshot' in frame:
                snap=frame['snapshot'];assert snap['version']==version
                sm,sp=replay(base,snap,[],ctx,[version,snap['head']]);assert sm==m
                if p is not None:assert sp==p and snap['head']==head
                else:p=sp;head=snap['head']
                independent(m,p,ctx);snaps+=1
                continue
            event=frame['event'];payload=event['payload'];msg=payload['message']
            assert msg=={'version':version,'context':ctx,'changes':inputs['heldout'][w['index']]['changes'][version]}
            assert event['previous']==head and event['head']==hashed(head,payload)
            for z in msg['changes']:assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
            if payload['action']=='recertify':
                p=apply_proof(p,payload['difference']) if 'difference' in payload else copy.deepcopy(payload['proof'])
                if 'model' in payload:assert payload['model']==m
            else:p['model']=digest(m);p['cost_units']=payload['cost_units']
            independent(m,p,ctx);assert verify(m,p,ctx);head=event['head'];version+=1
        assert version==48
        m=copy.deepcopy(base);p=None
        for i,rec in enumerate(w['records']):
            if i:
                for z in inputs['heldout'][w['index']]['changes'][i-1]:m['edges'][z['edge']]['c']=z['new']
            if 'proof' in rec:p=copy.deepcopy(rec['proof'])
            else:p['model']=digest(m);p['cost_units']=rec['value']
            independent(m,p,ctx);assert verify(m,p,ctx) and rec['value']==p['cost_units']
            assert rec['live_bytes']<=inputs['policies'][w['policy']]['budget']
            key=digest(m)
            if key not in answers:answers[key]=reference(m)
            assert answers[key]==p['cost_units'];pid=hashlib.sha256(encode(p)).hexdigest()
            if pid not in unique:
                bad=copy.deepcopy(p);bad['cost_units']+=1;assert not verify(m,bad,ctx)
                bad=copy.deepcopy(p);bad['flow'][0]=m['edges'][0]['u']+1;assert not verify(m,bad,ctx)
                unique[pid]=key;checks+=2
            queries+=1;per.append({'record':rec,'model':key,'proof':pid})
        assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        active=out/'active'
        restored=replay(json.loads((active/'base.json').read_bytes()),json.loads((active/'snapshot.json').read_bytes()),[],ctx,json.loads((active/'anchor.json').read_bytes()))
        assert restored==(m,p) and (active/'journal.jsonl').stat().st_size==0
        assert sum(f.stat().st_size for f in active.iterdir())==w['active_final_bytes']
        logical[session['name']]={'records':per,'worker':{k:v for k,v in w.items() if k not in ('records','worker_wall_s','worker_cpu_s','worker_maxrss_kib')},
              'evidence_sha256':hashlib.sha256((out/'Evidence.jsonl').read_bytes()).hexdigest(),
              'active_hashes':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(active.iterdir())}}
    recorded=json.loads((ROOT/'Controls.json').read_text());assert recorded==controls(ctx)
    report={'passed':True,'workers':72,'queries':queries,'distinct_models':len(answers),'distinct_proofs':len(unique),
            'invalid_certificate_controls':checks,'recovery_controls':len(recorded['controls']),'snapshots_replayed':snaps,'audit_wall_s':time.perf_counter()-tick}
    (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'Logical.json').write_text(json.dumps(logical,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':run()
