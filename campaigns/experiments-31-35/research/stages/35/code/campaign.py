"""Resume-safe sequential five-stage campaign. Run from campaign/; standard library."""
import json,random,time,sys,hashlib,shutil,platform,statistics,os
from pathlib import Path
import engine as E
from source_clean import solve
from audit_new import Auditor
from experiment import directions
ROOT=Path(__file__).resolve().parents[1]
def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,separators=(',',':')));tmp.replace(path)
def read(path):return json.loads(Path(path).read_text())
def status_update(stage,**data):
 path=ROOT/'Campaign-status.json';status=read(path) if path.exists() else {str(x):dict(status='not_started') for x in range(26,31)};status[str(stage)].update(data);save(path,status)
def spec(name,strategy=None,cooldown=0):return dict(name=name,strategy=strategy or name,cooldown=cooldown)
def policies(stage):
 if stage==26:return [spec('maintain'),spec('root_all'),spec('root_gated')]
 if stage==27:
  sel=read(ROOT/'stages/26/Selection.json')['gated_root'];return [spec('maintain'),spec(sel),spec('local')]
 if stage>=28:
  selection=read(ROOT/'stages/27/Selection.json');strategy=selection['probe_strategy']
  base=[spec('maintain')]+[spec('ordinary',strategy),spec('skip3',strategy,3),spec('skip15',strategy,15)]
  if stage==28:return base
  if stage==29:return [dict(x,name=x['name']+'_'+suffix,normalization=norm) for norm,suffix in ((False,'raw'),(True,'normalized')) for x in base]
  selected=read(ROOT/'stages/28/Selection.json')['selected_probe_spec'];return [spec('maintain'),dict(selected,name='selected'),spec('rebuild')]

def inputs(stage,split):
 seed0=141000+1000*(stage-26);seeds=[seed0] if split=='development' else [seed0+500,seed0+501,seed0+502];sizes=[8,12] if stage<30 else [12,16]
 out=[]
 for n in sizes:
  for seed in seeds:
   rng=random.Random(seed);w=[rng.randint(2,20) for _ in range(n)];c=sum(w)//3
   families=dict(random=[rng.randint(5,50) for _ in w],proportional=[wi+15+rng.randint(-2,2) for wi in w],mixed=[rng.randint(-15,40) for _ in w],negative=[-rng.randint(1,10) for _ in w])
   for family,p in families.items():
    # Directions require the native optimizer's packing, just as stage 25.
    out.append(dict(n=n,seed=seed,family=family,weights=w,profits=p,capacity=c,rng_state=rng.getstate()))
    # Advance RNG exactly as directions does, independently of packing for random draws.
    directions(p,0,rng)
 return out

def canonical(x):
 if isinstance(x,dict):return {k:canonical(v) for k,v in x.items() if not k.endswith('cpu') and k not in ('wall','algorithm_cpu','construction_wall','event_cpu')}
 if isinstance(x,list):return [canonical(v) for v in x]
 return x

def extend(row,ps):
 paths=[];cache={};initial=row['source'];p=row['profits'];v=row['slopes'];w=row['weights'];c=row['capacity'];end=row['end']
 for s in ps:
  phases=[];m=row['packing'];proof=row['initial_proof'];t=0;switches=0;optimizer_steps=initial['construction_steps'];optimizer_cpu=initial['algorithm_cpu'];tot=E.empty_counts();cpu0=time.process_time();wall0=time.perf_counter();peak=0;peak_nodes=0
  while True:
   phase=E.run(w,p,v,c,m,proof,s,end,normalization=True,phase_start=t,spent=tot['bound_evaluations'],elapsed=time.perf_counter()-wall0);phases.append(phase);E.plus(tot,phase['totals']);peak=max(peak,phase['peak_cells']);peak_nodes=max(peak_nodes,phase['peak_nodes'])
   if phase['status']!='packing_lost':break
   t=phase['final_time'];q=[a+t*b for a,b in zip(p,v)]
   if t not in cache:
    try:cache[t]=solve(w,q,c)
    except E.Cap as exc:phase['replacement_capped']=str(exc);break
   replacement=cache[t];phase['replacement']=replacement;optimizer_steps+=replacement['construction_steps'];optimizer_cpu+=replacement['algorithm_cpu'];m=replacement['packing'];proof=replacement['proof'];switches+=1
   if tot['bound_evaluations']>=E.LIMITS['evaluations'] or optimizer_steps>2000000:
    phase['replacement_capped']='cumulative maintenance/search cap';break
  status='capped' if phases[-1].get('replacement_capped') else phases[-1]['status']
  paths.append(dict(mode=s['name'],spec=s,phases=phases,status=status,final_time=phases[-1]['final_time'],totals=tot,switches=switches,phase_lengths=[x['final_time']-(x['events'][0]['previous_time'] if x['events'] else x['last_verified_time']) for x in phases],peak_cells=peak,peak_nodes=peak_nodes,optimizer_search_steps=optimizer_steps,optimizer_cpu=optimizer_cpu,optimizer_calls=switches+1,search_charging='identical solves shared physically, full construction steps and recorded clean CPU charged to each policy',algorithm_cpu=tot['algorithm_cpu']+optimizer_cpu))
 row['optimizer_cache']={str(t):o for t,o in cache.items()};return paths

