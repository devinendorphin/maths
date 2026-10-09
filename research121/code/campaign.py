from fractions import Fraction as Q
import collections
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time
import backend as B
import native as N
from routes import choose,envelope,pair,stream
from controls import fault_trial,invalidation

ROOT=Path(__file__).resolve().parents[1]
ROWS=json.loads((ROOT/'Inputs.json').read_text())
TRAIN=[r for r in ROWS if r['split']=='training'];EVAL=[r for r in ROWS if r['split']=='heldout']
STREAMS=dict(sparse=[Q(0),Q(6)],dense=[Q(i,2) for i in range(13)],repeated=[Q(i) for i in [0,2,0,2,0,2,0,2,0,2,0,2,0]])


def save(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')


def verify():
    for name,digest in json.loads((ROOT/'Freeze.json').read_text())['files'].items():assert N.sha((ROOT/name).read_bytes())==digest,name
    for name,digest in B.SDK['files'].items():assert N.sha(Path(name).read_bytes())==digest,name


def record(stage,logical,measurement,repeat=0):
    return dict(stage=stage,repeat=repeat,logical=logical,measurements=measurement)


def train():
    verify();records=[];start=time.monotonic();groups=collections.defaultdict(list)
    for case,row in enumerate(TRAIN):
        for bucket,obs in STREAMS.items():
            for repeat in range(3):
                methods=['points','snapshot','window2','lru4'];rotation=(case+repeat)%4;methods=methods[rotation:]+methods[:rotation]
                for method in methods:
                    d,m=stream(row,obs,method);d.update(bucket=bucket,training=True)
                    records.append(record(126,d,m,repeat));groups[(bucket,method)].append(m['total']['cpu'])
    choices={b:min(['points','snapshot','window2','lru4'],key=lambda method:(statistics.median(groups[(b,method)]),method)) for b in STREAMS}
    policy=dict(choices=choices,factor_override=True,fit='lowest pooled median across training models and repeats only',models=[r['case_id'] for r in TRAIN])
    save('Training.json',records);save('Policy.json',policy)
    save('Policy-freeze.json',dict(policy_sha256=N.sha((ROOT/'Policy.json').read_bytes()),training_sha256=N.sha((ROOT/'Training.json').read_bytes()),source_freeze_sha256=N.sha((ROOT/'Freeze.json').read_bytes()),heldout_started=False))
    save('Training-execution.json',dict(records=len(records),wall=time.monotonic()-start,total_training_cpu=sum(r['measurements']['total']['cpu'] for r in records)))
    print('Frozen trained policy:',json.dumps(policy),flush=True)


def checker_trial(first,second,method):
    folder=ROOT/'evidence/checker-controls';folder.mkdir(parents=True,exist_ok=True)
    source=(ROOT/first['proof']).read_text();m=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',source);v=int(m[1])-1
    false=folder/'false.veripb';false.write_text(source[:m.start()]+f'conclusion BOUNDS {v} {v}'+source[m.end():])
    malformed=folder/'malformed.veripb';malformed.write_text('INVALID\n')
    request=[(first['formula'],first['proof'],True),(first['formula'],str(false.relative_to(ROOT)),False),(second['formula'],second['proof'],True),(first['formula'],str(malformed.relative_to(ROOT)),False),(first['formula'],first['proof'],True)]*4
    begin=N.clock();session=B.Session('fork' if method=='fork' else 'process');decisions=[]
    for formula,proof,expected in request:
        accepted,_=session.check(ROOT/formula,ROOT/proof);assert accepted==expected;decisions.append(accepted)
    session.close();return dict(method=method,requests=[dict(formula=f,proof=p,expected=e) for f,p,e in request],decisions=decisions,pristine_parent=method=='fork'),dict(total=N.elapsed(begin),fork_child_cpu_reported=session.reported)


def rational_trial(row,route,method="points"):
    start=N.clock();blocks=envelope(row);crossings=sorted({Q(*b['lo']) for b in blocks if Q(*b['lo'])>0});assert len(crossings)<=10
    obs=sorted({Q(0),Q(row['end'])}|{t+delta for t in crossings for delta in [-Q(1,1000),Q(0),Q(1,1000)] if 0<=t+delta<=row['end']})
    actual=route;unsupported=[]
    if route.startswith('cp-') and any(max(map(abs,N.scaled(row,t)))>1000000 for t in obs):
        actual='native';unsupported=['CP coefficient cap exceeded; explicitly substituted native point control']
    d,m=stream(row,obs,method,actual)
    for output in d['outputs']:
        t=Q(*output['time']);block=next(b for b in blocks if Q(*b['lo'])<=t<=Q(*b['hi']))
        assert N.value(N.scaled(row,t),block['packing'])==output['objective']
    d.update(requested_route=route,unsupported=unsupported,crossings=[pair(t) for t in crossings],discovered_blocks=blocks,outside_queries=[[-1,1000],[6001,1000]],outside_accepted=[False,False])
    # Outside controls exercise the actual interval predicate before any answer.
    assert all(not any(Q(*b['lo'])<=t<=Q(*b['hi']) for b in blocks) for t in [Q(-1,1000),Q(6001,1000)])
    m['total']=N.elapsed(start);m['residual_cpu']=m['total']['cpu']-m['phase_sum'];return d,m


def run():
    verify();policy=json.loads((ROOT/'Policy.json').read_text());seal=json.loads((ROOT/'Policy-freeze.json').read_text());assert N.sha((ROOT/'Policy.json').read_bytes())==seal['policy_sha256']
    results=[];begin=time.monotonic()
    def add(stage,d,m,repeat=0):
        assert time.monotonic()-begin<900
        if not results or results[-1]['stage']!=stage:
            assert sum(p.stat().st_size for p in (ROOT/'evidence').rglob('*') if p.is_file())<=268435456
        results.append(record(stage,d,m,repeat))
        save('Results-progress.json',results)
    s=B.Session();a,_=B.produce(EVAL[0],0,'cp-process',s);b,_=B.produce(EVAL[-1],3,'cp-process',s);s.close()
    save('Checker-fixtures.json',[dict(row=EVAL[0],fact=a),dict(row=EVAL[-1],fact=b)])
    for repeat in range(3):
        methods=['process','fork'];methods=methods[repeat%2:]+methods[:repeat%2]
        for method in methods:
            d,m=checker_trial(a,b,method);add(121,d,m,repeat)
    for case,row in enumerate(EVAL):
        for repeat in range(3):
            methods=['native','cp-process','cp-fork','scip-exact'];rot=(case+repeat)%4;methods=methods[rot:]+methods[:rot]
            for route in methods:
                d,m=stream(row,[0,3,6],'points',route);add(122,d,m,repeat)
    for case,row in enumerate([EVAL[2],EVAL[3]]):
        for bucket in ['sparse','dense']:
            for repeat in range(3):
                methods=[('snapshot','native'),('snapshot','cp-fork'),('factor','cp-fork')];rot=(case+repeat)%3;methods=methods[rot:]+methods[:rot]
                for method,route in methods:
                    d,m=stream(row,STREAMS[bucket],method,route);d['bucket']=bucket;add(123,d,m,repeat)
    for case,row in enumerate([EVAL[0],EVAL[2]]):
        for count in [1,3,7,13]:
            obs=[Q(0)] if count==1 else [Q(6*i,count-1) for i in range(count)]
            for repeat in range(3):
                methods=['points','guarded','snapshot'];rot=(case+repeat)%3;methods=methods[rot:]+methods[:rot]
                for method in methods:
                    d,m=stream(row,obs,method);d['query_count']=count;add(124,d,m,repeat)
    for row in [EVAL[0],EVAL[2],ROWS[-1]]:
        for route,method in [('native','points'),('cp-process','points'),('native','snapshot')]:
            d,m=rational_trial(row,route,method);add(125,d,m)
    for case,row in enumerate(EVAL):
        for bucket,obs in STREAMS.items():
            for repeat in range(3):
                methods=['policy','points','snapshot','window2','lru4','factor'];rot=(case+repeat)%6;methods=methods[rot:]+methods[:rot]
                for method in methods:
                    chosen=choose(row,obs,policy) if method=='policy' else method;d,m=stream(row,obs,chosen)
                    d.update(bucket=bucket,requested_method=method,selected_method=chosen,training=False);add(126,d,m,repeat)
    for row in [EVAL[0],EVAL[2]]:
        for route in ['native','cp-process']:
            for budget in [4096,131072]:
                spec=ROOT/'evidence/memory-spec.json';spec.write_text(json.dumps(dict(row=row,route=route,budget=budget)))
                p=subprocess.run([sys.executable,str(ROOT/'code/memory_worker.py'),str(spec)],capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stderr
                result=json.loads(p.stdout);add(127,result['logical'],result['measurements'])
            d,m=invalidation(row,route);add(128,d,m)
            d,m=fault_trial(row,route);add(129,d,m)
    for case,row in enumerate([EVAL[0],EVAL[2]]):
        for bucket in ['sparse','dense']:
            obs=STREAMS[bucket]
            for repeat in range(3):
                methods=['points','policy-correct','policy-wrong','snapshot-cap'];rot=(case+repeat)%4;methods=methods[rot:]+methods[:rot]
                for method in methods:
                    forecast=len(obs) if method!='policy-wrong' else (13 if bucket=='sparse' else 2)
                    selected=choose(row,obs,policy,forecast) if method.startswith('policy') else ('snapshot' if method=='snapshot-cap' else 'points')
                    d,m=stream(row,obs,selected,certificate_cap=4 if method=='snapshot-cap' else None)
                    d.update(bucket=bucket,requested_method=method,selected_method=selected,forecast_count=forecast);add(130,d,m,repeat)
    assert sum(p.stat().st_size for p in (ROOT/'evidence').rglob('*') if p.is_file())<=268435456
    save('Results.json',results);counts=collections.Counter(r['stage'] for r in results)
    save('Execution.json',dict(status='complete',records=len(results),counts=counts,wall=time.monotonic()-begin,training_records=72))
    print('Campaign completed:',json.dumps(counts),flush=True)


if __name__=='__main__':train() if sys.argv[1]=='train' else run()
