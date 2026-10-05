"""Frozen experiments; standard library. Read Temporal-protocol.md."""
import argparse,collections,hashlib,inspect,json,os,platform,random,statistics,textwrap,time
from pathlib import Path
import flat_baseline as F
import proof_slack_experiment as P
MODES=P.MODES
CAP=3_000_000
class Limit(Exception):pass

def save(name,value):Path(name).write_text(json.dumps(value,indent=2))

def solvers(g=1,lattice=False):
    src=inspect.getsource(F.solve);out={}
    for m in MODES:
        code=src.replace(P.ORIGINAL,P.REPLACEMENTS[m]);ns=vars(F).copy();ns['G']=g
        if lattice:
            code=code.replace('num // cell.b <= best','(num // (cell.b*G))*G <= best')
            code=code.replace('upper = fixed_value + num // den','upper = ((fixed_value*den+num) // (den*G))*G')
        if m=='endpoint' and not lattice:out[m]=F.solve
        else:exec(compile(code,'<'+m+'>','exec'),ns);out[m]=ns['solve']
    return out

def diagnose(pop,cell,i,p,q,w,delta):
    pop['examined']+=1;bit=1<<i
    for key,x in [('price',cell.a),('den',cell.b),('num',cell.num),('bp',cell.b*p),('aw',cell.a*w),('d',cell.b*delta)]:
        pop['bit_'+key]=max(pop['bit_'+key],abs(x).bit_length())
    if cell.fixed&bit:
        pop['fixed']+=1;pop['nonzero_terms']+=int(delta!=0);return
    if not cell.free&bit:pop['excluded']+=1;return
    s=cell.b*p-cell.a*w;t=cell.b*q-cell.a*w
    key='active' if s>0 and t>0 else 'leaving' if s>0 else 'entering' if t>0 else 'inactive'
    pop[key]+=1;pop['free']+=1;pop['equality']+=int(s==0 or t==0)
    pop['nonzero_terms']+=int(max(0,s)!=max(0,t))
    pop['bit_s']=max(pop['bit_s'],abs(s).bit_length());pop['bit_t']=max(pop['bit_t'],abs(t).bit_length())

def diagnostic_solver(g,lattice):
    src=inspect.getsource(F.solve)
    src=src.replace('                num = cell.num','                num = cell.num\n                term_start = DIAG["nonzero_terms"]')
    src=src.replace('                    bit = 1 << i','                    bit = 1 << i\n                    diagnose(DIAG,cell,i,anchor[i],p[i],w[i],delta)')
    src=src.replace('                reuse = sharing and num == cell.num','''                DIAG['net_unchanged'] += int(num == cell.num)
                DIAG['net_cancellations'] += int(num == cell.num and DIAG['nonzero_terms']>term_start)
                DIAG['bit_updated_num'] = max(DIAG['bit_updated_num'],abs(num).bit_length())
                reuse = sharing and num == cell.num''')
    if lattice:src=src.replace('num // cell.b <= best','(num // (cell.b*G))*G <= best').replace('upper = fixed_value + num // den','upper = ((fixed_value*den+num) // (den*G))*G')
    ns=vars(F).copy();ns.update(G=g,DIAG=collections.Counter(),diagnose=diagnose)
    # Inspect sort and fractional-bound intermediates only in this untimed replay.
    for name in ('metered_order','metered_lp'):
        helper=inspect.getsource(getattr(F,name))
        if name=='metered_order':
            helper=helper.replace('            before=p[i]*w[left]>p[left]*w[i]',
                "            DIAG['bit_rank_product']=max(DIAG['bit_rank_product'],abs(p[i]*w[left]).bit_length(),abs(p[left]*w[i]).bit_length())\n            before=p[i]*w[left]>p[left]*w[i]")
        else:
            helper=helper.replace('            result=(profit*w[i]+p[i]*room,w[i],i,chosen,p[i],w[i])',
                "            DIAG['bit_fractional_lp_num']=max(DIAG['bit_fractional_lp_num'],abs(profit*w[i]+p[i]*room).bit_length())\n            result=(profit*w[i]+p[i]*room,w[i],i,chosen,p[i],w[i])")
        exec(compile(helper,'<untimed-'+name+'>','exec'),ns)
    exec(compile(src,'<untimed-diagnostics>','exec'),ns)
    return ns['solve'],ns['DIAG']