def ledger(path,end,key='bound_evaluations'):
 events=path.get('events')
 if events is None:events=[e for ph in path['phases'] for e in ph['events']]
 values=[0]*(end+1)
 for e in events:values[e['time']]+=e['counters'][key]
 for t in range(1,len(values)):values[t]+=values[t-1]
 return values

def comparison(row,base,path):
 b=ledger(base,row['end']);z=ledger(path,row['end']);s=[x-y for x,y in zip(b,z)];positive=[t for t,x in enumerate(s) if x>0];lastbad=max((t for t,x in enumerate(s) if x<=0),default=-1);persist=lastbad+1 if s[-1]>0 else None
 return dict(case_id=row['case_id'],regime=row['regime'],mode=path['mode'],saving=s[-1],savings_by_time=s,first_advantage=positive[0] if positive else None,persistent_advantage=persist,first_debt=next((-x for x in s if x<0),0),paired=base['status']!='capped' and path['status']!='capped')

def summarize(rows):
 modes={};comparisons=[]
 for row in rows:
  for path in row['paths'][1:]:comparisons.append(comparison(row,row['paths'][0],path))
 names=[x['mode'] for x in rows[0]['paths']] if rows else []
 for name in names:
  ps=[next(x for x in r['paths'] if x['mode']==name) for r in rows];tot={k:sum(x['totals'][k] for x in ps) for k in E.COUNT_KEYS+E.TIME_KEYS};complete=[x for x in ps if x['status']!='capped'];cs=[x for x in comparisons if x['mode']==name and x['paired']];savings=[x['saving'] for x in cs];largest=max(cs,key=lambda x:x['saving']) if cs else None
  modes[name]=dict(totals=tot,complete=len(complete),capped=len(ps)-len(complete),peak_cells=max((x['peak_cells'] for x in ps),default=0),peak_nodes=max((x['peak_nodes'] for x in ps),default=0),final_cells=[len(x.get('final_proof',x.get('phases',[{}])[-1].get('final_proof',[]))) for x in ps],events=tot['maintenance_events'],statuses={st:sum(x['status']==st for x in ps) for st in sorted({x['status'] for x in ps})},paired=len(cs),benefited=sum(s>0 for s in savings),harmed=sum(s<0 for s in savings),tied=sum(s==0 for s in savings),saving=sum(savings),saving_distribution=sorted(savings),largest=None if largest is None else {k:largest[k] for k in ('case_id','saving')},saving_without_largest=sum(savings)-(largest['saving'] if largest else 0),saving_excluding_scale=sum(x['saving'] for x in cs if x['regime']!='scale'),first_advantage_count=sum(x['first_advantage'] is not None for x in cs),persistent_advantage_count=sum(x['persistent_advantage'] is not None for x in cs))
  if 'phases' in ps[0]:modes[name].update(switches=sum(x['switches'] for x in ps),optimizer_search_steps=sum(x['optimizer_search_steps'] for x in ps),optimizer_cpu=sum(x['optimizer_cpu'] for x in ps),algorithm_with_search_cpu=sum(x['algorithm_cpu'] for x in ps),phase_lengths=[l for x in ps for l in x['phase_lengths']])
 return dict(cases=len(rows),modes=modes,comparisons=comparisons)

