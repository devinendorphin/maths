from dataclasses import replace
from fractions import Fraction
import copy
import gc
import json
import os
from pathlib import Path
import re
import subprocess
import time
import tracemalloc
from pyscipopt import Model, quicksum
from core import ROOT, Cache, NATIVE_CHECKER, WRAPPER, clock, elapsed, encode, produce, replay, scaled, scope, sha, value, verify_file
from memory import Sampler, reachable_bytes

SDK = Path('/workspace/maths-toolchains/repair-sdk')
SCIP = SDK/'scip-build/bin/scip'


def write(name, data):
    path=ROOT/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(encode(data)); return str(path.relative_to(ROOT))


def record_fact(fact, row):
    return dict(row=row, fact=fact.record())


def scip_stream(row, observations, method):
    start=clock(); phases={'ordinary_scip_candidate':0.0}; outputs=[]; facts=[]; proof_costs=[]
    solver=None; variables=None
    for t in observations:
        q=scaled(row,t); begin=clock()
        if method=='cold' or solver is None:
            solver=Model(); solver.hideOutput(); solver.setRealParam('limits/time',20)
            solver.setIntParam('parallel/maxnthreads',1); solver.setIntParam('randomization/randomseedshift',0)
            if method=='reoptimized': solver.enableReoptimization()
            variables=[solver.addVar(vtype='B',name=f'x{i}') for i in range(row['n'])]
            solver.addCons(quicksum(w*x for w,x in zip(row['weights'],variables))<=row['capacity'])
            solver.setObjective(quicksum(qi*x for qi,x in zip(q,variables)),'maximize')
        else:
            solver.freeReoptSolve()
            solver.chgReoptObjective(quicksum(qi*x for qi,x in zip(q,variables)),sense='maximize')
        solver.optimize(); assert str(solver.getStatus())=='optimal'
        vals=[solver.getVal(x) for x in variables]
        assert all(min(abs(v),abs(v-1))<1e-7 for v in vals)
        candidate=sum(1<<i for i,v in enumerate(vals) if v>0.5)
        phases['ordinary_scip_candidate']+=elapsed(begin)['cpu']
        fact,cost=produce(row,t,candidate=candidate)
        for k,v in cost['phases'].items(): phases[k]=phases.get(k,0.0)+v
        outputs.append(dict(time=[Fraction(t).numerator,Fraction(t).denominator],packing=candidate,objective=fact.objective))
        facts.append(record_fact(fact,row)); proof_costs.append(cost)
    begin=clock(); write(f'evidence/streams/scip-{row["case_id"]}-{method}-{len(observations)}.json',outputs)
    phases['observation_output_io']=elapsed(begin)['cpu']; total=elapsed(start)
    return dict(outputs=outputs,facts=facts,solver_contract='ordinary SCIP + fully duplicated native exact/VIPR certification',method=method),dict(phases=phases,phase_sum=sum(phases.values()),residual_cpu=total['cpu']-sum(phases.values()),total=total,point_costs=proof_costs)


def admission_stream(row, observations, method):
    start=clock(); facts=[]; outputs=[]; checks=0; failed=0
    endpoints=[]
    if method!='points':
        for t in [0,row['end']]:
            f,_=produce(row,t); endpoints.append(f); facts.append(record_fact(f,row)); checks+=1
        same=endpoints[0].packing==endpoints[1].packing
        if not same: failed+=1
    for t in observations:
        t=Fraction(t)
        if method!='points' and same:
            if method=='replay':
                assert all(replay(row,f) for f in endpoints); checks+=2
            mask=endpoints[0].packing
        else:
            f,_=produce(row,t); facts.append(record_fact(f,row)); checks+=1; mask=f.packing
        outputs.append(dict(time=[t.numerator,t.denominator],packing=mask,objective=value(scaled(row,t),mask)))
    write(f'evidence/streams/admit-{row["case_id"]}-{method}-{len(observations)}.json',outputs)
    return dict(method=method,outputs=outputs,facts=facts,endpoint_checks=checks,failed_probes=failed,immutable_file_monitoring=False),elapsed(start)


