"""Complete fresh sessions, all producer/proof/admission/log costs charged."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import networkx as nx
from basis import Basis
from checker import digest,encode,verify
from delta import Captured
from producer import certificate,feasibility,potentials
from predecessor_worker import solve

ROOT=Path(__file__).resolve().parents[1]


def proof(m,x,ctx):
    if x is None:
        _,cut=feasibility(m);p=certificate(m,ctx,cut=cut)
    else:
        pi,cycle=potentials(m,x);assert cycle is None;p=certificate(m,ctx,flow=x,pi=pi)
    assert verify(m,p,ctx);return p


def fresh(m,ctx,route):
    if route=='cold':return None,solve(m,ctx),0
    basis=Basis(m)
    try:x=basis.optimize()
    except nx.NetworkXUnfeasible:x=None
    p=proof(m,x,ctx);return (basis if x is not None else None),p,basis.last_pivots


def run(destination,index,route,rep):
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    tick,cpu=time.perf_counter(),time.process_time();f=json.loads((ROOT/'Freeze.json').read_text());ctx=f['context']
    for name,h in f['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    entry=json.loads((ROOT/'Inputs.json').read_text())['heldout'][index];m=copy.deepcopy(entry['model'])
    out=Path(destination);out.mkdir();records=[];nbytes=0
    with (out/'Evidence.jsonl').open('wb') as log:
        def write(rec):
            nonlocal nbytes
            data=encode(rec)+b'\n';log.write(data);log.flush();nbytes+=len(data);records.append(copy.deepcopy(rec))
        solver,p,pivots=fresh(m,ctx,route);state=Captured(m,p,ctx,budget=10**9) if p['kind']=='optimal' else None
        write({'step':0,'action':'initial','proof':p,'pivots':pivots,'edge_checks':0,'model':digest(m)})
        for step,update in enumerate(entry['updates'],1):
            assert digest(m)==update['old_model'];accepted=False;checks=0;pivots=0
            if update['kind']=='cost':
                changes=update['changes'];msg={'version':step-1,'context':ctx,'changes':changes}
                if route=='guard' and state is not None:
                    result=state.patch(msg);accepted=result['accepted'];checks=result['edge_checks']
                if solver is not None:solver.change_costs(changes)
                for z in changes:
                    assert m['edges'][z['edge']]['c']==z['old'];m['edges'][z['edge']]['c']=z['new']
                if accepted:
                    assert p['kind']=='optimal';p['model']=digest(m);p['cost_units']=state._p['cost_units'];action='certificate-patch'
                elif solver is not None:
                    x=solver.optimize();p=proof(m,x,ctx);pivots=solver.last_pivots;action='retained-basis'
                else:
                    solver,p,pivots=fresh(m,ctx,route);action='cold' if route=='cold' else 'basis-rebuild'
            else:
                if solver is not None:
                    try:solver.require_fixed(update['model'])
                    except ValueError:pass
                    else:raise AssertionError('noncost update admitted into old basis')
                m=copy.deepcopy(update['model']);solver,p,pivots=fresh(m,ctx,route);action='model-reset'
            if not accepted:state=Captured(m,p,ctx,step,budget=10**9) if p['kind']=='optimal' else None
            rec={'step':step,'action':action,'model':digest(m),'kind':p['kind'],'pivots':pivots,'edge_checks':checks}
            if accepted:rec['cost_units']=p['cost_units']
            else:rec['proof']=copy.deepcopy(p)
            write(rec)
        if state is not None:
            mm,pp=state.export();assert mm==m and pp==p
    result={'index':index,'route':route,'repetition':rep,'context':ctx,'records':records,'evidence_bytes':nbytes,
            'final_model':digest(m),'final_proof':hashlib.sha256(encode(p)).hexdigest(),
            'worker_wall_s':time.perf_counter()-tick,'worker_cpu_s':time.process_time()-cpu,'worker_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (out/'Worker.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