def verify(stage,ps,out):
 cases=[]
 # successful root collapse, optimal fractional-gap root failure, negative profits, losing root rejection
 for label,w,p,c,m in [('collapse',[2,3],[4,5],3,2),('fractional_gap',[2,2],[3,3],3,1),('negative',[1,2],[-5,-2],2,0),('losing',[2,3],[8,5],3,2)]:
  work=E.Work(w,p,m,E.empty_counts(),time.perf_counter()+10);root=[0,3,c,0,1,0];priced=work.price(root,'fixture');passes=priced[5]//priced[4]<=sum(x for i,x in enumerate(p) if m>>i&1)
  if label=='collapse':assert passes
  if label=='fractional_gap':assert not passes and Hdp(w,p,c)==3
  if label=='negative':assert passes
  if label=='losing':assert not passes
  cases.append(dict(label=label,priced=priced,success=passes))
 # Exact cover & prospective sibling merge, including omitted infeasible include branch.
 w=[2,2];p=[3,3];c=3;ct=E.empty_counts();forest=E.Forest([[0,3,3,0,1,0]],ct);children=forest.split(0,0,w,ct);forest.active=children;proof=[[0,2,3,0,1,3],[1,2,1,3,2,9]];work=E.Work(w,[0,0],1,E.empty_counts(),time.perf_counter()+10)
 new,ff,reuse,logs,hit=E.probe(work,proof,forest,'local');assert hit and len(new)==1 and len(ff.nodes)==1;Auditor(w,[0,0],[0,0],c).forest(ff.snapshot(),new)
 # Local complete subtree can merge even when the full-domain relaxation has a gap.
 w=[2,2];p=[3,3];ct=E.empty_counts();forest=E.Forest([[0,2,3,0,1,3],[1,0,1,0,1,3]],ct);kids=forest.split(0,1,w,ct);forest.active=kids+[1];proof=[[0,0,3,0,1,0],[2,0,1,0,1,3],[1,0,1,0,1,3]]
 work=E.Work(w,p,1,E.empty_counts(),time.perf_counter()+10);new,ff,reuse,logs,hit=E.probe(work,proof,forest,'local');assert hit and len(new)==2;root=work.price([0,3,3,0,1,0],'fixture_root');assert root[5]//root[4]>3;aud=Auditor(w,p,[0,0],3);aud.cover(new);aud.forest(ff.snapshot(),new)
 cases.append(dict(label='local_merge_root_fails',proof=new,root=root,probe=logs))
 # Infeasible include branch is omitted but the remaining child covers the full feasible parent.
 ct=E.empty_counts();ff=E.Forest([[1,2,1,0,1,3]],ct);kids=ff.split(0,1,w,ct);assert len(kids)==1;ff.active=kids;Auditor(w,p,[0,0],3).forest(ff.snapshot(),[[1,0,1,0,1,3]])
 # Fractional failure followed by branching, negative profits, losses and long-run switches.
 rng=random.Random(140900+stage)
 for j in range(12):
  w=[rng.randint(1,9) for _ in range(6)];p=[rng.randint(-12,25) for _ in w];v=[rng.randint(-3,3) for _ in w];c=sum(w)//3;source=solve(w,p,c);row=dict(case_id=f'verify-{j}',weights=w,profits=p,slopes=v,capacity=c,packing=source['packing'],initial_proof=source['proof'],source=source,end=24)
  row['paths']=extend(row,ps) if stage==30 else [E.run(w,p,v,c,row['packing'],row['initial_proof'],s,24,normalization=s.get('normalization',False)) for s in ps]
  checks=Auditor(w,p,v,c).row(row);cases.append(dict(row=row,audit=checks))
 # Guard must interrupt inside a price call; partial work is logged and cannot return a certificate.
 old_source=E.LIMITS['source_steps'];E.LIMITS['source_steps']=0
 try:solve([1,2],[3,4],2);raise AssertionError('source guard did not interrupt')
 except E.Cap:pass
 finally:E.LIMITS['source_steps']=old_source
 old=E.LIMITS['evaluations'];E.LIMITS['evaluations']=1;work=E.Work([1,1],[10,9],1,E.empty_counts(),time.perf_counter()+10)
 try:work.price([0,3,1,0,1,0],'cap');raise AssertionError('guard did not interrupt')
 except E.Cap:assert work.ct['bound_evaluations']==1 and work.calls[-1]['priced'] is None
 finally:E.LIMITS['evaluations']=old
 if stage>=29:
  w=[2,3];p=[4,5];source=solve(w,p,3);E.normalized_certificate(w,p,p,3,source['packing'],source['proof'])
  for v,f,iv in [([4,6],(1,1),(0,None)),(p,(0,1),(0,None)),(p,(1,-1),(0,None)),(p,(-1,-1),(0,None))]:
   try:E.normalized_certificate(w,p,v,3,source['packing'],source['proof'],f,iv);raise AssertionError('invalid factor accepted')
   except ValueError:pass
 save(out/'Verification.json',dict(passed=True,fixtures=cases,interruptible_guard=True,normalization_rejections=stage>=29))