def drain(gen,budget=None,store=None):
    steps=0
    while True:
        try:next(gen);steps+=1
        except StopIteration as done:return done.value,steps+1
        if budget and steps%8192==0:
            if budget['steps']+steps>=CAP or budget['cpu']+time.process_time()-budget['c0']>5 or budget['wall']+time.perf_counter()-budget['w0']>10 or len(store.cells)>100000:
                budget['steps']+=steps;raise Limit('stream execution budget')

def check(w,p,c,best,chosen,proof,g,exhaustive=False):
    assert sum(w[i] for i in range(len(w)) if chosen>>i&1)<=c
    assert best==sum(p[i] for i in range(len(w)) if chosen>>i&1)==F.dp(w,p,c)
    F.ownership(proof.store,[proof]);fs=proof.fields()
    for fixed,free,residual,a,b,num in fs:
        assert fixed&free==0 and a>=0 and b>0
        assert residual==c-sum(w[i] for i in range(len(w)) if fixed>>i&1)
        calc=b*sum(p[i] for i in range(len(w)) if fixed>>i&1)+a*residual
        calc+=sum(max(0,b*p[i]-a*w[i]) for i in range(len(w)) if free>>i&1)
        assert calc==num and num//(b*g)*g<=best
    if exhaustive:
        for mask in range(1<<len(w)):
            if sum(w[i] for i in range(len(w)) if mask>>i&1)<=c:
                assert sum(mask&fixed==fixed and mask&~(fixed|free)==0 for fixed,free,*_ in fs)==1
    return fs

