import collections,copy,hashlib,json,pathlib,resource,subprocess,sys,time
from fractions import Fraction
import dp,checker
from routes import ROOT,admit,cert,clock,elapsed,encode,model,solve_stream

def save(name,data):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(data))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 start=time.perf_counter();freeze=json.loads((ROOT/'Freeze.json').read_text())
 for name,sha in freeze['files'].items():assert digest(ROOT/name)==sha,name
 rows=json.loads((ROOT/'Inputs.json').read_text());held=[r for r in rows if r['split']=='heldout'];training=json.loads((ROOT/'Training.json').read_text());results=[]
 def emit(stage,row,variant,body,c):
  assert time.perf_counter()-start<300
  results.append(dict(stage=stage,case_id=row['case_id'],variant=variant,**body,**elapsed(c)))
 # Availability reports are not successful solve/check workers.
 caps=json.loads((ROOT/'Capabilities.json').read_text())
 save('Availability.json',{'111':dict(status='unavailable',reason=caps['blocking_dependency']),'112':dict(status='unsupported',native_scip_certificates=0),'113_native_vipr_amortization':dict(status='unimplemented',tested_route='independent DP recurrence checker')})
 # 113: same request order, startup per proof versus one stateless verifier process.
 requests=[]
 for row in held:
  good=cert(row,4);bad=copy.deepcopy(good);bad['table'][-1][-1]+=1
  changed=dict(row,capacity=row['capacity']+1)
  requests.extend([dict(row=row,time=4,certificate=good,expected=True),dict(row=row,time=4,certificate=bad,expected=False),dict(row=changed,time=4,certificate=good,expected=False),dict(row=row,time=4,certificate=good,expected=True)])
 for mode in ['per-request','persistent']:
  c=clock();decisions=[];peak_combined=0
  if mode=='persistent':process=subprocess.Popen([sys.executable,str(ROOT/'code/worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  for request in requests:
   line=json.dumps(request)+'\n'
   if mode=='per-request':
    p=subprocess.run([sys.executable,str(ROOT/'code/worker.py')],input=line,capture_output=True,text=True,timeout=10,check=True);decision=json.loads(p.stdout)['accepted']
   else:
    process.stdin.write(line);process.stdin.flush();decision=json.loads(process.stdout.readline())['accepted']
    def rss(pid):
     for line in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines():
      if line.startswith('VmRSS:'):return int(line.split()[1])
     return 0
    peak_combined=max(peak_combined,rss(__import__('os').getpid())+rss(process.pid))
   assert decision==request['expected'];decisions.append(decision)
  if mode=='persistent':process.stdin.close();process.wait(timeout=10);assert process.returncode==0
  emit(113,held[0],mode,dict(requests=requests,decisions=decisions,sampled_combined_rss_kib=peak_combined,processes_started=20 if mode=='per-request' else 1),c)
 for row in held:
  # 114: decomposition preserves total, including serialization/write/read and admission.
  c=clock();ticks={};s=clock();certificate=dp.produce(row,4);ticks['solver_cpu']=elapsed(s)['cpu'];s=clock();assert admit(row,4,certificate);ticks['checker_cpu']=elapsed(s)['cpu']
  s=clock();payload=encode(certificate);ticks['encoding_cpu']=elapsed(s)['cpu'];s=clock();path=ROOT/'evidence/decomposition'/f"{row['case_id']}.json";path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload);loaded=json.loads(path.read_bytes());assert admit(row,4,loaded);ticks['io_and_readmission_cpu']=elapsed(s)['cpu']
  emit(114,row,'dp-components',dict(certificate=str(path.relative_to(ROOT)),components=ticks,component_sum=sum(ticks.values()),exact_objective=certificate['objective'],native_scip_decomposition='unsupported; no native certificates'),c)
  # 115: bounded larger fixture validation, explicit certificate byte/cell caps.
  for t in [0,4,8]:
   c=clock();certificate=cert(row,t);payload=encode(certificate);assert len(payload)<=1048576
   emit(115,row,str(t),dict(time=[t,1],certificate=certificate,bytes=len(payload),cell_cap=200000,storage_cap_bytes=1048576),c)
  # 117: width policy was trained before held-out evaluation.
  for repeat in range(3):
   for label,width in [('fixed2',2),('fixed4',4),('fixed8',8),('trained',training['window_width'])]:
    c=clock();r=solve_stream(row,list(range(9)),'snapshot',width);emit(117,row,f'{label}/{repeat}',dict(policy=label,repeat=repeat,route=r),c)
  # 118: compare all routes; separately execute the frozen density-policy choice.
  for density,obs in [('dense',list(range(9))),('sparse',[0,4,8])]:
   for repeat in range(3):
    methods=['point','factor','guarded','snapshot'];methods=methods[repeat:]+methods[:repeat]
    for method in methods+['policy']:
     c=clock();selected=training['density_policy'][density] if method=='policy' else method
     r=solve_stream(row,obs,selected);emit(118,row,f'{density}/{repeat}/{method}',dict(density=density,repeat=repeat,method=method,selected=selected,route=r),c)
  # 119: two-entry LRU cache, observed retained bytes, eviction and changed-model miss.
  c=clock();cache=collections.OrderedDict();history=[];hits=evictions=0
  for index,t in enumerate([0,4,0,8,4,8,0]):
   key=(json.dumps(model(row),sort_keys=True),t)
   hit=key in cache
   if hit:certificate=cache.pop(key);assert admit(row,t,certificate);hits+=1
   else:certificate=cert(row,t)
   cache[key]=certificate
   if len(cache)>2:cache.popitem(last=False);evictions+=1
   history.append(dict(time=t,hit=hit,objective=certificate['objective'],packing=certificate['packing'],entries=len(cache),serialized_bytes=sum(len(encode(p)) for p in cache.values())))
  changed=dict(row,capacity=row['capacity']+1);changed_key=(json.dumps(model(changed),sort_keys=True),0);assert changed_key not in cache;new=cert(changed,0)
  emit(119,row,'lru2',dict(history=history,hits=hits,evictions=evictions,changed_model_miss=True,changed_model=changed,changed_certificate=new,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),c)
  # 120: strict declared scope with dependency identity plus model/time binding.
  c=clock();original=cert(row,4);dependency=digest(ROOT/'code/checker.py');controls=[]
  for kind in ['capacity','weight','domain','nonlinear','dependency','time']:
   changed=copy.deepcopy(row);time_query=4;identity=dependency
   if kind=='capacity':changed['capacity']+=1
   elif kind=='weight':changed['weights'][0]+=1
   elif kind=='domain':changed['domain']='continuous'
   elif kind=='nonlinear':changed['objective_class']='quadratic';changed['quadratic']=[1]*row['n']
   elif kind=='dependency':identity='changed-checker'
   else:time_query=5
   accepted=identity==dependency and admit(changed,time_query,original);assert not accepted
   controls.append(dict(kind=kind,changed_model=changed,time=time_query,identity=identity,accepted=accepted))
  assert admit(row,4,original)
  emit(120,row,'scope',dict(certificate=original,dependency=dependency,controls=controls,restored_accepted=True),c)
 # 116: fixed known crossing plus generic endpoint-neighborhood rational controls.
 for row in held+[r for r in rows if r['case_id']=='crossing']:
  for t in [Fraction(0),Fraction(1,1000),Fraction(1499,1000),Fraction(3,2),Fraction(1501,1000),Fraction(row['end'])-Fraction(1,1000),Fraction(row['end'])]:
   c=clock();certificate=cert(row,t);emit(116,row,str(t),dict(time=[t.numerator,t.denominator],certificate=certificate),c)
 save('Results.json',results);save('Execution.json',dict(status='complete',workers=len(results),heldout_models=len(held),training_models=2,control_models=1,wall=time.perf_counter()-start,unsupported_experiments=[112],capability_experiment=111))
 print(json.dumps(json.loads((ROOT/'Execution.json').read_text())),flush=True)
if __name__=='__main__':run()
