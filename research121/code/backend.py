"""Matched proof producers; fact identities separate from all measurements."""
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import re
import subprocess
import native as N

ROOT=Path(__file__).resolve().parents[1]
SDK=json.loads((ROOT/'SDK.json').read_text())
CP=ROOT/'external/cp2024/knapsack'


def epoch(route):
    return N.sha(N.encode(dict(route=route,sdk=SDK['identity'],adapter=N.sha((ROOT/'code/pb_parent.py').read_bytes()))))


class Session:
    def __init__(self,mode='process'):
        self.mode=mode;self.process=None;self.reported=0.0
        if mode=='fork':
            self.process=subprocess.Popen([SDK['pb_python'],str(ROOT/'code/pb_parent.py'),SDK['pb_source']],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
            assert self.process.stdout.readline().strip()=='READY'

    def check(self,formula,proof):
        if self.process is None:
            env=dict(os.environ,PYTHONPATH=SDK['pb_source'],PYTHONDONTWRITEBYTECODE='1')
            p=subprocess.run([SDK['pb_python'],'-m','veripb',str(formula),str(proof)],env=env,capture_output=True,text=True,timeout=30)
            return p.returncode==0 and 'Verification succeeded' in p.stdout and 'Verification failed' not in p.stdout,0.0
        self.process.stdin.write(json.dumps(dict(formula=str(formula),proof=str(proof)))+'\n');self.process.stdin.flush()
        answer=json.loads(self.process.stdout.readline());self.reported+=answer['cpu']
        return answer['code']==0,answer['cpu']

    def close(self):
        if self.process is not None:
            self.process.stdin.close();self.process.wait(timeout=30);assert self.process.returncode==0


def expansion(text,row,q):
    line=next(l for l in text.splitlines() if l.startswith('soli '))
    mask=sum(1<<int(x[1:]) for x in line.split()[1:] if re.fullmatch(r'x\d+',x))
    names=set(re.findall(r'\b(?:[wp]\d+_-?\d+|c\d+_-?\d+_-?\d+)\b',text));assignment=[]
    for name in sorted(names):
        if name[0] in 'wp':
            layer,threshold=map(int,name[1:].split('_'));values=row['weights'] if name[0]=='w' else q
            value=sum(values[j] for j in range(layer) if mask>>j&1)
            truth=value>=threshold if name[0]=='w' else value<=threshold
        else:
            layer,w,p=map(int,name[1:].split('_'))
            truth=sum(row['weights'][j] for j in range(layer) if mask>>j&1)>=w and sum(q[j] for j in range(layer) if mask>>j&1)<=p
        assignment.append(name if truth else '~'+name)
    return text.replace(line,line+' '+' '.join(assignment)),mask


def produce(row,t,route='native',session=None):
    t=Q(t);model=N.scope(row);q=N.scaled(row,t)
    if route=='native' or route=='native-alt':
        checker=N.NATIVE_CHECKER if route=='native' else N.WRAPPER
        fact,cost=N.produce(row,t,epoch(route),checker)
        d=fact.record();d.update(producer='native',proof=d.pop('path'),bytes=cost['bytes'])
        return d,cost['phases']
    if route=='scip-exact':return exact(row,t)
    assert route.startswith('cp-') and 0<row['n']<=16 and max(map(abs,q),default=0)<=1000000
    assert session is not None
    folder=ROOT/'evidence/cp'/N.sha(N.encode([model,[t.numerator,t.denominator]]));folder.mkdir(parents=True,exist_ok=True)
    phases={};start=N.clock();inp=folder/'input.txt'
    inp.write_text(f'{row["n"]} {row["capacity"]}\n'+''.join(f'{w} {p}\n' for w,p in zip(row['weights'],q)))
    phases['cp_input_encoding_io']=N.elapsed(start)['cpu'];start=N.clock()
    p=subprocess.run([str(CP),str(inp)],cwd=folder,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr
    phases['cp_solve_and_proof_including_child']=N.elapsed(start)['cpu'];start=N.clock()
    proof=folder/'knapsack.veripb';formula=folder/'knapsack.opb';raw=proof.read_text();(folder/'producer.veripb').write_text(raw)
    text,mask=expansion(raw,row,q);proof.write_text(text);assert proof.stat().st_size<=8388608
    formula_sha=N.sha(formula.read_bytes());proof_sha=N.sha(proof.read_bytes())
    phases['cp_solution_expansion_hash_io']=N.elapsed(start)['cpu'];start=N.clock()
    accepted,child=session.check(formula,proof);assert accepted
    phases['external_checker_requests']=N.elapsed(start)['cpu']+child;start=N.clock()
    bounds=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);assert bounds and bounds[1]==bounds[2]
    target=-int(bounds[1]);assert N.value(row['weights'],mask)<=row['capacity'] and N.value(q,mask)==target
    expected='min:'+''.join(f' {-p} x{j}' for j,p in enumerate(q))+' ;\n'+''.join(f'-{w} x{j} ' for j,w in enumerate(row['weights']))+f'>= -{row["capacity"]} ;\n'
    assert formula.read_text()==expected
    fact=dict(model=model,epoch=epoch(route),time=[t.numerator,t.denominator],packing=mask,objective=target,producer='cp',
        proof=str(proof.relative_to(ROOT)),proof_sha256=proof_sha,formula=str(formula.relative_to(ROOT)),formula_sha256=formula_sha,
        raw_proof=str((folder/'producer.veripb').relative_to(ROOT)),raw_sha256=N.sha(raw.encode()),bytes=proof.stat().st_size+formula.stat().st_size)
    phases['cp_model_primal_admission']=N.elapsed(start)['cpu'];return fact,phases


def exact(row,t):
    q=N.scaled(row,t);folder=ROOT/'evidence/scip'/N.sha(N.encode([N.scope(row),[t.numerator,t.denominator]]));folder.mkdir(parents=True,exist_ok=True)
    phases={};start=N.clock();lp=folder/'problem.lp';settings=folder/'settings.set';proof=folder/'raw.vipr'
    expression=' '.join(('+' if p>=0 else '-')+f' {abs(p)} x{j}' for j,p in enumerate(q))
    lp.write_text('Maximize\n objective: '+expression+'\nSubject To\n capacity: '+' + '.join(f'{w} x{j}' for j,w in enumerate(row['weights']))+f' <= {row["capacity"]}\nBinary\n '+' '.join(f'x{j}' for j in range(row['n']))+'\nEnd\n')
    settings.write_text('exact/enable = TRUE\ncertificate/filename = "'+str(proof)+'"\npresolving/maxrounds = 0\npresolving/maxrestarts = 0\nseparating/maxrounds = 0\nseparating/maxroundsroot = 0\nlimits/time = 20\nrandomization/randomseedshift = 0\n')
    phases['scip_encoding_io']=N.elapsed(start)['cpu'];start=N.clock()
    p=subprocess.run([SDK['exact_scip'],'-s',str(settings),'-f',str(lp)],capture_output=True,text=True,timeout=20)
    assert p.returncode==0 and '[optimal solution found]' in p.stdout and 'solving problem in exact solving mode' in p.stdout
    phases['scip_exact_solve_and_proof_child']=N.elapsed(start)['cpu'];start=N.clock();(folder/'solver.log').write_text(p.stdout+p.stderr)
    raw_sha=N.sha(proof.read_bytes());raw_path=str(proof.relative_to(ROOT));text=proof.read_text();completion=' weak ' in text or ' incomplete' in text
    phases['scip_log_hash_io']=N.elapsed(start)['cpu']
    if completion:
        out=folder/'complete.vipr';start=N.clock()
        p=subprocess.run([SDK['completion'],'--verbosity=0','--threads=1','--soplex=on','--outfile='+str(out),str(proof)],capture_output=True,text=True,timeout=20)
        assert p.returncode==0;proof=out;phases['scip_completion_including_child']=N.elapsed(start)['cpu']
    start=N.clock();assert N.verify_file(proof);phases['external_checker_requests']=N.elapsed(start)['cpu'];start=N.clock()
    assert proof.stat().st_size<=1048576
    tokens=proof.read_text().split();vi=tokens.index('VAR');n=int(tokens[vi+1]);names=tokens[vi+2:vi+2+n];si=tokens.index('SOL');assert tokens[si+1]=='1';k=int(tokens[si+3]);mask=0
    for i in range(k):
        j=int(tokens[si+4+2*i]);amount=Q(tokens[si+5+2*i]);assert amount in [0,1]
        if amount:mask|=1<<int(names[j].removeprefix('t_').removeprefix('x'))
    fact=dict(model=N.scope(row),epoch=epoch('scip-exact'),time=[t.numerator,t.denominator],packing=mask,objective=N.value(q,mask),producer='scip',proof=str(proof.relative_to(ROOT)),proof_sha256=N.sha(proof.read_bytes()),raw_proof=raw_path,raw_sha256=raw_sha,bytes=proof.stat().st_size,completion=completion)
    phases['scip_primal_admission_hash_io']=N.elapsed(start)['cpu'];return fact,phases


def refresh(row,fact,session=None):
    if N.scope(row)!=fact['model'] or N.sha((ROOT/fact['proof']).read_bytes())!=fact['proof_sha256']:return False
    if fact['producer']=='cp':
        if N.sha((ROOT/fact['formula']).read_bytes())!=fact['formula_sha256']:return False
        return session.check(ROOT/fact['formula'],ROOT/fact['proof'])[0]
    return N.verify_file(ROOT/fact['proof'])
