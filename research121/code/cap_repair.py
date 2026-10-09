"""Separately frozen repair: exercise a preparation cap that actually binds."""
import json
from pathlib import Path
import native as N
from routes import stream
ROOT=Path(__file__).resolve().parents[1]
for name,sha in json.loads((ROOT/'Supplement-freeze.json').read_text())['files'].items():assert N.sha((ROOT/name).read_bytes())==sha,name
rows=json.loads((ROOT/'Inputs.json').read_text());row=next(r for r in rows if r['case_id']=='eval12');records=[]
for bucket,obs in [('sparse',[0,6]),('dense',[N.Fraction(i,2) for i in range(13)])]:
    for repeat in range(3):
        d,m=stream(row,obs,'snapshot',certificate_cap=2);assert d['preparation_capped'] and d['failed_probes']==1
        d.update(bucket=bucket,requested_method='snapshot-cap2-repair',selected_method='snapshot',supplement=True)
        records.append(dict(stage=130,repeat=repeat,logical=d,measurements=m))
(ROOT/'Supplement.json').write_text(json.dumps(records,indent=2)+'\n')
print('Completed separately frozen cap repair:',len(records),'records')