def Hdp(w,p,c):
 import flat_baseline as F
 return F.dp(w,p,c)

PROTOCOL_COMMON='''All prices are exact nonnegative rationals. Fixed packings remain until strict loss; ties do not switch. Probe successes reuse the priced cells. Pricing and fractional-item branching match stage 25, including repricing failing roots in repair. No audit DP/enumeration selects prices, branches, probes or policy actions. Root probes never reconstruct on failure. Initial proof cells have no invented ancestors. Local probes reserve free-item-count+1 from one n+1 per-expiry budget, choose most leaves then fixed/free/residual/node tie order, and merge only complete feasible domains. No combined root/local variant is used. Cooldowns count eligible expiry opportunities, not time steps: a failure sets 3/15 skips; skipped eligible expiry decrements; ineligible expiry leaves it unchanged; any successful probe clears it. Local eligibility means a prospectively recorded ancestor has >=2 active leaves; budget ineligibility is recorded but does not set cooldown. Counts charge every candidate and hinge term, probe, split, selection comparison/visit and lineage operation, including loss detection. Structural counts are separate units, never added to pricing counts. Clean end-to-end algorithm CPU excludes enumeration/DP auditing, includes horizons, selection, lineage and representation recognition; kernel CPU is secondary. Timings are descriptive only, with no runtime performance claim. Source construction uses the same native exact optimizer and always disposes stores; construction, cleanup, disposal and audit are separately reported. Every proof, bound, expiry, witness, parent cover and replacement optimum is independently audited. Cached domain bitsets are a bounded exact-cover audit, not a policy oracle. Caps: 4096 returned/pending cells, 500000 candidate evaluations per policy trajectory, 45 seconds per trajectory; source 500000 native generator steps/4096 live cells/20 seconds per solve; audit 45 seconds per case; stage wall 600 seconds per split. Cap attempts are incomplete, save the last complete certificate and failed partial logs, and never contribute to paired-completed headlines. Inputs, completed cases, unstarted cases and cursor are saved atomically per case. Resume never reruns completed cases or stages. Trajectories sharing source instances are dependent descriptive comparisons. Largest-contributor exclusions are retrospective sensitivity diagnostics, never retuning. No previous experiments are rerun.\n'''

def protocol(stage,ps,out):
 size='n=8/12, integer time 0–64, four families and six directions' if stage<30 else 'n=12/16, integer time 0–256, four families, sparse/signed/scale/harm directions'
 seeds=141000+1000*(stage-26)
 text=f'# Experiment {stage}\n\n{size}. Development seed {seeds}; held-out {seeds+500}/{seeds+501}/{seeds+502}. Full prescribed matrix: '+('48 development, 144 held-out.' if stage<30 else '32 development, 96 held-out.')+'\n\n'+PROTOCOL_COMMON+'\nPolicies fixed before this stage: '+json.dumps(ps)+'\n'
 if stage>=28:text+='\nStrategy selected only on development from preceding stages. If no probe wins, maintenance remains the recommended reference; the least-cost probe is retained as an explicit hypothesis.\n'
 if stage==29:text+='\nPositive-factor representation recognizes vector equality v=p, not labels. For factor 1+t >0, scaled price and bound satisfy B(t)=(1+t)B(0); all packing values lie on the factor lattice, so floor(B(t)/(1+t)) <= V(p) proves optimality for all t>=0. This is a known representation ablation. No arbitrary gcd or fractional slope horizon is used.\n'
 if stage==30:text+='\nAt exact loss, each phase uses the same native cold optimizer with initial empty packing. Identical replacement solves can be shared, but their complete measured search steps and clean CPU are charged identically to every policy. Search generator steps, bound evaluations and audits remain separate. Cooldown and forest reset at phase change. Cumulative search cap 2 million steps per policy. Scaling is normalized identically for all policies.\n'
 (out/'Protocol.md').write_text(text)

