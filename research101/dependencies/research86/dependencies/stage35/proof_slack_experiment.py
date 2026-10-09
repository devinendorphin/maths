"""Inline arithmetic experiment. Standard library only; see frozen protocol."""
import argparse
import hashlib
import inspect
import json
import platform
import random
import textwrap
import time
from dataclasses import asdict
import flat_baseline as flat

MODES=('endpoint','slack_max','slack_branch')
ORIGINAL='''                        num += (max(0, cell.b*p[i]-cell.a*w[i])
                                - max(0, cell.b*anchor[i]-cell.a*w[i]))'''
REPLACEMENTS={
    'endpoint':ORIGINAL,
    'slack_max':'''                        slack = cell.b*anchor[i]-cell.a*w[i]
                        increment = cell.b*delta
                        num += max(0, slack+increment)-max(0, slack)''',
    'slack_branch':'''                        slack = cell.b*anchor[i]-cell.a*w[i]
                        increment = cell.b*delta
                        next_slack = slack+increment
                        if slack > 0:
                            num += increment if next_slack > 0 else -slack
                        elif next_slack > 0:
                            num += next_slack'''}

def compile_solvers():
    source=inspect.getsource(flat.solve)
    assert source.count(ORIGINAL)==1
    solvers={'endpoint':flat.solve}
    for mode in MODES[1:]:
        namespace=vars(flat).copy()
        variant=source.replace(ORIGINAL,REPLACEMENTS[mode])
        exec(compile(variant,'<inline-'+mode+'>','exec'),namespace)
        solvers[mode]=namespace['solve']
    return solvers

SOLVERS=compile_solvers()

def begin(store,w,p,c,chosen,old,anchor,mode):
    arena=flat.Arena(store)
    return arena,SOLVERS[mode](w,p,c,chosen,old,anchor,'flat_share',arena)

def advance(store,w,p,c,chosen,old,anchor,mode):
    arena,gen=begin(store,w,p,c,chosen,old,anchor,mode)
    answer,steps=flat.run_to_completion(gen)
    gen.close();steps+=1
    _,cleanup=flat.run_to_completion(arena.cleanup(answer[2]));steps+=cleanup
    if old is not None:
        _,retirement=flat.run_to_completion(old.release());steps+=retirement
    return answer,steps,arena.refreshes,arena.splits

def snapshot(store,old):
    return (None if old is None else tuple(old.ids),
            {i:(asdict(cell),refs) for i,(cell,refs) in store.cells.items()},
            dict(store.blocks))

def cancel(store,old,arena,gen,saved):
    flat.ownership(store,[] if old is None else [old],[arena])
    gen.close();flat.run_to_completion(arena.cleanup())
    assert snapshot(store,old)==saved
    flat.ownership(store,[] if old is None else [old])

