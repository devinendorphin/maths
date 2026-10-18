"""Re-audit serialized results using only the independent witness evaluator."""
import argparse,json,hashlib
from pathlib import Path
from fractions import Fraction as Q
import audit


def replay(inputs_path,results_path,output):
    assert not output.exists(),'Never overwrite audit evidence'
    inputs=json.loads(inputs_path.read_text());result=json.loads(results_path.read_text())
    models={m['id']:m for group in ('tiny','heldout') for m in inputs[group]}
    tiny={m['id'] for m in inputs['tiny']}
    allflows={k:audit.enumerate_flows(models[k]) for k in tiny}
    checked_queries=checked_intervals=bad=0;seen=set()
    for r in result['records']:
        m=models[r['model']];x=r['flow'];p=r['interval'];key=(m['id'],p['edge'])
        assert key not in seen;seen.add(key)
        assert audit.admit_interval(m,x,r['base_pi'],p)
        if m['id'] in tiny:assert (p['lower'],p['upper'])==audit.exhaustive_interval(m,x,p['edge'],allflows[m['id']])
        for q in r['queries']:
            t=Q(q['delta']);new=json.loads(json.dumps(m))
            i=p['edge'];new['edges'][i]['c']=str(Q(new['edges'][i]['c'])+t)
            inside=(p['lower'] is None or t>=Q(p['lower'])) and (p['upper'] is None or t<=Q(p['upper']))
            assert inside==q['inside']
            if inside:assert audit.optimal(new,x,q['pi'])
            else:
                y=q['competitor']['flow']
                assert audit.feasible(new,y) and audit.value(new,y)<audit.value(new,x)
            if m['id'] in tiny:
                assert inside==all(audit.value(new,x)<=audit.value(new,y) for y in allflows[m['id']])
            checked_queries+=1
        # Recreate bad interval endpoint and bad-flow controls from serialized data.
        for side in ('lower','upper'):
            if p[side] is None:continue
            corrupt=json.loads(json.dumps(p));corrupt[side]=str(Q(p[side])+1)
            assert not audit.admit_interval(m,x,r['base_pi'],corrupt);bad+=1
        invalid=x.copy();invalid[p['edge']]=m['edges'][p['edge']]['u']+1
        assert not audit.admit_interval(m,invalid,r['base_pi'],p);bad+=1
        checked_intervals+=1
    assert len(seen)==sum(len(m['edges']) for m in models.values())
    expected={(k,tuple(x)) for k,flows in allflows.items() for x in flows
              if audit.value(models[k],x)==min(audit.value(models[k],y) for y in flows)}
    actual=set();alt_intervals=0
    for a in result['all_optima']:
        m=models[a['model']];x=a['flow'];key=(m['id'],tuple(x))
        assert key not in actual;actual.add(key)
        assert audit.optimal(m,x,a['pi'])
        assert {p['edge'] for p in a['intervals']}==set(range(len(m['edges'])))
        for p in a['intervals']:
            assert audit.admit_interval(m,x,a['pi'],p)
            assert (p['lower'],p['upper'])==audit.exhaustive_interval(m,x,p['edge'],allflows[m['id']])
            alt_intervals+=1
    assert actual==expected
    s=result['simultaneous'];m=s['base'];x=s['flow']
    def update(changes):
        new=json.loads(json.dumps(m))
        for i,t in changes.items():new['edges'][int(i)]['c']=str(Q(new['edges'][int(i)]['c'])+Q(t))
        return new
    for change in (s['first_delta'],s['second_delta']):
        new=update(change)
        assert all(audit.value(new,x)<=audit.value(new,y) for y in audit.enumerate_flows(new))
    both=update(dict(s['first_delta'],**s['second_delta']));y=s['joint_better_flow']
    assert audit.feasible(both,y) and audit.value(both,y)<audit.value(both,x)
    assert audit.optimal(update(s['safe_joint_delta']),x,s['safe_joint_pi'])
    c=result['counts']
    assert c['models']==len(models) and c['query_checks']==checked_queries and c['intervals']==checked_intervals
    assert c['all_optimal_flows']==len(actual) and c['all_optimal_intervals']==alt_intervals
    report={'passed':True,'serialized_intervals_rechecked':checked_intervals,
            'serialized_queries_rechecked':checked_queries,'all_optimal_flows_rechecked':len(actual),
            'all_optimal_intervals_rechecked':alt_intervals,'recreated_rejected_controls':bad,
            'results_sha256':hashlib.sha256(results_path.read_bytes()).hexdigest()}
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',type=Path);p.add_argument('results',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();replay(a.inputs,a.results,a.output)
