"""Recover only policy result records missing from earlier checkpoint versions.
Original aggregate counts are retained; repeat work is disclosed separately.
"""
import json,sys,subprocess,uuid,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 with q.open('w') as f:json.dump(x,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
 q.replace(p)
if sys.argv[1]=='worker':
 stage=int(sys.argv[2]);split=sys.argv[3];cid=sys.argv[4];name=sys.argv[5];sys.path.insert(0,str(ROOT/'stages'/str(stage)/'code'));import runner as R
 f=ROOT/'stages'/str(stage)/split/'cases'/(cid+'.json');row=read(f);cache={int(k):v for k,v in row.get('optimizer_cache',{}).items()}
 for pp in row['paths']:
  for ph in pp['phases']:
   if 'replacement' in ph:cache[ph['final_time']]=ph['replacement']
 pol=dict(R.specs(stage))[name];p=R.run_policy(row,name,pol,cache);save(ROOT/'stages'/str(stage)/split/'path-results'/(cid+'-'+name+'.json'),p);print(json.dumps({'status':p['status'],'candidate_evaluations':p['totals']['bound_evaluations']}));raise SystemExit
stage=int(sys.argv[1]);out=ROOT/'stages'/str(stage);names=[x for x in read(out/'held/Summary.json')['modes']];records=[]
for split in ('development','held'):
 rows=[read(f) for f in (out/split/'cases').glob('*.json')];summary=read(out/split/'Summary.json')
 for row in rows:
  missing=[name for name in names if not any(p['mode']==name for p in row['paths'])]
  for name in missing:
   mode=summary['modes'][name];others=[p for r in rows for p in r['paths'] if p['mode']==name]
   original_totals={k:v-sum(p['totals'].get(k,0) for p in others) for k,v in mode['totals'].items()}
   original_cpu=mode['algorithm_cpu']-sum(p['algorithm_cpu'] for p in others);old_fields={k:mode[k]-sum(p[k] for p in others) for k in ('optimizer_search_steps','optimizer_cpu','switches','construction_cpu')}
   proc=subprocess.run([sys.executable,__file__,'worker',str(stage),split,row['case_id'],name],check=True,capture_output=True,text=True)
   pf=out/split/'path-results'/(row['case_id']+'-'+name+'.json');path=read(pf);assert path['totals']['bound_evaluations']==original_totals['bound_evaluations']
   for key in ('dp_entries','dp_transitions','splits','probes','hits'):assert path['totals'].get(key,0)==original_totals.get(key,0)
   original_comparison=next(cmp for cmp in summary['comparisons'] if cmp['case_id']==row['case_id'] and cmp['mode']==name)
   records.append(dict(case_id=row['case_id'],split=split,policy=name,original_execution=dict(totals=original_totals,algorithm_cpu=original_cpu,**old_fields),original_comparison=original_comparison,repeated_execution=dict(totals=path['totals'],algorithm_cpu=path['algorithm_cpu'],optimizer_search_steps=path['optimizer_search_steps'],optimizer_cpu=path['optimizer_cpu']),reason='case file retained earlier partial version; missing policy record regenerated only; original aggregates and all surviving paths retained',missing_trace_cannot_be_recovered=True))
   row['paths'].append(path);row['paths'].sort(key=lambda p:names.index(p['mode']));save(out/split/'cases'/(row['case_id']+'.json'),row)
   print('RECOVERED',stage,split,row['case_id'],name,flush=True)
old=read(out/'Evidence-recovery.json')['records'] if (out/'Evidence-recovery.json').exists() else []
save(out/'Evidence-recovery.json',dict(records=old+records,original_summary_unchanged=True,repeated_work_not_pooled_into_unique_case_headlines=True))