def cancellation_checks(store,w,p,c,chosen,old,anchor,mode,all_prefixes=False):
    saved=snapshot(store,old)
    arena,gen=begin(store,w,p,c,chosen,old,anchor,mode)
    _,length=flat.run_to_completion(gen)
    cancel(store,old,arena,gen,saved)
    # length includes the terminal next(); there are length-1 suspensions.
    points=range(length) if all_prefixes else sorted(set(
        (0,1,2,10,length//4,length//2,3*length//4,length-2)))
    points=[x for x in points if 0<=x<length]
    for stop in points:
        arena,gen=begin(store,w,p,c,chosen,old,anchor,mode)
        for _ in range(stop):next(gen)
        cancel(store,old,arena,gen,saved)
    return dict(canceled_prefixes=len(points),suspensions=length-1,
                completed_uncommitted_cancel=1)

def dispose(store,old):
    _,steps=flat.run_to_completion(old.release());store.empty()
    return steps

def audit(store,w,p,c,best,chosen,old):
    flat.ownership(store,[old])
    return flat.audit(w,p,c,best,chosen,old)

def scalar_checks():
    # Compile the exact replacement text into an untimed arithmetic adapter.
    adapters={}
    for mode,clause in REPLACEMENTS.items():
        namespace={}
        body=textwrap.dedent(clause)
        source='def update(cell,p,anchor,w,i,delta,num):\n'+textwrap.indent(body,'    ')+'\n    return num\n'
        exec(compile(source,'<scalar-'+mode+'>','exec'),namespace)
        adapters[mode]=namespace['update']
    count=0;pop=dict(stable=0,entering=0,leaving=0,inactive=0,zero_endpoint=0)
    for weight in range(1,6):
        for a in range(6):
            for b in range(1,5):
                cell=flat.Cell(0,1,0,a,b,0)
                for p in range(-8,9):
                    for q in range(-8,9):
                        s=b*p-a*weight;t=b*q-a*weight
                        expected=max(0,t)-max(0,s)
                        for fn in adapters.values():
                            assert fn(cell,[q],[p],[weight],0,q-p,17)==17+expected
                        pop['stable' if s>0 and t>0 else 'entering' if t>0 else
                            'leaving' if s>0 else 'inactive']+=1
                        pop['zero_endpoint']+=int(s==0 or t==0);count+=1
    # Two opposite active contributions cancel exactly without allocating a cache.
    cell=flat.Cell(0,3,0,1,1,0);p=[4,6];q=[5,5];w=[1,1]
    for fn in adapters.values():
        num=9
        for i in range(2):num=fn(cell,q,p,w,i,q[i]-p[i],num)
        assert num==9
    return dict(signed_lattice_cases=count,population=pop,net_cancellation=True)

def falling_fixture():
    w,c=[6,10,5,2,9,7],13;p,q=[9,25,17,23,16,30],[9,25,17,-7,16,30]
    records=[]
    for mode in MODES[1:]:
        store=flat.Store();chosen=0;old=None
        construction=cancellation_checks(store,w,p,c,chosen,old,None,mode,True)
        (best,chosen,old),_,_,_=advance(store,w,p,c,chosen,old,None,mode)
        audit(store,w,p,c,best,chosen,old)
        incumbent=sum(q[i] for i in range(len(w)) if chosen>>i&1)
        threats=0
        for fixed,free,residual,a,b,num in old.fields():
            updated=b*sum(q[i] for i in range(len(w)) if fixed>>i&1)+a*residual
            updated+=sum(max(0,b*q[i]-a*w[i]) for i in range(len(w)) if free>>i&1)
            threats+=int(updated==num and updated//b>incumbent)
        assert threats>0
        repair=cancellation_checks(store,w,q,c,chosen,old,p,mode,True)
        (after,chosen,old),_,_,_=advance(store,w,q,c,chosen,old,p,mode)
        audit(store,w,q,c,after,chosen,old);dispose(store,old)
        records.append(dict(mode=mode,construction=construction,repair=repair,
            old_optimum=best,new_incumbent=incumbent,unchanged_threats=threats,new_optimum=after))
    return records

def verify():
    rng=random.Random(799173)
    counts=dict(exact_queries=0,numerator_checks=0,canonical_matches=0,
        sampled_prefix_cancellations=0,completed_uncommitted_cancellations=0,
        recoveries=0,negative_streams=0,zero_capacities=0)
    for trial in range(60):
        w=[rng.randint(1,15) for _ in range(8)]
        c=0 if trial%10==0 else rng.randrange(sum(w)+1)
        p=[rng.randint(-10,30) for _ in w];stream=[p]
        counts['negative_streams']+=int(min(p)<0);counts['zero_capacities']+=int(c==0)
        for _ in range(7):
            q=p.copy()
            for i in rng.sample(range(8),rng.choice((1,3,8))):q[i]+=rng.choice((-1,1))*rng.randint(1,20)
            stream.append(q);p=q
        stream.append([value+rng.randint(-15,15) for value in p])
        canonical=[]
        for mode in MODES:
            store=flat.Store();chosen=0;old=None;anchor=None
            for t,profits in enumerate(stream):
                if mode!='endpoint' and t in (0,8):
                    check=cancellation_checks(store,w,profits,c,chosen,old,anchor,mode)
                    counts['sampled_prefix_cancellations']+=check['canceled_prefixes']
                    counts['completed_uncommitted_cancellations']+=1
                (best,chosen,old),_,_,_=advance(store,w,profits,c,chosen,old,anchor,mode)
                counts['numerator_checks']+=audit(store,w,profits,c,best,chosen,old)
                record=(best,chosen,old.fields())
                if mode=='endpoint':canonical.append(record)
                else:
                    assert record==canonical[t];counts['canonical_matches']+=1
                    if t==8:counts['recoveries']+=1
                counts['exact_queries']+=1;anchor=profits
            dispose(store,old)
    return dict(counts=counts,arithmetic=scalar_checks(),falling_incumbent=falling_fixture(),
                all_final_stores_empty=True)

def timed_stream(w,c,stream,mode):
    store=flat.Store();anchor=None;chosen=0;old=None;rows=[];digest=hashlib.sha256()
    for p in stream:
        previous=store.stats.copy();cpu0,wall0=time.process_time(),time.perf_counter()
        (best,chosen,old),steps,refreshes,splits=advance(store,w,p,c,chosen,old,anchor,mode)
        cpu,wall=time.process_time()-cpu0,time.perf_counter()-wall0
        assert best==flat.dp(w,p,c)
        fs=old.fields();digest.update(repr((best,chosen,fs)).encode())
        rows.append(dict(cpu=cpu,wall=wall,steps=steps,refreshes=refreshes,splits=splits,
            cover_cells=len(fs),counters={k:store.stats[k]-previous[k] for k in previous
            if not k.startswith('peak')}));anchor=p
    cpu0,wall0=time.process_time(),time.perf_counter();final_steps=dispose(store,old)
    final_cpu,final_wall=time.process_time()-cpu0,time.perf_counter()-wall0
    return dict(mode=mode,queries=rows,final_steps=final_steps,final_cpu=final_cpu,
        final_wall=final_wall,stats=store.stats,digest=digest.hexdigest(),
        cpu=sum(r['cpu'] for r in rows)+final_cpu,wall=sum(r['wall'] for r in rows)+final_wall,
        steps=sum(r['steps'] for r in rows)+final_steps)

def signature(run):
    return (run['digest'],run['steps'],run['stats'],
        [(q['steps'],q['refreshes'],q['splits'],q['cover_cells'],q['counters']) for q in run['queries']])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='slack-results.json')
    parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    checks=verify()
    with open('slack-verification.json','w') as f:json.dump(checks,f,indent=2)
    print('Verification:',json.dumps(checks),flush=True)
    if args.verify_only:return
    results=dict(protocol='Proof-slack-protocol.md',python=platform.python_version(),
        platform=platform.platform(),verification=checks,runs=[])
    shuffle=random.Random(553819);deterministic={}
    for rep in range(3):
        for family in ('uncorrelated','proportional'):
            for regime in ('sparse1','sparse6','dense24','alternating','pulse10','mixed'):
                for seed in (51000,51001):
                    w,c,stream=flat.workload(seed,family,regime)
                    modes=list(MODES);shuffle.shuffle(modes);canonical=None
                    for mode in modes:
                        run=timed_stream(w,c,stream,mode);run.update(rep=rep,family=family,regime=regime,seed=seed)
                        sig=signature(run)
                        if canonical is None:canonical=sig
                        else:assert sig==canonical,(rep,family,regime,seed,mode)
                        key=(family,regime,seed)
                        if key in deterministic:assert sig==deterministic[key]
                        else:deterministic[key]=sig
                        results['runs'].append(run)
                print('Finished',rep,family,regime,flush=True)
        with open(args.output,'w') as f:json.dump(results,f,indent=2)
    print('CPU totals:',{m:[sum(x['cpu'] for x in results['runs'] if x['mode']==m and x['rep']==r)
        for r in range(3)] for m in MODES},flush=True)

if __name__=='__main__':main()
