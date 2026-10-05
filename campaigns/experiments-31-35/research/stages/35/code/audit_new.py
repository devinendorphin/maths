"""Independent saved-evidence audits. Enumeration and DP are audit-only."""
from fractions import Fraction
import time
from engine import Cap,LIMITS
import horizon as H
import flat_baseline as F
from audit_horizon import rational_horizon
from audit_renewal import fractional_bound

class Auditor:
 def __init__(self,w,p,v,c):
  self.deadline=time.perf_counter()+LIMITS['audit_seconds'];self.w,self.p,self.v,self.c=w,p,v,c;self.n=len(w);N=1<<self.n
  self.weights=[0]*N;self.intercepts=[0]*N;self.slopes=[0]*N;self.feasible=[];self.feas_bits=0;self.cache={};self.cover_cache=set();self.price_cache={};self.checks=dict(covers=0,cells=0,horizons=0,price_calls=0,forests=0,witnesses=0,normalized_samples=0,optimizer_solves=0)
  for m in range(N):
   if m:
    bit=m&-m;j=bit.bit_length()-1;prev=m^bit
    self.weights[m]=self.weights[prev]+w[j];self.intercepts[m]=self.intercepts[prev]+p[j];self.slopes[m]=self.slopes[prev]+v[j]
   if self.weights[m]<=c:self.feasible.append(m);self.feas_bits|=1<<m
 def guard(self):
  if time.perf_counter()>self.deadline:raise Cap('independent audit batch wall cap')
 def domain(self,d):
  self.guard()
  f,u,r=d[:3];key=(f,u,r)
  assert f&u==0 and (f|u)<1<<self.n and r==self.c-self.weights[f] and r>=0
  if key not in self.cache:
   bits=0;s=u
   while True:
    m=f|s
    if self.weights[m]<=self.c:bits|=1<<m
    if not s:break
    s=(s-1)&u
   self.cache[key]=bits
  return self.cache[key]
 def cover(self,proof):
  key=tuple(tuple(x[:3]) for x in proof)
  if key in self.cover_cache:return
  got=0
  for cell in proof:
   z=self.domain(cell);assert not got&z;got|=z
  assert got==self.feas_bits;self.cover_cache.add(key);self.checks['covers']+=1
 def prices(self,proof,t,m,minimal=True):
  q=[a+t*b for a,b in zip(self.p,self.v)];target=self.intercepts[m]+t*self.slopes[m]
  for cell in proof:
   f,u,r,a,b,z=cell;self.domain(cell);assert a>=0 and b>0
   expected=b*sum(q[i] for i in range(self.n) if f>>i&1)+a*r+sum(max(0,b*q[i]-a*self.w[i]) for i in range(self.n) if u>>i&1)
   assert expected==z and z//b<=target
   if minimal:assert Fraction(z,b)==fractional_bound(cell,self.w,q)
   self.checks['cells']+=1
  assert F.dp(self.w,q,self.c)==target
 def cert(self,proof,t,m,cert):
  q=[a+t*b for a,b in zip(self.p,self.v)];hs=[rational_horizon(x,self.w,q,self.v,m) for x in proof]
  assert hs==cert['cell_horizons'];finite=[x for x in hs if x is not None];assert cert['first_failure']==(min(finite) if finite else None);self.checks['horizons']+=len(hs)
 def loss(self,t,m):
  target=self.intercepts[m]+t*self.slopes[m];candidates=[]
  for mask in self.feasible:
   A=self.intercepts[mask]+t*self.slopes[mask];assert A<=target
   d=self.slopes[mask]-self.slopes[m]
   if d>0:candidates.append(t+(target-A)//d+1)
  return min(candidates) if candidates else None
 def forest(self,snap,proof):
  if snap is None:return
  nodes={int(k):v for k,v in snap['nodes'].items()};active=snap['active'];assert len(active)==len(proof)==len(set(active));parents={}
  for ident,node in nodes.items():
   parent=self.domain(node['domain']);children=node['children']
   if children:
    got=0
    for child in children:
     assert child in nodes and child not in parents;parents[child]=ident;z=self.domain(nodes[child]['domain']);assert not got&z;got|=z
    assert got==parent
  for i,cell in zip(active,proof):assert nodes[i]['domain']==list(cell[:3]) and nodes[i]['children'] is None
  # No fabricated cross-root ancestors; each active node's root exists and forest is acyclic.
  for i in active:
   seen=set()
   while i in parents:assert i not in seen;seen.add(i);i=parents[i]
  self.checks['forests']+=1
 def normalized(self,path,m):
  cert=path['final_certificate'];assert cert['kind']=='positive_factor_v_equals_p' and cert['factor']==dict(intercept=1,slope=1,interval=[0,None]);assert self.p==self.v
  assert cert['base_profits']==self.p and cert['base_packing']==m;proof=cert['base_proof'];self.cover(proof);self.prices(proof,0,m)
  for t in (0,1,2,64,256,1024,1000000):
   g=1+t;q=[g*x for x in self.p];assert F.dp(self.w,q,self.c)==g*self.intercepts[m]
   for cell in proof:
    f,u,r,a,b,z=cell;price=Fraction(g*a,b);aa,bb=price.numerator,price.denominator
    zz=bb*sum(q[i] for i in range(self.n) if f>>i&1)+aa*r+sum(max(0,bb*q[i]-aa*self.w[i]) for i in range(self.n) if u>>i&1)
    assert Fraction(zz,bb)==g*Fraction(z,b) and zz//(bb*g)<=self.intercepts[m]
   self.checks['normalized_samples']+=1
 def path(self,path,m,initial,start,end,resume_cooldown=0):
  self.cover(initial);self.prices(initial,start,m);old=initial;t0=start;cooldown=resume_cooldown;spec=path['spec'];strategy=spec.get('strategy','maintain');loss=self.loss(start,m)
  if path['status']=='normalized_forever':self.normalized(path,m);assert not path['events'];return
  totals={k:0 for k in ('price_calls','bound_evaluations','free_term_evaluations','splits','probes','hits','eligible','skipped','maintenance_events')}
  for e in path['events']:
   t=e['time'];assert e['previous_time']==t0 and e['packing']==m;self.cert(old,t0,m,e['previous_certificate']);assert t==t0+e['previous_certificate']['first_failure'];self.forest(e['forest_before'],old)
   q=[a+t*b for a,b in zip(self.p,self.v)];target=self.intercepts[m]+t*self.slopes[m];ct=e['counters'];calls=e['calls']
   assert ct['price_calls']==len(calls);bounds=0;terms=0
   for call in calls:
    self.guard()
    f,u,r=call['domain'];self.domain(call['domain']);ratios={Fraction(0)}|{Fraction(q[i],self.w[i]) for i in range(self.n) if u>>i&1 and q[i]>0};assert call['candidates']==len(ratios)
    assert 0<=call['evaluated']<=len(ratios);bounds+=call['evaluated'];terms+=call['evaluated']*u.bit_count()
    if call['priced'] is not None:
     assert call['evaluated']==len(ratios);priced=call['priced'];assert priced[:3]==call['domain'];a,b,z=priced[3:];assert b>0 and a>=0
     cache_key=(t,tuple(priced))
     if cache_key in self.price_cache:
      self.checks['price_calls']+=1
      continue
     expected=b*sum(q[i] for i in range(self.n) if f>>i&1)+a*r+sum(max(0,b*q[i]-a*self.w[i]) for i in range(self.n) if u>>i&1)
     assert expected==z and Fraction(z,b)==fractional_bound(priced,self.w,q)
     # Independently locate the left endpoint of the convex dual minimum using slope groups.
     # Exact fill permits the next (lower) ratio; zero remaining capacity uses the highest ratio.
     groups={}
     for i in range(self.n):
      if u>>i&1 and q[i]>0:
       ratio=Fraction(q[i],self.w[i]);groups[ratio]=groups.get(ratio,0)+self.w[i]
     remaining=r;left_price=Fraction(0)
     for ratio,weight in sorted(groups.items(),reverse=True):
      if remaining<weight:left_price=ratio;break
      remaining-=weight
     assert Fraction(a,b)==left_price
     self.price_cache[cache_key]=True
    self.checks['price_calls']+=1
   assert bounds==ct['bound_evaluations'] and terms==ct['free_term_evaluations'];assert ct['maintenance_events']==1
   eligible=len(old)>1 if strategy=='root_all' else len(old)>=self.n+1 if strategy=='root_gated' else e['eligible'] if strategy=='local' else False
   assert eligible==e['eligible'] and e['cooldown_before']==cooldown
   if eligible and cooldown:
    assert e['skipped'] and not e['probes'];cooldown-=1
   else:
    assert not e['skipped']
    if e['probes']:cooldown=0 if any(x['success'] for x in e['probes']) else spec.get('cooldown',0)
   assert e['cooldown_after']==cooldown
   probe_calls=[x for x in calls if x['kind'].startswith('probe')];assert ct['probes']==len(probe_calls)
   assert ct['hits']==sum(x['success'] for x in e['probes']) and ct['eligible']==int(eligible) and ct['skipped']==int(e['skipped'])
   domain=list(old);reserved=0;active=None;nodes=None
   if e['forest_before']:
    active=e['forest_before']['active'].copy();nodes={int(k):dict(v) for k,v in e['forest_before']['nodes'].items()}
   for pr in e['probes']:
    priced=pr['priced'];assert pr['success']==(priced[5]//priced[4]<=target)
    if pr['kind']=='root':
     assert priced[:3]==[0,(1<<self.n)-1,self.c]
     if pr['success']:domain=[priced]
    else:
     ident=pr['node'];assert nodes[ident]['domain']==priced[:3];leaves=pr['leaves'];assert set(leaves)<=set(active)
     parent=self.domain(priced);got=0
     for j in leaves:
      z=self.domain(nodes[j]['domain']);assert not got&z;got|=z
     assert got==parent;assert pr['reserved']==priced[1].bit_count()+1;reserved+=pr['reserved']
     if pr['success']:
      new=[];ids=[];inserted=False
      for j,cell in zip(active,domain):
       if j in leaves:
        if not inserted:new.append(priced);ids.append(ident);inserted=True
       else:new.append(cell);ids.append(j)
      domain=new;active=ids;nodes[ident]['children']=None
   assert reserved<=self.n+1
   # A successful priced cell must be reused: no renew call on its domain.
   successful={tuple(x['priced'][:3]) for x in e['probes'] if x['success']}
   assert not any(tuple(x['domain']) in successful for x in calls if x['kind']=='renew')
   r=e['result'];trace=r.get('trace',[])
   if not r.get('incomplete'):assert ct['splits']==len(trace)
   for z in trace:
    f,u,res=z['domain'];i=z['pivot'];assert u>>i&1;bit=1<<i;children=[[f,u^bit,res]]
    if self.w[i]<=res:children.append([f|bit,u^bit,res-self.w[i]])
    assert children==z['children'];got=0
    for child in children:
     b=self.domain(child);assert not got&b;got|=b
    assert got==self.domain(z['domain'])
   for k in totals:totals[k]+=ct[k]
   if r.get('incomplete'):assert path['status']=='capped';break
   if not r['success']:
    mask=r['witness'];assert self.weights[mask]<=self.c and self.intercepts[mask]+t*self.slopes[mask]>target;assert t==loss;self.checks['witnesses']+=1;assert path['status']=='packing_lost';break
   new=r['proof'];self.cover(new);self.prices(new,t,m);self.forest(e['forest_after'],new)
   for cell,o in zip(new,r['origins']):
    root=domain[o] if strategy!='rebuild' else [0,(1<<self.n)-1,self.c]
    assert self.domain(cell)&~self.domain(root)==0
   old=new;t0=t
  assert all(path['totals'][k]==z for k,z in totals.items())
  assert path['final_proof']==old and path['last_verified_time']==t0
  if path['status'] not in ('packing_lost','capped'):
   self.cert(old,t0,m,path['final_certificate']);dt=path['final_certificate']['first_failure'];assert dt is None or t0+dt>end;assert loss is None or loss>end
  self.cover(old);self.prices(old,t0,m)
 def row(self,row):
  start=time.process_time();m=row['packing'];initial=row['initial_proof'];end=row['end'];assert self.intercepts[m]==F.dp(self.w,self.p,self.c)
  for path in row['paths']:
   self.guard()
   if 'phases' not in path:self.path(path,m,initial,0,end)
   else:
    pm=m;proof=initial;start_t=0;switches=0
    for phase in path['phases']:
     self.path(phase,pm,proof,start_t,end)
     if phase['status']=='packing_lost':
      opt=phase['replacement'];start_t=phase['final_time'];q=[a+start_t*b for a,b in zip(self.p,self.v)];pm=opt['packing'];proof=opt['proof'];assert opt['objective']==F.dp(self.w,q,self.c)==self.intercepts[pm]+start_t*self.slopes[pm];assert opt['empty'];self.cover(proof);self.prices(proof,start_t,pm);self.checks['optimizer_solves']+=1;switches+=1
     else:break
    assert switches==path['switches']
  return dict(passed=True,**self.checks,audit_cpu=time.process_time()-start)
