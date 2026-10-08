"""Integrated cost includes discovery, source proofs, checking, cache and outputs."""
from fractions import Fraction
import resource,time
from shared import value,frac
import curves
from certificates import PointCache,produce

def factor(row):
 alpha=None
 for p,v in zip(row['profits'],row['slopes']):
  if p:
   a=Fraction(v,p)
   if alpha is not None and a!=alpha:return None
   alpha=a
  elif v:return None
 alpha=alpha or Fraction(0)
 return alpha if min(Fraction(1),1+alpha*row['end'])>0 else None

def run(row,method):
 start=time.process_time();wall=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN);records=[];bundles=[];requests=[];curve=None;cache=PointCache(method in ('guarded','factor'));hits=0;alpha=factor(row) if method=='factor' else None
 def point(t,mask=None):
  nonlocal hits
  old=cache.get(row,t,mask) if method!='points' else None
  if old is None:
   old=produce(row,t);records.append(old)
   if method!='points':cache.put(row,t,old)
  else:hits+=1
  if mask is None:mask=old['packing']
  assert value(row['weights'],mask)<=row['capacity']
  t=Fraction(t);assert value([t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])],mask)==old['objective']
  requests.append(dict(time=frac(t),packing=mask,proof_sha256=old['proof_sha256']));return mask
 if method=='points':packings=[point(t) for t in row['observations']]
 elif alpha is not None:
  packing=point(0);assert cache.get(row,0,packing) is not None
  packings=[packing for t in row['observations']];bundles=[dict(left=[0,1],right=[row['end'],1],packing=packing,rule='positive_common_factor',alpha=frac(alpha),basis=records[0]['proof_sha256'])]
 else:
  curve=curves.run(row,'real','dense',True);assert curve['status']=='complete'
  for piece in curve['intervals']:
   l,h=Fraction(*piece['left']),Fraction(*piece['right']);packing=piece['line'][2];point(l,packing);point(h,packing)
   bundles.append(dict(left=frac(l),right=frac(h),packing=packing,rule='same_packing_affine_endpoints'))
  packings=[curve['packings'][t] for t in row['observations']]
 after=resource.getrusage(resource.RUSAGE_CHILDREN);parent=time.process_time()-start;child=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
 return dict(status='complete',method=method,records=records,requests=requests,cache_hits=hits,bundles=bundles,curve=curve,packings=packings,observations=row['observations'],factor_used=alpha is not None,algorithm_cpu=parent+child,parent_cpu=parent,child_cpu=child,algorithm_wall=time.perf_counter()-wall,certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),derivations=sum(r['info']['derivations'] for r in records))
