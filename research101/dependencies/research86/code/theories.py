"""Executable constructions and narrowly stated soundness contracts."""
from fractions import Fraction as F
import resource,time
from shared import ROOT,SG,value,frac,digest
import oracles,curves,horizon
from certificates import produce,valid_receipt,receipt_seal,context,scalar,PointCache

def objective(row,mask,t):
 t=F(t);return value(row['profits'],mask)+t*value(row['slopes'],mask)+t*t*value(row.get('quadratic',[0]*row['n']),mask)
def masks(row):return [m for m in range(1<<row['n']) if value(row['weights'],m)<=row['capacity']]
def samples(l,h,observations):return sorted({l+(h-l)*F(k,8) for k in range(9)}|{F(t) for t in observations if l<=t<=h})
def connector(row,l,h,mask):
 return row.get('objective_type','affine')=='affine' and row.get('feasible_type','constant')=='constant' and not any(row.get('quadratic',[])) and 0<=l<=h<=row['end'] and 0<=mask<1<<row['n'] and value(row['weights'],mask)<=row['capacity']
def interval(row):
 curve=curves.run(row,'real','dense',True);assert curve['status']=='complete';blocks=[]
 for piece in curve['intervals']:
  l,h=F(*piece['left']),F(*piece['right']);mask=piece['line'][2];assert connector(row,l,h,mask)
  blocks.append(dict(left=frac(l),right=frac(h),packing=mask,claims=[dict(time=frac(t),value=frac(objective(row,mask,t))) for t in samples(l,h,row['observations'])]))
 rejected=[]
 for label,changed in [('nonlinear',dict(row,objective_type='quadratic')),('changing_feasibility',dict(row,feasible_type='varying'))]:assert not connector(changed,F(0),F(row['end']),0);rejected.append(label)
 assert not connector(row,F(-1),F(row['end']),0);rejected.append('outside_domain')
 return dict(status='complete',curve=curve,blocks=blocks,rejected=rejected)
def gap(row):
 l,h=F(0),F(row['end']);queries=[oracles.solve(row,t,'dense',normalize=True) for t in (l,h,(l+h)/2)];mask=queries[-1]['packing'];gaps=[F(q['scaled_objective'],F(*q['time']).denominator)-objective(row,mask,F(*q['time'])) for q in queries[:2]]
 points=[]
 for t in samples(l,h,row['observations']):
  z=(t-l)/(h-l);bound=(1-z)*gaps[0]+z*gaps[1];points.append(dict(time=frac(t),candidate=frac(objective(row,mask,t)),gap_bound=frac(bound)))
 return dict(status='complete',queries=queries,packing=mask,endpoint_gaps=[frac(x) for x in gaps],claims=points,uniform_gap_bound=frac(max(gaps)))
def subset_ok(old,new,t,r,mask):
 return valid_receipt(old,t,r,mask,True) and new['n']==old['n'] and new['weights']==old['weights'] and new['profits']==old['profits'] and new['slopes']==old['slopes'] and 0<=new['capacity']<=old['capacity'] and value(new['weights'],mask)<=new['capacity']
