"""Guarded common exact kernel and prospective forest; no audit oracle imports."""
from fractions import Fraction
import time,copy
import horizon as H
import refine as RF

class Cap(Exception):pass
LIMITS=dict(cells=4096,evaluations=2000000,trajectory_seconds=120,source_steps=500000,source_cells=4096,source_seconds=30,audit_seconds=45)
COUNT_KEYS=('price_calls','bound_evaluations','free_term_evaluations','splits','probes','hits','eligible','skipped','selection_visits','selection_comparisons','lineage_ops','recognition_terms','horizon_evaluations','maintenance_events')
TIME_KEYS=('kernel_cpu','horizon_cpu','policy_cpu','algorithm_cpu','recognition_cpu')
def empty_counts():return {k:0 for k in COUNT_KEYS+TIME_KEYS}
def plus(a,b):
 for k,v in b.items():a[k]=a.get(k,0)+v

def normalized_certificate(w,p,v,c,m,proof,factor=(1,1),interval=(0,None)):
 a,d=factor;left,right=interval
 if not all(vi==pi for pi,vi in zip(p,v)) or len(v)!=len(p):raise ValueError('not v=p')
 if factor!=(1,1) or interval!=(0,None):raise ValueError('unsupported factor or interval')
 if a+d*left<=0 or (right is not None and a+d*right<=0) or (right is None and d<0):raise ValueError('nonpositive factor')
 for cell in proof:
  if H.numerator(cell,w,p,[0]*len(p),0)!=cell[5] or cell[5]//cell[4]>H.value(p,m):raise ValueError('invalid base certificate')
 return dict(kind='positive_factor_v_equals_p',factor=dict(intercept=a,slope=d,interval=[left,right]),base_proof=copy.deepcopy(proof),base_packing=m,base_profits=p,first_failure=None)

class Forest:
 def __init__(self,proof,ct):
  self.nodes={};self.active=[];self.next_id=0
  for cell in proof:self.active.append(self.add(cell[:3],ct))
 def add(self,domain,ct):
  i=self.next_id;self.next_id+=1;self.nodes[i]=dict(domain=list(domain),children=None);ct['lineage_ops']+=1;return i
 def split(self,i,pivot,w,ct):
  f,u,r=self.nodes[i]['domain'];bit=1<<pivot;doms=[[f,u^bit,r]]
  if w[pivot]<=r:doms.append([f|bit,u^bit,r-w[pivot]])
  children=[self.add(x,ct) for x in doms];self.nodes[i]['children']=children;ct['lineage_ops']+=1;return children
 @classmethod
 def restore(cls,snap):
  obj=cls.__new__(cls);obj.nodes={int(k):copy.deepcopy(v) for k,v in snap['nodes'].items()};obj.active=snap['active'].copy();obj.next_id=snap['next_id'];return obj
 def snapshot(self):return dict(nodes=copy.deepcopy(self.nodes),active=self.active.copy(),next_id=self.next_id)
 def descendants(self,i,active,ct):
  ct['selection_visits']+=1
  if i in active:return [i]
  ch=self.nodes[i]['children']
  if ch is None:return None
  out=[]
  for j in ch:
   z=self.descendants(j,active,ct)
   if z is None:return None
   out.extend(z)
  return out
 def candidates(self,ct):
  active=set(self.active);rows=[]
  for i in self.nodes:
   ct['selection_visits']+=1
   if i in active or self.nodes[i]['children'] is None:continue
   leaves=self.descendants(i,active,ct)
   if leaves is not None and len(leaves)>1:rows.append((i,leaves))
  # Deterministic insertion sort, exposing comparisons separately from pricing.
  def key(x):return (-len(x[1]),*self.nodes[x[0]]['domain'],x[0])
  ordered=[]
  for row in rows:
   j=len(ordered);ordered.append(row)
   while j:
    ct['selection_comparisons']+=1
    if key(ordered[j-1])<=key(row):break
    ordered[j]=ordered[j-1];j-=1
   ordered[j]=row
  return ordered
 def merge(self,i,leaves,proof,priced,ct):
  leaves=set(leaves);out=[];ids=[];inserted=False
  for j,cell in zip(self.active,proof):
   ct['lineage_ops']+=1
   if j in leaves:
    if not inserted:out.append(priced);ids.append(i);inserted=True
   else:out.append(cell);ids.append(j)
  # Remove superseded descendants; parent can split afresh prospectively.
  def prune(j):
   for k in self.nodes[j]['children'] or []:prune(k)
   del self.nodes[j];ct['lineage_ops']+=1
  for j in self.nodes[i]['children'] or []:prune(j)
  self.nodes[i]['children']=None;self.active=ids;return out

