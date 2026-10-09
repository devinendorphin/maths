"""Independent original-model enumeration, certificate binding and cache-trace audit.

Imports no campaign, cache, adapter, native producer, or SCIP Python API.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import time
import collections
import os
import re
import statistics

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


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def encoded(data):return json.dumps(data,sort_keys=True,separators=(',',':')).encode()
def model(row):return hashlib.sha256(encoded({k:row[k] for k in ['n','weights','capacity','profits','slopes']})).hexdigest()


def check_pb(formula,proof):
    sdk=json.loads((ROOT/'SDK.json').read_text())
    p=subprocess.run([sdk['pb_python'],'-m','veripb',str(formula),str(proof)],env=dict(os.environ,PYTHONPATH=sdk['pb_source'],PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=30)
    return p.returncode==0 and 'Verification succeeded' in p.stdout and 'Verification failed' not in p.stdout


def check_vipr(proof):
    p=subprocess.run([str(CHECKER),str(proof)],capture_output=True,text=True,timeout=30)
    return p.returncode==0 and 'Successfully verified optimal value range' in p.stdout


def run():
    start=time.perf_counter();proofs={};events=0
    sdk=json.loads((ROOT/'SDK.json').read_text())
    for name,sha in json.loads((ROOT/'Freeze.json').read_text())['files'].items():assert digest(ROOT/name)==sha,name
    for name,sha in sdk['files'].items():assert digest(Path(name))==sha,name
    for name,sha in json.loads((ROOT/'Audit-amendment.json').read_text())['files'].items():assert digest(ROOT/name)==sha,name
    seal=json.loads((ROOT/'Policy-freeze.json').read_text())
    assert digest(ROOT/'Policy.json')==seal['policy_sha256'] and digest(ROOT/'Training.json')==seal['training_sha256']
    assert digest(ROOT/'Freeze.json')==seal['source_freeze_sha256'] and seal['heldout_started'] is False
    training=json.loads((ROOT/'Training.json').read_text());results=json.loads((ROOT/'Results.json').read_text());policy=json.loads((ROOT/'Policy.json').read_text())
    assert len(training)==72 and len(results)==451
    counts=collections.Counter(r['stage'] for r in results)
    assert counts=={121:6,122:48,123:36,124:72,125:9,126:216,127:8,128:4,129:4,130:48},counts
    groups=collections.defaultdict(list)
    for item in training:
        d=item['logical'];assert d['training'] and d['row']['split']=='training';groups[d['bucket'],d['method']].append(item['measurements']['total']['cpu'])
    fitted={b:min(['points','snapshot','window2','lru4'],key=lambda method:(statistics.median(groups[b,method]),method)) for b in ['sparse','dense','repeated']}
    assert policy['choices']==fitted and set(policy['models'])=={'train8','train10'}
    def fact(row,f):
        t=Fraction(*f['time']);answer(row,t,f['packing'],f['objective']);assert f['model']==model(row)
        p=ROOT/f['proof'];assert digest(p)==f['proof_sha256']
        if f['producer']=='cp':
            formula=ROOT/f['formula'];assert digest(formula)==f['formula_sha256']
            q=[t.denominator*a+t.numerator*b for a,b in zip(row['profits'],row['slopes'])]
            expected='min:'+''.join(f' {-a} x{j}' for j,a in enumerate(q))+' ;\n'+''.join(f'-{w} x{j} ' for j,w in enumerate(row['weights']))+f'>= -{row["capacity"]} ;\n'
            assert formula.read_text()==expected
            conclusion=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',p.read_text());assert conclusion and int(conclusion[1])==int(conclusion[2])==-f['objective']
            assert digest(ROOT/f['raw_proof'])==f['raw_sha256']
            soli=next(l for l in p.read_text().splitlines() if l.startswith('soli '))
            assert sum(1<<int(x[1:]) for x in soli.split()[1:] if re.fullmatch(r'x\d+',x))==f['packing']
            proofs[('cp',f['formula_sha256'],f['proof_sha256'])]=(p,formula);COUNTS['proof_bindings']+=1
        else:
            header_binding(p,row,t);proofs[(f['producer'],f['proof_sha256'])]=(p,None)
            if f['producer']=='scip':assert digest(ROOT/f['raw_proof'])==f['raw_sha256']
        return f
    def selected(d,forecast=None):
        row=d['row'];alpha=None;factor=True
        for a,b in zip(row['profits'],row['slopes']):
            if a:
                v=Fraction(b,a)
                if alpha is not None and alpha!=v:factor=False
                alpha=v
            elif b:factor=False
        alpha=alpha or Fraction(0)
        if factor and min(Fraction(1),1+alpha*row['end'])>0:return 'factor'
        obs=[Fraction(*t) for t in d['observations']];count=len(obs) if forecast is None else forecast
        bucket='repeated' if forecast is None and len(set(obs))<=4 and count>4 else ('dense' if count>4 else 'sparse')
        return policy['choices'][bucket]
    memory=[]
    for item in training+results:
        d=item['logical'];m=item['measurements'];stage=item['stage']
        if 'phase_sum' in m:
            assert abs(m['phase_sum']+m['residual_cpu']-m['total']['cpu'])<1e-8
            assert m['residual_cpu']>=-0.002,(stage,m)
        assert m['total']['cpu']>=0 and abs(m['total']['cpu']-m['total']['parent_cpu']-m['total']['child_cpu'])<1e-8
        for f in d.get('facts',[]):fact(f['row'],f['fact'])
        for o in d.get('outputs',[]):answer(d['row'],Fraction(*o['time']),o['packing'],o['objective'])
        for b in d.get('blocks',[]):
            row=d['row'];lo,hi=Fraction(*b['lo']),Fraction(*b['hi']);assert 0<=lo<=hi<=row['end']
            for t in [lo,hi]:answer(row,t,b['packing'],sum((t.denominator*p+t.numerator*v) for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])) if b['packing']>>j&1))
            if b['rule']=='endpoints':
                assert b['left']['time']==b['lo'] and b['right']['time']==b['hi']
                for f in [b['left'],b['right']]:fact(row,f)
            else:
                alpha=Fraction(*b['alpha']);assert all(Fraction(v)==alpha*p for p,v in zip(row['profits'],row['slopes'])) and min(1,1+alpha*hi)>0
                fact(row,b['basis'])
        if d.get('method')=='guarded':assert d['guarded_file_reads']==2*len(d['outputs'])
        if stage==121:
            assert len(d['requests'])==len(d['decisions'])==20
            for req,decision in zip(d['requests'],d['decisions']):
                assert check_pb(ROOT/req['formula'],ROOT/req['proof'])==decision==req['expected'];events+=1
            assert m['total']['child_cpu']+0.002>=m['fork_child_cpu_reported']
        if stage==125:
            assert d['outside_accepted']==[False,False]
            obs=set(map(lambda x:Fraction(*x),d['observations']))
            for crossing in d['crossings']:
                t=Fraction(*crossing)
                for delta in [-Fraction(1,1000),Fraction(0),Fraction(1,1000)]:
                    if 0<=t+delta<=d['row']['end']:assert t+delta in obs
            for b in d['discovered_blocks']:
                for t in [Fraction(*b['lo']),Fraction(*b['hi'])]:
                    answer(d['row'],t,b['packing'],sum((t.denominator*p+t.numerator*v) for j,(p,v) in enumerate(zip(d['row']['profits'],d['row']['slopes'])) if b['packing']>>j&1))
            if d['unsupported']:assert d['requested_route']=='cp-process' and d['route']=='native'
        if stage==126 and not d.get('training'):
            assert d['row']['split']=='heldout'
            if d['requested_method']=='policy':assert d['selected_method']==selected(d)
        if stage==127:
            cache=collections.OrderedDict();fresh=iter(d['facts']);evictions=0
            for e in d['events']:
                t=tuple(e['time']);hit=t in cache;assert e['hit']==hit
                if hit:f,size=cache.pop(t);cache[t]=(f,size)
                else:
                    f=next(fresh)['fact'];assert f['time']==e['time']
                    size=len(encoded(f))+(ROOT/f['proof']).stat().st_size+((ROOT/f['formula']).stat().st_size if f['producer']=='cp' else 0)
                    assert e['entry_payload_bytes']==size and e['admitted']==(size<=d['budget'])
                    if size<=d['budget']:
                        while sum(z[1] for z in cache.values())+size>d['budget']:cache.popitem(last=False);evictions+=1
                        cache[t]=(f,size)
                assert e['entries']==len(cache) and e['evictions']==evictions and e['retained_payload_bytes']==sum(z[1] for z in cache.values())<=d['budget'];events+=1
                answer(d['row'],Fraction(*e['time']),e['packing'],e['objective'])
            assert next(fresh,None) is None
            assert m['retained_payload_bytes']==sum(z[1] for z in cache.values()) and m['reachable_cache_bytes']>=m['reachable_after_clear']>0
            assert m['process_tree']['samples']>0 and m['process_tree']['observed_peak_tree_rss_kib']>0
            memory.append(dict(case=d['row']['case_id'],route=d['route'],budget=d['budget'],child_observed=m['process_tree']['max_positive_processes']>=2,measurement=m['process_tree']))
        if stage==128:
            assert {e['change'] for e in d['events']}=={'capacity','weight','objective','domain','nonlinear','dependency'}
            for e in d['events']:
                assert e['old_entries_evicted'] and e['old_retained_bytes']>0 and e['rejected']==(e['change'] in ['domain','nonlinear']);events+=1
                if not e['rejected']:
                    assert e['new_context']==[e['new_fact']['model'],e['new_fact']['epoch']] and e['old_context']!=e['new_context']
                    fact(e['changed_row'],e['new_fact'])
                else:assert e['new_fact'] is None
        if stage==129:
            for e in d['events']:
                assert e['immutable_captured_packing']==d['basis']['packing'] and e['explicit_refresh_accepted'] is False
                accepted=check_pb(ROOT/d['basis']['formula'],ROOT/e['copy_proof']) if d['basis']['producer']=='cp' else check_vipr(ROOT/e['copy_proof'])
                assert accepted==e['redeclared_hash_checker_accepted']==(e['corruption']=='appended-bytes');events+=1
                fact(d['row'],e['fallback'])
        if stage==130:
            if d['requested_method'].startswith('policy'):assert d['selected_method']==selected(d,d['forecast_count'])
            if d['preparation_capped']:assert not d['blocks'] and d['failed_probes']>=1 and d['certificate_cap']==4
    for f in json.loads((ROOT/'Checker-fixtures.json').read_text()):fact(f['row'],f['fact'])
    controls=ROOT/'evidence/audit-false';controls.mkdir(parents=True,exist_ok=True);replays=[]
    for identity,(p,formula) in proofs.items():
        assert check_pb(formula,p) if formula else check_vipr(p)
        COUNTS['valid_external']+=1;text=p.read_text()
        if formula:
            match=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);v=int(match[1])-1
            text=text[:match.start()]+f'conclusion BOUNDS {v} {v}'+text[match.end():]
        else:
            lines=text.splitlines();last=lines[-1].split();assert last[1] in ['G','L'];last[2]=str(Fraction(last[2])+(1 if last[1]=='G' else -1));lines[-1]=' '.join(last);text='\n'.join(lines)+'\n'
        bad=controls/(hashlib.sha256(encoded(identity)).hexdigest()+p.suffix);bad.write_text(text)
        assert not (check_pb(formula,bad) if formula else check_vipr(bad));COUNTS['false_external_rejected']+=1
        replays.append(dict(identity=identity,proof=str(p.relative_to(ROOT)),false_proof=str(bad.relative_to(ROOT)),accepted=True,false_rejected=True))
    report=dict(passed=True,training_records=len(training),heldout_and_control_records=len(results),distinct_base_models=7,counts=COUNTS,events_checked=events,distinct_oracle_queries=len(ORACLES),distinct_proof_counts=dict(collections.Counter(i[0] for i in proofs)),memory_observations=memory,wall=time.perf_counter()-start)
    (ROOT/'Proof-replay.json').write_text(json.dumps(replays,indent=2)+'\n');(ROOT/'Audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':run()

