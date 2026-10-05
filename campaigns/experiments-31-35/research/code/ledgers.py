"""Read-only original-time work ledgers; unlike counters remain separate."""
import sys,statistics
from pathlib import Path
from runner import ROOT,read,save

def work_ledger(row,path):
 keys=set(path['totals']);keys={k for k in keys if not k.endswith('cpu')};events=[]
 def add(t,kind,ct):events.append(dict(time=t,kind=kind,counters={k:v for k,v in ct.items() if k in keys and v}))
 for e in path['ledger']:
  if e['kind']=='construction':add(0,'frontier_construction',e['counters'])
 for ph in path['phases']:
  if ph['kind']=='frontier':
   ct=ph['totals'].copy();ct['factor_dispatches']=0;add(ph['anchor'],'frontier_horizon',ct)
   if ph['status']=='factor_handoff':add(ph['final_time'],'factor_dispatch',{'factor_dispatches':1});add(ph['final_time'],'scalar_boundary_repair',ph['handoff']['counters'])
  else:
   sums={k:0 for k in keys}
   for e in ph['events']:
    add(e['time'],'scalar_expiry_including_failed_detection',e['counters'])
    for k in keys:sums[k]+=e['counters'].get(k,0)
    cert=e['previous_certificate'];add(e['previous_time'],'scalar_horizon',{'horizon_evaluations':cert['evaluations']});sums['horizon_evaluations']=sums.get('horizon_evaluations',0)+cert['evaluations']
   if ph['status'] not in ('packing_lost','capped','normalized_forever'):
    cert=ph['final_certificate'];add(ph['last_verified_time'],'scalar_horizon',{'horizon_evaluations':cert['evaluations']});sums['horizon_evaluations']=sums.get('horizon_evaluations',0)+cert['evaluations']
   remainder={k:ph['totals'].get(k,0)-sums.get(k,0) for k in keys};assert all(v>=0 for v in remainder.values());add(ph['anchor'],'scalar_initialization_recognition_lineage',remainder)
 observed={k:sum(e['counters'].get(k,0) for e in events) for k in keys}
 # Frontier-policy shortcut recognition happens before its scalar phase.
 remainder={k:path['totals'].get(k,0)-observed.get(k,0) for k in keys};assert all(v>=0 for v in remainder.values());add(0,'policy_recognition',remainder)
 for opt in path['optimizer']:events.append(dict(time=opt['time'],kind='native_optimizer',counters=dict(native_generator_steps=opt['construction_steps'],native_cleanup_steps=opt['cleanup_steps'],native_disposal_steps=opt['disposal_steps'])))
 keys|={'native_generator_steps','native_cleanup_steps','native_disposal_steps'};arr={k:[0]*257 for k in keys}
 for e in events:
  for k,v in e['counters'].items():arr[k][e['time']]+=v
 for k in keys:
  for t in range(1,257):arr[k][t]+=arr[k][t-1]
 return events,arr

def run(stage):
 out=ROOT/'stages'/str(stage)
 for split in ('development','held'):
  rows=[read(p) for p in (out/split/'cases').glob('*.json')];comparisons=[];records=[]
  for row in rows:
   ledgers={};times={0,64,128,256}
   for path in row['paths']:
    events,arrays=work_ledger(row,path);ledgers[path['mode']]=arrays;times|={e['time'] for e in events};records.append(dict(case_id=row['case_id'],policy=path['mode'],status=path['status'],events=events,common_time_cumulative={str(t):{k:a[t] for k,a in arrays.items()} for t in sorted(times)}))
   base=row['paths'][0];b=ledgers[base['mode']]
   for path in row['paths'][1:]:
    measures={};q=ledgers[path['mode']]
    for k in sorted(b):
     diff=[x-y for x,y in zip(b[k],q[k])];pos=[t for t,x in enumerate(diff) if x>0];lastbad=max((t for t,x in enumerate(diff) if x<=0),default=-1)
     measures[k]=dict(saving=diff[-1],initial_debt=max(0,-diff[0]),first_strict_advantage=pos[0] if pos else None,first_persistent_advantage=lastbad+1 if diff[-1]>0 else None,common_time_pairs={str(t):[b[k][t],q[k][t]] for t in sorted(times)})
    comparisons.append(dict(case_id=row['case_id'],mode=path['mode'],paired=base['status']!='capped' and path['status']!='capped',recognized=row['profits']==row['slopes'] or path['frontier'] is not None,measures=measures))
  aggregates={}
  for mode in [p['mode'] for p in rows[0]['paths'][1:]]:
   cmp=[x for x in comparisons if x['mode']==mode and x['paired']];agg={}
   for k in cmp[0]['measures'] if cmp else []:
    values=[x['measures'][k]['saving'] for x in cmp];largest=max(values,default=0);agg[k]=dict(pairs=len(cmp),saving=sum(values),benefited=sum(x>0 for x in values),harmed=sum(x<0 for x in values),tied=sum(x==0 for x in values),without_largest=sum(values)-largest,excluding_recognized=sum(x['measures'][k]['saving'] for x in cmp if not x['recognized']))
   aggregates[mode]=agg
  save(out/split/'Complete-work-ledgers.json',dict(counter_units_never_added=True,records=records,comparisons=comparisons,aggregates=aggregates,CPU_note='Measured CPU and conservative common-time CPU payback are in Summary.json; these ledgers reconstruct exact operation locations including horizon evaluations at original phase anchors.'))
 print('LEDGERS',stage,flush=True)
if __name__=='__main__':
 for x in sys.argv[1:]:run(int(x))
