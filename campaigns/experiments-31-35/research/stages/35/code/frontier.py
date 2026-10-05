"""Algorithm-side recurrence certificates. No audit oracle imports."""
import time,itertools,math
from fractions import Fraction
import engine as E
import horizon as H
DP_KEYS=('dp_entries','dp_transitions','backpointer_work','frontier_lines','envelope_evaluations','envelope_intersections','recognition','sorting_comparisons','dominance_comparisons','dominance_deletions','dominance_witness_work','factor_dispatches')
class ConstructionCap(E.Cap):
 def __init__(self,reason,partial):super().__init__(reason);self.partial=partial
class Guard:
 def __init__(self,deadline,ct):self.deadline=deadline;self.ct=ct
 def check(self,partial):
  reason=None
  if time.perf_counter()>=self.deadline:reason='algorithm wall cap'
  elif self.ct['dp_entries']>=500000:reason='DP proof entry cap'
  elif self.ct['dp_transitions']>=2000000:reason='DP transition cap'
  elif self.ct['dominance_comparisons']>=5000000:reason='dominance comparison cap'
  if reason:raise ConstructionCap(reason,partial)
def affine(p,v,ct):
 ct['recognition']+=len(p);pair=next(((i,j) for i in range(len(p)) for j in range(i+1,len(p)) if p[i]!=p[j]),None)
 if pair is None:return (Fraction(0),Fraction(v[0])) if all(x==v[0] for x in v) else None
 i,j=pair;a=Fraction(v[j]-v[i],p[j]-p[i]);b=v[i]-a*p[i]
 return (a,b) if all(vi==a*pi+b for pi,vi in zip(p,v)) else None
class SortKey:
 def __init__(self,key,ct):self.key=key;self.ct=ct
 def __lt__(self,other):self.ct['sorting_comparisons']+=1;return self.key<other.key
def ordered(xs,key,ct):return sorted(xs,key=lambda x:SortKey(key(x),ct))
def hull(lines,ct):
 rows=ordered(lines,lambda x:(x[1],-x[0],x[2]),ct);unique=[]
 for row in rows:
  if not unique or row[1]!=unique[-1][1]:unique.append(row)
 out=[];starts=[]
 for row in unique:
  cross=None
  while out:
   ct['envelope_intersections']+=1;cross=Fraction(out[-1][0]-row[0],row[1]-out[-1][1])
   if starts[-1] is None or cross>starts[-1]:break
   out.pop();starts.pop()
  out.append(row);starts.append(cross if out[:-1] else None)
 return out,[[z.numerator,z.denominator] if z is not None else None for z in starts]
def dense(w,p,c,classes,which,guard,ct):
 # capacity-at-most recurrence; every Cartesian prefix count entry, including None.
 dim=max(classes)+1;n=len(w);zero=(0,)*dim;layers=[];sizes=[0]*dim
 base=[]
 for r in range(c+1):base.append([r,list(zero),0,0,None]);ct['dp_entries']+=1
 layers.append(base);prev={(x[0],tuple(x[1])):x for x in base};cursor={}
 for j,(wi,pi,cl) in enumerate(zip(w,p,classes),1):
  sizes[cl]+=1;layer=[];part=dict(kind='dense',which=which,classes=classes,layers=layers,current_layer=layer,cursor=cursor,complete=False)
  for r in range(c+1):
   for k in itertools.product(*(range(z+1) for z in sizes)):
    cursor.update(prefix=j,capacity=r,key=list(k));guard.check(part)
    options=[];ex=prev.get((r,k));ct['dp_transitions']+=1
    if ex is not None and ex[2] is not None:options.append((ex[2],ex[3],[r,list(k),False]))
    if r>=wi and k[cl]:
     kk=list(k);kk[cl]-=1;inc=prev.get((r-wi,tuple(kk)));ct['dp_transitions']+=1
     if inc is not None and inc[2] is not None:options.append((inc[2]+pi,inc[3]|1<<(j-1),[r-wi,kk,True]))
    chosen=None
    for z in options:
     if chosen is None or (z[0]>chosen[0] if which=='max' else z[0]<chosen[0]):chosen=z
    row=[r,list(k),None if chosen is None else chosen[0],None if chosen is None else chosen[1],None if chosen is None else chosen[2]]
    layer.append(row);ct['dp_entries']+=1;ct['backpointer_work']+=int(chosen is not None)
  layers.append(layer);prev={(x[0],tuple(x[1])):x for x in layer}
 return dict(kind='dense',which=which,classes=classes,layers=layers,complete=True)