def checker_trials(row, first, second, repetition, method):
    original=(ROOT/first.path).read_text(); lines=original.splitlines(); tokens=lines[-1].split();tokens[2]=str(int(tokens[2])-1);lines[-1]=' '.join(tokens)
    bad=ROOT/'evidence/controls/false.vipr';bad.parent.mkdir(parents=True,exist_ok=True);bad.write_text('\n'.join(lines)+'\n')
    malformed=bad.with_name('malformed.vipr');malformed.write_text('INVALID\n')
    request=[(ROOT/first.path,True),(bad,False),(ROOT/second.path,True),(malformed,False),(ROOT/first.path,True)]*4
    start=clock(); decisions=[]; child_accounted=[]
    if method=='fork-resident':
        process=subprocess.Popen([str(WRAPPER),'--stream'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        for path,expected in request:
            process.stdin.write(str(path)+'\n');process.stdin.flush();code,cpu=process.stdout.readline().split();accepted=int(code)==0
            assert accepted==expected;decisions.append(accepted);child_accounted.append(float(cpu))
        process.stdin.close();process.wait(timeout=10);assert process.returncode==0
    else:
        for path,expected in request:
            accepted=verify_file(path);assert accepted==expected;decisions.append(accepted)
    return dict(method=method,requests=[dict(path=str(p.relative_to(ROOT)),expected=e) for p,e in request],decisions=decisions,pristine_parent=True if method=='fork-resident' else None),dict(total=elapsed(start),fork_child_cpu_reported=sum(child_accounted))


def cache_trial(row):
    cache=Cache(row);events=[];facts=[];measurement={};tracemalloc.start()
    gc.collect();baseline=tracemalloc.get_traced_memory()[0]
    with Sampler() as sampler:
        for t in [0,4,0,8,4,8,0]:
            fact,hit,cost=cache.point(t);facts.append(record_fact(fact,row))
            events.append(dict(kind='point',time=t,hit=hit,entries=len(cache.points),evictions=cache.evictions,packing=fact.packing,objective=fact.objective))
        cache.switch(row=row);entry=cache.snapshot(0,row['end'])
        events.append(dict(kind='snapshot',admitted=entry is not None,lookup=cache.lookup(4)))
        measurement['reachable_cache_bytes']=reachable_bytes((cache.points,cache.snapshots))
        measurement['serialized_fact_bytes']=len(encode([x.record() for x in cache.points.values()]))
        measurement['traced_scenario_bytes_above_baseline']=tracemalloc.get_traced_memory()[0]-baseline
        # These are live context changes, not detached verifier predicates.
        for change in ['capacity','weight','objective','domain','nonlinear','dependency']:
            cache.switch(row=row,checker=NATIVE_CHECKER);cache.snapshot(0,row['end'])
            changed=copy.deepcopy(row);rejected=False
            if change=='capacity':changed['capacity']+=1
            if change=='weight':changed['weights'][0]+=1
            if change=='objective':changed['profits'][0]+=1
            if change=='domain':changed['domain']='continuous'
            if change=='nonlinear':changed['quadratic']=[1]*row['n'];changed['objective_class']='quadratic'
            try:cache.switch(row=changed,checker=WRAPPER if change=='dependency' else NATIVE_CHECKER)
            except ValueError:rejected=True
            assert cache.lookup(4) is None and not cache.points
            fresh=None
            if not rejected:
                fact,hit,_=cache.point(4);assert not hit;facts.append(record_fact(fact,changed));fresh=fact.record()
            events.append(dict(kind='context-change',change=change,changed_model=changed,rejected=rejected,new_fact=fresh,old_snapshot_miss=True,epoch=cache.epoch,evictions=cache.evictions))
        cache.switch(row=row,checker=NATIVE_CHECKER);entry=cache.snapshot(0,row['end'])
        if entry is not None:
            original=entry[5];data=(ROOT/original.path).read_bytes()
            path=ROOT/'evidence/controls/modified-external.vipr';path.write_bytes(data+b'\n')
            mutated=replace(original,path=str(path.relative_to(ROOT)))
            # Bytes after immutable admission can change without changing captured mathematical facts.
            captured=cache.lookup(4);assert captured==entry[4]
            refreshed=cache.refresh(mutated);assert not refreshed and cache.lookup(4) is None
            events.append(dict(kind='external-edit',immutable_lookup=captured,explicit_refresh_accepted=refreshed,proof_hash_changed=True))
        measurement['cache_bytes_before_clear']=reachable_bytes((cache.points,cache.snapshots))
        cache.points.clear();cache.snapshots.clear();gc.collect()
        measurement['cache_bytes_after_clear']=reachable_bytes((cache.points,cache.snapshots))
        measurement['traced_peak_scenario_bytes']=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop();measurement['resident_process_tree']=sampler.report()
    return dict(events=events,facts=facts,immutable_contract='fixed model and explicit dependency epoch; external file changes require explicit refresh'),measurement


def exact_point(row,t):
    begin=clock();t=Fraction(t);q=scaled(row,t);folder=ROOT/'evidence/scip';folder.mkdir(parents=True,exist_ok=True)
    label=f'{row["case_id"]}-{t.numerator}-{t.denominator}'
    lp=folder/(label+'.lp');proof=folder/(label+'.vipr');settings=folder/(label+'.set')
    expression=' '.join(('+' if v>=0 else '-')+' '+str(abs(v))+' x'+str(i) for i,v in enumerate(q))
    lp.write_text('Maximize\n objective: '+expression+'\nSubject To\n capacity: '+' + '.join(f'{w} x{i}' for i,w in enumerate(row['weights']))+f' <= {row["capacity"]}\nBinary\n '+' '.join(f'x{i}' for i in range(row['n']))+'\nEnd\n')
    settings.write_text('exact/enable = TRUE\ncertificate/filename = "'+str(proof)+'"\npresolving/maxrounds = 0\npresolving/maxrestarts = 0\nseparating/maxrounds = 0\nseparating/maxroundsroot = 0\nlimits/time = 20\nrandomization/randomseedshift = 0\n')
    encoded=elapsed(begin)['cpu'];start=clock();p=subprocess.run([str(SCIP),'-s',str(settings),'-f',str(lp)],capture_output=True,text=True,timeout=20)
    solver=elapsed(start);(folder/(label+'.log')).write_text(p.stdout+p.stderr)
    assert p.returncode==0 and '[optimal solution found]' in p.stdout and 'solving problem in exact solving mode' in p.stdout
    assert proof.exists() and proof.stat().st_size<=1048576
    raw_identity=sha(proof.read_bytes()); raw_path=str(proof.relative_to(ROOT)); completion=0.0
    required=(' weak ' in proof.read_text() or ' incomplete' in proof.read_text())
    if required:
        completed=folder/(label+'-complete.vipr');start=clock()
        pcomp=subprocess.run([str(SDK/'vipr-build-compatible/viprcomp'),'--verbosity=0','--threads=1','--soplex=on','--outfile='+str(completed),str(proof)],capture_output=True,text=True,timeout=20)
        completion=elapsed(start)['cpu'];(folder/(label+'-completion.log')).write_text(pcomp.stdout+pcomp.stderr)
        assert pcomp.returncode==0 and completed.exists();proof=completed
    start=clock();accepted=verify_file(proof);checker_cost=elapsed(start)
    if not accepted:
        return dict(status='certificate_not_verified',row=row,time=[t.numerator,t.denominator],proof=str(proof.relative_to(ROOT)),sha256=sha(proof.read_bytes())),dict(total=elapsed(begin),solver=solver,checker=checker_cost)
    tokens=proof.read_text().split();vi=tokens.index('VAR');n=int(tokens[vi+1]);names=tokens[vi+2:vi+2+n];si=tokens.index('SOL');assert int(tokens[si+1])==1;k=int(tokens[si+3]);packing=0
    for index in range(k):
        j=int(tokens[si+4+2*index]);amount=Fraction(tokens[si+5+2*index]);assert amount in [0,1]
        original=int(names[j].removeprefix('t_').removeprefix('x'))
        if amount:packing|=1<<original
    return dict(status='verified_native_scip',row=row,time=[t.numerator,t.denominator],packing=packing,objective=value(q,packing),proof=str(proof.relative_to(ROOT)),sha256=sha(proof.read_bytes()),raw_proof=raw_path,raw_sha256=raw_identity,presolve_rounds=0,separation_rounds=0,completion_work_required=required),dict(total=elapsed(begin),encoding_cpu=encoded,solver=solver,checker=checker_cost,completion_cpu=completion)


def run():
    freeze=json.loads((ROOT/'Freeze.json').read_text())
    for name,digest in freeze['files'].items():assert sha((ROOT/name).read_bytes())==digest,name
    sdk=json.loads((ROOT/'SDK-manifest.json').read_text())
    for binary in sdk['binaries'].values():assert sha(Path(binary['path']).read_bytes())==binary['sha256']
    rows={r['case_id']:r for r in json.loads((ROOT/'Inputs.json').read_text())};results=[];start=time.perf_counter()
    def add(kind,logical,measurements):
        assert time.perf_counter()-start<300
        results.append(dict(kind=kind,logical=logical,measurements=measurements))
    first,_=produce(rows['heldout-n18-0'],0);second,_=produce(rows['heldout-factor'],4)
    write('Checker-fixtures.json',[record_fact(first,rows['heldout-n18-0']),record_fact(second,rows['heldout-factor'])])
    for repeat in range(3):
        order=['per-request','fork-resident'];order=order[repeat%2:]+order[:repeat%2]
        for method in order:
            logical,measured=checker_trials(rows['heldout-n18-0'],first,second,repeat,method);logical['repeat']=repeat;add('R113',logical,measured)
    for case in ['heldout-n18-0','heldout-factor']:
        row=rows[case]
        for density,observations in [('dense',list(range(9))),('sparse',[0,4,8])]:
            for repeat in range(3):
                methods=['points','replay','immutable'];methods=methods[repeat:]+methods[:repeat]
                for method in methods:
                    logical,measured=admission_stream(row,observations,method);logical.update(case_id=case,row=row,density=density,repeat=repeat);add('R-admission',logical,measured)
                order=['cold','reoptimized'];order=order[repeat%2:]+order[:repeat%2]
                for method in order:
                    logical,measured=scip_stream(row,observations,method);logical.update(case_id=case,row=row,density=density,repeat=repeat);add('R114-scip',logical,measured)
        logical,measured=cache_trial(row);logical.update(case_id=case,row=row);add('R119-120',logical,measured)
    if SCIP.exists():
        for case in ['heldout-n18-0','heldout-factor','crossing']:
            row=rows[case]
            for t in ([0,4,8] if case!='crossing' else [Fraction(1499,1000),Fraction(3,2),Fraction(1501,1000)]):
                logical,measured=exact_point(row,t);add('R112-native',logical,measured)
    write('Results.json',results);write('Execution.json',dict(status='complete',records=len(results),wall=time.perf_counter()-start,counts={k:sum(x['kind']==k for x in results) for k in sorted({x['kind'] for x in results})}))
    print(json.dumps(json.loads((ROOT/'Execution.json').read_text())),flush=True)

if __name__=='__main__':run()