def freeze(out):
 names=[p for p in (out/'code').glob('*.py')]+[out/'Protocol.md'];save(out/'Frozen.json',{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in names})
def check_frozen(out):
 assert all(hashlib.sha256((out/k).read_bytes()).hexdigest()==v for k,v in read(out/'Frozen.json').items())

def run_split(stage,split,ps,out):
 directory=out/split;directory.mkdir(exist_ok=True);cursor_path=directory/'Cursor.json';groups=inputs(stage,split);ids=[];rows=[];start=time.perf_counter();caplog=[];source_files=[];audit_counts=[]
 for group in groups:
  key=f"{group['n']}-{group['seed']}-{group['family']}";source_path=directory/'sources'/f'{key}.json'
  if source_path.exists():source=read(source_path)
  else:
   try:source=solve(group['weights'],group['profits'],group['capacity']);save(source_path,source)
   except E.Cap as exc:caplog.append(dict(source=key,reason=str(exc)));continue
  source_files.append(str(source_path.relative_to(out)));rng=random.Random();rng.setstate(group['rng_state']);ds=directions(group['profits'],source['packing'],rng)
  if stage==30:ds={k:v for k,v in ds.items() if k in ('sparse','signed','scale','harm')}
  for regime,v in ds.items():
   cid=key+'-'+regime;ids.append(cid);path=directory/'cases'/f'{cid}.json'
   if path.exists():row=read(path);rows.append(row);audit_counts.append(row['audit']);continue
   if time.perf_counter()-start>600:caplog.append(dict(case_id=cid,reason='split wall cap',unstarted=True));continue
   status_update(stage,status='running',split=split,current_case=cid,completed_cases=len(rows))
   row=dict(case_id=cid,n=group['n'],seed=group['seed'],family=group['family'],regime=regime,weights=group['weights'],profits=group['profits'],slopes=v,capacity=group['capacity'],packing=source['packing'],initial_proof=source['proof'],source=source,end=256 if stage==30 else 64)
   pending=directory/'pending'/f'{cid}.json'
   if pending.exists():row=read(pending)
   else:
    row['paths']=extend(row,ps) if stage==30 else [E.run(row['weights'],row['profits'],v,row['capacity'],row['packing'],row['initial_proof'],s,row['end'],normalization=s.get('normalization',False)) for s in ps]
    save(pending,row)
   audit_start=time.perf_counter();audit_cpu0=time.process_time();auditor=Auditor(row['weights'],row['profits'],v,row['capacity']);row['audit']=auditor.row(row);row['audit']['audit_total_cpu']=time.process_time()-audit_cpu0
   if time.perf_counter()-audit_start>E.LIMITS['audit_seconds']:caplog.append(dict(case_id=cid,reason='audit batch exceeded soft wall threshold',completed_audit=True))
   # Algorithms already use hard candidate/cell/source guards; audit batches complete atomically.
   save(path,row);pending.unlink(missing_ok=True);rows.append(row);audit_counts.append(row['audit'])
   capped=[p['mode'] for p in row['paths'] if p['status']=='capped']
   if capped:caplog.append(dict(case_id=cid,capped_policies=capped))
   save(cursor_path,dict(status='running',completed=[r['case_id'] for r in rows],last_completed=cid,next_group=key,resource_log=caplog))
   print(stage,split,len(rows),cid,[(p['mode'],p['status'],p['totals']['bound_evaluations']) for p in row['paths']],flush=True)
 summary=summarize(rows);save(directory/'Summary.json',summary);completed=[r['case_id'] for r in rows];unstarted=[cid for cid in ids if cid not in completed]
 save(directory/'Inputs-index.json',dict(case_ids=ids,source_files=source_files));save(directory/'Resource-log.json',dict(limits=E.LIMITS,elapsed_seconds=time.perf_counter()-start,caps=caplog,unstarted=unstarted));save(directory/'Audit.json',dict(passed=True,cases=len(rows),checks={k:sum(x[k] for x in audit_counts) for k in audit_counts[0] if k!='passed'} if audit_counts else {},all_source_stores_disposed=all(read(out/x)['empty'] for x in source_files)));save(cursor_path,dict(status='completed' if not unstarted else 'capped',completed=completed,unstarted=unstarted,last_completed=completed[-1] if completed else None))
 return summary,rows

