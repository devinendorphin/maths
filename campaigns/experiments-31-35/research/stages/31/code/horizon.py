"""Exact nonnegative integer-time horizons for a fixed linear-profit certificate."""
import time
import flat_baseline as F
import proof_slack_experiment as P
import continuation as C

def value(p,mask):return sum(v for i,v in enumerate(p) if mask>>i&1)
def numerator(cell,w,p,v,t):
 fixed,free,res,a,b,num0=cell
 return b*sum(p[i]+v[i]*t for i in range(len(w)) if fixed>>i&1)+a*res+sum(max(0,b*(p[i]+v[i]*t)-a*w[i]) for i in range(len(w)) if free>>i&1)
def cell_horizon(cell,w,p,v,chosen):
 fixed,free,res,a,b,num0=cell;V0=value(p,chosen);V1=value(v,chosen)
 assert b>0 and a>=0 and numerator(cell,w,p,v,0)==num0 and num0//b<=V0
 final_slope=b*(value(v,fixed)-V1+sum(max(0,v[i]) for i in range(len(w)) if free>>i&1))
 if final_slope<=0:return None,dict(evaluations=0,final_slope=final_slope)
 evaluations=0
 def invalid(t):
  nonlocal evaluations
  evaluations+=1;return numerator(cell,w,p,v,t)-b*(V0+V1*t)>b-1
 lo,hi=0,1
 while not invalid(hi):lo,hi=hi,hi*2
 while hi-lo>1:
  mid=(lo+hi)//2
  if invalid(mid):hi=mid
  else:lo=mid
 assert not invalid(hi-1) and invalid(hi)
 return hi,dict(evaluations=evaluations,final_slope=final_slope)
def certificate_horizon(proof,w,p,v,chosen):
 horizons=[];stats=[]
 for cell in proof:
  h,s=cell_horizon(cell,w,p,v,chosen);horizons.append(h);stats.append(s)
 finite=[(t,i) for i,t in enumerate(horizons) if t is not None];first,index=min(finite) if finite else (None,None)
 return dict(first_failure=first,critical_cell=index,cell_horizons=horizons,evaluations=sum(x['evaluations'] for x in stats),final_slopes=[x['final_slope'] for x in stats])
def packing_lines(w,p,v,c):
 lines=[]
 for mask in range(1<<len(w)):
  if value(w,mask)<=c:lines.append((mask,value(p,mask),value(v,mask)))
 return lines
def optimum_horizon(lines,p,v,chosen):
 A,B=value(p,chosen),value(v,chosen);candidates=[]
 for mask,a,b in lines:
  assert a<=A
  if b>B:candidates.append(((A-a)//(b-B)+1,mask,a,b))
 if not candidates:return dict(first_loss=None,witness=None)
 t,mask,a,b=min(candidates);return dict(first_loss=t,witness=dict(mask=mask,intercept=a,slope=b,margin_at_loss=a+b*t-A-B*t))
def source(w,p,c,deadline):
 store=F.Store();ar=F.Arena(store);gen=P.SOLVERS['slack_branch'](w,p,c,0,None,None,'flat_share',ar);steps=0;start=time.perf_counter()
 try:
  while True:
   if steps%256==0 and (steps>=500000 or len(store.cells)>=5000 or time.perf_counter()>=deadline):raise RuntimeError('source construction cap')
   steps+=1
   try:next(gen)
   except StopIteration as done:best,chosen,root=done.value;break
  gen.close();F.run_to_completion(ar.cleanup(root));C.check(w,p,c,best,chosen,root,1,True)
  proof=root.fields();F.run_to_completion(root.release());store.empty()
  return dict(objective=best,packing=chosen,proof=proof,construction_steps=steps,construction_wall=time.perf_counter()-start,stats=store.stats,empty=True)
 except BaseException:
  gen.close();F.run_to_completion(ar.cleanup());store.empty();raise
