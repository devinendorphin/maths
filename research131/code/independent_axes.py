"""Separately frozen rank-two objective control; no previous run is replaced."""
import json
from pathlib import Path
import native as N
from campaign import point,value,inside
ROOT=Path(__file__).resolve().parents[1]
for name,sha in json.loads((ROOT/'Axes-freeze.json').read_text())['files'].items():assert N.sha((ROOT/name).read_bytes())==sha,name
row=json.loads((ROOT/'Axes-input.json').read_text());facts=[];vertices=[];start=N.clock()
for q in row['vertices']:
    f,cost=point(row,q);facts.append(f);vertices.append(value(row,row['candidate'],q)==N.Fraction(f['fact']['objective'],f['scale']))
admitted=all(vertices);assert admitted;outputs=[]
for q in row['queries']:
    reused=inside(row['vertices'],q)
    if reused:mask=row['candidate']
    else:
        f,cost=point(row,q);facts.append(f);mask=f['fact']['packing']
    v=value(row,mask,q);outputs.append(dict(parameter=q,packing=mask,value=[v.numerator,v.denominator],reused=reused))
(ROOT/'Axes-results.json').write_text(json.dumps(dict(stage=132,logical=dict(row=row,admitted=admitted,facts=facts,outputs=outputs),measurements=dict(total=N.elapsed(start))),indent=2)+'\n')
print('Independent priority axes completed')
