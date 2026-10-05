"""Fresh stages 31-35; policy code never reads audit answers."""
import json,time,copy,random,hashlib,shutil,statistics,sys,zipfile,os,uuid
from pathlib import Path
from fractions import Fraction
import engine as E
import horizon as H
import frontier as FR
from source_guarded import solve,SourceCap
from experiment import directions
ROOT=Path(__file__).resolve().parents[1]
SAVE_METRICS=[]
def json_safe(x):
 if isinstance(x,dict):return {str(k) if not isinstance(k,str) else k:json_safe(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [json_safe(v) for v in x]
 return x
def save(p,x):
 save_cpu=time.process_time();p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');payload=json.dumps(json_safe(x),separators=(',',':'));
 with q.open('w') as fh:fh.write(payload);fh.flush();os.fsync(fh.fileno())
 q.replace(p);SAVE_METRICS.append(dict(path=str(p),cpu=time.process_time()-save_cpu,bytes=p.stat().st_size))
def read(p):return json.loads(Path(p).read_text())
def counts():return dict(**E.empty_counts(),**{k:0 for k in FR.DP_KEYS})
def specs(stage):
 if stage==31:return [('maintain','maintain'),('selected','local'),('rebuild','rebuild')]
 if stage==32:return [('maintain','maintain'),('uniform','uniform')]
 if stage==33:return [('maintain','maintain'),('affine_max','affine_max'),('affine_pair','affine_pair')]
 if stage==34:return [('maintain','maintain'),('affine_pair','affine_pair'),('two_class','two_class')]
 s=read(ROOT/'stages/34/Selection.json')['candidate'];return [('maintain','maintain'),(s,s),('slope','slope'),('pruned','pruned')]
def inputs(stage,split,source_dir):
 seed0=146000+(stage-31)*1000;seeds=[seed0] if split=='development' else [seed0+500,seed0+501,seed0+502]
 rows=[]
 for n in (12,16):
  for seed in seeds:
   rng=random.Random(seed);w=[rng.randint(2,20) for _ in range(n)];c=sum(w)//3
   families=dict(random=[rng.randint(5,50) for _ in w],proportional=[wi+15+rng.randint(-2,2) for wi in w],mixed=[rng.randint(-15,40) for _ in w],negative=[-rng.randint(1,10) for _ in w])
   controls={f:rng.randrange(n) for f in families} if stage in (32,33) else {}
   for family,p in families.items():
    sf=source_dir/f'{n}-{seed}-{family}.json'
    if sf.exists():source=read(sf)
    else:
     source=solve(w,p,c);save(sf,source)
    if stage==32:
     vecs={'uniform_plus':[1]*n,'uniform_minus':[-1]*n,'zero':[0]*n,'near_uniform':[1]*n};vecs['near_uniform'][controls[family]]=2
    elif stage==33:
     vecs={'scale':p.copy(),'affine_plus':[x+1 for x in p],'affine_negative':[-x+1 for x in p],'near_affine':[x+1 for x in p]};vecs['near_affine'][controls[family]]+=1
    else:vecs={k:v for k,v in directions(p,source['packing'],rng).items() if k in ('sparse','signed','scale','harm')}
    for regime,v in vecs.items():rows.append(dict(case_id=f'{n}-{seed}-{family}-{regime}',n=n,seed=seed,family=family,regime=regime,weights=w,profits=p,slopes=v,capacity=c,packing=source['packing'],initial_proof=source['proof'],source=source,end=256,control_index=controls.get(family)))
 return rows

def run_policy(row,name,policy,cache):
 cpu=time.process_time();wall=time.perf_counter();source=row['source'];initial_cpu=source['algorithm_cpu'];charged_extra_cpu=0;charged_extra_wall=source['wall'];w,p,v,c=[row[k] for k in ('weights','profits','slopes','capacity')];m=row['packing'];proof=copy.deepcopy(row['initial_proof']);t=0;tot=counts();phases=[];cert=None;partial=None;dispatch='scalar';construction_cpu=0;optimizer=[dict(time=0,**source)];ledger=[];pending=None
 deadline=wall+120-source['wall']
 if policy not in ('maintain','local','rebuild'):
  a=time.process_time();tot['recognition']+=len(p)
  if p==v:dispatch='normalized'
  else:
   b=time.process_time()
   try:cert=FR.build(w,p,v,c,policy,deadline,tot)
   except FR.ConstructionCap as exc:
    partial=exc.partial;partial['reason']=str(exc);dispatch='construction_fallback'
   construction_cpu=time.process_time()-b
   if cert is not None:dispatch='frontier'
  ledger.append(dict(time=0,kind='construction',counters={k:tot[k] for k in FR.DP_KEYS},algorithm_cpu=time.process_time()-a))
 spec=dict(name=name,strategy=policy if policy in ('local','rebuild') else 'maintain',cooldown=15 if policy=='local' else 0)
 while True:
  if time.perf_counter()>=deadline or sum(x['construction_steps'] for x in optimizer)>=2000000:
   pending=dict(kind='phase_start',time=t,packing=m,proof=proof);status='capped';break
  if cert is not None:
   phase_cpu=time.process_time();ct=counts();loss,witness=FR.horizon(cert,p,v,m,t,ct);boundary=cert.get('boundary');nextt=min([x for x in (loss,boundary) if x is not None],default=None)
   phase=dict(kind='frontier',packing=m,anchor=t,loss=loss,witness=witness,boundary=boundary,events=[],totals=ct)
   if nextt is None or nextt>256:phase.update(status='window_complete',final_time=256)
   elif boundary is not None and boundary==nextt:phase.update(status='factor_handoff',final_time=nextt);ct['factor_dispatches']+=1
   else:phase.update(status='packing_lost',final_time=nextt)
   ct['algorithm_cpu']=time.process_time()-phase_cpu;E.plus(tot,ct);ledger.append(dict(time=phase['final_time'] if phase['status']!='window_complete' else t,kind='frontier_horizon',counters=ct,algorithm_cpu=ct['algorithm_cpu']));phases.append(phase)
   if phase['status']=='window_complete':status='window_complete';break
   t=phase['final_time']
   if phase['status']=='factor_handoff':
    cert_saved=cert;cert=None;dispatch='frontier_then_scalar';q=[a+t*b for a,b in zip(p,v)];work=E.Work(w,q,m,tot,deadline);ct0=time.process_time()
    try:repair=work.repair(proof)
    except E.Cap as exc:repair=dict(incomplete=True,success=False,reason=str(exc))
    event=dict(kind='boundary_repair',time=t,proof_before=proof,calls=work.calls,result=repair,counters=work.ct);event['algorithm_cpu']=time.process_time()-ct0;E.plus(tot,work.ct);ledger.append(dict(time=t,kind='boundary_repair',counters=work.ct,algorithm_cpu=event['algorithm_cpu']));phase['handoff']=event
    if repair.get('incomplete'):pending=dict(kind='boundary_repair',time=t,packing=m,proof=proof);status='capped';break
    if repair['success']:proof=repair['proof'];continue
    phase['strict_witness']=repair['witness']
  else:
   ph=E.run(w,p,v,c,m,proof,spec,256,normalization=True,phase_start=t,spent=tot['bound_evaluations'],elapsed=max(0,120-(deadline-time.perf_counter())))
   ph['kind']='scalar';ph['anchor']=t;phases.append(ph);E.plus(tot,ph['totals'])
   for he in ph.get('horizon_ledger',[]):ledger.append(dict(time=he['time'],kind='scalar_horizon',counters={},algorithm_cpu=he['algorithm_cpu']))
   remainder=ph['totals']['algorithm_cpu']-sum(e['event_cpu'] for e in ph['events'])-sum(e['algorithm_cpu'] for e in ph.get('horizon_ledger',[]))
   ledger.append(dict(time=t,kind='scalar_initialization_and_bookkeeping',counters={},algorithm_cpu=remainder))
   for e in ph['events']:ledger.append(dict(time=e['time'],kind='scalar_expiry',counters=e['counters'],algorithm_cpu=e['event_cpu']))
   if ph['status']!='packing_lost':
    status=ph['status']
    if status=='capped':pending=dict(kind='scalar_attempt',phase=len(phases)-1,anchor=ph['last_verified_time'],next_time=ph['final_time'],packing=m,proof=ph['final_proof'],forest=ph['final_forest'],cooldown=ph['events'][-1]['cooldown_before'])
    break
   t=ph['final_time']
  # Any strict loss, irrespective of certificate format, uses common native optimizer.
  try:
   if t in cache:
    opt=cache[t];charged_extra_cpu+=opt['algorithm_cpu'];charged_extra_wall+=opt['wall'];deadline-=opt['wall']
   else:
    opt=solve(w,[a+t*b for a,b in zip(p,v)],c,deadline=deadline,max_steps=2000000-sum(x['construction_steps'] for x in optimizer));cache[t]=opt
   optimizer.append(dict(time=t,**opt));phases[-1]['replacement']=opt
  except SourceCap as exc:
   optimizer.append(dict(time=t,aborted=True,**exc.cost));pending=dict(kind='optimizer',time=t,packing=m,proof=proof);status='capped';break
  ledger.append(dict(time=t,kind='optimizer',counters={},algorithm_cpu=opt['algorithm_cpu'],native_cost=opt));m=opt['packing'];proof=opt['proof']
 certificate=cert if cert is not None else locals().get('cert_saved')
 fullcpu=time.process_time()-cpu+initial_cpu+charged_extra_cpu
 return dict(phase_lengths=[ph['final_time']-ph.get('anchor',0) for ph in phases],mode=name,policy=policy,spec=spec,status=status,dispatch=dispatch,phases=phases,frontier=certificate,partial_frontier=partial,totals=tot,construction_cpu=construction_cpu,optimizer=optimizer,optimizer_search_steps=sum(x['construction_steps'] for x in optimizer),optimizer_cpu=sum(x['algorithm_cpu'] for x in optimizer),algorithm_cpu=fullcpu,algorithm_wall=time.perf_counter()-wall+charged_extra_wall,switches=sum('replacement' in x for x in phases),pending=pending,ledger=ledger,initial_cpu=initial_cpu)

def audit_path(row,path,out):
 from audit_new import Auditor
 from check_frontier import Checker,independent_dp,check_samples
 from extend30 import audit_phase
 if out.exists() and read(out).get('passed'):return
 records=read(out).get('records',[]) if out.exists() else [];done={x['key'] for x in records}
 w,p,v,c=[row[k] for k in ('weights','profits','slopes','capacity')]
 def commit(key,cpu,details):records.append(dict(key=key,cpu=cpu,details=details,passed=True));save(out,dict(passed=False,records=records,next_range=key))
 partial=path['partial_frontier']
 if partial:
  for ti,table in enumerate(partial.get('completed_tables',[])):
   for j in range(len(table['layers'])):
    key=f'partial_completed:{ti}:{j}'
    if key in done:continue
    ck=Checker(w,p,v,c);start=time.process_time();(ck.dense_layer if table['kind']=='dense' else ck.sparse_layer)(table,j);commit(key,time.process_time()-start,dict(entries_checked=ck.checks))
  for j in range(len(partial['layers'])):
   key=f'partial_prefix:{j}'
   if key in done:continue
   ck=Checker(w,p,v,c);start=time.process_time();(ck.dense_layer if partial['kind']=='dense' else ck.sparse_layer)(partial,j);commit(key,time.process_time()-start,dict(entries_checked=ck.checks,not_a_complete_certificate=True))
  if 'partial_current' not in done:
   ck=Checker(w,p,v,c);start=time.process_time()
   if partial['kind']=='dense':
    table=dict(partial);table['layers']=partial['layers']+[partial.get('current_layer',[])];ck.dense_layer(table,len(table['layers'])-1,complete=False)
   else:
    j=partial['cursor']['prefix'];previous=partial['layers'][-1]
    current=partial.get('current',{});rows=list(current.values()) if isinstance(current,dict) else current
    for W,S,P,M,pr in rows:
     ck.guard();ck.witness(j,W,P,M,S);i,inc=pr;assert i in previous['retained'];z=previous['raw'][i]
     assert (W,S,P,M)==((z[0]+w[j-1],z[1]+v[j-1],z[2]+p[j-1],z[3]|1<<(j-1)) if inc else tuple(z[:4]))
   commit('partial_current',time.process_time()-start,dict(verified=True,not_a_complete_certificate=True))
 cert=path['frontier']
 if cert:
  for ti,table in enumerate(cert['tables']):
   for j in range(len(table['layers'])):
    key=f'table:{ti}:layer:{j}'
    if key in done:continue
    ck=Checker(w,p,v,c);start=time.process_time();(ck.dense_layer if table['kind']=='dense' else ck.sparse_layer)(table,j);commit(key,time.process_time()-start,dict(entries_checked=ck.checks))
  if 'terminal' not in done:
   ck=Checker(w,p,v,c);start=time.process_time();details=ck.terminal(cert);details['integer_samples']=check_samples(w,p,v,c,cert);commit('terminal',time.process_time()-start,details)
 m=row['packing'];proof=row['initial_proof'];t=0
 for i,ph in enumerate(path['phases']):
  key=f'phase:{i}'
  if key not in done:
   start=time.process_time();a=Auditor(w,p,v,c)
   if ph['kind']=='scalar':
    batches=audit_phase(row,ph,proof,t,0,out.parent/(out.stem+'-phase-'+str(i)+'.json'));details=dict(batches=len(batches))
   else:
    target=H.value(p,m)+t*H.value(v,m);assert target==independent_dp(w,[x+t*y for x,y in zip(p,v)],c)
    loss=a.loss(t,m)
    if ph.get('boundary') is None:assert loss==ph['loss']
    else:
     boundary=ph['boundary']
     if loss is not None and loss<boundary or ph['loss'] is not None and ph['loss']<boundary:assert loss==ph['loss']
    a.cover(proof)
    # Stored scalar proof can have an older anchor while frontier is active.
    if ph['status']=='packing_lost':assert H.value(w,ph['witness'])<=c and H.value(p,ph['witness'])+ph['final_time']*H.value(v,ph['witness'])>H.value(p,m)+ph['final_time']*H.value(v,m)
    if ph['status']=='factor_handoff':
     b=Fraction(*path['frontier']['alpha']);boundary=ph['boundary'];assert 1+b*(boundary-1)>0 and 1+b*boundary<=0
     event=ph['handoff'];tt=event['time'];q=[x+tt*y for x,y in zip(p,v)];rr=event['result']
     # Exact independently priced bound checks at original integer profits.
     from audit_renewal import fractional_bound
     for call in event['calls']:
      if call['priced'] is not None:
       cell=call['priced'];assert H.numerator(cell,w,q,[0]*len(w),0)==cell[5] and Fraction(cell[5],cell[4])==fractional_bound(cell,w,q)
     if rr.get('success'):a.cover(rr['proof']);a.prices(rr['proof'],tt,m)
     elif not rr.get('incomplete'):assert H.value(w,rr['witness'])<=c and H.value(q,rr['witness'])>H.value(q,m)
    details=dict(horizon_checked=True)
   if 'replacement' in ph:
    opt=ph['replacement'];tt=ph['final_time'];mm=opt['packing'];assert opt['objective']==independent_dp(w,[x+tt*y for x,y in zip(p,v)],c)==H.value(p,mm)+tt*H.value(v,mm);a.cover(opt['proof']);a.prices(opt['proof'],tt,mm);assert opt['empty']
   commit(key,time.process_time()-start,details)
  if 'replacement' in ph:m=ph['replacement']['packing'];proof=ph['replacement']['proof'];t=ph['final_time']
  elif ph.get('handoff') and ph['handoff']['result'].get('success'):proof=ph['handoff']['result']['proof'];t=ph['final_time']
 save(out,dict(passed=True,records=records,pending=None,audit_cpu=sum(x['cpu'] for x in records)))

def cumulative(path,key):
 arr=[0.0]*(257);arr[0]=path['initial_cpu'] if key=='algorithm_cpu' else 0
 for e in path['ledger']:arr[min(256,e['time'])]+=e.get('algorithm_cpu',0) if key=='algorithm_cpu' else e['counters'].get(key,0)
 if key=='algorithm_cpu':arr[256]+=path['algorithm_cpu']-sum(arr)
 for t in range(1,257):arr[t]+=arr[t-1]
 return arr

def summary(rows):
 modes={};comparisons=[];keys=['bound_evaluations','free_term_evaluations','dp_entries','dp_transitions','dominance_comparisons','algorithm_cpu']
 for row in rows:
  base=row['paths'][0]
  for path in row['paths'][1:]:
   measures={}
   for key in keys:
    b,z=cumulative(base,key),cumulative(path,key);diff=[x-y for x,y in zip(b,z)];pos=[t for t,x in enumerate(diff) if x>0];lastbad=max((t for t,x in enumerate(diff) if x<=0),default=-1);times=sorted({0,64,128,256}|{e['time'] for p in (base,path) for e in p['ledger']})
    measures[key]=dict(saving=diff[-1],initial_debt=max(0,z[0]-b[0]),first_advantage=pos[0] if pos else None,persistent_advantage=lastbad+1 if diff[-1]>0 else None,ledgers=[dict(time=t,baseline=b[t],candidate=z[t]) for t in times])
   comparisons.append(dict(case_id=row['case_id'],mode=path['mode'],paired=base['status']!='capped' and path['status']!='capped',recognized=path['dispatch'] not in ('scalar','construction_fallback'),measures=measures))
 for name in [p['mode'] for p in rows[0]['paths']]:
  paths=[next(p for p in r['paths'] if p['mode']==name) for r in rows];tot=counts()
  for p in paths:E.plus(tot,p['totals'])
  cm=[x for x in comparisons if x['mode']==name and x['paired']];stats={}
  for key in keys:
   savings=[x['measures'][key]['saving'] for x in cm];largest=max(savings,default=0);stats[key]=dict(pairs=len(cm),saving=sum(savings),benefited=sum(x>0 for x in savings),harmed=sum(x<0 for x in savings),tied=sum(x==0 for x in savings),without_largest=sum(savings)-largest,excluding_recognized=sum(x['measures'][key]['saving'] for x in cm if not x['recognized']),distribution=savings)
  modes[name]=dict(complete=sum(p['status']!='capped' for p in paths),capped=sum(p['status']=='capped' for p in paths),totals=tot,algorithm_cpu=sum(p['algorithm_cpu'] for p in paths),optimizer_cpu=sum(p['optimizer_cpu'] for p in paths),optimizer_search_steps=sum(p['optimizer_search_steps'] for p in paths),switches=sum(p['switches'] for p in paths),construction_cpu=sum(p['construction_cpu'] for p in paths),construction_caps=sum(p['partial_frontier'] is not None for p in paths),recognized=sum(p['frontier'] is not None for p in paths),comparisons=stats)
 return dict(cases=len(rows),modes=modes,comparisons=comparisons)

def run_split(stage,split,out):
 rows=inputs(stage,split,out/split/'sources');save(out/split/'Inputs.json',rows);names=specs(stage);result=[];batch_start=time.perf_counter();batch=0
 for idx,row in enumerate(rows):
  f=out/split/'cases'/(row['case_id']+'.json');af=out/split/'audits';cache={}
  if f.exists():row=read(f)
  else:
   row['paths']=[]
   for name,pol in names:
    save(out/split/'Cursor.json',dict(case=row['case_id'],case_index=idx,policy=name,status='computing',unstarted=[r['case_id'] for r in rows[idx+1:]]))
    path=run_policy(row,name,pol,cache);save(out/split/'path-results'/(row['case_id']+'-'+name+'.json'),path);row['paths'].append(path);row['optimizer_cache']={str(k):v for k,v in cache.items()};save(f,row)
  # Cases are fully committed before any audit. Resume skips existing policy paths.
  if len(row['paths'])<len(names):
   cache={int(k):v for k,v in row.get('optimizer_cache',{}).items()}
   for name,pol in names[len(row['paths']):]:
    pf=out/split/'path-results'/(row['case_id']+'-'+name+'.json');path=read(pf) if pf.exists() else run_policy(row,name,pol,cache);save(pf,path);row['paths'].append(path);save(f,row)
  row['optimizer_cache']={str(k):v for k,v in cache.items()};save(f,row)
  for path in row['paths']:
   audit_file=af/(row['case_id']+'-'+path['mode']+'.json');audit_path(row,path,audit_file);assert read(audit_file)['passed']
  result.append(row)
  save(out/split/'Cursor.json',dict(status='running' if idx+1<len(rows) else 'all_attempted',completed_cases=idx+1,unstarted=[r['case_id'] for r in rows[idx+1:]],pending_audit=None))
  if time.perf_counter()-batch_start>=900:
   save(out/split/f'Batch-{batch}.json',dict(seconds=time.perf_counter()-batch_start,next_case=idx+1,bounded_continuation=True));batch+=1;batch_start=time.perf_counter()
  if idx%8==7:print('PROGRESS',stage,split,idx+1,'/',len(rows),flush=True)
 sm=summary(result);save(out/split/'Summary.json',sm)
 pending=[dict(case_id=r['case_id'],policy=p['mode'],cursor=p['pending'],totals=p['totals']) for r in result for p in r['paths'] if p['status']=='capped']
 construction_caps=[dict(case_id=r['case_id'],policy=p['mode'],partial_file=f'cases/{r["case_id"]}.json',field='paths[policy].partial_frontier',cursor=p['partial_frontier'].get('cursor'),status='incomplete_construction_with_scalar_fallback',trajectory_status=p['status']) for r in result for p in r['paths'] if p['partial_frontier'] is not None]
 save(out/split/'Resource-log.json',dict(construction_caps=construction_caps,limits=E.LIMITS,frontier_limits=dict(entries=500000,transitions=2000000,dominance_comparisons=5000000),capped_paths=pending,unstarted=[],pending_audit=None));save(out/split/'Resume-cursors.json',dict(incomplete_constructions=construction_caps,capped_paths=pending,unstarted=[],pending_audit=None));save(out/split/'Audit.json',dict(passed=True,cases=len(rows),paths=sum(len(r['paths']) for r in result)))
 return sm,result

def timings(stage,rows,out):
 selected=[r for r in rows if r['n']==12 and r['family'] in ('random','negative')];result=[]
 for rep in range(3):
  aggregate={name:0. for name,pol in specs(stage)};caps=[]
  for original in selected:
   row={k:v for k,v in original.items() if k not in ('paths','optimizer_cache')};row['source']=solve(row['weights'],row['profits'],row['capacity']);row['packing']=row['source']['packing'];row['initial_proof']=row['source']['proof'];cache={};row['paths']=[]
   for name,pol in specs(stage):
    path=run_policy(row,name,pol,cache);save(out/'timing'/f'rep{rep}-{row["case_id"]}-{name}.json',path);row['paths'].append(path)
    expected=next(x for x in original['paths'] if x['mode']==name)
    assert path['status']==expected['status'] and path['optimizer_search_steps']==expected['optimizer_search_steps'] and path['switches']==expected['switches']
    assert all(path['totals'][k]==expected['totals'][k] for k in path['totals'] if not k.endswith('cpu'))
    if path['status']=='capped':caps.append(dict(case_id=row['case_id'],policy=name))
    else:aggregate[name]+=path['algorithm_cpu']
   save(out/'timing'/f'rep{rep}-{row["case_id"]}.json',row)
  result.append(dict(repetition=rep,aggregate_cpu=aggregate,capped=caps));print('TIMING',stage,rep,aggregate,flush=True)
 score={name:statistics.median(x['aggregate_cpu'][name] for x in result) if not any(any(y['policy']==name for y in x['capped']) for x in result) else None for name,pol in specs(stage)}
 save(out/'Timing.json',dict(subset=[x['case_id'] for x in selected],repetitions=result,score=score,selection_split='development',fresh_state=True))
 names=['affine_pair','two_class'];eligible=[n for n in names if score[n] is not None];candidate=min(eligible,key=lambda n:(score[n],n)) if eligible else 'affine_pair';preferred=candidate if score[candidate] is not None and score['maintain'] is not None and score[candidate]<score['maintain'] else 'maintain'
 save(out/'Selection.json',dict(candidate=candidate,reference=preferred,basis='median three aggregate end-to-end CPU repetitions on declared eight development cases',scores=score,status='preferred_on_development' if preferred!='maintain' else 'hypothesis_only',sealed_before_stage35=True))

PROOF_TEXT='''Complete recurrence induction accounts for exclude and feasible include packings at each prefix, with unreachable classes explicit. A maximum intercept for a fixed cardinality/count/slope bounds all packings in that group, and its predecessor mask attains it. Uniform slopes give A_k+gamma*k*t. Affine slopes give (1+alpha*t)*P+beta*k*t: maximize P when the factor is positive, minimize P when negative, and any feasible intercept when zero. Maximizing over both extrema therefore gives the exact global optimum for every sign; every line is feasible. Count-vector lines have slope sum(gamma_j*k_j); exact slope states group by their actual integer sum(v). These completed unpruned certificates are valid for all t>=0 (max-only only in its positive domain). For endpoint pruning at the same prefix, a lighter state with both endpoint values at least those of the deleted state dominates throughout [0,256] by affinity and permits every identical remaining-item completion. Witness edges point to retained states and are acyclic. This proof has no implication beyond 256 for the pruned format. Tables, masks, grouping, crossings and every dominance witness are independently checked. These are elementary parametric optimization constructions, with potentially exponential slope-state width, and no new arithmetic claim.'''
def freeze(stage,out):
 if (out/'Frozen.json').exists():
  for f,h in read(out/'Frozen.json').items():assert hashlib.sha256((out/f).read_bytes()).hexdigest()==h
  return
 out.mkdir(parents=True,exist_ok=True);shutil.copytree(ROOT/'code',out/'code',ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
 (out/'Protocol.md').write_text(f'# Experiment {stage}\n\n'+(ROOT/'Handoff.md').read_text()+f'\n\nFixed policies: {specs(stage)}. Construction-cap fallback discards the incomplete frontier and uses the last full scalar partition. Any overall wall cap leaves the trajectory incomplete. Deterministic DP ties keep the first transition; pruning equal endpoints retains the first sorted state. Max/min omits min only when alpha>=0. No per-held-case tuning. CPU descriptive except stage34 development selection; no held-out runtime advantage claim. Stage34 predeclares 3 repeats of 8 n12 random/negative development trajectories; scores are median aggregate full CPU and capped methods ineligible. Audit batches are one layer or at most four scalar events, each <=45 seconds; 900-second outer batches checkpoint then continue.\n\n'+PROOF_TEXT)
 # Fixtures run before freeze.
 import fixtures
 fixtures.run(stage,out)
 save(out/'Frozen.json',{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'code').glob('*.py')}|{'Protocol.md':hashlib.sha256((out/'Protocol.md').read_bytes()).hexdigest()})
def report(stage,dev,held,out):
 lines=[f'# Experiment {stage}: results','',f'32 development and 96 held-out unique trajectories; all policy paths attempted and independently audited. Unlike work units remain separate. Full counters and paired common-time debt/payback are in Summary.json. CPU outside stage34 selection is descriptive; no held-out runtime advantage is claimed.','', '| Policy | Complete / 96 | Candidate evaluations | DP entries | DP transitions | Dominance comparisons | Switches | Charged CPU seconds |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name,z in held['modes'].items():
  t=z['totals'];lines.append(f'| {name} | {z["complete"]} | {t["bound_evaluations"]:,} | {t["dp_entries"]:,} | {t["dp_transitions"]:,} | {t["dominance_comparisons"]:,} | {z["switches"]} | {z["algorithm_cpu"]:.6f} |')
 lines+=['','| Comparison vs maintenance | Completed pairs | Candidate saving | Benefited / harmed / tied | Saving without largest beneficiary |','|---|---:|---:|---:|---:|']
 for name,z in held['modes'].items():
  if name=='maintain':continue
  a=z['comparisons']['bound_evaluations'];lines.append(f'| {name} | {a["pairs"]} | {a["saving"]:,} | {a["benefited"]} / {a["harmed"]} / {a["tied"]} | {a["without_largest"]:,} |')
 lines+=['',PROOF_TEXT,'','Preparation is charged at time zero; scalar expiry detection includes failed detection and optimizer replacement. Price counts, DP work and dominance work cannot be summed into a speedup. Common-time CPU includes event costs and remaining driver/recognition/horizon bookkeeping at observation end, so intermediate CPU payback is a conservative ledger description rather than clean continuous wall sampling. All initialization/native optimizer costs are charged fully to each policy despite physical sharing. Serialization and audit are outside algorithm CPU and separately saved.']
 (out/'Report.md').write_text('\n'.join(lines)+'\n')
def main():
 for stage in [int(x) for x in sys.argv[1:]]:
  out=ROOT/'stages'/str(stage)
  if (out/'Complete.json').exists():print('SKIP',stage,flush=True);continue
  freeze(stage,out);dev,devrows=run_split(stage,'development',out)
  if stage==34:timings(stage,devrows,out)
  freeze(stage,out);held,heldrows=run_split(stage,'held',out);freeze(stage,out);report(stage,dev,held,out)
  caps=sum(x['capped'] for x in dev['modes'].values())+sum(x['capped'] for x in held['modes'].values());save(out/'Complete.json',dict(status='completed' if not caps else 'capped',all_cases_attempted=True,all_policy_paths_complete=not caps,development=32,held=96,capped_paths=caps,audit_passed=True))
  save(out/'Serialization-accounting.json',dict(excluded_from_algorithm=True,records=[m for m in SAVE_METRICS if str(out) in m['path']]))
  print('STAGE COMPLETE',stage,{k:{'complete':z['complete'],'evaluations':z['totals']['bound_evaluations'],'dp_entries':z['totals']['dp_entries']} for k,z in held['modes'].items()},flush=True)
if __name__=='__main__':main()
