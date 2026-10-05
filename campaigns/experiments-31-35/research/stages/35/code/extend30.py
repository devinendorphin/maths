import json,time,copy,hashlib
from pathlib import Path
import engine as E
import horizon as H
from source_clean import solve
from audit_new import Auditor
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'campaign'
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');q.write_text(json.dumps(x,separators=(',',':')));q.replace(p)
def audit_phase(row,phase,initial,start,cool,out):
 # Bounded event batches; verified prefixes committed between batches.
 events=phase['events'];proof=initial;t=start;checks=[];auditor=None;resume_index=0
 if Path(out).exists():
  prior=json.loads(Path(out).read_text());checks=prior.get('batches',[]);resume_index=prior.get('verified_event_prefix',0)
  if prior.get('passed'):return checks
  if resume_index:
   prev=events[resume_index-1];proof=prev['result']['proof'];t=prev['time'];cool=prev['cooldown_after']
 for i in range(resume_index,max(1,len(events)),4):
  batch=events[i:i+4];last=i+len(batch)>=len(events);part=copy.copy(phase);part['events']=batch
  total=E.empty_counts()
  for e in batch:E.plus(total,e['counters'])
  part['totals']=total
  if not last:
   proofend=batch[-1]['result']['proof'];anchor=batch[-1]['time'];part.update(status='window_complete',final_time=anchor,last_verified_time=anchor,final_proof=proofend,final_certificate=H.certificate_horizon(proofend,row['weights'],[p+anchor*v for p,v in zip(row['profits'],row['slopes'])],row['slopes'],phase['packing']))
  end=phase['final_time'] if last else part['final_time']
  
  if auditor is None or time.perf_counter()>auditor.deadline-15:auditor=Auditor(row['weights'],row['profits'],row['slopes'],row['capacity'])
  a=auditor;cpu=time.process_time();a.path(part,phase['packing'],proof,t,end,resume_cooldown=cool)
  # Independent fractional branch validation in addition to saved-evidence validator.
  from fractions import Fraction
  for e in batch:
   q=[p+e['time']*v for p,v in zip(row['profits'],row['slopes'])]
   for tr in e['result'].get('trace',[]):
    f,u,r=tr['domain'];expected=None
    for j in sorted((j for j in range(len(q)) if u>>j&1 and q[j]>0),key=lambda j:(-Fraction(q[j],row['weights'][j]),j)):
     if row['weights'][j]<=r:r-=row['weights'][j]
     elif r>0:expected=j;break
     else:break
    assert expected==tr['pivot']
  checks.append(dict(event_range=[i,i+len(batch)],passed=True,cpu=time.process_time()-cpu,checks=a.checks));save(out,dict(passed=last,verified_event_prefix=i+len(batch),batches=checks))
  if batch and batch[-1]['result'].get('success'):
   proof=batch[-1]['result']['proof'];t=batch[-1]['time'];cool=batch[-1]['cooldown_after']
 return checks

def main():
 out=ROOT/'stage30-extension';out.mkdir(exist_ok=True)
 curs=json.loads((OLD/'stages/30/Resume-cursors.json').read_text())['unfinished_policy_paths'];results=[]
 save(out/'Protocol.json',dict(total_candidate_budget=2000000,old_spent_counts=True,additional_wall_budget=120,partial_attempt_restart_charged=True,preserve_old=True,limits=E.LIMITS))
 for cursor in sorted(curs,key=lambda x:(x['case_id'],x['policy'])):
  target=out/(cursor['case_id']+'-'+cursor['policy']+'.json')
  if target.exists():results.append(json.loads(target.read_text()));continue
  row=json.loads((OLD/cursor['source_case']).read_text());path=next(p for p in row['paths'] if p['mode']==cursor['policy']);ph=path['phases'][cursor['phase']];m=ph['packing'];proof=ph['final_proof'];start=ph['last_verified_time'];forest=ph['final_forest'];cool=cursor['cooldown_before_attempt'];spent=path['totals']['bound_evaluations'];cache={int(k):v for k,v in row['optimizer_cache'].items()};phases=[];tot=E.empty_counts();wall=time.perf_counter();optimizer_steps=path['optimizer_search_steps'];optimizer_extra=[]
  assert spent==500000 and start+1==cursor['first_uncompleted_attempt_time'] and row['slopes']==[1]*16 and row['packing']==0
  a=Auditor(row['weights'],row['profits'],row['slopes'],row['capacity']);a.cover(proof);a.prices(proof,start,m);a.forest(forest,proof);a.cert(proof,start,m,ph['final_certificate'])
  while True:
   nxt=E.run(row['weights'],row['profits'],row['slopes'],row['capacity'],m,proof,path['spec'],256,phase_start=start,spent=spent+tot['bound_evaluations'],elapsed=time.perf_counter()-wall,resume_forest=forest,resume_cooldown=cool);phases.append(nxt);E.plus(tot,nxt['totals'])
   result=dict(cursor=cursor,extension_phases=phases,extension_totals=tot,original_totals=path['totals'],cumulative_candidate_evaluations=spent+tot['bound_evaluations'],status=nxt['status'],optimizer_extra=optimizer_extra,optimizer_cache=cache,algorithm_wall=time.perf_counter()-wall)
   save(target,result)
   audit_phase(row,nxt,proof,start,cool,out/(target.stem+'-audit-'+str(len(phases)-1)+'.json'))
   if nxt['status']!='packing_lost':break
   start=nxt['final_time']
   try:
    if start not in cache:cache[start]=solve(row['weights'],[p+start*v for p,v in zip(row['profits'],row['slopes'])],row['capacity'])
    opt=cache[start];optimizer_steps+=opt['construction_steps'];optimizer_extra.append(opt)
    if optimizer_steps>2000000:raise E.Cap('cumulative optimizer cap')
   except E.Cap as exc:result['status']='capped';result['pending_optimizer']=dict(time=start,reason=str(exc));save(target,result);break
   nxt['replacement']=opt;m=opt['packing'];proof=opt['proof'];forest=None;cool=0
  results.append(result);print('EXTENSION',cursor['case_id'],cursor['policy'],result['status'],result['cumulative_candidate_evaluations'],flush=True)
  pending=[]
  for rr in results:
   if rr['status']=='capped':
    pp=rr['extension_phases'][-1];pending.append(dict(file=rr['cursor']['case_id']+'-'+rr['cursor']['policy']+'.json',phase=len(rr['extension_phases'])-1,packing=pp['packing'],anchor=pp['last_verified_time'],next_time=pp['final_time'],cooldown=pp['events'][-1]['cooldown_before'] if pp['events'] else 0,cumulative_candidate_evaluations=rr['cumulative_candidate_evaluations']))
  save(out/'Resume-cursors.json',dict(pending=pending,unstarted=[x for x in curs if not any(x['case_id']==r['cursor']['case_id'] and x['policy']==r['cursor']['policy'] for r in results)]))
 save(out/'Complete.json',dict(attempted=len(results),complete=sum(x['status']!='capped' for x in results),capped=sum(x['status']=='capped' for x in results)))
if __name__=='__main__':main()
