"""Include the selector itself inside the complete route cost boundary."""
import json
from pathlib import Path
import native as N
from routes import choose,stream
ROOT=Path(__file__).resolve().parents[1]
for name,sha in json.loads((ROOT/'Selector-freeze.json').read_text())['files'].items():assert N.sha((ROOT/name).read_bytes())==sha,name
rows=json.loads((ROOT/'Inputs.json').read_text());policy=json.loads((ROOT/'Policy.json').read_text())
streams=dict(sparse=[0,6],dense=[N.Fraction(i,2) for i in range(13)],repeated=[0,2,0,2,0,2,0,2,0,2,0,2,0]);records=[]


def trial(row,bucket,forecast,stage,repeat,requested):
    begin=N.clock();obs=streams[bucket];selected=choose(row,obs,policy,forecast);selection=N.elapsed(begin)['cpu']
    d,m=stream(row,obs,selected);m['method_total']=m['total'];m['phases']['policy_selection']=selection
    d.update(bucket=bucket,requested_method=requested,selected_method=selected,forecast_count=forecast,selector_repair=True)
    m['total']=N.elapsed(begin);m['phase_sum']=sum(m['phases'].values());m['residual_cpu']=m['total']['cpu']-m['phase_sum']
    return dict(stage=stage,repeat=repeat,logical=d,measurements=m)


for row in [r for r in rows if r['split']=='heldout']:
    for bucket in streams:
        for repeat in range(3):records.append(trial(row,bucket,None,126,repeat,'policy'))
for case in ['eval8','eval12']:
    row=next(r for r in rows if r['case_id']==case)
    for bucket in ['sparse','dense']:
        for repeat in range(3):
            methods=['policy-correct','policy-wrong'];rot=repeat%2;methods=methods[rot:]+methods[:rot]
            for method in methods:
                forecast=len(streams[bucket]) if method=='policy-correct' else (13 if bucket=='sparse' else 2)
                records.append(trial(row,bucket,forecast,130,repeat,method))
(ROOT/'Selector-results.json').write_text(json.dumps(records,indent=2)+'\n');print('Selector-inclusive routes completed:',len(records))
