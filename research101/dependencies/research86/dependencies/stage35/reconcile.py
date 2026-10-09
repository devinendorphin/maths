"""Reconcile mutable case/marker views against immutable full policy records."""
import sys
from pathlib import Path
from runner import ROOT,read,save,specs,audit_path
for stage in [int(x) for x in sys.argv[1:]]:
 out=ROOT/'stages'/str(stage);records=[]
 for sp in ('development','held'):
  for f in (out/sp/'cases').glob('*.json'):
   row=read(f);names=[p[0] for p in specs(stage)];stored={p['mode']:p for p in row['paths']};changed=False
   for name in names:
    pf=out/sp/'path-results'/(row['case_id']+'-'+name+'.json')
    if pf.exists():
     path=read(pf)
     if name not in stored or stored[name]!=path:stored[name]=path;changed=True
    assert name in stored,(stage,sp,row['case_id'],name)
   if changed:
    row['paths']=[stored[n] for n in names];save(f,row);records.append(dict(split=sp,case_id=row['case_id'],action='restored case view from immutable full path records',policy_replayed=False))
   for path in row['paths']:
    af=out/sp/'audits'/(row['case_id']+'-'+path['mode']+'.json')
    if not af.exists() or not read(af)['passed']:audit_path(row,path,af);records.append(dict(split=sp,case_id=row['case_id'],policy=path['mode'],action='continued saved audit range',policy_replayed=False))
    assert read(af)['passed']
 save(out/'Record-reconciliation.json',dict(passed=True,records=records,policy_reruns=False))
 print('RECONCILED',stage,len(records),flush=True)