class Work:
 def __init__(self,w,q,m,totals,deadline,spent=0):self.w=w;self.q=q;self.m=m;self.ct=empty_counts();self.calls=[];self.totals=totals;self.deadline=deadline;self.spent=spent
 def guard(self):
  if self.spent+self.totals['bound_evaluations']+self.ct['bound_evaluations']>=LIMITS['evaluations']:raise Cap('candidate evaluation cap')
  if time.perf_counter()>=self.deadline:raise Cap('trajectory wall cap')
 def price(self,cell,kind):
  start=time.process_time();f,u,r,*_=cell;candidates={Fraction(0)}
  for i in range(len(self.w)):
   if u>>i&1 and self.q[i]>0:candidates.add(Fraction(self.q[i],self.w[i]))
  call=dict(domain=[f,u,r],kind=kind,candidates=len(candidates),evaluated=0,priced=None);self.calls.append(call);self.ct['price_calls']+=1
  best=None
  try:
   for price in sorted(candidates):
    self.guard();a,b=price.numerator,price.denominator
    z=b*H.value(self.q,f)+a*r+sum(max(0,b*self.q[i]-a*self.w[i]) for i in range(len(self.w)) if u>>i&1)
    self.ct['bound_evaluations']+=1;self.ct['free_term_evaluations']+=u.bit_count();call['evaluated']+=1
    score=(Fraction(z,b),price,z)
    if best is None or score<best:best=score
   bound,price,z=best;out=[f,u,r,price.numerator,price.denominator,z];call['priced']=out;return out
  finally:self.ct['kernel_cpu']+=time.process_time()-start
 def repair(self,proof,forest=None,reuse=None):
  target=H.value(self.q,self.m);reuse=reuse or {};renewed=[];trace=[];self.repair_trace=trace;self.partial_repair=dict(renewed=renewed,returned=[],pending=[])
  for cell in proof:renewed.append(reuse.get(tuple(cell[:3])) or self.price(cell,'renew'))
  out=[];ids=[];origins=[];max_depth=0;self.partial_repair['returned']=out
  oldids=forest.active.copy() if forest else [None]*len(proof)
  for origin,root in enumerate(renewed):
   stack=[(root,oldids[origin],0,True)]
   while stack:
    self.partial_repair['pending']=stack;self.guard();cell,ident,depth,isroot=stack.pop();max_depth=max(max_depth,depth)
    if isroot and cell[5]//cell[4]<=target:priced=cell
    else:priced=self.price(cell,'repair')
    if priced[5]//priced[4]<=target:
     out.append(priced);ids.append(ident);origins.append(origin)
     if len(out)>LIMITS['cells']:raise Cap('returned cell cap')
     continue
    c0=time.process_time();witness,pivot=RF.greedy(priced,self.w,self.q);self.ct['kernel_cpu']+=time.process_time()-c0
    if pivot is None:
     assert H.value(self.q,witness)>target
     return dict(success=False,witness=witness,trace=trace,splits=len(trace),max_depth=max_depth)
    f,u,r,*_=priced;bit=1<<pivot;children=[[f,u^bit,r]]
    if self.w[pivot]<=r:children.append([f|bit,u^bit,r-self.w[pivot]])
    if forest:
     c0=time.process_time();child_ids=forest.split(ident,pivot,self.w,self.ct);self.ct['policy_cpu']+=time.process_time()-c0
    else:child_ids=[None]*len(children)
    trace.append(dict(origin=origin,node=ident,depth=depth,domain=[f,u,r],pivot=pivot,children=children,child_ids=child_ids));self.ct['splits']+=1
    stack.extend((d+[0,1,0],i,depth+1,False) for d,i in reversed(list(zip(children,child_ids))))
    if len(stack)+len(out)>LIMITS['cells']:raise Cap('pending cell cap')
  if forest:forest.active=ids
  return dict(success=True,proof=out,origins=origins,trace=trace,splits=len(trace),max_depth=max_depth)

def probe(work,proof,forest,strategy):
 ct=work.ct;target=H.value(work.q,work.m);logs=[];reuse={};hit=False
 if strategy.startswith('root'):
  root=[0,(1<<len(work.w))-1,0,0,1,0] # residual filled by caller from any old cell
  root[2]=proof[0][2]+H.value(work.w,proof[0][0]);ct['probes']+=1
  priced=work.price(root,'probe_root');success=priced[5]//priced[4]<=target
  logs.append(dict(kind='root',success=success,prior_cells=len(proof),priced=priced))
  if success:
   ct['hits']+=1;hit=True;proof=[priced];reuse[tuple(priced[:3])]=priced
   if forest:forest=Forest(proof,ct)
 else:
  budget=len(work.w)+1;used=0;attempted=set()
  while True:
   c0=time.process_time();candidates=forest.candidates(ct);ct['policy_cpu']+=time.process_time()-c0
   choice=None
   for i,leaves in candidates:
    ct['selection_visits']+=1
    if i in attempted:continue
    cost=forest.nodes[i]['domain'][1].bit_count()+1
    if cost<=budget-used:choice=(i,leaves,cost);break
   if choice is None:break
   i,leaves,cost=choice;used+=cost;attempted.add(i);ct['probes']+=1;domain=forest.nodes[i]['domain'];priced=work.price(domain+[0,1,0],'probe_local');success=priced[5]//priced[4]<=target
   logs.append(dict(kind='local',node=i,leaves=leaves,reserved=cost,success=success,priced=priced))
   if success:
    c0=time.process_time();proof=forest.merge(i,leaves,proof,priced,ct);ct['policy_cpu']+=time.process_time()-c0
    ct['hits']+=1;hit=True;reuse[tuple(priced[:3])]=priced
  assert used<=budget
 return proof,forest,reuse,logs,hit

