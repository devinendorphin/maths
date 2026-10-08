"""Independent exact optima, analytic counterexamples and certificate binding."""
from fractions import Fraction as F
import hashlib,time
from shared import ROOT,DEPS,value,frac,digest,vipr_adapter
from audit import Auditor
class Checker:
 def __init__(self,row):self.row=row;self.auditors={};self.numerical=0;self.bounds=0;self.integer=0
 def auditor(self,row):
  key=digest([row['n'],row['weights'],row['capacity'],row['profits'],row['slopes']])
  if key not in self.auditors:self.auditors[key]=Auditor(row)
  return self.auditors[key]
 def best(self,row,t):
  t=F(t);return F(self.auditor(row).optimum(t)[0],t.denominator)
 def val(self,row,m,t):
  t=F(t);return sum((row['profits'][j]+t*row['slopes'][j]+t*t*row.get('quadratic',[0]*row['n'])[j]) for j in range(row['n']) if m>>j&1)
 def feasible(self,row,m):return 0<=m<1<<row['n'] and sum(row['weights'][j] for j in range(row['n']) if m>>j&1)<=row['capacity']
 def answer(self,row,m,t):
  t=F(t);assert self.feasible(row,m) and self.val(row,m,t)==self.best(row,t);self.numerical+=1;self.integer+=t.denominator==1
 def cert(self,row,r):
  t=F(*r['time']);q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])];assert self.feasible(row,r['packing']) and value(q,r['packing'])==r['objective']==r['source']['objective']==self.auditor(row).optimum(t)[0]
  assert r['domain']==digest([row['n'],row['weights'],row['capacity']]) and r['coefficients']==digest([row['profits'],row['slopes']]);assert r['accepted']
  text,info=vipr_adapter.certificate(row,t,r['packing'],r['source']['proof']);assert info==r['info'] and (ROOT/r['path']).read_text()==text and hashlib.sha256(text.encode()).hexdigest()==r['proof_sha256'] and hashlib.sha256((DEPS/'vipr/viprchk').read_bytes()).hexdigest()==r['checker_sha256']
  self.numerical+=1;self.integer+=t.denominator==1
 def curve(self,row,r):
  a=self.auditor(row).check(r);assert a['passed'];self.numerical+=a['rational_checks']+a['integer_checks'];self.integer+=a['integer_checks']
  seg=r['intervals'];assert F(*seg[0]['left'])==0 and F(*seg[-1]['right'])==row['end']
  for l,h in zip(seg,seg[1:]):assert l['right']==h['left']
 def query(self,row,q):
  a=self.auditor(row).check(dict(status='query_only',kind='special',queries=[q],incomplete_attempts=[],packings=[],intervals=[]));assert a['passed'];self.numerical+=a['rational_checks']
 def polynomial_best(self,row,t):
  t=F(t);den=t.denominator**2;q=[int(den*(p+t*v+t*t*a)) for p,v,a in zip(row['profits'],row['slopes'],row['quadratic'])];data=dict(row,profits=q,slopes=[0]*row['n']);data.pop('quadratic');return F(self.auditor(data).optimum(0)[0],den)
 def run(self,row,r):
  begin=time.process_time();initial=(self.numerical,self.integer,self.bounds);method=r.get('method');assert r['status']=='complete'
  if method in ('points','envelope','guarded','factor'):
   for rec in r['records']:self.cert(row,rec)
   for t,m in zip(r['observations'],r['packings']):self.answer(row,m,t)
   if r['curve'] is not None:self.curve(row,r['curve'])
   records={x['proof_sha256']:x for x in r['records']};assert all(x['proof_sha256'] in records for x in r['requests'])
   for req in r['requests']:self.answer(row,req['packing'],F(*req['time']))
   if method=='points':assert not r['bundles'] and r['certificates']==len(row['observations'])
   elif r['factor_used']:
    assert len(r['records'])==1 and r['bundles'][0]['rule']=='positive_common_factor';alpha=F(*r['bundles'][0]['alpha']);assert all(v==alpha*p for p,v in zip(row['profits'],row['slopes'])) and min(1,1+alpha*row['end'])>0
   else:
    last=F(0);times=set()
    for b in r['bundles']:
     l,h=F(*b['left']),F(*b['right']);assert l==last and l<h;last=h
     for t in (l,h):
      self.answer(row,b['packing'],t);times.add(t)
      assert any(F(*x['time'])==t and x['packing']==b['packing'] for x in r['requests'])
    assert last==row['end'] and len(r['records'])==len(times)==len(r['bundles'])+1
  elif 'blocks' in r:
   self.curve(row,r['curve'])
   for b in r['blocks']:
    l,h=F(*b['left']),F(*b['right']);self.answer(row,b['packing'],l);self.answer(row,b['packing'],h)
    for c in b['claims']:t=F(*c['time']);assert l<=t<=h and F(*c['value'])==self.val(row,b['packing'],t);self.answer(row,b['packing'],t)
   assert r['rejected']==['nonlinear','changing_feasibility','outside_domain']
  elif 'endpoint_gaps' in r and 'quadratic' not in row:
   for q in r['queries']:self.query(row,q)
   mask=r['packing'];gaps=[self.best(row,t)-self.val(row,mask,t) for t in (0,row['end'])];assert [frac(x) for x in gaps]==r['endpoint_gaps'] and F(*r['uniform_gap_bound'])==max(gaps)
   for c in r['claims']:
    t=F(*c['time']);bound=F(*c['gap_bound']);assert self.feasible(row,mask) and F(*c['candidate'])==self.val(row,mask,t);assert 0<=self.best(row,t)-self.val(row,mask,t)<=bound;self.bounds+=1;self.integer+=t.denominator==1
  elif 'tests' in r:
   for rec in r['records']:self.cert(row,rec)
   for test in r['tests']:
    t=F(*test['time']);new=dict(row,capacity=test['capacity']);safe=new['capacity']<=row['capacity'] and self.feasible(new,test['packing']);assert safe==test['accepted']
    if safe:self.answer(new,test['packing'],t);assert test['objective']==self.auditor(new).optimum(t)[0]
    else:self.bounds+=1
  elif 'quadratic' in row:
   mask=r['packing'];assert self.feasible(row,mask);strength=sum(abs(x) for x in row['quadratic']);assert strength==r['curvature_strength']
   for p in r['queries']:
    t=F(*p['time']);assert F(p['query']['scaled_objective'],p['scale'])==self.polynomial_best(row,t);assert self.val(row,p['query']['packing'],t)==self.polynomial_best(row,t);self.numerical+=1
   actual=F(0);all_m=[m for m in range(1<<row['n']) if self.feasible(row,m)]
   for m in all_m:
    a=value(row['quadratic'],m)-value(row['quadratic'],mask);b=value(row['slopes'],m)-value(row['slopes'],mask);c=value(row['profits'],m)-value(row['profits'],mask);ts=[F(0),F(row['end'])]
    if a<0:
     vertex=F(-b,2*a)
     if 0<=vertex<=row['end']:ts.append(vertex)
    actual=max(actual,max(a*t*t+b*t+c for t in ts))
   assert actual<=F(*r['uniform_gap_bound'])
   if r['exact_margin_certified']:assert actual==0
   for c in r['claims']:
    t=F(*c['time']);assert 0<=self.polynomial_best(row,t)-self.val(row,mask,t)<=F(*c['gap_bound']);self.bounds+=1;self.integer+=t.denominator==1
   if row['case_id']=='89-interior_failure':assert r['naive_same_endpoint'] and actual==3 and not r['exact_margin_certified']
   if row['case_id']=='89-margin_safe':assert r['exact_margin_certified'] and actual==0
  elif 'certificate' in r:
   mask=r['packing'];assert self.val(row,mask,0)==self.best(row,0);proof=r['source']['proof'];feasible=[m for m in range(1<<row['n']) if self.feasible(row,m)]
   for m in feasible:assert sum((m&cell[0]==cell[0] and m&~(cell[0]|cell[1])==0) for cell in proof)==1
   for cell in proof:
    fixed,free,res,a,b,num=cell;assert not fixed&free and a>=0 and b>0 and res==row['capacity']-value(row['weights'],fixed)
    calculated=b*value(row['profits'],fixed)+a*res+sum(max(0,b*p-a*w) for j,(p,w) in enumerate(zip(row['profits'],row['weights'])) if free>>j&1);assert calculated==num and num//b<=r['source']['objective']
   possibilities=[]
   for m in feasible:
    intercept=value(row['profits'],m)-value(row['profits'],mask);slope=value(row['slopes'],m)-value(row['slopes'],mask)
    if slope>0:possibilities.append((-intercept)//slope+1)
   loss=min(possibilities) if possibilities else None;assert loss==r['true_loss']['first_loss'];failure=r['certificate']['first_failure']
   if loss is not None:assert failure is not None and failure<=loss
   for c in r['claims']:
    t=c['time'];bounds=[]
    for cell in proof:
     f,u,res,a,b,num=cell;bound=(b*self.val(row,f,t)+a*res+sum(max(0,b*(p+t*v)-a*w) for j,(p,v,w) in enumerate(zip(row['profits'],row['slopes'],row['weights'])) if u>>j&1))//b;bounds.append(int(bound))
     for m in feasible:
      if m&f==f and m&~(f|u)==0:assert self.val(row,m,t)<=bound
    assert bounds==c['bounds'] and c['certificate_valid']==(max(bounds)<=self.val(row,mask,t));assert c['certificate_valid']==(failure is None or t<failure);self.bounds+=len(bounds);self.integer+=1
  elif 'rejections' in r:
   for rec in r['records']:self.cert(row,rec)
   from theories import integrity
   replay=integrity(row,r['records'][0],write_tamper=False);assert replay['rejections']==r['rejections'] and len(r['rejections'])==13;self.bounds+=13
  elif 'paths' in r:
   for path in r['paths']:
    seen={x['proof_sha256']:x for x in path['records']}
    for c in path['claims']:
     self.cert(c['model'],seen[c['proof_sha256']]);self.answer(c['model'],c['packing'],0)
    assert len(path['records'])==(2 if path['reuse'] else 4) and path['hits']==(2 if path['reuse'] else 0)
   assert r['new_optimum']>r['old_bound'] and r['stale_bound_would_be_invalid'];self.bounds+=1
  else:raise ValueError('unknown result')
  return dict(passed=True,numerical_checks=self.numerical-initial[0],integer_checks=self.integer-initial[1],bound_checks=self.bounds-initial[2],audit_cpu=time.process_time()-begin)
