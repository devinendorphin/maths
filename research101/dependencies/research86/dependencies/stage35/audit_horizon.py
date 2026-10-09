"""Independent rational piecewise-affine horizon and saved-result audit."""
import json,itertools
from fractions import Fraction
from pathlib import Path
import flat_baseline as F

def val(p,mask):return sum(v for i,v in enumerate(p) if mask>>i&1)
def bound(cell,w,p,v,t):
 fixed,free,res,a,b,num=cell
 return b*val([pi+vi*t for pi,vi in zip(p,v)],fixed)+a*res+sum(max(0,b*(pi+vi*t)-a*wi) for i,(pi,vi,wi) in enumerate(zip(p,v,w)) if free>>i&1)
def rational_horizon(cell,w,p,v,chosen):
 fixed,free,res,a,b,_=cell;terms=[(b*pi-a*wi,b*vi) for i,(pi,vi,wi) in enumerate(zip(p,v,w)) if free>>i&1]
 events=sorted({Fraction(-u,d) for u,d in terms if d and Fraction(-u,d)>0});points=[Fraction(0)]+events+[None]
 for left,right in zip(points,points[1:]):
  test=left+1 if right is None else (left+right)/2;active=[(u,d) for u,d in terms if u+d*test>0]
  A=b*(val(p,fixed)-val(p,chosen))+a*res+sum(u for u,d in active);B=b*(val(v,fixed)-val(v,chosen))+sum(d for u,d in active)
  if B<=0:continue
  t=max(1,-((-left.numerator)//left.denominator),(b-1-A)//B+1)
  if right is None or t<=right:
   assert bound(cell,w,p,v,t)//b>val(p,chosen)+t*val(v,chosen);return t
 return None

def verify_case(x,dense=False):
 w,p,v,c,chosen,proof=x['weights'],x['profits'],x['slopes'],x['capacity'],x['packing'],x['proof'];hc=x['certificate']['first_failure'];ho=x['optimum']['first_loss'];V0=val(p,chosen);V1=val(v,chosen)
 assert val(w,chosen)<=c and V0==F.dp(w,p,c)
 # Independent full feasible cover and valid initial numerators.
 feasible=[m for m in range(1<<len(w)) if val(w,m)<=c]
 for m in feasible:assert sum(m&fixed==fixed and m&~(fixed|free)==0 for fixed,free,*_ in proof)==1
 horizons=[rational_horizon(cell,w,p,v,chosen) for cell in proof];finite=[h for h in horizons if h is not None]
 assert horizons==x['certificate']['cell_horizons'] and hc==(min(finite) if finite else None)
 candidates=[]
 for m in feasible:
  A,B=val(p,m),val(v,m);assert A<=V0
  if B>V1:candidates.append((Fraction(V0-A,B-V1),m))
 ref=None if not candidates else min(z.numerator//z.denominator+1 for z,m in candidates)
 assert ho==ref
 if ho is not None:assert hc is not None and hc<=ho
 if hc is None:assert ho is None
 times={0,1,2,4,8,16,32,64,128}
 if dense:times.update(range(65))
 for h in (hc,ho):
  if h is not None:times.update((h-1,h,h+1))
 checks=[]
 for t in sorted(times):
  q=[pi+vi*t for pi,vi in zip(p,v)];value=V0+V1*t;cert=all(bound(cell,w,p,v,t)//cell[4]<=value for cell in proof);optimal=F.dp(w,q,c)==value
  assert cert==(hc is None or t<hc) and optimal==(ho is None or t<ho)
  checks.append(dict(time=t,certified=cert,optimal=optimal,value=value,optimum=F.dp(w,q,c)))
 if ho is not None:
  a=x['optimum']['witness'];assert val(w,a['mask'])<=c and val(p,a['mask'])==a['intercept'] and val(v,a['mask'])==a['slope'] and a['margin_at_loss']>0
 return checks

def audit(stage):
 data=json.loads(Path(stage+'-results.json').read_text());rows=[]
 for x in data['cases']:rows.append(dict(case_id=x['case_id'],checks=verify_case(x)))
 out=dict(passed=True,cases=len(rows),time_checks=sum(len(x['checks']) for x in rows),rows=rows);Path(stage+'-audit.json').write_text(json.dumps(out,indent=2));print(stage,'audited',len(rows),'cases and',out['time_checks'],'times')
if __name__=='__main__':
 for stage in ('development','heldout'):audit(stage)