def run(w,p,v,c,m,initial,spec,end=64,normalization=False,phase_start=0,spent=0,elapsed=0,resume_forest=None,resume_cooldown=0):
 cpu0=time.process_time();wall0=time.perf_counter();proof=copy.deepcopy(initial);t=phase_start;events=[];horizon_ledger=[];total=empty_counts();forest=None;cooldown=resume_cooldown;peak=len(proof);peak_nodes=0
 strategy=spec.get('strategy','maintain');cool=spec.get('cooldown',0)
 if normalization:
  r0=time.process_time();total['recognition_terms']=len(p);recognized=len(p)==len(v) and all(a==b for a,b in zip(p,v));total['recognition_cpu']=time.process_time()-r0
  if recognized:
   cert=normalized_certificate(w,p,v,c,m,proof);total['algorithm_cpu']=time.process_time()-cpu0
   return dict(mode=spec['name'],spec=spec,status='normalized_forever',final_time=end,last_verified_time=t,events=[],final_proof=proof,final_certificate=cert,packing=m,totals=total,peak_cells=peak,peak_nodes=0,wall=time.perf_counter()-wall0)
 if strategy=='local':
  r0=time.process_time();forest=Forest(proof,total) if resume_forest is None else Forest.restore(resume_forest);total['policy_cpu']+=time.process_time()-r0;peak_nodes=len(forest.nodes)
 deadline=wall0+max(0,LIMITS['trajectory_seconds']-elapsed)
 while True:
  q=[a+t*b for a,b in zip(p,v)];r0=time.process_time();cert=H.certificate_horizon(proof,w,q,v,m);hc=time.process_time()-r0;total['horizon_cpu']+=hc;horizon_ledger.append(dict(time=t,algorithm_cpu=hc));total['horizon_evaluations']+=cert['evaluations'];dt=cert['first_failure']
  def finish(status,final_time,reason=None):
   total['algorithm_cpu']=time.process_time()-cpu0
   return dict(mode=spec['name'],spec=spec,status=status,reason=reason,final_time=final_time,last_verified_time=t,events=events,horizon_ledger=horizon_ledger,final_proof=proof,final_certificate=cert,packing=m,totals=total,peak_cells=peak,peak_nodes=peak_nodes,final_forest=None if forest is None else forest.snapshot(),final_cooldown=cooldown,wall=time.perf_counter()-wall0)
  if dt is None:return finish('forever_certified',end)
  nt=t+dt
  if nt>end:return finish('window_complete',end)
  event_cpu=time.process_time();q1=[a+nt*b for a,b in zip(p,v)];work=Work(w,q1,m,total,deadline,spent);work.ct['maintenance_events']=1;prior_forest=forest.snapshot() if forest else None
  domain=proof;wf=copy.deepcopy(forest);reuse={};logs=[];hit=False;skipped=False;eligible=False;before_cool=cooldown
  try:
   work.guard();r0=time.process_time()
   if strategy=='root_all':eligible=len(proof)>1
   elif strategy=='root_gated':eligible=len(proof)>=len(w)+1
   elif strategy=='local':eligible=bool(wf.candidates(work.ct))
   work.ct['policy_cpu']+=time.process_time()-r0
   if eligible:
    work.ct['eligible']+=1
    if cooldown>0:cooldown-=1;skipped=True;work.ct['skipped']+=1
    else:
     domain,wf,reuse,logs,hit=probe(work,domain,wf,strategy)
     if logs:cooldown=0 if hit else cool
   if strategy=='rebuild':domain=[[0,(1<<len(w))-1,c,0,1,0]]
   result=work.repair(domain,wf,reuse)
  except Cap as exc:
   result=dict(success=False,incomplete=True,reason=str(exc),trace=getattr(work,'repair_trace',[]),partial_repair=getattr(work,'partial_repair',None))
  event=dict(time=nt,previous_time=t,packing=m,previous_certificate=cert,prior_cells=len(proof),eligible=eligible,skipped=skipped,cooldown_before=before_cool,cooldown_after=cooldown,probes=logs,calls=work.calls,result=result,counters=work.ct,forest_before=prior_forest,forest_after=wf.snapshot() if wf else None)
  event['event_cpu']=time.process_time()-event_cpu;events.append(event);plus(total,work.ct)
  if wf:peak_nodes=max(peak_nodes,len(wf.nodes))
  if result.get('incomplete'):return finish('capped',nt,result['reason'])
  if not result['success']:return finish('packing_lost',nt)
  proof=result['proof'];forest=wf;t=nt;peak=max(peak,len(proof))
  assert len(events)<=end-phase_start
