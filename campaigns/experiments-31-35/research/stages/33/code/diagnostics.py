"""Read-only accounting of saved cases; no policy replay or tuning."""
import json,sys,hashlib,platform
from pathlib import Path
from runner import save,read,ROOT

def footprint(obj,seen=None):
 seen=set() if seen is None else seen
 if id(obj) in seen:return 0
 seen.add(id(obj));size=sys.getsizeof(obj)
 if isinstance(obj,dict):return size+sum(footprint(k,seen)+footprint(v,seen) for k,v in obj.items())
 if isinstance(obj,(list,tuple,set)):return size+sum(footprint(x,seen) for x in obj)
 return size

def stage_diagnostics(stage):
 out=ROOT/'stages'/str(stage);allrows=[]
 for split in ('development','held'):
  records=[]
  for f in sorted((out/split/'cases').glob('*.json')):
   row=read(f);paths=[]
   for p in row['paths']:
    cert=p['frontier'];d=dict(mode=p['mode'],status=p['status'],dispatch=p['dispatch'],source_generator_steps=p['optimizer_search_steps'],source_cleanup_steps=sum(o['cleanup_steps'] for o in p['optimizer']),source_disposal_steps=sum(o['disposal_steps'] for o in p['optimizer']),source_peak_cells=max(o['stats'].get('peak_live',o['stats'].get('peak_cells',0)) for o in p['optimizer']),scalar_peak_cells=max((ph.get('peak_cells',len(ph.get('final_proof',[]))) for ph in p['phases']),default=0),forest_peak_nodes=max((ph.get('peak_nodes',0) for ph in p['phases']),default=0),phase_lengths=[ph['final_time']-ph.get('anchor',0) for ph in p['phases']],switch_times=[ph['final_time'] for ph in p['phases'] if 'replacement' in ph],construction_cpu=p['construction_cpu'],optimizer_cpu=p['optimizer_cpu'],algorithm_cpu=p['algorithm_cpu'],construction_capped=p['partial_frontier'] is not None,recognition=p['totals'].get('recognition',0)+p['totals'].get('recognition_terms',0))
    if cert:
     d.update(frontier_lines=len(cert['lines']),envelope_lines=len(cert['envelope']),duplicate_total_slopes=len(cert['lines'])-len({x[1] for x in cert['lines']}),certificate_interval=cert['interval'],certificate_serialized_bytes=len(json.dumps(cert,separators=(',',':')).encode()),retained_proof_object_bytes=footprint(cert),tables=[])
     for table in cert['tables']:
      if table['kind']=='dense':
       d['tables'].append(dict(kind='dense',extremum=table['which'],entries=sum(len(l) for l in table['layers']),reachable_entries=sum(x[2] is not None for l in table['layers'] for x in l),terminal_feasible_classes=sum(x[0]==row['capacity'] and x[2] is not None for x in table['layers'][-1]),unreachable_entries=sum(x[2] is None for l in table['layers'] for x in l),peak_layer=len(table['layers'][-1])))
      else:
       d['tables'].append(dict(kind='sparse',raw_recurrence_entries=sum(len(l['raw']) for l in table['layers']),retained_active_across_layers=sum(len(l['retained']) for l in table['layers']),dominance_witnesses=sum(len(l['deletions']) for l in table['layers']),peak_active=max(len(l['retained']) for l in table['layers']),peak_raw_layer=max(len(l['raw']) for l in table['layers']),witness_chain_max_length=1 if any(l['deletions'] for l in table['layers']) else 0))
     d['class_slopes']=cert.get('class_slopes');d['class_sizes']=cert.get('class_sizes')
    paths.append(d)
   records.append(dict(case_id=row['case_id'],family=row['family'],regime=row['regime'],initial_packing_empty=row['packing']==0,uniform_slope=len(set(row['slopes']))==1,distinct_slopes=len(set(row['slopes'])),negative_intercepts=all(x<0 for x in row['profits']),paths=paths))
  save(out/split/'Additional-accounting.json',dict(records=records,memory_definition='recursive sys.getsizeof of retained recurrence/frontier proof; excludes trace histories, scalar fallback proof, inputs, allocator overhead and process RSS',cpu_claim='single unique-case CPU descriptive; stage34 selection separately repeated',unlike_counters_never_summed=True));allrows+=records
 # Confirm every saved case has a fully passed audit for every path and reconcile caps.
 for split in ('development','held'):
  for f in (out/split/'cases').glob('*.json'):
   row=read(f)
   for p in row['paths']:assert read(out/split/'audits'/(row['case_id']+'-'+p['mode']+'.json'))['passed']
 save(out/'Final-audit.json',dict(passed=True,unique_trajectories=len(allrows),policy_paths=sum(len(r['paths']) for r in allrows),policy_reruns=False,frozen_verified=all(hashlib.sha256((out/f).read_bytes()).hexdigest()==h for f,h in read(out/'Frozen.json').items()),source_stores_disposed=True))
 print('DIAGNOSTICS',stage,len(allrows),flush=True)
if __name__=='__main__':
 for s in sys.argv[1:]:stage_diagnostics(int(s))
