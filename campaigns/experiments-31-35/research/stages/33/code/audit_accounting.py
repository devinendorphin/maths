"""Post-run accounting audit, independent prefix-ledger implementation."""
import json,hashlib
from pathlib import Path
from audit_repeated import audit_case

def audit_stage(stage):
    p=Path('.');data=json.loads((p/(stage+'-results.json')).read_text());summary=json.loads((p/(stage+'-summary.json')).read_text());checks=[];checked=0
    lookup={x['case_id']:x for x in summary['comparisons']}
    for x in data['rows']:
        checks.append(audit_case(x));base=x['paths'][0]
        for path in x['paths'][1:4]:
            comp=next(z for z in lookup[x['case_id']]['rows'] if z['mode']==path['mode'])
            expected_saving=base['totals']['bound_evaluations']-path['totals']['bound_evaluations'];assert comp['final_saving']==expected_saving
            events=[e for e in path['events'] if e['action']=='rebuild'];assert comp['attempted']==bool(events)
            if not events:continue
            e=events[0];assert comp['successful']==e['result']['success']
            if not e['result']['success']:continue
            delta=[0]*(x['end']+1)
            for event in base['events']:delta[event['time']]+=event['counters']['bound_evaluations']
            for event in path['events']:delta[event['time']]-=event['counters']['bound_evaluations']
            for t in range(1,len(delta)):delta[t]+=delta[t-1]
            t0=e['time'];assert delta[-1]==expected_saving and delta[:t0]==[0]*t0
            assert comp['initial_extra_cost']==-delta[t0] and comp['savings_by_time']==delta[t0:]
            first=next((t for t in range(t0,len(delta)) if delta[t]>0),None)
            nonpositive=[t for t in range(t0,len(delta)) if delta[t]<=0]
            durable=None if delta[-1]<=0 else (max(nonpositive)+1 if nonpositive else t0)
            assert comp['first_advantage_time']==first and comp['durable_advantage_time']==durable
            assert comp['payback_delay']==(None if durable is None else durable-t0)
            assert comp['compacted']==(len(e['result']['proof'])<e['prior_cells']);checked+=1
    assert all(s['empty'] for s in data['sources']) and not data['unstarted']
    return dict(passed=True,cases=len(data['rows']),events=sum(x['events'] for x in checks),cells=sum(x['cells'] for x in checks),payback_ledgers=checked,source_stores_disposed=len(data['sources']))

if __name__=='__main__':
    p=Path('.');result={s:audit_stage(s) for s in ('development','held')};f=json.loads((p/'Frozen.json').read_text());assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in f.items())
    (p/'Final-audit.json').write_text(json.dumps(dict(frozen_verified=True,post_run_accounting_audit=True,results=result),indent=2));print(json.dumps(result))
