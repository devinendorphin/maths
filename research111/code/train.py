import json,pathlib,statistics
from routes import solve_stream
ROOT=pathlib.Path(__file__).resolve().parents[1]
rows=[r for r in json.loads((ROOT/'Inputs.json').read_text()) if r['split']=='training'];records=[]
for row in rows:
 for repeat in range(3):
  for width in [2,4,8]:records.append(dict(case_id=row['case_id'],task='window',repeat=repeat,**solve_stream(row,list(range(9)),'snapshot',width)))
  for density,obs in [('dense',list(range(9))),('sparse',[0,4,8])]:
   methods=['point','factor','guarded','snapshot'];methods=methods[repeat:]+methods[:repeat]
   for method in methods:records.append(dict(case_id=row['case_id'],task='density',density=density,repeat=repeat,**solve_stream(row,obs,method)))
width_scores={w:statistics.median(r['cpu'] for r in records if r['task']=='window' and r['width']==w) for w in [2,4,8]}
policy={d:min(['point','factor','guarded','snapshot'],key=lambda m:statistics.median(r['cpu'] for r in records if r['task']=='density' and r['density']==d and r['method']==m)) for d in ['dense','sparse']}
(ROOT/'Training.json').write_text(json.dumps(dict(window_width=min(width_scores,key=width_scores.get),window_scores=width_scores,density_policy=policy,records=records,heldout_used=False),indent=2)+'\n')
print('Training frozen choices',policy,min(width_scores,key=width_scores.get),flush=True)
