"""Designed four-edge illustration, not a benchmark or general allocation solver.

Certificate checking uses residual reduced costs. A separate one-variable
enumerator checks the tiny 2x2 transportation model exactly.
"""
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent


def costs(model,t,s):
    return [Q(e['cost'])+t*e['t']+s*e['s'] for e in model['edges']]


def certificate(model,c,x,potential):
    balances={v:Q(0) for v in model['balance']};violations=[];reduced=[]
    if len(x)!=len(model['edges']) or len(c)!=len(x) or set(potential)!=set(balances):return dict(valid=False,violations=['shape'])
    for edge,cost,flow in zip(model['edges'],c,x):
        if type(flow)!=int or not edge['lower']<=flow<=edge['upper']:violations.append('bound:'+edge['name'])
        balances[edge['tail']]+=flow;balances[edge['head']]-=flow
        r=Q(cost)+Q(potential[edge['tail']])-Q(potential[edge['head']]);reduced.append(str(r))
        if flow<edge['upper'] and r<0:violations.append('forward:'+edge['name'])
        if flow>edge['lower'] and r>0:violations.append('reverse:'+edge['name'])
    for node,b in model['balance'].items():
        if balances[node]!=b:violations.append('balance:'+node)
    return dict(valid=not violations,violations=violations,reduced_costs=reduced,objective=str(sum(a*b for a,b in zip(c,x))))


def tiny_oracle(model,c):
    # Conservation determines all four flows from k=x_AS; independent of the
    # potential checker and valid only for this designed 2x2 graph.
    feasible=[]
    for k in range(model['edges'][1]['lower'],model['edges'][1]['upper']+1):
        ar=model['balance']['A']-k;br=-model['balance']['R']-ar;bs=model['balance']['B']-br
        x=[ar,k,br,bs]
        if k+bs!=-model['balance']['S']:continue
        if all(e['lower']<=a<=e['upper'] for e,a in zip(model['edges'],x)):feasible.append((sum(a*b for a,b in zip(c,x)),x))
    assert feasible
    return min(v for v,x in feasible),[x for v,x in feasible if v==min(z for z,x in feasible)]


def run():
    for name,sha in json.loads((ROOT/'Example-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    model=json.loads((ROOT/'Example-input.json').read_text());diag=[2,0,0,2];crossed=[0,2,2,0]
    initial={'A':0,'B':0,'R':1,'S':1};repaired={'A':1,'B':0,'R':2,'S':1};new={'A':0,'B':0,'R':1,'S':0}
    constrained=copy.deepcopy(model);constrained['edges'][0]['upper']=1
    changed_balance=copy.deepcopy(model);changed_balance['balance'].update(A=3,B=1)
    specs=[('initial',model,0,0,diag,initial,True),('potential_expires_plan_stable',model,4,0,diag,initial,False),('repair_potentials_keep_plan',model,4,0,diag,repaired,True),('plan_loses_optimality',model,4,2,diag,repaired,False),('repair_plan',model,4,2,crossed,new,True),('capacity_change_invalidates',constrained,0,0,diag,initial,False),('capacity_repair',constrained,0,0,[1,1,1,1],{'A':-3,'B':0,'R':3,'S':1},True),('supply_change_invalidates',changed_balance,0,0,diag,initial,False),('supply_repair',changed_balance,0,0,[2,1,0,1],{'A':-3,'B':0,'R':0,'S':1},True)]
    records=[]
    for name,m,t,s,x,p,expected in specs:
        c=costs(m,Q(t),Q(s));check=certificate(m,c,x,p);assert check['valid']==expected,(name,check)
        optimum,solutions=tiny_oracle(m,c)
        if expected:assert Q(check['objective'])==optimum and x in solutions
        records.append(dict(case=name,model=m,parameters=[t,s],flow=x,potential=p,check=check,independent_optimum=str(optimum),independently_optimal_flows=solutions))
    controls=[]
    bad_cost=costs(model,0,0);bad_cost[0]+=10
    for label,c,x,p in [('false_cost',bad_cost,diag,initial),('false_flow',costs(model,0,0),[2,0,0,1],initial),('false_potential',costs(model,0,0),diag,{v:0 for v in initial}),('negative_flow',costs(model,0,0),[-1,3,3,-1],initial)]:
        check=certificate(model,c,x,p);assert not check['valid'];controls.append(dict(control=label,check=check))
    grid=[]
    for a in range(11):
        for b in range(11):
            t,s=Q(a,2),Q(b,2);c=costs(model,t,s);optimum,solutions=tiny_oracle(model,c);check=certificate(model,c,diag,initial)
            plan_stable=diag in solutions;proof_applies=check['valid'];assert plan_stable==(t+s<=5) and proof_applies==(t<=3 and s<=2)
            grid.append(dict(t=str(t),s=str(s),diagonal_plan_optimal=plan_stable,initial_potential_applicable=proof_applies,independent_optimum=str(optimum)))
    report=dict(status='checked illustrative example; not a new general theorem or large performance experiment',scenario_checks=len(records),invalid_controls_rejected=len(controls),exact_grid_checks=len(grid),records=records,controls=controls,grid=grid,formal_verification=False,external_proof_format='none: exact residual-potential algebra plus separate tiny enumeration')
    (ROOT/'Worked-example.json').write_text(json.dumps(report,indent=2)+'\n');print('Worked example checked:',len(records),'scenarios,',len(controls),'invalid controls,',len(grid),'rational points')


if __name__=='__main__':run()