def run_stream(w,c,stream,fn,g=1,exhaustive=False,limited=True):
    phases=collections.defaultdict(lambda:[0.,0.]);budget=dict(cpu=0.,wall=0.,steps=0)
    c0,w0=time.process_time(),time.perf_counter();store=F.Store();stream=[list(p) for p in stream];chosen=0;old=None;anchor=None
    phases['prepare']=[time.process_time()-c0,time.perf_counter()-w0]
    budget['cpu'],budget['wall']=phases['prepare'];rows=[];digest=hashlib.sha256();status='complete';reason=None
    def phase(name,gen,guard=False):
        c0,w0=time.process_time(),time.perf_counter();budget.update(c0=c0,w0=w0)
        try:
            result,k=drain(gen,budget if guard and limited else None,store);budget['steps']+=k
            return result,k
        finally:
            cpu,wall=time.process_time()-c0,time.perf_counter()-w0
            phases[name][0]+=cpu;phases[name][1]+=wall;budget['cpu']+=cpu;budget['wall']+=wall
    for p in stream:
        previous=store.stats.copy();committed=False
        c0,w0=time.process_time(),time.perf_counter();arena=F.Arena(store);gen=fn(w,p,c,chosen,old,anchor,'flat_share',arena)
        phases['prepare'][0]+=time.process_time()-c0;phases['prepare'][1]+=time.perf_counter()-w0
        try:
            (best,newchosen,new),steps=phase('solve',gen,True)
            c0,w0=time.process_time(),time.perf_counter();gen.close();budget['steps']+=1;steps+=1
            phases['solve'][0]+=time.process_time()-c0;phases['solve'][1]+=time.perf_counter()-w0
            _,k=phase('cleanup',arena.cleanup(new));steps+=k
            if old:
                _,k=phase('retire',old.release());steps+=k
            old=new;chosen=newchosen;committed=True
            fs=check(w,p,c,best,chosen,old,g,exhaustive)
            assert all(a%g==0 and num%g==0 for _,_,_,a,_,num in fs)
            normalized=[(I,J,C,a//g,b,num//g) for I,J,C,a,b,num in fs]
            digest.update(repr((best//g,chosen,normalized)).encode())
            rows.append(dict(objective=best,packing=chosen,steps=steps,cover=len(fs),refreshes=arena.refreshes,splits=arena.splits,counters={k:store.stats[k]-previous[k] for k in previous if not k.startswith('peak')},max_price_bits=max((abs(f[3]).bit_length() for f in fs),default=0),max_num_bits=max((abs(f[5]).bit_length() for f in fs),default=0)))
            anchor=p
            if limited and (budget['steps']>=CAP or budget['cpu']>5 or budget['wall']>10):raise Limit('stream budget after committed query')
        except Limit as err:
            status='incomplete';reason=str(err)
            if not committed:
                c0,w0=time.process_time(),time.perf_counter();gen.close()
                phases['cancel_close'][0]+=time.process_time()-c0;phases['cancel_close'][1]+=time.perf_counter()-w0
                phase('cancel_cleanup',arena.cleanup())
            F.ownership(store,[] if old is None else [old]);break
    if old:phase('dispose',old.release())
    store.empty()
    return dict(status=status,reason=reason,queries=rows,digest=digest.hexdigest(),phases=dict(phases),cpu=sum(v[0] for v in phases.values()),wall=sum(v[1] for v in phases.values()),stats=store.stats,empty=True,steps=budget['steps'])

def semantic(run):return (run['status'],run['digest'],run['stats'],[(q['steps'],q['cover'],q['refreshes'],q['splits'],q['counters']) for q in run['queries']])

def workload(n,seed,family,regime,count):
    rng=random.Random(seed);w=[rng.randint(5,70) for _ in range(n)];c=sum(w)//3
    p=[rng.randint(10,150) for _ in w] if family=='uncorrelated' else [x+40+rng.randint(-3,3) for x in w];stream=[p]
    for t in range(1,count):
        q=p.copy();k={'sparse1':1,'dense':n,'alternating':n if t%2 else 1,'pulse5':n if t%5==0 else 1,'mixed':n if 7<=t<14 else 1,'signed_reset':1}[regime]
        if regime=='signed_reset' and t%3==0:q=[rng.randint(-50,150) for _ in w]
        else:
            for i in rng.sample(range(n),k):q[i]=max(1,q[i]+rng.choice((-1,1))*rng.randint(1,20))
        stream.append(q);p=q
    return w,c,stream

def kernel(mode):
    clause={'endpoint':'total += max(0,b*q-a*w)-max(0,b*p-a*w)','slack_max':'s=b*p-a*w\nd=b*delta\ntotal += max(0,s+d)-max(0,s)','slack_branch':'s=b*p-a*w\nd=b*delta\nt=s+d\nif s>0:\n    total += d if t>0 else -s\nelif t>0:\n    total += t'}[mode]
    body='for _ in range(sweeps):\n    for p,q,w,a,b,delta,fixed in rows:\n        if fixed:\n            total += b*delta\n        else:\n'+textwrap.indent(clause,'            ')
    src='def run(rows,sweeps):\n    total=0\n'+textwrap.indent(body,'    ')+'\n    return total\n';ns={};exec(compile(src,'<arithmetic-'+mode+'>','exec'),ns);return ns['run']
LABELS=[f'cross_{r}' for r in (0,.1,.5,1)]+['stable-active','inactive','entering','leaving','equality','signed-profit','fixed','cancellation']

def arithmetic_rows(bits,label,rng):
    M=1<<(bits-1);rows=[]
    if label.startswith('cross_'):
        n=int(float(label[6:])*2048);types=['entering' if i%2 else 'leaving' for i in range(n)]
        types+=['active' if i%2 else 'inactive' for i in range(2048-n)];rng.shuffle(types)
    else:types=[label]*2048
    for i,kind in enumerate(types):
        x,y=rng.randint(1,M//4),rng.randint(1,M//4);a=M;w=b=3;fixed=False
        if kind in ('active','stable-active'):p,q=M+x,M+y
        elif kind=='inactive':p,q=M-x,M-y
        elif kind=='entering':p,q=M-x,M+y
        elif kind=='leaving':p,q=M+x,M-y
        elif kind=='equality':p,q=(M,M+x) if i%2 else (M+x,M)
        elif kind=='signed-profit':p,q=-M-x,(-M-y if i%2 else M+y)
        elif kind=='fixed':p,q=M+x,-M-y;fixed=True
        elif kind=='cancellation':
            if i%2:p,q=rows[-1][1],rows[-1][0]
            else:p,q=M+x,M+y
        rows.append((p,q,w,a,b,q-p,fixed))
    return rows

def row_info(rows):
    pop=collections.Counter();sizes=collections.Counter();expected=0
    for p,q,w,a,b,delta,fixed in rows:
        s=b*p-a*w;t=b*q-a*w
        if fixed:kind='fixed';inc=b*delta
        else:
            kind='active' if s>0 and t>0 else 'leaving' if s>0 else 'entering' if t>0 else 'inactive'
            inc=(t if t>0 else 0)-(s if s>0 else 0)
        pop[kind]+=1;pop['equality']+=int(s==0 or t==0);pop['signed_profit']+=int(p<0 or q<0);expected+=inc
        for key,value in [('p',p),('q',q),('a',a),('b',b),('bp',b*p),('aw',a*w),('s',s),('t',t),('d',b*delta)]:sizes[key]=max(sizes[key],abs(value).bit_length())
    return dict(population=dict(pop),max_bits=dict(sizes),expected=expected)

def verify():
    result=dict(exhaustive_queries=0,cancellation_prefixes=0,completed_uncommitted=0,scalar_cases=0,normalized_matches=0)
    rng=random.Random(1012026);kernels={m:kernel(m) for m in MODES}
    for bits in (16,64,256,1024):
        for label in LABELS:
            rows=arithmetic_rows(bits,label,rng);info=row_info(rows)
            for fn in kernels.values():
                assert fn(rows,1)==info['expected']
                for row in rows:
                    p,q,w,a,b,delta,fixed=row
                    old=b*p-a*w;new=b*q-a*w
                    oracle=b*delta if fixed else (new if new>0 else 0)-(old if old>0 else 0)
                    assert fn([row],1)==oracle
            result['scalar_cases']+=len(rows)
    canonical={}
    for shift in (0,64,256,1024):
        g=1<<shift;fns=solvers(g,True)
        for trial in range(12):
            r=random.Random(20261001+trial);w=[r.randint(1,10) for _ in range(7)];c=0 if trial%4==0 else sum(w)//3
            p=[r.randint(-8,25) for _ in w];q=[r.randint(-8,25) for _ in w]
            stream=[[v*g for v in x] for x in (p,p,q,[0]*7,p)]
            for mode,fn in fns.items():
                run=run_stream(w,c,stream,fn,g,True,False);result['exhaustive_queries']+=5
                if trial in canonical:assert semantic(run)==canonical[trial];result['normalized_matches']+=1
                else:canonical[trial]=semantic(run)
        fixtures=[([6,10,5,2,9,7],13,[[9,25,17,23,16,30],[9,25,17,-7,16,30]]),([1,1],1,[[4,6],[5,5],[5,5]])]
        for w,c,ss in fixtures:
            sig=None
            for fn in fns.values():
                run=run_stream(w,c,[[v*g for v in p] for p in ss],fn,g,True,False);result['exhaustive_queries']+=len(ss)
                if sig is None:sig=semantic(run)
                else:assert semantic(run)==sig
        for fn in fns.values():
            store=F.Store();old=None;anchor=None;chosen=0;w,c,ss=fixtures[0]
            for p in [[v*g for v in x] for x in ss]:
                saved=P.snapshot(store,old);arena=F.Arena(store);gen=fn(w,p,c,chosen,old,anchor,'flat_share',arena)
                _,length=drain(gen);P.cancel(store,old,arena,gen,saved);result['completed_uncommitted']+=1
                for stop in sorted(set((0,1,2,10,length//4,length//2,length-2))):
                    if stop>=length:continue
                    arena=F.Arena(store);gen=fn(w,p,c,chosen,old,anchor,'flat_share',arena)
                    for _ in range(stop):next(gen)
                    P.cancel(store,old,arena,gen,saved);result['cancellation_prefixes']+=1
                arena=F.Arena(store);gen=fn(w,p,c,chosen,old,anchor,'flat_share',arena)
                (best,chosen,new),_=drain(gen);gen.close();drain(arena.cleanup(new))
                if old:drain(old.release())
                old=new;anchor=p;check(w,p,c,best,chosen,old,g,True)
            drain(old.release());store.empty()
    result.update(passed=True,all_stores_empty=True);save('continuation-verification.json',result);print(result,flush=True)

def arithmetic():
    rng=random.Random(1012026);shuffle=random.Random(1012027);fns={m:kernel(m) for m in MODES};cells=[]
    for bits in (16,64,256,1024):
        for label in LABELS:
            rows=arithmetic_rows(bits,label,rng);info=row_info(rows);cell=dict(bits=bits,label=label,diagnostics=info,runs=[])
            for rep in range(5):
                modes=list(MODES);shuffle.shuffle(modes)
                for order,m in enumerate(modes):
                    c0,w0=time.process_time(),time.perf_counter();value=fns[m](rows,32);cpu,wall=time.process_time()-c0,time.perf_counter()-w0
                    assert value==info['expected']*32 and cpu<20 and wall<30
                    cell['runs'].append(dict(rep=rep,mode=m,order=order,cpu=cpu,wall=wall,consumed=value))
            cells.append(cell)
        save('arithmetic-results.json',dict(cells=cells));print('Arithmetic complete',bits,flush=True)

def benchmark(stage):
    runs=[];diagnostics=[];deterministic={};crossscale={};outer=time.perf_counter();skipped=[]
    shuffle=random.Random(1012028 if stage==1 else 1012029)
    sizes=(24,) if stage==1 else (16,32,48);shifts=(0,64,256,1024) if stage==1 else (0,)
    seeds=(61000,61001) if stage==1 else (71000,)
    regimes=('sparse1','dense','signed_reset') if stage==1 else ('sparse1','dense','alternating','pulse5','mixed')
    cases=[]
    for n in sizes:
        for family in ('uncorrelated','proportional'):
            for regime in regimes:
                for seed in seeds:
                    c0,w0=time.process_time(),time.perf_counter();w,c,base=workload(n,seed,family,regime,30 if stage==1 else 20)
                    generate=(time.process_time()-c0,time.perf_counter()-w0)
                    for shift in shifts:
                        g=1<<shift;c0,w0=time.process_time(),time.perf_counter();ss=[[v*g for v in p] for p in base];scaling=(time.process_time()-c0,time.perf_counter()-w0)
                        cases.append((dict(n=n,family=family,regime=regime,seed=seed,shift=shift),w,c,ss,g,dict(generate=generate,scale=scaling,max_profit_bits=max(abs(v).bit_length() for p in ss for v in p),profit_encoding_bits=sum(max(1,abs(v).bit_length())+1 for p in ss for v in p))))
    for rep in range(3):
        for meta,w,c,ss,g,costs in cases:
            if time.perf_counter()-outer>900:skipped.append(dict(rep=rep,**meta));continue
            c0,w0=time.process_time(),time.perf_counter();fns=solvers(g,stage==1);compilation=(time.process_time()-c0,time.perf_counter()-w0)
            if stage==1 and g==1:fns['endpoint_original']=F.solve
            modes=list(fns);shuffle.shuffle(modes);sig=None
            for order,m in enumerate(modes):
                run=run_stream(w,c,ss,fns[m],g);run.update(**meta,rep=rep,mode=m,order=order,input_costs=costs,compilation_cost=compilation);sem=semantic(run)
                if run['status']=='complete':
                    if sig is None:sig=sem
                    else:assert sem==sig,(meta,m)
                    key=tuple(meta.values())
                    if key in deterministic:assert sem==deterministic[key]
                    else:deterministic[key]=sem
                    crosskey=(meta['n'],meta['family'],meta['regime'],meta['seed'])
                    if stage==1:
                        if crosskey in crossscale:assert sem==crossscale[crosskey],('scale',meta)
                        else:crossscale[crosskey]=sem
                runs.append(run)
            if rep==0:
                fn,pop=diagnostic_solver(g,stage==1);trace=run_stream(w,c,ss,fn,g)
                diagnostics.append(dict(**meta,population=dict(pop),status=trace['status'],queries=len(trace['queries']),digest=trace['digest'],max_price_bits=max((q['max_price_bits'] for q in trace['queries']),default=0),max_num_bits=max((q['max_num_bits'] for q in trace['queries']),default=0),input_costs=costs))
                if trace['status']=='complete' and sig:assert semantic(trace)==sig
            save(f'solver{stage}-results.json',dict(runs=runs,diagnostics=diagnostics,unexecuted=skipped,matched_complete_semantics=True))
            print('Stage',stage,'rep',rep,meta,[(r['mode'],r['status'],len(r['queries'])) for r in runs[-len(modes):]],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('task',choices=('verify','arithmetic','solver1','solver2'));args=ap.parse_args()
    save('environment.json',dict(python=platform.python_version(),platform=platform.platform(),cpu_count=os.cpu_count(),clock=vars(time.get_clock_info('process_time'))))
    if args.task=='verify':verify()
    elif args.task=='arithmetic':arithmetic()
    else:benchmark(int(args.task[-1]))
if __name__=='__main__':main()
