import json,random,time,sys
from pathlib import Path
import horizon as H
from compaction import run,POLICIES
from audit_repeated import audit_case
from payback import summarize,comparison

def save(name,x):Path(name).write_text(json.dumps(x,indent=2))
def directions(p,m,rng):
    one=[0]*len(p);one[rng.randrange(len(p))]=rng.choice((-1,1))
    return dict(zero=[0]*len(p),sparse=one,signed=[rng.randint(-3,3) for _ in p],scale=p.copy(),reinforce=[1 if m>>i&1 else -1 for i in range(len(p))],harm=[-1 if m>>i&1 else 1 for i in range(len(p))])
def case(meta,w,p,v,c,source,end=64):
    return dict(**meta,weights=w,profits=p,slopes=v,capacity=c,packing=source['packing'],initial_proof=source['proof'],end=end,paths=[run(w,p,v,c,source['packing'],source['proof'],mode,end) for mode in POLICIES])
def verify():
    rows=[]
    for label,w,p,v,c,m,proof in [('scale',[1,1],[10,9],[10,9],1,1,[[0,3,1,10,1,10]]),('loss',[2,3],[4,5],[1,0],3,2,[[0,3,3,5,3,17]]),('zero',[2,3],[4,5],[0,0],3,2,[[0,3,3,5,3,17]])]:rows.append(case(dict(case_id=label),w,p,v,c,dict(packing=m,proof=proof),20))
    for path in rows[0]['paths'][1:4]:assert sum(e['action']=='rebuild' for e in path['events'])==1
    assert all(path['status']=='packing_lost' and path['final_time']==2 for path in rows[1]['paths'])
    assert all(path['status']=='forever_certified' for path in rows[2]['paths'])
    rng=random.Random(136900)
    for j in range(10):
        w=[rng.randint(1,9) for _ in range(6)];c=sum(w)//3;p=[rng.randint(-10,25) for _ in w];v=[rng.randint(-2,2) for _ in w];source=H.source(w,p,c,time.perf_counter()+30);rows.append(case(dict(case_id=f'verify-{j}'),w,p,v,c,source,20))
    # Synthetic accounting: initially expensive reconstruction gains a durable advantage later.
    def ledger(mode,entries):return dict(mode=mode,events=[dict(time=t,action=a,prior_cells=4,result=dict(success=True,proof=[[0]*6]*2),counters=dict(bound_evaluations=n)) for t,a,n in entries],totals=dict(bound_evaluations=sum(z[2] for z in entries)))
    base=ledger('maintain',[(1,'repair',10),(2,'repair',10),(3,'repair',10)])
    hybrid=ledger('once_1',[(1,'rebuild',18),(2,'repair',2),(3,'repair',2)])
    check=comparison(base,hybrid,4);assert check['initial_extra_cost']==8 and check['durable_advantage_time']==3 and check['payback_delay']==2
    save('Verification.json',dict(passed=True,rows=rows,audit=[audit_case(x) for x in rows],payback_fixture=check))
def experiment(stage):
    seeds=(136000,) if stage=='development' else (136500,136501,136502);rows=[];sources=[]
    for n in (8,12):
        for seed in seeds:
            rng=random.Random(seed);w=[rng.randint(2,20) for _ in range(n)];c=sum(w)//3
            families=dict(random=[rng.randint(5,50) for _ in w],proportional=[wi+15+rng.randint(-2,2) for wi in w],mixed=[rng.randint(-15,40) for _ in w],negative=[-rng.randint(1,10) for _ in w])
            for family,p in families.items():
                source=H.source(w,p,c,time.perf_counter()+60);sources.append(dict(n=n,seed=seed,family=family,**source))
                for regime,v in directions(p,source['packing'],rng).items():rows.append(case(dict(case_id=f'{n}-{seed}-{family}-{regime}',n=n,seed=seed,family=family,regime=regime),w,p,v,c,source))
    save(stage+'-results.json',dict(rows=rows,sources=sources,unstarted=[]));summary=summarize(rows);save(stage+'-summary.json',summary);print(stage,json.dumps({k:v for k,v in summary.items() if k!='comparisons'}),flush=True)
    checks=[audit_case(x) for x in rows];save(stage+'-audit.json',dict(passed=True,cases=len(rows),events=sum(x['events'] for x in checks),cells=sum(x['cells'] for x in checks)));print(stage,'audit passed',flush=True)
if __name__=='__main__':verify() if sys.argv[1]=='verify' else experiment(sys.argv[1])