def subset(row):
 records=[];tests=[]
 for t in (0,row['end']//2,row['end']):
  r=produce(row,t);records.append(r);used=value(row['weights'],r['packing'])
  for c in sorted({row['capacity'],used,max(0,used-1),row['capacity']+min(row['weights']),sum(row['weights'])}):
   new=dict(row,capacity=c);accepted=subset_ok(row,new,t,r,r['packing']);tests.append(dict(time=frac(F(t)),capacity=c,packing=r['packing'],accepted=accepted,objective=r['objective']))
 return dict(status='complete',records=records,tests=tests)
def poly_query(row,t):
 t=F(t);scale=t.denominator**2;q=[int(scale*(p+t*v+t*t*a)) for p,v,a in zip(row['profits'],row['slopes'],row['quadratic'])];data=dict(row,profits=q,slopes=[0]*row['n']);data.pop('quadratic');r=oracles.solve(data,0,'dense',normalize=True);return dict(time=frac(t),scale=scale,query=r)
def peak(a,b,c,l,h):
 ts=[l,h]
 if a<0:
  t=-b/(2*a)
  if l<=t<=h:ts.append(t)
 return max((a*t*t+b*t+c,t) for t in ts)
def curvature(row):
 h=F(row['end']);queries=[poly_query(row,F(t)) for t in (0,h)];mask=queries[0]['query']['packing'];feasible=masks(row);gaps=[F(q['query']['scaled_objective'],q['scale'])-objective(row,mask,F(*q['time'])) for q in queries];strength=sum(abs(a) for a in row['quadratic']);margins=[min(objective(row,mask,t)-objective(row,m,t) for m in feasible if m!=mask) for t in (0,h)]
 ceiling,where=peak(F(-strength),strength*h+(gaps[1]-gaps[0])/h,gaps[0],F(0),h);margin_ceiling,_=peak(F(-strength),strength*h+(margins[0]-margins[1])/h,-margins[0],F(0),h)
 claims=[]
 for t in samples(F(0),h,row['observations']):
  z=t/h;bound=(1-z)*gaps[0]+z*gaps[1]+strength*t*(h-t);claims.append(dict(time=frac(t),candidate=frac(objective(row,mask,t)),gap_bound=frac(bound)))
 return dict(status='complete',queries=queries,packing=mask,endpoint_gaps=[frac(x) for x in gaps],endpoint_margins=[frac(x) for x in margins],curvature_strength=strength,uniform_gap_bound=frac(ceiling),maximum_bound_at=frac(where),margin_bound=frac(margin_ceiling),exact_margin_certified=margin_ceiling<=0,naive_same_endpoint=queries[0]['query']['packing']==queries[1]['query']['packing'],claims=claims)
def expiry(row):
 source=SG.solve(row['weights'],row['profits'],row['capacity'],deadline=time.perf_counter()+30);proof=source['proof'];mask=source['packing'];certificate=horizon.certificate_horizon(proof,row['weights'],row['profits'],row['slopes'],mask);lines=horizon.packing_lines(row['weights'],row['profits'],row['slopes'],row['capacity']);loss=horizon.optimum_horizon(lines,row['profits'],row['slopes'],mask)
 times=set(row['observations'])
 for t in (certificate['first_failure'],loss['first_loss']):
  if t is not None:times.update((max(0,t-1),t))
 claims=[]
 for t in sorted(times):
  bounds=[horizon.numerator(cell,row['weights'],row['profits'],row['slopes'],t)//cell[4] for cell in proof];claims.append(dict(time=t,certificate_valid=max(bounds)<=objective(row,mask,t),candidate=frac(objective(row,mask,t)),bounds=bounds))
 return dict(status='complete',source=source,packing=mask,certificate=certificate,true_loss=loss,claims=claims)
def integrity(row,receipt=None,write_tamper=True):
 r=receipt if receipt is not None else produce(row,0);tests=[];assert valid_receipt(row,0,r,r['packing'],True)
 def reject(label,changed=r,model=row,packing=None):
  ok=valid_receipt(model,0,changed,packing,True);assert not ok,label;tests.append(dict(label=label,rejected=True))
 path=ROOT/'evidence/tamper'/(row['case_id']+'-changed.vipr');path.parent.mkdir(parents=True,exist_ok=True);payload=(ROOT/r['path']).read_bytes()+b'\nchanged artifact\n'
 if write_tamper:path.write_bytes(payload)
 else:assert path.read_bytes()==payload
 reject('proof_bytes',dict(r,path=str(path.relative_to(ROOT))))
 reject('bound_metadata',dict(r,objective=r['objective']+1));reject('time_metadata',dict(r,time=[1,1]));reject('context_metadata',dict(r,coefficients='wrong'));reject('unchecked_receipt',dict(r,accepted=False))
 bad=dict(r,checker_sha256='wrong');bad['seal']=receipt_seal(bad);reject('checker_identity',bad)
 badmask=next(m for m in masks(row) if value(row['profits'],m)!=r['objective']);bad=dict(r,objective=value(row['profits'],badmask),packing=badmask);bad['seal']=receipt_seal(bad);reject('forged_bound_and_seal',bad)
 changed=dict(row,profits=[row['profits'][0]+1]+row['profits'][1:]);dom,coef=context(changed);bad=dict(r,domain=dom,coefficients=coef,objective=value(changed['profits'],r['packing']));bad['seal']=receipt_seal(bad);reject('forged_model_and_seal',bad,changed)
 reject('nonlinear_scope',model=dict(row,objective_type='quadratic'));reject('changing_feasibility_scope',model=dict(row,feasible_type='varying'));reject('out_of_range_packing',packing=1<<row['n']);reject('infeasible_packing',packing=(1<<row['n'])-1);reject('suboptimal_packing',packing=badmask)
 return dict(status='complete',records=[r],accepted_original=True,rejections=tests,trust='Trusted generated receipt and fixed checker identity; hash seals are not signatures or formal verification. Concurrent file replacement is outside this experiment.')
def epochs(row):
 if row['case_id'].endswith('capacity_expansion'):changed=dict(row,capacity=sum(row['weights']))
 else:
  original=oracles.solve(row,0,'dense',normalize=True)['packing'];j=next(j for j,w in enumerate(row['weights']) if w<=row['capacity'] and not original>>j&1);p=list(row['profits']);p[j]+=1+sum(abs(x) for x in p);changed=dict(row,profits=p)
 models=[row,row,changed,changed];paths=[]
 for reuse in (False,True):
  begin=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN);cache=PointCache(True);records=[];claims=[];hits=0
  for model in models:
   r=cache.get(model,0) if reuse else None
   if r is None:r=produce(model,0);records.append(r);cache.put(model,0,r)
   else:hits+=1
   claims.append(dict(model=model,packing=r['packing'],objective=r['objective'],proof_sha256=r['proof_sha256']))
  after=resource.getrusage(resource.RUSAGE_CHILDREN);cost=time.process_time()-begin+after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
  paths.append(dict(reuse=reuse,records=records,claims=claims,hits=hits,algorithm_cpu=cost))
 old=paths[0]['claims'][0]['objective'];new=paths[0]['claims'][2]['objective'];assert new>old
 return dict(status='complete',paths=paths,old_bound=old,new_optimum=new,stale_bound_would_be_invalid=True)
DISPATCH={'interval':interval,'gap':gap,'subset':subset,'curvature':curvature,'expiry':expiry,'integrity':integrity,'epochs':epochs}
