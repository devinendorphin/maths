"""Separate original-model binder, residual/cut evaluation and simplex encoder."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import time
import networkx as nx
from checker import verify

ROOT=Path(__file__).resolve().parents[1]


def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def sha(o):return hashlib.sha256(canonical(o)).hexdigest()


def independent(m,p,context):
    assert p['model']==sha(m) and p['dependency']==context
    if p['kind']=='cut':
        s=set(p['set']);assert len(s)==len(p['set'])
        assert sum(m['b'][v] for v in s)>sum(e['u'] for e in m['edges'] if e['a'] in s and e['z'] not in s)-sum(e['l'] for e in m['edges'] if e['a'] not in s and e['z'] in s)
        return
    balance=[0]*m['n'];value=0
    assert len(p['flow'])==len(m['edges']) and len(p['pi'])==m['n']
    for i,e in enumerate(m['edges']):
        x=p['flow'][i];assert type(x) is int and e['l']<=x<=e['u']
        balance[e['a']]+=x;balance[e['z']]-=x;value+=x*e['c']
        reduced=e['c']+p['pi'][e['a']]-p['pi'][e['z']]
        if x!=e['u']:assert reduced>=0
        if x!=e['l']:assert reduced<=0
    assert balance==m['b'] and value==p['cost_units']


def reference(m):
    g=nx.MultiDiGraph();demand=[-b for b in m['b']];constant=0
    for i,e in enumerate(m['edges']):
        demand[e['a']]+=e['l'];demand[e['z']]-=e['l'];constant+=e['l']*e['c']
        g.add_edge(e['a'],e['z'],key=i,weight=e['c'],capacity=e['u']-e['l'])
    for v,d in enumerate(demand):g.add_node(v,demand=d)
    try:return nx.network_simplex(g)[0]+constant
    except nx.NetworkXUnfeasible:return None


def mutations(m,p,context):
    tests=[]
    q=copy.deepcopy(p);q['dependency']='wrong';tests.append(('context',m,q))
    if p['kind']=='cut':
        q=copy.deepcopy(p);q['set']=[];tests.append(('false-cut',m,q))
    else:
        q=copy.deepcopy(p);q['cost_units']+=1;tests.append(('cost',m,q))
        q=copy.deepcopy(p);q['flow'][0]=m['edges'][0]['u']+1;tests.append(('flow',m,q))
        q=copy.deepcopy(p)
        i=next(i for i,e in enumerate(m['edges']) if e['a']!=e['z'] and p['flow'][i]<e['u'])
        e=m['edges'][i];q['pi'][e['z']]=e['c']+q['pi'][e['a']]+1
        tests.append(('potential',m,q))
        mm=copy.deepcopy(m);i=next(i for i,x in enumerate(p['flow']) if x>0)
        mm['edges'][i]['u']=p['flow'][i]-1;q=copy.deepcopy(p);q['model']=sha(mm)
        tests.append(('capacity-rebound',mm,q))
    for name,mm,pp in tests:assert not verify(mm,pp,context),name
    return [name for name,_,_ in tests]


def replay_journal(file,models,context):
    state=None;proof=None;version=None;head=None;events=0;snapshots=0
    for line in file.read_bytes().splitlines():
        obj=json.loads(line)
        if 'snapshot' in obj:
            b=obj['snapshot'];assert not b['events'] and b['version']==b['base']['version']
            base=b['base'];version=base['version'];state=copy.deepcopy(base['model']);proof=copy.deepcopy(base['proof'])
            assert state==models[version]
            independent(state,proof,context)
            head=sha(base);assert b['head']==head;snapshots+=1
        elif 'patch' in obj:
            event=obj['patch'];msg=event['message']
            assert msg['version']==version and msg['context']==context and event['previous']==head
            newhead=hashlib.sha256(head.encode()+canonical({'message':msg,'cost_units':event['cost_units']})).hexdigest()
            assert newhead==event['head']
            for z in msg['changes']:
                assert state['edges'][z['edge']]['c']==z['old']
                state['edges'][z['edge']]['c']=z['new']
            proof['cost_units']=event['cost_units'];proof['model']=sha(state)
            version+=1;assert state==models[version]
            independent(state,proof,context);head=newhead;events+=1
        else:
            version=obj['version'];state=copy.deepcopy(models[version]);proof=obj['proof']
            assert obj['model_digest']==sha(state);independent(state,proof,context)
    assert version==24
    return {'snapshots':snapshots,'patches':events}


def run():
    tick=time.perf_counter();freeze=json.loads((ROOT/'Freeze.json').read_text());ctx=freeze['context']
    for path,h in freeze['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    assert nx.__version__==freeze['environment']['networkx']
    import networkx.algorithms.flow.networksimplex as mod
    assert hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()==freeze['environment']['networksimplex_sha256']
    inputs=json.loads((ROOT/'Inputs.json').read_text())['heldout'];sessions=json.loads((ROOT/'Sessions.json').read_text())
    assert len(sessions)==78 and all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
    allmodels=[];answers={};proofs={};records={};checks=0;invalid=0;compactions=0;fallbacks=0;patches=0
    for entry in inputs:
        m=copy.deepcopy(entry['model']);models=[copy.deepcopy(m)]
        for changes in entry['changes']:
            for z in changes:
                assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
            models.append(copy.deepcopy(m))
        allmodels.append(models)
    for session in sessions:
        out=ROOT/'outputs'/session['name'];w=json.loads((out/'Worker.json').read_text())
        assert w['context']==ctx and len(w['records'])==25
        assert w['journal_write_bytes']==(out/'Journal.jsonl').stat().st_size
        journal=replay_journal(out/'Journal.jsonl',allmodels[w['index']],ctx)
        p=None;math=[]
        for rec,m in zip(w['records'],allmodels[w['index']]):
            if 'proof' in rec:p=copy.deepcopy(rec['proof'])
            else:
                p['cost_units']=rec['cost_units'];p['model']=sha(m)
            independent(m,p,ctx);assert verify(m,p,ctx)
            assert rec['cost_units']==p['cost_units'];key=sha(m)
            if key not in answers:answers[key]=reference(m)
            assert p['cost_units']==answers[key]
            proofkey=sha(p)
            if proofkey not in proofs:
                names=mutations(m,p,ctx);invalid+=len(names)
                proofs[proofkey]={'model_digest':key,'controls':names}
            checks+=1
            if rec['action']=='patch':
                patches+=1;compactions+=int(rec['compacted']);assert rec['journal_bytes']<=w['budget']
                assert rec['edge_checks']==len(inputs[w['index']]['changes'][rec['step']-1])
            if rec['action']=='fallback':fallbacks+=1
            math.append({'record':rec,'proof_digest':proofkey,'model_digest':key})
        assert sha(p)==w['final_proof'] and sha(allmodels[w['index']][-1])==w['final_model']
        # Final checkpoint is independently replayed by the production restore;
        # here its terminal proof/model must bind the separately evaluated state.
        from delta import Captured
        rm,rp=Captured.restore(json.loads((out/'Checkpoint.json').read_bytes()),ctx).export()
        assert rm==allmodels[w['index']][-1] and sha(rp)==sha(p)
        records[session['name']]={'records':math,'journal':journal,
            'journal_sha256':hashlib.sha256((out/'Journal.jsonl').read_bytes()).hexdigest(),
            'checkpoint_sha256':hashlib.sha256((out/'Checkpoint.json').read_bytes()).hexdigest(),
            'journal_write_bytes':w['journal_write_bytes'],'checkpoint_bytes':w['checkpoint_bytes']}
    controls=json.loads((ROOT/'Controls.json').read_text())
    from controls import run as control_run
    assert control_run(ctx)==controls
    for case in controls['noncost_cases']:
        independent(case['model'],case['proof'],ctx);assert case['proof'].get('cost_units')==reference(case['model'])
        invalid+=len(mutations(case['model'],case['proof'],ctx))
    assert all(c['rejected'] for c in controls['transaction_controls']+controls['recovery_controls'])
    # Small independent brute-force regression; does not count as held-out scale.
    from suite import model
    tiny=model(2,True,31);best=None;enumerated=0
    for x in itertools.product(range(4),repeat=4):
        enumerated+=1;balance=[0]*4
        for e,v in zip(tiny['edges'],x):balance[e['a']]+=v;balance[e['z']]-=v
        if balance==tiny['b']:
            value=sum(e['c']*v for e,v in zip(tiny['edges'],x));best=value if best is None else min(best,value)
    assert best==reference(tiny)
    report={'passed':True,'workers':len(sessions),'queries_checked':checks,'distinct_models':len(answers),
            'distinct_proofs':len(proofs),'invalid_certificate_controls':invalid,
            'transaction_controls':len(controls['transaction_controls']),'recovery_controls':len(controls['recovery_controls']),
            'noncost_controls':len(controls['noncost_cases']),'patch_records':patches,'fallback_records':fallbacks,
            'compaction_records':compactions,'tiny_enumerated_assignments':enumerated,'audit_wall_s':time.perf_counter()-tick}
    (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'Mathematical-records.json').write_text(json.dumps(records,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':run()
