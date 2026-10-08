"""Compact native witnesses, independently checked before unchanged VIPR admission.

Coverage is checked structurally. Search never acts as its own verifier.
This checker and its model parser are ordinary Python, not formally verified.
"""
from fractions import Fraction as Q
import json,subprocess,time
from support import ROOT,BIN,shared,certificates as C,digest,data,model,dependencies,hashfile

def make(row,t,source):
 t=Q(t)
 return dict(schema=1,model=model(row),time=[t.numerator,t.denominator],packing=source['packing'],
  objective=source['objective'],cells=[[f,u,a,b] for f,u,r,a,b,num in source['proof']])

def check(row,t,w):
 if w.get('schema')!=1 or w.get('model')!=model(row):raise ValueError('model binding')
 if row.get('objective_type','affine')!='affine' or row.get('feasible_type','constant')!='constant' or any(row.get('quadratic',[])):raise ValueError('model class')
 t=Q(t)
 if w['time']!=[t.numerator,t.denominator]:raise ValueError('time binding')
 n=row['n'];weights=row['weights'];cap=row['capacity'];full=(1<<n)-1
 if not 0<n<=12 or len(weights)!=n or len(row['profits'])!=n or len(row['slopes'])!=n or cap<0 or any(type(x)!=int or x<=0 for x in weights):raise ValueError('input domain')
 packing=w['packing'];target=w['objective']
 if type(packing)!=int or not 0<=packing<=full or shared.value(weights,packing)>cap:raise ValueError('primal feasibility')
 q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
 if type(target)!=int or shared.value(q,packing)!=target:raise ValueError('primal objective')
 cells=w['cells'];proof=[]
 if not 0<len(cells)<=4096:raise ValueError('cover size')
 for cell in cells:
  if len(cell)!=4 or any(type(v)!=int for v in cell):raise ValueError('cell encoding')
  f,u,a,b=cell
  if min(f,u,a)<0 or b<=0 or f|u>full or f&u:raise ValueError('cell domain')
  residual=cap-shared.value(weights,f)
  if residual<0:raise ValueError('infeasible leaf')
  num=b*shared.value(q,f)+a*residual+sum(max(0,b*q[j]-a*weights[j]) for j in range(n) if u>>j&1)
  if num//b>target:raise ValueError('cell bound')
  proof.append([f,u,residual,a,b,num])
 nodes=0
 def cover(f,u,candidates):
  nonlocal nodes
  nodes+=1
  if nodes>8191:raise ValueError('coverage work cap')
  if shared.value(weights,f)>cap:return
  intersect=[c for c in candidates if not(f&~(c[0]|c[1]) or c[0]&~(f|u))]
  if not intersect:raise ValueError('uncovered feasible cube')
  if any(c[0]&f==c[0] and not(f|u)&~(c[0]|c[1]) for c in intersect):return
  bits=u&~intersect[0][1]
  if not bits:raise ValueError('invalid cover split')
  bit=bits&-bits
  cover(f,u^bit,intersect);cover(f|bit,u^bit,intersect)
 cover(0,full,proof)
 return proof,dict(cells=len(cells),coverage_nodes=nodes)

def produce(row,t):
 t=Q(t);q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
 source=shared.SG.solve(row['weights'],q,row['capacity'],deadline=time.perf_counter()+30)
 w=make(row,t,source);proof,admission=check(row,t,w)
 text,info=shared.vipr_adapter.certificate(row,t,w['packing'],proof)
 if not text.startswith(C.prefix(row,t,w['objective'])):raise ValueError('original problem prefix')
 sha=digest(w);wpath=ROOT/'evidence/witnesses'/f'{sha}.json';wpath.parent.mkdir(parents=True,exist_ok=True);wpath.write_bytes(data(w))
 psha=__import__('hashlib').sha256(text.encode()).hexdigest();path=ROOT/'evidence/vipr'/f'{psha}.vipr';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
 out=subprocess.run([str(BIN),str(path)],capture_output=True,text=True,timeout=10)
 if out.returncode or 'Successfully verified optimal value range' not in out.stdout:raise ValueError('VIPR rejection')
 r=dict(schema=2,model=digest(model(row)),time=w['time'],objective=w['objective'],packing=w['packing'],
  witness_sha256=sha,proof_sha256=psha,dependencies=dependencies(),accepted=True,
  witness_path=str(wpath.relative_to(ROOT)),proof_path=str(path.relative_to(ROOT)),
  witness_bytes=len(data(w)),bytes=len(text.encode()),info=info,admission=admission,source=source)
 r['seal']=digest(r);return r

def valid(row,t,r,expected=None):
 try:
  if not r['accepted'] or r['schema']!=2 or r['model']!=digest(model(row)) or r['time']!=[Q(t).numerator,Q(t).denominator]:return False
  if r['dependencies']!=(expected if expected is not None else dependencies()):return False
  if r['seal']!=digest({k:v for k,v in r.items() if k!='seal'}):return False
  wp=ROOT/r['witness_path'];pp=ROOT/r['proof_path']
  if hashfile(wp)!=r['witness_sha256'] or hashfile(pp)!=r['proof_sha256']:return False
  w=json.loads(wp.read_bytes());check(row,t,w)
  if (w['packing'],w['objective'])!=(r['packing'],r['objective']):return False
  if not pp.read_text().startswith(C.prefix(row,t,r['objective'])):return False
  return True
 except (KeyError,ValueError,TypeError,OSError,json.JSONDecodeError):return False
