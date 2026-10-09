import hashlib,json,pathlib,resource,sys,time
from fractions import Fraction
import dp,checker
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'dependencies/research86/code'))
import certificates,economy
certificates.ROOT=ROOT

def clock():
 a=resource.getrusage(resource.RUSAGE_CHILDREN);return time.process_time(),a.ru_utime+a.ru_stime,time.perf_counter()
def elapsed(c):
 a=clock();return dict(cpu=a[0]-c[0]+a[1]-c[1],wall=a[2]-c[2])
def encode(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def model(row):return {k:row[k] for k in ['n','weights','capacity','profits','slopes']}
def admit(row,t,cert):
 if row.get('domain','binary')!='binary' or row.get('objective_class','affine')!='affine' or any(row.get('quadratic',[])):return False
 return checker.verify(row,t,cert)
def cert(row,t):
 c=dp.produce(row,t,200000);assert admit(row,t,c);return c
def objective(row,t,mask):
 t=Fraction(t);return sum((t.denominator*p+t.numerator*s) for i,(p,s) in enumerate(zip(row['profits'],row['slopes'])) if mask>>i&1)
def solve_stream(row,obs,method,width=4):
 begin=clock();proofs=[];packings=[];windows=[];failed=0;extra={}
 if method=='guarded':
  modified=dict(row,observations=obs);data=economy.run(modified,'guarded');packings=data['packings'];extra={'vipr':data}
 elif method=='factor' and economy.factor(row) is not None:
  c=cert(row,0);proofs.append(c);packings=[c['packing']]*len(obs)
 elif method=='snapshot':
  cache={};active=[]
  for t in obs:
   t=Fraction(t);found=next((w for w in active if Fraction(*w['left'])<=t<=Fraction(*w['right'])),None)
   if found:packings.append(found['packing']);continue
   left=t;right=min(Fraction(row['end']),left+width)
   a=cert(row,left);b=cert(row,right);proofs.extend([a,b]);cache[left]=a;cache[right]=b
   if a['packing']==b['packing']:
    w={'left':[left.numerator,left.denominator],'right':[right.numerator,right.denominator],'packing':a['packing']};active.append(w);windows.append(w);packings.append(a['packing'])
   else:failed+=1;packings.append(a['packing'])
 else:
  for t in obs:
   c=cert(row,t);proofs.append(c);packings.append(c['packing'])
 # Serialize and save all evidence as part of each full path measurement.
 evidence={'model':model(row),'observations':obs,'packings':packings,'dp_proofs':proofs,'windows':windows,'failed_probes':failed,**extra}
 payload=encode(evidence);path=ROOT/'evidence/streams'/f'{hashlib.sha256(payload).hexdigest()}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
 assert len(payload)<=8*1024*1024,'proof storage cap'
 return dict(method=method,width=width,observations=obs,packings=packings,failed_probes=failed,dp_certificates=len(proofs),dp_raw_bytes=sum(len(encode(p)) for p in proofs),evidence=str(path.relative_to(ROOT)),evidence_sha256=hashlib.sha256(payload).hexdigest(),evidence_bytes=len(payload),**elapsed(begin))
