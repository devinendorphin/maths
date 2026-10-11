"""Frozen reconstruction, separate primal/residual/cut arithmetic, same solver reference."""
import copy
import hashlib
import json
from pathlib import Path
import time
import networkx as nx
from checker import digest,encode,verify
from controls import run as controls
ROOT=Path(__file__).resolve().parents[1]


def independent(m,p,ctx):
    assert p['model']==digest(m) and p['dependency']==ctx
    if p['kind']=='cut':
        s=set(p['set']);lhs=sum(m['b'][v] for v in s)
        rhs=sum(e['u'] for e in m['edges'] if e['a'] in s and e['z'] not in s)-sum(e['l'] for e in m['edges'] if e['a'] not in s and e['z'] in s)
        assert lhs>rhs;return None
    balance=[0]*m['n'];value=0
    assert len(p['flow'])==len(m['edges']) and len(p['pi'])==m['n']
    for e,x in zip(m['edges'],p['flow']):
        assert type(x) is int and e['l']<=x<=e['u'];balance[e['a']]+=x;balance[e['z']]-=x;value+=e['c']*x
        r=e['c']+p['pi'][e['a']]-p['pi'][e['z']]
        if x<e['u']:assert r>=0
        if x>e['l']:assert r<=0
    assert balance==m['b'] and value==p['cost_units'];return value


def reference(m):
    g=nx.MultiDiGraph();b=m['b'].copy();constant=0
    for v in range(m['n']):g.add_node(v)
    for i,e in enumerate(m['edges']):
        b[e['a']]-=e['l'];b[e['z']]+=e['l'];constant+=e['l']*e['c']
        g.add_edge(e['a'],e['z'],key=i,capacity=e['u']-e['l'],weight=e['c'])
    for v in range(m['n']):g.nodes[v]['demand']=-b[v]
    try:return nx.network_simplex(g)[0]+constant
    except nx.NetworkXUnfeasible:return None


def run():
    tick=time.perf_counter();f=json.loads((ROOT/'Freeze.json').read_text());ctx=f['context']
    for name,h in f['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    import networkx.algorithms.flow.networksimplex as mod
    assert nx.__version__==f['environment']['networkx'] and hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()==f['environment']['networksimplex_sha256']
    inputs=json.loads((ROOT/'Inputs.json').read_text());sessions=json.loads((ROOT/'Sessions.json').read_text())
    assert len(sessions)==54 and {(s['index'],s['route'],s['repetition']) for s in sessions}=={(i,r,k) for i in range(9) for r in ('cold','basis','guard') for k in range(2)}
    assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
    answers={};proofs={};logical={};queries=0;cut_queries=0;invalid=0;actions={}
    for session in sessions:
        out=ROOT/'outputs'/session['name'];w=json.loads((out/'Worker.json').read_text());entry=inputs['heldout'][w['index']];m=copy.deepcopy(entry['model']);p=None;per=[]
        assert len(w['records'])==25 and all(w[k]==session[k] for k in ('index','route','repetition'))
        raw=(out/'Evidence.jsonl').read_bytes();assert len(raw)==w['evidence_bytes'] and [json.loads(z) for z in raw.splitlines()]==w['records']
        for step,rec in enumerate(w['records']):
            if step:
                update=entry['updates'][step-1];assert digest(m)==update['old_model']
                if update['kind']=='cost':
                    for z in update['changes']:assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                else:m=copy.deepcopy(update['model']);assert rec['action']=='model-reset'
            assert rec['step']==step and rec['model']==digest(m)
            if 'proof' in rec:p=copy.deepcopy(rec['proof'])
            else:
                assert rec['action']=='certificate-patch' and w['route']=='guard' and p['kind']=='optimal'
                p['model']=digest(m);p['cost_units']=rec['cost_units']
                assert rec['edge_checks']==len(entry['updates'][step-1]['changes'])
            value=independent(m,p,ctx);assert verify(m,p,ctx)
            key=digest(m)
            if key not in answers:answers[key]=reference(m)
            assert answers[key]==value
            if p['kind']=='cut':cut_queries+=1
            pid=hashlib.sha256(encode(p)).hexdigest()
            if pid not in proofs:
                bad=copy.deepcopy(p);bad['dependency']='wrong';assert not verify(m,bad,ctx);invalid+=1
                bad=copy.deepcopy(p)
                if p['kind']=='optimal':bad['cost_units']+=1
                else:bad['set']=[]
                assert not verify(m,bad,ctx);invalid+=1;proofs[pid]=key
            actions[rec['action']]=actions.get(rec['action'],0)+1;queries+=1
            per.append({'record':rec,'proof':pid})
        assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        logical[session['name']]={'records':per,'worker':{k:v for k,v in w.items() if k not in ('records','worker_wall_s','worker_cpu_s','worker_maxrss_kib')},'evidence_sha256':hashlib.sha256(raw).hexdigest()}
    assert json.loads((ROOT/'Controls.json').read_text())==controls(ctx)
    report={'passed':True,'workers':54,'queries':queries,'cut_queries':cut_queries,'distinct_models':len(answers),'distinct_proofs':len(proofs),
            'invalid_certificate_controls':invalid,'adapter_controls':len(controls(ctx)['controls']),'actions':actions,'audit_wall_s':time.perf_counter()-tick}
    (ROOT/'Logical.json').write_text(json.dumps(logical,sort_keys=True,indent=2)+'\n');(ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':run()