def selection(stage,summary,out):
 if stage>=29:return
 modes=summary['modes'];base=modes['maintain']['totals']['bound_evaluations']
 if stage==26:
  name=min(('root_all','root_gated'),key=lambda k:(modes[k]['totals']['bound_evaluations'],k!='root_gated'));data=dict(gated_root=name,reference='maintain',basis='stage26 development bound evaluations, conservative gated tie break',development={k:modes[k]['totals']['bound_evaluations'] for k in modes})
 elif stage==27:
  names=[k for k in modes if k!='maintain'];name=min(names,key=lambda k:(modes[k]['totals']['bound_evaluations'],k));data=dict(probe_strategy=name,reference='maintain' if modes[name]['totals']['bound_evaluations']>=base else name,improved_on_development=modes[name]['totals']['bound_evaluations']<base,basis='stage27 development only; stage26 determines included root gate',development={k:modes[k]['totals']['bound_evaluations'] for k in modes})
 elif stage==28:
  names=[k for k in modes if k!='maintain'];name=min(names,key=lambda k:(modes[k]['totals']['bound_evaluations'],k));s=next(x for x in policies(stage) if x['name']==name);data=dict(selected_probe_spec=s,reference='maintain' if modes[name]['totals']['bound_evaluations']>=base else name,basis='stage28 development only',development={k:modes[k]['totals']['bound_evaluations'] for k in modes})
 else:return
 save(out/'Selection.json',data)

