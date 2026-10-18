"""Frozen exact validation, witness replay and counterexamples. No timings claimed."""
import argparse,copy,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path
import audit
from sensitivity import interval,changed_model,potential,boundary_competitor

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
sys.path.insert(0,str(REPO/'research133/code'))
from producer import feasibility,optimize


def solve(m):
    den=math.lcm(*(Q(e['c']).denominator for e in m['edges']))
    old=copy.deepcopy(m);old['denominator']=den
    for e in old['edges']:e['c']=int(Q(e['c'])*den)
    flow,cut=feasibility(old)
    assert cut is None
    p=optimize(old,flow,'research137',{})
    return p['flow'],[str(Q(v,den)) for v in p['pi']]


def probes(p):
    out={Q(0),Q(-1),Q(1)}
    for key in ('lower','upper'):
        if p[key] is not None:
            v=Q(p[key]);out.update([v-Q(1,2),v,v+Q(1,2)])
    if p['lower'] is not None and p['upper'] is not None:
        out.add((Q(p['lower'])+Q(p['upper']))/2)
    return sorted(out)


def run(destination):
    assert not destination.exists(),'Never overwrite evidence'
    freeze=json.loads((ROOT/'Freeze.json').read_text())
    for name,sha in freeze['files'].items():assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==sha,name
    inputs=json.loads((ROOT/'Inputs.json').read_text())
    records=[];all_optima=[];counts=dict(models=0,intervals=0,enumerated_flows=0,query_checks=0,
                           strict_competitors=0,rejected_controls=0,proof_gap_queries=0,all_optimal_flows=0,all_optimal_intervals=0)
    for group in ('tiny','heldout'):
        for m in inputs[group]:
            x,pi=solve(m);assert audit.optimal(m,x,pi)
            flows=audit.enumerate_flows(m) if group=='tiny' else None
            if flows is not None:
                counts['enumerated_flows']+=len(flows)
                assert audit.value(m,x)==min(audit.value(m,y) for y in flows)
                for alt in flows:
                    if audit.value(m,alt)!=audit.value(m,x):continue
                    altpi=potential(m,alt);ranges=[]
                    assert audit.optimal(m,alt,altpi)
                    for j in range(len(m['edges'])):
                        ap=interval(m,alt,j);assert audit.admit_interval(m,alt,altpi,ap)
                        assert (ap['lower'],ap['upper'])==audit.exhaustive_interval(m,alt,j,flows)
                        ranges.append(ap);counts['all_optimal_intervals']+=1
                    all_optima.append({'model':m['id'],'flow':alt,'pi':altpi,'intervals':ranges})
                    counts['all_optimal_flows']+=1
            counts['models']+=1
            for i in range(len(m['edges'])):
                p=interval(m,x,i);assert audit.admit_interval(m,x,pi,p)
                if flows is not None:assert (p['lower'],p['upper'])==audit.exhaustive_interval(m,x,i,flows)
                queries=[];controls=[]
                for t in probes(p):
                    new=changed_model(m,{i:t})
                    inside=(p['lower'] is None or Q(p['lower'])<=t) and (p['upper'] is None or t<=Q(p['upper']))
                    if flows is not None:
                        exhaustive=all(audit.value(new,x)<=audit.value(new,y) for y in flows)
                        assert inside==exhaustive
                    entry={'delta':str(t),'inside':inside}
                    if inside:
                        newpi=potential(new,x);assert audit.optimal(new,x,newpi)
                        entry['pi']=newpi
                        if not audit.optimal(new,x,pi):counts['proof_gap_queries']+=1
                    else:
                        side='lower' if p['lower'] is not None and t<Q(p['lower']) else 'upper'
                        witness=boundary_competitor(m,x,p,side)
                        assert audit.feasible(new,witness['flow']) and audit.value(new,witness['flow'])<audit.value(new,x)
                        entry['competitor']=witness
                        counts['strict_competitors']+=1
                    queries.append(entry);counts['query_checks']+=1
                for side in ('lower','upper'):
                    if p[side] is None:continue
                    at=changed_model(m,{i:p[side]});competitor=boundary_competitor(m,x,p,side)
                    assert competitor['flow']!=x and audit.feasible(at,competitor['flow'])
                    assert audit.value(at,x)==audit.value(at,competitor['flow'])
                    bad=copy.deepcopy(p);bad[side]=str(Q(p[side])+1)
                    assert not audit.admit_interval(m,x,pi,bad);controls.append('false-'+side)
                for field in ('forward_return','reverse_return'):
                    w=p[field]
                    if w is None:continue
                    bad=copy.deepcopy(p);bad[field]['labels'][w['source']]='1'
                    assert not audit.admit_interval(m,x,pi,bad);controls.append('false-source-distance')
                    if w['path']:
                        bad=copy.deepcopy(p);bad[field]['path']=[]
                        assert not audit.admit_interval(m,x,pi,bad);controls.append('missing-path')
                    elif w['labels'][w['target']] is None:
                        bad=copy.deepcopy(p);bad[field]['labels'][w['target']]='0'
                        assert not audit.admit_interval(m,x,pi,bad);controls.append('false-reachability')
                badx=x.copy();badx[i]=m['edges'][i]['u']+1
                assert not audit.admit_interval(m,badx,pi,p);controls.append('false-flow')
                counts['rejected_controls']+=len(controls);counts['intervals']+=1
                records.append({'group':group,'model':m['id'],'flow':x,'base_pi':pi,
                                'interval':p,'queries':queries,'controls':controls})
    # Two independently safe closed-endpoint changes fail when combined.
    m=inputs['tiny'][0];x,pi=solve(m)
    first=changed_model(m,{0:2});second=changed_model(m,{1:-2});both=changed_model(m,{0:2,1:-2})
    assert audit.optimal(first,x,potential(first,x)) and audit.optimal(second,x,potential(second,x))
    winner=[0,1];assert audit.feasible(both,winner) and audit.value(both,winner)<audit.value(both,x)
    # Safe interaction-aware route: recompute a potential for the entire update.
    safe=changed_model(m,{0:1,1:'-1/2'});assert audit.optimal(safe,x,potential(safe,x))
    # Local return paths cannot substitute for the required base-optimality proof.
    badbase=copy.deepcopy(m);badbase['edges'][1]['c']='-2'
    local=interval(badbase,x,0)
    assert not audit.admit_interval(badbase,x,pi,local)
    result={'passed':True,'counts':counts,'records':records,'all_optima':all_optima,
            'simultaneous':{'base':m,'flow':x,'first_delta':{'0':'2'},'second_delta':{'1':'-2'},
                            'each_alone_optimal':True,'joint_old_cost':str(audit.value(both,x)),
                            'joint_better_flow':winner,'joint_better_cost':str(audit.value(both,winner)),
                            'safe_joint_delta':{'0':'1','1':'-1/2'},'safe_joint_pi':potential(safe,x)},
            'nonoptimal_base_rejected':True,
            'scope':'Exact witnesses and finite validation; general sensitivity theorem is prose, certificate soundness is Lean checked separately.'}
    destination.mkdir(parents=True)
    (destination/'Results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'counts':counts}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('destination',type=Path)
    run(parser.parse_args().destination)
