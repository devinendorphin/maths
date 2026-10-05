"""Independent certificate checker. No algorithm frontier builders imported."""
import itertools,time
from fractions import Fraction
class Checker:
 def __init__(self,w,p,v,c):self.w=w;self.p=p;self.v=v;self.c=c;self.deadline=time.perf_counter()+45;self.checks=0
 def guard(self):
  if time.perf_counter()>self.deadline:raise TimeoutError('45-second audit batch')
 def witness(self,j,W,P,M,S=None):
  assert M is not None and 0<=M<1<<j
  assert sum(x for i,x in enumerate(self.w) if M>>i&1)==W
  assert sum(x for i,x in enumerate(self.p) if M>>i&1)==P
  if S is not None:assert sum(x for i,x in enumerate(self.v) if M>>i&1)==S
 def dense_layer(self,table,j):
  rows=table['layers'][j];classes=table['classes'];dims=max(classes)+1;counts=[classes[:j].count(d) for d in range(dims)];expected_keys={(r,k) for r in range(self.c+1) for k in itertools.product(*(range(x+1) for x in counts))};got={(x[0],tuple(x[1])):x for x in rows};assert len(got)==len(rows) and set(got)==expected_keys
  prev={(x[0],tuple(x[1])):x for x in table['layers'][j-1]} if j else {}
  for (r,k),row in got.items():
   self.guard();self.checks+=1;P,M,pr=row[2:]
   if j==0:assert k==(0,)*dims and (P,M,pr)==(0,0,None);continue
   wi,pi,cl=self.w[j-1],self.p[j-1],classes[j-1];poss=[]
   if (r,k) in prev and prev[r,k][2] is not None:poss.append(prev[r,k][2])
   if r>=wi and k[cl]>0:
    kk=list(k);kk[cl]-=1;x=prev.get((r-wi,tuple(kk)))
    if x and x[2] is not None:poss.append(pi+x[2])
   expected=(max(poss) if table['which']=='max' else min(poss)) if poss else None;assert P==expected
   if P is None:assert M is None and pr is None;continue
   assert pr is not None;rr,kk,inc=pr;prior=prev[rr,tuple(kk)]
   assert prior[2] is not None
   if inc:
    knew=list(kk);knew[cl]+=1;assert rr==r-wi and tuple(knew)==k and P==prior[2]+pi and M==prior[3]|1<<(j-1)
   else:assert rr==r and tuple(kk)==k and P==prior[2] and M==prior[3]
   assert sum(x for i,x in enumerate(self.w) if M>>i&1)<=r
   assert sum(x for i,x in enumerate(self.p) if M>>i&1)==P and M<1<<j
   assert tuple(sum(1 for i in range(j) if M>>i&1 and classes[i]==d) for d in range(dims))==k
 def sparse_layer(self,table,j):
  lay=table['layers'][j];raw=lay['raw'];got={(r[0],r[1]):r for r in raw};assert len(got)==len(raw)
  if j==0:assert raw==[[0,0,0,0,None]] and lay['retained']==[0] and not lay['deletions'];return
  prev=table['layers'][j-1];expected={};wi,pi,vi=self.w[j-1],self.p[j-1],self.v[j-1]
  for i in prev['retained']:
   W,S,P,M,_=prev['raw'][i]
   for WW,SS,PP in ((W,S,P),(W+wi,S+vi,P+pi)):
    if WW<=self.c:expected[WW,SS]=max(expected.get((WW,SS),PP),PP)
  assert set(got)==set(expected)
  for (W,S),row in got.items():
   self.guard();self.checks+=1;P,M,pr=row[2:];assert P==expected[W,S];self.witness(j,W,P,M,S);i,inc=pr;assert i in prev['retained'];w0,s0,p0,m0,_=prev['raw'][i]
   assert (W,S,P,M)==((w0+wi,s0+vi,p0+pi,m0|1<<(j-1)) if inc else (w0,s0,p0,m0))
  retained=lay['retained'];deletes=lay['deletions'];assert len(set(retained))==len(retained);assert len(set(y for y,x in deletes))==len(deletes)
  assert set(retained)|{y for y,x in deletes}==set(range(len(raw))) and not set(retained)&{y for y,x in deletes}
  for y,x in deletes:
   assert table['interval']==[0,256] and x in retained and x!=y
   X,Y=raw[x],raw[y];assert X[0]<=Y[0] and X[2]>=Y[2] and X[2]+256*X[1]>=Y[2]+256*Y[1]
   # All deletion chains have one edge to a surviving prefix state; acyclic.
 def terminal(self,cert):
  self.guard();lines=cert['lines'];expected=[]
  for table in cert['tables']:
   if table['kind']=='dense':expected.extend([r[2],sum(x for i,x in enumerate(self.v) if r[3]>>i&1),r[3],r[1]] for r in table['layers'][-1] if r[0]==self.c and r[2] is not None)
   else:
    layer=table['layers'][-1];best={}
    for i in layer['retained']:
     W,S,P,M,_=layer['raw'][i]
     if S not in best or P>best[S][0]:best[S]=[P,S,M,[S]]
    expected.extend(best.values())
  assert lines==expected and cert['complete']
  if 'alpha' in cert:
   a=Fraction(*cert['alpha']);b=Fraction(*cert['beta']);assert all(vi==a*pi+b for pi,vi in zip(self.p,self.v))
   for A,s,m,k in lines:assert a*A+b*k[0]==s and (a*A+b*k[0]).denominator==1
  elif 'gamma' in cert:assert all(x==cert['gamma'] for x in self.v)
  elif 'class_slopes' in cert:
   slopes=cert['class_slopes'];assert sorted(set(self.v))==slopes and len(slopes)<=2
   for A,s,m,k in lines:assert s==sum(x*y for x,y in zip(slopes,k))
  # Verify exact hull algebra, independently, including hidden middle intersections.
  hull=cert['envelope'];starts=cert['envelope_starts'];assert len(hull)==len(starts) and starts[0] is None
  for i,L in enumerate(hull):
   assert L in lines
   if i:
    assert hull[i-1][1]<L[1];cross=Fraction(hull[i-1][0]-L[0],L[1]-hull[i-1][1]);assert cross==Fraction(*starts[i])
    if i>1:assert Fraction(*starts[i-1])<cross
   left=Fraction(*starts[i]) if i else None;right=Fraction(*starts[i+1]) if i+1<len(starts) else None
   for A,s,*_ in lines:
    if left is None:assert s>=L[1]
    else:assert L[0]+L[1]*left>=A+s*left
    if right is None:assert s<=L[1]
    else:assert L[0]+L[1]*right>=A+s*right
  # Exhaustive domain grouping audit: generated independently, never supplied to policy.
  groups={};class_slopes=sorted(set(self.v))
  for m in range(1<<len(self.w)):
   self.guard();W=sum(w for i,w in enumerate(self.w) if m>>i&1)
   if W>self.c:continue
   P=sum(p for i,p in enumerate(self.p) if m>>i&1);S=sum(v for i,v in enumerate(self.v) if m>>i&1)
   if cert['policy'] in ('uniform','affine_max','affine_pair'):key=(m.bit_count(),)
   elif cert['policy']=='two_class':key=tuple(sum(1 for i in range(len(self.v)) if m>>i&1 and self.v[i]==s) for s in class_slopes)
   else:key=(S,)
   if key not in groups:groups[key]=[P,P]
   else:groups[key]=[max(groups[key][0],P),min(groups[key][1],P)]
  if cert['policy']!='pruned':
   maximum={tuple(k):A for A,s,m,k in lines[:len(groups)]};assert maximum=={k:z[0] for k,z in groups.items()}
   if len(cert['tables'])==2:assert {tuple(k):A for A,s,m,k in lines[len(groups):]}=={k:z[1] for k,z in groups.items()}
  return dict(groups=len(groups),lines=len(lines),envelope=len(hull))
def independent_dp(w,q,c):
 # Item-subset capacity DP, audit only; signed profits and empty packing.
 a=[0]*(c+1)
 for wi,qi in zip(w,q):
  b=a.copy()
  for r in range(wi,c+1):b[r]=max(a[r],qi+a[r-wi])
  a=b
 return a[c]
def check_samples(w,p,v,c,cert):
 hi=cert['interval'][1];last=256 if hi is None else min(256,hi)
 for t in range(last+1):assert max(A+s*t for A,s,*_ in cert['lines'])==independent_dp(w,[a+t*b for a,b in zip(p,v)],c)
 return last+1