def report(stage,dev,held,out):
 lines=[f'# Experiment {stage}: audited results','',f'Development: {dev["cases"]} trajectories. Held-out: {held["cases"]}. Cases share weights/source proofs; these are descriptive paired results.','', '| Policy | Completed | Paired vs first policy | Bound evaluations | Hinge evaluations | Probes / hits | Saving | Benefited / harmed / tied | Saving excluding largest |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for name,d in held['modes'].items():
  t=d['totals'];lines.append(f'| {name} | {d["complete"]} | {d["paired"]} | {t["bound_evaluations"]:,} | {t["free_term_evaluations"]:,} | {t["probes"]} / {t["hits"]} | {d["saving"]:,} | {d["benefited"]} / {d["harmed"]} / {d["tied"]} | {d["saving_without_largest"]:,} |')
 lines+=['','All probe checks, successful and failed, are included. Candidate, hinge, structural and native search counters are different units. Summary.json saves every trajectory saving, common-time cumulative ledger, first/persistent advantage, status and largest-contributor sensitivity. Raw totals include capped prefixes; paired summaries include completed pairs only.','', 'CPU scopes (seconds; single instrumented runs, descriptive, no speed claim):','', '| Policy | Algorithm excluding audits | Horizons | Policy/lineage | Kernel | Selection visits / comparisons | Lineage operations | Peak proof cells / forest nodes |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name,d in held['modes'].items():
  t=d['totals'];lines.append(f'| {name} | {t["algorithm_cpu"]:.6f} | {t["horizon_cpu"]:.6f} | {t["policy_cpu"]:.6f} | {t["kernel_cpu"]:.6f} | {t["selection_visits"]} / {t["selection_comparisons"]} | {t["lineage_ops"]} | {d["peak_cells"]} / {d["peak_nodes"]} |')
 limitations={26:'A root fractional bound can miss real local simplifications; aggregate benefit is finite-data evidence, and the largest-contributor deletion is only descriptive.',27:'Initial proof cells have no recoverable ancestry. Prospective merges cannot cross those roots, and the n+1 reservation budget excludes some ancestors.',28:'Failures provide no guarantee about future opportunities. Cooldowns can delay profitable checks; schedule selection used development only.',29:'Only exact vector equality v=p with positive factor 1+t is recognized. This removes redundant representation work, not a new arithmetic or arbitrary gcd theorem.',30:'This bounded two-size, 256-time matrix tests incumbent switches for the first time. Native optimizer steps are separate from certificate evaluations; no general best policy or asymptotic guarantee follows.'}
 lines+=['','Decisive limitation: '+limitations[stage],'','Implementation and protocol were verified and frozen before held-out execution. Source hashes were verified without rerunning stage 25. Every saved proof, price, cover, expiry and improving witness was checked independently; audit oracle costs are excluded from algorithm CPU. Resource logs and atomic cursors disclose caps, unstarted cases and partial prefixes.']
 if stage==29:
  lines+=['','All-time guarantee: for g(t)=1+t>0, q(t)=g(t)p and lambda(t)=g(t)lambda(0). Each hinge, fixed term and price-capacity term scales by g, hence B(t)=gB(0). Each feasible packing value is g times an integer; its bound rounds down on that lattice to g floor(B(0)). A base certificate floor(B(0))<=V_M(p) therefore certifies M for every t>=0, including signed p and ties. Direct original-profit DP samples supplement this analytic proof. This is known normalization, not novelty.']
 if stage==30:
  lines+=['','Search accounting: identical phase optimizations are physically shared, with their full steps and recorded clean CPU charged to every policy. All-time normalized scale trajectories have no incumbent switches.','', '| Policy | Strict incumbent switches | Native search steps | Charged optimizer CPU | Certificate + optimizer CPU |','|---|---:|---:|---:|---:|']
  for name,d in held['modes'].items():lines.append(f'| {name} | {d["switches"]} | {d["optimizer_search_steps"]:,} | {d["optimizer_cpu"]:.6f} | {d["algorithm_with_search_cpu"]:.6f} |')
 (out/'Report.md').write_text('\n'.join(lines)+'\n')

def main():
 stages=[int(x) for x in sys.argv[1:]] or list(range(26,31))
 for stage in stages:
  out=ROOT/'stages'/str(stage);out.mkdir(parents=True,exist_ok=True)
  if (out/'Complete.json').exists():print('skip completed stage',stage,flush=True);continue
  ps=policies(stage)
  if not (out/'Frozen.json').exists():
   (out/'code').mkdir(exist_ok=True)
   for p in (ROOT/'code').glob('*.py'):shutil.copy2(p,out/'code'/p.name)
   protocol(stage,ps,out);verify(stage,ps,out);freeze(out)
  check_frozen(out);status_update(stage,status='running',policies=ps)
  dev,devrows=run_split(stage,'development',ps,out);selection(stage,dev,out);check_frozen(out)
  # Development selection is sealed before first held-out case; does not alter this stage's policies.
  if (out/'Selection.json').exists():save(out/'Selection-frozen.json',dict(sha256=hashlib.sha256((out/'Selection.json').read_bytes()).hexdigest(),basis='development only, sealed before held-out'))
  held,heldrows=run_split(stage,'held',ps,out);check_frozen(out);report(stage,dev,held,out)
  incomplete=any((out/s/'Cursor.json').exists() and read(out/s/'Cursor.json')['status']!='completed' for s in ('development','held'));caps=sum(d['capped'] for d in held['modes'].values())
  save(out/'Complete.json',dict(status='capped' if incomplete or caps else 'completed',development=dev['cases'],held=held['cases'],frozen_verified=True));status_update(stage,status='capped' if incomplete or caps else 'completed',development=dev['cases'],held=held['cases'],current_case=None,completed_cases=held['cases'])
  print('STAGE COMPLETE',stage,json.dumps({k:{'evals':v['totals']['bound_evaluations'],'saving':v['saving'],'paired':v['paired'],'hits':v['totals']['hits']} for k,v in held['modes'].items()}),flush=True)
if __name__=='__main__':main()
