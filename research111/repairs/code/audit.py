"""Independent original-model enumeration, certificate binding and cache-trace audit.

Imports no campaign, cache, adapter, native producer, or SCIP Python API.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
CHECKER=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
ORACLES={}; COUNTS={'answers':0,'proof_bindings':0,'valid_external':0,'false_external_rejected':0}


def optimum(row,t):
    t=Fraction(t);key=json.dumps([row['weights'],row['capacity'],row['profits'],row['slopes'],str(t)])
    if key not in ORACLES:
        q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
        weights=[0]*(1<<row['n']);profits=[0]*(1<<row['n']);best=0
        for mask in range(1,1<<row['n']):
            bit=mask&-mask;j=bit.bit_length()-1;old=mask^bit
            weights[mask]=weights[old]+row['weights'][j];profits[mask]=profits[old]+q[j]
            if weights[mask]<=row['capacity']:best=max(best,profits[mask])
        ORACLES[key]=best
    return ORACLES[key]


def answer(row,t,mask,objective):
    t=Fraction(t);assert type(mask)==int and 0<=mask<(1<<row['n'])
    assert sum(w for j,w in enumerate(row['weights']) if mask>>j&1)<=row['capacity']
    exact=sum((t.denominator*p+t.numerator*v) for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])) if mask>>j&1)
    assert exact==objective==optimum(row,t);COUNTS['answers']+=1


def header_binding(path,row,t):
    """Check the original feasible set and positive objective normalization exactly."""
    text=path.read_text().split();pos=0
    def take():
        nonlocal pos
        result=text[pos];pos+=1;return result
    def expect(token):assert take()==token
    def vector():
        k=int(take());out={}
        for _ in range(k):
            j=int(take());v=Fraction(take());out[j]=out.get(j,Fraction(0))+v
        return {j:v for j,v in out.items() if v}
    expect('VER');assert take() in ['1.0','1.1'];expect('VAR');n=int(take());assert n==row['n'];names=[take() for _ in range(n)]
    # Native adapter uses x0 labels; native SCIP uses t_x0.
    def original(name):
        name=name.removeprefix('t_').removeprefix('x');return int(name)
    mapping={j:original(name) for j,name in enumerate(names)}
    assert set(mapping.values())==set(range(n))
    expect('INT');assert int(take())==n;assert set(int(take()) for _ in range(n))==set(range(n))
    expect('OBJ');sense=take();assert sense in ['max','min'];coef=vector();t=Fraction(t)
    q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
    sign=1 if sense=='max' else -1;ratios=[]
    for j in range(n):
        v=coef.get(j,0);wanted=sign*q[mapping[j]]
        if wanted:assert v!=0;ratios.append(Fraction(wanted,v))
        else:assert v==0
    scale=ratios[0] if ratios else Fraction(1)
    assert scale>0 and all(x==scale for x in ratios)
    expect('CON');m=int(take());take();assert m==2*n+1
    expected=[]
    for j in range(n):expected.extend([('G',Fraction(0),((j,Fraction(1)),)),('L',Fraction(1),((j,Fraction(1)),))])
    expected.append(('L',Fraction(row['capacity']),tuple((j,Fraction(row['weights'][j])) for j in range(n))))
    observed=[]
    for _ in range(m):
        take();relation=take();rhs=Fraction(take());v=vector();v={mapping[j]:x for j,x in v.items()}
        observed.append((relation,rhs,tuple(sorted(v.items()))))
    assert sorted(observed)==sorted(expected)
    expect('RTP');expect('range');lo=Fraction(take());hi=Fraction(take());assert lo==hi
    assert (lo*scale*sign)==optimum(row,t)
    COUNTS['proof_bindings']+=1
    return dict(objective_scale=[scale.numerator,scale.denominator],sense=sense)


def run():
    start=time.perf_counter();results=json.loads((ROOT/'Results.json').read_text());proofs={};events_checked=0;normalizations={}
    for item in results:
        kind=item['kind'];data=item['logical'];measurement=item['measurements']
        for factrow in data.get('facts',[]):
            row=factrow['row'];fact=factrow['fact'];t=Fraction(*fact['time']);answer(row,t,fact['packing'],fact['objective'])
            expected_model=hashlib.sha256(json.dumps({k:row[k] for k in ['n','weights','capacity','profits','slopes']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert fact['model']==expected_model
            p=ROOT/fact['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==fact['proof_sha256'];header_binding(p,row,t);proofs[fact['proof_sha256']]=p
        if kind in ['R-admission','R114-scip']:
            row=data['row']
            for output in data['outputs']:answer(row,Fraction(*output['time']),output['packing'],output['objective'])
            if kind=='R-admission' and data['method']!='points' and data['failed_probes']==0:
                endpoints=data['facts'][:2];assert endpoints[0]['fact']['packing']==endpoints[1]['fact']['packing'];assert endpoints[0]['fact']['time']==[0,1] and endpoints[1]['fact']['time']==[row['end'],1]
            if kind=='R114-scip':
                assert measurement['total']['cpu']>=measurement['phase_sum']-1e-5
                assert abs(measurement['phase_sum']+measurement['residual_cpu']-measurement['total']['cpu'])<1e-9
                assert 'native_exact_solve_and_witness' in measurement['phases']
        if kind=='R113':
            assert len(data['requests'])==len(data['decisions'])==20
            for request,decision in zip(data['requests'],data['decisions']):
                p=subprocess.run([str(CHECKER),str(ROOT/request['path'])],capture_output=True,text=True,timeout=10)
                accepted=p.returncode==0 and 'Successfully verified optimal value range' in p.stdout
                assert accepted==decision==request['expected'];events_checked+=1
            if data['method']=='fork-resident':assert measurement['total']['child_cpu']+0.001>=measurement['fork_child_cpu_reported']
        if kind=='R119-120':
            for event in data['events']:
                events_checked+=1
                if event['kind']=='point':
                    assert event['entries']<=2;answer(data['row'],event['time'],event['packing'],event['objective'])
                if event['kind']=='context-change':
                    assert event['old_snapshot_miss']
                    assert event['rejected']==(event['change'] in ['domain','nonlinear'])
                    if event['new_fact'] is not None:
                        f=event['new_fact'];answer(event['changed_model'],Fraction(*f['time']),f['packing'],f['objective'])
                        assert f['epoch']==event['epoch']
                        assert f['checker_sha256']==event['epoch']
                if event['kind']=='external-edit':assert event['immutable_lookup'] is not None and event['explicit_refresh_accepted']==False
            assert measurement['cache_bytes_after_clear']<=measurement['cache_bytes_before_clear']
            assert measurement['reachable_cache_bytes']>0 and measurement['resident_process_tree']['samples']>0
            assert measurement['resident_process_tree']['max_observed_processes']>=2
        if kind=='R112-native':
            if data['status']=='verified_native_scip':
                p=ROOT/data['proof'];assert hashlib.sha256(p.read_bytes()).hexdigest()==data['sha256']
                answer(data['row'],Fraction(*data['time']),data['packing'],data['objective']);normalizations[data['proof']]=header_binding(p,data['row'],Fraction(*data['time']));proofs[data['sha256']]=p
                assert data['presolve_rounds']==data['separation_rounds']==0
            else:assert data['status']=='certificate_not_verified'
    for f in json.loads((ROOT/'Checker-fixtures.json').read_text()):
        fact=f['fact'];p=ROOT/fact['path'];answer(f['row'],Fraction(*fact['time']),fact['packing'],fact['objective']);header_binding(p,f['row'],Fraction(*fact['time']));proofs[fact['proof_sha256']]=p
    controls=ROOT/'evidence/audit-false';controls.mkdir(parents=True,exist_ok=True)
    for digest,p in proofs.items():
        checked=subprocess.run([str(CHECKER),str(p)],capture_output=True,text=True,timeout=10);assert checked.returncode==0;COUNTS['valid_external']+=1
        lines=p.read_text().splitlines();last=lines[-1].split();relation=last[1];assert relation in ['G','L'];rhs=Fraction(last[2])+(1 if relation=='G' else -1);last[2]=str(rhs);lines[-1]=' '.join(last)
        bad=controls/(digest+'.vipr');bad.write_text('\n'.join(lines)+'\n');checked=subprocess.run([str(CHECKER),str(bad)],capture_output=True,text=True,timeout=10);assert checked.returncode!=0;COUNTS['false_external_rejected']+=1
    report=dict(passed=True,records=len(results),counts=COUNTS,cache_and_checker_events_checked=events_checked,distinct_oracle_queries=len(ORACLES),native_objective_normalizations=normalizations,wall=time.perf_counter()-start)
    (ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':run()
