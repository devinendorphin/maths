"""Independent arithmetic, two algorithm references, full transcript and rollback replay."""
import copy
import hashlib
import json
from pathlib import Path
import time
import networkx as nx
from ortools.graph.python import min_cost_flow
from checker import digest, encode, verify
from controls import run as controls
from engine import ROUTES
from environment import capture
from transaction import Transaction

ROOT=Path(__file__).resolve().parents[1]


def independent(m,p,ctx):
    assert p['model']==digest(m) and p['dependency']==ctx
    if p['kind']=='cut':
        assert len(p['set'])==len(set(p['set']))
        s=set(p['set']);assert all(type(v) is int and 0<=v<m['n'] for v in s)
        lhs=sum(m['b'][v] for v in s)
        rhs=sum(e['u'] for e in m['edges'] if e['a'] in s and e['z'] not in s)-sum(e['l'] for e in m['edges'] if e['a'] not in s and e['z'] in s)
        assert lhs>rhs;return None
    balance=[0]*m['n'];value=0
    assert len(p['flow'])==len(m['edges']) and len(p['pi'])==m['n'] and all(type(v) is int for v in p['pi'])
    for e,x in zip(m['edges'],p['flow']):
        assert type(x) is int and e['l']<=x<=e['u'];balance[e['a']]+=x;balance[e['z']]-=x;value+=e['c']*x
        r=e['c']+p['pi'][e['a']]-p['pi'][e['z']]
        if x<e['u']:assert r>=0
        if x>e['l']:assert r<=0
    assert balance==m['b'] and value==p['cost_units'];return value


def references(m):
    g=nx.MultiDiGraph();b=m['b'].copy();constant=0
    native=min_cost_flow.SimpleMinCostFlow()
    for v in range(m['n']):g.add_node(v)
    for i,e in enumerate(m['edges']):
        b[e['a']]-=e['l'];b[e['z']]+=e['l'];constant+=e['l']*e['c']
        g.add_edge(e['a'],e['z'],key=i,capacity=e['u']-e['l'],weight=e['c'])
        native.add_arc_with_capacity_and_unit_cost(e['a'],e['z'],e['u']-e['l'],e['c'])
    for v in range(m['n']):g.nodes[v]['demand']=-b[v];native.set_node_supply(v,b[v])
    try:a=nx.network_simplex(g)[0]+constant
    except nx.NetworkXUnfeasible:a=None
    status=native.solve();assert status in (native.OPTIMAL,native.INFEASIBLE)
    z=native.optimal_cost()+constant if status==native.OPTIMAL else None
    assert a==z;return a


def run():
    tick=time.perf_counter();f=json.loads((ROOT/'Freeze.json').read_text());ctx=f['context']
    for name,h in f['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    assert capture()==f['environment']
    inputs=json.loads((ROOT/'Inputs.json').read_text());sessions=json.loads((ROOT/'Sessions.json').read_text())
    assert len(sessions)==48 and {(s['index'],s['route'],s['repetition']) for s in sessions}=={(i,r,k) for i in range(6) for r in ROUTES for k in range(2)}
    assert all(s['exit_code']==0 and not s['timed_out'] for s in sessions)
    answers={};proofs={};logical={};queries=0;cut_queries=0;invalid=0;actions={};below_old=0;lower_above_old=0;recovered=0;fallbacks=0;guards=0
    for session in sessions:
        out=ROOT/'outputs'/session['name'];w=json.loads((out/'Worker.json').read_text());entry=inputs['heldout'][w['index']]
        state=Transaction(entry['model'],ctx);previous=None;per=[]
        assert len(w['records'])==25 and len(w['query_wall_s'])==25 and all(w[k]==session[k] for k in ('index','route','repetition'))
        raw=(out/'Evidence.jsonl').read_bytes();assert len(raw)==w['evidence_bytes'] and [json.loads(z) for z in raw.splitlines()]==w['records']
        for step,rec in enumerate(w['records']):
            if step:
                q=dict(copy.deepcopy(entry['updates'][step-1]['message']),context=ctx)
                if previous['kind']=='optimal':
                    for z in q['edges']:
                        if z['field']=='u' and z['new']<previous['flow'][z['edge']]:below_old+=1
                        if z['field']=='l' and z['new']>previous['flow'][z['edge']]:lower_above_old+=1
                state.apply(q)
            m=state.model;p=rec['proof'];assert rec['step']==step and rec['version']==step and rec['model']==digest(m)
            value=independent(m,p,ctx);assert verify(m,p,ctx)
            key=digest(m)
            if key not in answers:answers[key]=references(m)
            assert answers[key]==value
            if p['kind']=='cut':cut_queries+=1
            if previous is not None and previous['kind']=='cut' and p['kind']=='optimal':recovered+=1
            if rec['stats']['guard_attempt']:
                assert w['route']=='guard-repair' and previous is not None and previous['kind']=='optimal'
                test=copy.deepcopy(previous);test['model']=key;test['cost_units']=sum(e['c']*x for e,x in zip(m['edges'],test['flow']))
                assert verify(m,test,ctx)==rec['stats']['guard_accepted']
            if rec['stats']['guard_accepted']:assert rec['action']=='certificate-admission';guards+=1
            if rec['stats']['budget_fallback']:assert rec['action']=='charged-cold-fallback';fallbacks+=1
            pid=hashlib.sha256(encode(p)).hexdigest()
            if pid not in proofs:
                bad=copy.deepcopy(p);bad['dependency']='wrong';assert not verify(m,bad,ctx);invalid+=1
                bad=copy.deepcopy(p)
                if p['kind']=='optimal':bad['cost_units']+=1
                else:bad['set']=[]
                assert not verify(m,bad,ctx);invalid+=1;proofs[pid]=key
            actions[rec['action']]=actions.get(rec['action'],0)+1;queries+=1;previous=copy.deepcopy(p)
            per.append({'record':rec,'proof':pid})
        assert digest(m)==w['final_model'] and hashlib.sha256(encode(p)).hexdigest()==w['final_proof']
        logical[session['name']]={'records':per,'worker':{k:v for k,v in w.items() if k not in ('records','query_wall_s','worker_wall_s','worker_cpu_s','worker_maxrss_kib')},'evidence_sha256':hashlib.sha256(raw).hexdigest()}
    c=controls(ctx);assert json.loads((ROOT/'Controls.json').read_text())==c
    assert verify(c['model'],c['initial_proof'],ctx) and verify(c['shortage_model'],c['shortage_proof'],ctx)
    report={'passed':True,'workers':48,'queries':queries,'cut_queries':cut_queries,'distinct_models':len(answers),'distinct_proofs':len(proofs),
            'invalid_certificate_controls':invalid,'transaction_controls':len(c['controls']),'actions':actions,'upper_reductions_below_previous_flow':below_old,
            'lower_increases_above_previous_flow':lower_above_old,'recovered_after_cut':recovered,'guard_admissions':guards,'budget_fallbacks':fallbacks,
            'audit_wall_s':time.perf_counter()-tick}
    (ROOT/'Logical.json').write_text(json.dumps(logical,sort_keys=True,indent=2)+'\n');(ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':run()
