"""Original-problem VIPR receipts and narrowly scoped point-bound reuse."""
from fractions import Fraction
import hashlib,resource,subprocess,time
from shared import ROOT,DEPS,SG,vipr_adapter,frac,value,digest
BIN=DEPS/'vipr/viprchk'
def terms(xs):return str(len(xs))+' '+ ' '.join(str(j)+' '+str(v) for j,v in xs)
def prefix(row,t,target):
 t=Fraction(t);n=row['n'];q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])];w=row['weights']
 lines=['VER 1.0',f'VAR {n}',' '.join('x'+str(j) for j in range(n)),f'INT {n}',' '.join(map(str,range(n))),'OBJ max',terms([(j,x) for j,x in enumerate(q) if x]),f'CON {2*n+1} {2*n}']
 for j in range(n):lines.extend([f'lb{j} G 0 1 {j} 1',f'ub{j} L 1 1 {j} 1'])
 lines.extend(['capacity L '+str(row['capacity'])+' '+terms(list(enumerate(w))),f'RTP range {target} {target}','SOL 1']);return '\n'.join(lines)+'\n'
def context(row):return digest([row['n'],row['weights'],row['capacity']]),digest([row['profits'],row['slopes']])
def scalar(row,t):
 t=Fraction(t);return [t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
def receipt_seal(r):return digest({k:r[k] for k in ('schema','domain','coefficients','time','objective','packing','proof_sha256','checker_sha256','accepted')})
def valid_receipt(row,t,r,packing=None,guarded=True):
 t=Fraction(t);domain,coeff=context(row)
 if row.get('objective_type','affine')!='affine' or row.get('feasible_type','constant')!='constant' or any(row.get('quadratic',[])):return False
 if not r['accepted'] or (r['domain'],r['coefficients'],r['time'])!=(domain,coeff,frac(t)):return False
 if packing is not None and (packing<0 or packing>=1<<row['n'] or value(row['weights'],packing)>row['capacity'] or value(scalar(row,t),packing)!=r['objective']):return False
 if guarded:
  if r['seal']!=receipt_seal(r):return False
  data=(ROOT/r['path']).read_bytes()
  if hashlib.sha256(data).hexdigest()!=r['proof_sha256'] or hashlib.sha256(BIN.read_bytes()).hexdigest()!=r['checker_sha256']:return False
  if not data.decode().startswith(prefix(row,t,r['objective'])):return False
 return True

def produce(row,t):
 t=Fraction(t);q=scalar(row,t);start=time.process_time();source=SG.solve(row['weights'],q,row['capacity'],deadline=time.perf_counter()+30);native=time.process_time()-start;mask=source['packing'];assert source['empty'] and value(row['weights'],mask)<=row['capacity'] and value(q,mask)==source['objective']
 start=time.process_time();text,info=vipr_adapter.certificate(row,t,mask,source['proof']);adapter=time.process_time()-start;assert text.startswith(prefix(row,t,source['objective']))
 sha=hashlib.sha256(text.encode()).hexdigest();folder=ROOT/'evidence/vipr';folder.mkdir(parents=True,exist_ok=True);path=folder/(sha+'.vipr');path.write_text(text)
 before=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.perf_counter();checked=subprocess.run([str(BIN),str(path)],capture_output=True,text=True,timeout=30);after=resource.getrusage(resource.RUSAGE_CHILDREN)
 assert checked.returncode==0 and 'Successfully verified optimal value range' in checked.stdout
 domain,coeff=context(row);record=dict(schema=1,domain=domain,coefficients=coeff,time=frac(t),objective=source['objective'],packing=mask,proof_sha256=sha,checker_sha256=hashlib.sha256(BIN.read_bytes()).hexdigest(),accepted=True,path=str(path.relative_to(ROOT)),source=source,info=info,bytes=len(text.encode()),native_cpu=native,adapter_cpu=adapter,checker_cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,checker_wall=time.perf_counter()-wall)
 record['seal']=receipt_seal(record);return record
class PointCache:
 def __init__(self,guarded=False):self.entries={};self.guarded=guarded
 def key(self,row,t):return (*context(row),Fraction(t))
 def put(self,row,t,r):
  assert valid_receipt(row,t,r,guarded=self.guarded);self.entries[self.key(row,t)]=r
 def get(self,row,t,packing=None):
  r=self.entries.get(self.key(row,t))
  return r if r is not None and valid_receipt(row,t,r,packing,self.guarded) else None
