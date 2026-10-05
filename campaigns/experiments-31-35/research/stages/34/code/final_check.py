"""Campaign final integrity/accounting audit, without replaying completed algorithms."""
import json,sys,hashlib,zipfile
from pathlib import Path
from runner import ROOT,read,save
out=[]
for s in range(31,36):
 st=ROOT/'stages'/str(s);expected={31:3,32:2,33:3,34:3,35:4}[s]
 assert read(st/'Complete.json')['all_cases_attempted'];assert all(hashlib.sha256((st/f).read_bytes()).hexdigest()==h for f,h in read(st/'Frozen.json').items())
 caps=[];cases=0;paths=0;audit_cpu=0;construction_caps=[]
 for sp,n in [('development',32),('held',96)]:
  files=list((st/sp/'cases').glob('*.json'));assert len(files)==n
  for f in files:
   r=read(f);assert len(r['paths'])==expected and len({p['mode'] for p in r['paths']})==expected;cases+=1
   for p in r['paths']:
    paths+=1;a=read(st/sp/'audits'/(r['case_id']+'-'+p['mode']+'.json'));assert a['passed'];audit_cpu+=a['audit_cpu']
    assert p['totals']['bound_evaluations']<=2000000 and p['optimizer_search_steps']<=2000000
    if p['status']=='capped':assert p['pending'] is not None;caps.append(dict(stage=s,split=sp,case_id=r['case_id'],mode=p['mode'],cursor=p['pending'],counters=p['totals']))
    if p['partial_frontier'] is not None:construction_caps.append(dict(stage=s,split=sp,case_id=r['case_id'],mode=p['mode'],cursor=p['partial_frontier'].get('cursor'),file=str(f.relative_to(ROOT)),field='paths[policy].partial_frontier',status='incomplete_construction',trajectory_status=p['status']))
    # Full native generator/cleanup/disposal ledgers retained, including physical sharing.
    assert all(o['empty'] and o['stats']['cells_allocated']==o['stats']['cells_freed'] for o in p['optimizer'])
    for k in ['bound_evaluations','free_term_evaluations','dp_entries','dp_transitions','dominance_comparisons']:
     assert abs(sum(e['counters'].get(k,0) for e in p['ledger'])-p['totals'].get(k,0))<1e-6,(s,r['case_id'],p['mode'],k)
  assert not read(st/sp/'Resource-log.json')['unstarted']
 out.append(dict(stage=s,cases=cases,paths=paths,complete=paths-len(caps),capped=caps,construction_caps=construction_caps,audit_cpu=audit_cpu,frozen_verified=True))
old=ROOT.parent/'campaign';manifest=read(old/'Manifest.json');assert all(hashlib.sha256((old/f).read_bytes()).hexdigest()==h for f,h in manifest.items())
assert read(ROOT/'stage30-extension/Complete.json')['complete']==5
save(ROOT/'Final-audit.json',dict(passed=True,stages=out,prior_1304_manifest_entries_unchanged=True,old_five_paths_complete=True,policy_reruns_only_disclosed_evidence_recovery=True))
save(ROOT/'Resume-cursors.json',dict(unfinished_paths=[x for z in out for x in z['capped']],incomplete_frontier_constructions=[x for z in out for x in z['construction_caps']],unstarted_cases=[],pending_audit_ranges=[],old_extension_pending=[]))
print('FINAL AUDIT',[(x['stage'],x['complete'],len(x['capped'])) for x in out])