def sparse(w,p,v,c,prune,guard,ct):
 # Exact W,S same-state max reduction, then optional interval-dominance.
 layers=[dict(raw=[[0,0,0,0,None]],retained=[0],deletions=[])];ct['dp_entries']+=1;prev=layers[0];cursor={}
 for j,(wi,pi,vi) in enumerate(zip(w,p,v),1):
  data={};part=dict(kind='sparse',interval=[0,256] if prune else [0,None],layers=layers,current=data,cursor=cursor,complete=False)
  for ident in prev['retained']:
   row=prev['raw'][ident];W,S,P,M,_=row
   for include in (False,True):
    cursor.update(stage='recurrence',prefix=j,predecessor=ident,include=include);guard.check(part)
    ct['dp_transitions']+=1
    WW,SS,PP,MM=(W+wi,S+vi,P+pi,M|1<<(j-1)) if include else (W,S,P,M)
    if WW>c:continue
    key=(WW,SS)
    if key not in data:
     data[key]=[WW,SS,PP,MM,[ident,include]];ct['dp_entries']+=1;ct['backpointer_work']+=1
    elif PP>data[key][2]:data[key]=[WW,SS,PP,MM,[ident,include]];ct['backpointer_work']+=1
  raw=list(data.values());retained=[];deletions=[]
  order=ordered(list(range(len(raw))),lambda i:(raw[i][0],-raw[i][2],-(raw[i][2]+256*raw[i][1]),raw[i][1],raw[i][3]),ct) if prune else list(range(len(raw)))
  # Survivors processed in nondecreasing weight and decreasing endpoints within equal weight.
  # Witnesses always point to an earlier retained survivor; no cycles or future deletions.
  for i in order:
   y=raw[i];dom=None
   if prune:
    for dom_index,x in enumerate(retained):
     cursor.update(stage='pruning',prefix=j,candidate=i,dominator=x,dominator_position=dom_index,order=order)
     guard.check(dict(**part,current_raw=raw,current_retained=retained,current_deletions=deletions));ct['dominance_comparisons']+=1
     z=raw[x]
     if z[0]<=y[0] and z[2]>=y[2] and z[2]+256*z[1]>=y[2]+256*y[1]:dom=x;break
   if dom is None:retained.append(i)
   else:deletions.append([i,dom]);ct['dominance_deletions']+=1;ct['dominance_witness_work']+=1
  prev=dict(raw=raw,retained=retained,deletions=deletions);layers.append(prev)
 return dict(kind='sparse',interval=[0,256] if prune else [0,None],layers=layers,complete=True)
def build(w,p,v,c,policy,deadline,ct):
 guard=Guard(deadline,ct);cert=dict(policy=policy,interval=[0,None],tables=[],complete=False);n=len(p)
 if policy=='uniform':
  ct['recognition']+=n
  if not all(x==v[0] for x in v):return None
  classes=[0]*n;table=dense(w,p,c,classes,'max',guard,ct);cert['tables']=[table];cert['gamma']=v[0]
 elif policy in ('affine_max','affine_pair'):
  ab=affine(p,v,ct)
  if ab is None:return None
  a,b=ab;cert['alpha']=[a.numerator,a.denominator];cert['beta']=[b.numerator,b.denominator];cert['tables'].append(dense(w,p,c,[0]*n,'max',guard,ct))
  if a<0:
   if policy=='affine_pair':
    try:cert['tables'].append(dense(w,p,c,[0]*n,'min',guard,ct))
    except ConstructionCap as exc:
     exc.partial['completed_tables']=cert['tables'];exc.partial['recognition_certificate']={k:z for k,z in cert.items() if k!='tables'};raise
   else:cert['boundary']=math.ceil(-1/a);cert['interval']=[0,cert['boundary']-1]
 elif policy=='two_class':
  ct['recognition']+=n;values=ordered(list(set(v)),lambda x:x,ct)
  if len(values)>2:return None
  cert['class_slopes']=values;classes=[values.index(x) for x in v];cert['class_sizes']=[classes.count(j) for j in range(len(values))];cert['tables']=[dense(w,p,c,classes,'max',guard,ct)]
 elif policy in ('slope','pruned'):
  cert['interval']=[0,256] if policy=='pruned' else [0,None];cert['tables']=[sparse(w,p,v,c,policy=='pruned',guard,ct)]
 else:raise ValueError(policy)
 lines=[]
 for table in cert['tables']:
  if table['kind']=='dense':terminal=[r for r in table['layers'][-1] if r[0]==c and r[2] is not None];lines.extend([r[2],H.value(v,r[3]),r[3],r[1]] for r in terminal)
  else:
   last=table['layers'][-1];best={}
   for i in last['retained']:
    W,S,P,M,_=last['raw'][i]
    if S not in best or P>best[S][0]:best[S]=[P,S,M,[S]]
   lines.extend(best.values())
 cert['lines']=lines;ct['frontier_lines']+=len(lines);cert['envelope'],cert['envelope_starts']=hull(lines,ct);cert['complete']=True
 return cert
def at(cert,t):
 lo,hi=cert['interval']
 if t<lo or hi is not None and t>hi:raise ValueError('certificate interval exceeded')
 return max(A+s*t for A,s,*_ in cert['lines'])
def horizon(cert,p,v,m,t,ct):
 ct['envelope_evaluations']+=len(cert['lines']);at(cert,t);A=H.value(p,m);s=H.value(v,m);value=A+t*s;loss=[]
 for B,d,mask,*_ in cert['envelope']:
  ct['envelope_evaluations']+=1;margin=value-B-d*t
  assert margin>=0
  if d>s:loss.append((t+margin//(d-s)+1,mask))
 return min(loss) if loss else (None,None)
