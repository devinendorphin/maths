"""Supplemental assurance controls; no timing/performance result."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from fractions import Fraction
from checker import encode, verify
from fairness_admission import admit, coverage_model
from routes import answer

ROOT=Path(__file__).resolve().parents[1]


class Captured:
    """Admission is full; subsequent patches assume a complete trusted delta."""
    def __init__(self,m,p,dependency):
        assert verify(m,p,dependency) and p['kind']=='optimal'
        self.model,self.proof,self.dependency=copy.deepcopy(m),copy.deepcopy(p),dependency
        self.version=0

    def patch(self,version,dependency,changes):
        if version!=self.version or dependency!=self.dependency:return False,0
        if len({i for i,_ in changes})!=len(changes):return False,0
        total=self.proof['cost_units'];checks=0
        for i,cost in changes:
            if type(i) is not int or not 0<=i<len(self.model['edges']) or type(cost) is not int or abs(cost)>100:return False,checks
            e=self.model['edges'][i];x=self.proof['flow'][i];pi=self.proof['pi']
            r=cost+pi[e['a']]-pi[e['z']];checks+=1
            if x<e['u'] and r<0 or x>e['l'] and r>0:return False,checks
            total+=(cost-e['c'])*x
        for i,cost in changes:self.model['edges'][i]['c']=cost
        self.proof['cost_units']=total
        # Model digest materialization is O(E); not part of the conditional O(k)
        # sign/value check. This prototype does it when exporting a full proof.
        from checker import digest
        self.proof['model']=digest(self.model)
        self.version+=1
        return True,checks


def run(directory,output):
    inputs=json.loads((directory/'Inputs.json').read_text());freeze=json.loads((directory/'Freeze.json').read_text());dep=freeze['dependency']
    supplement=json.loads((ROOT/'Maintenance-freeze.json').read_text())
    for name,sha in supplement['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    results=[]
    for k,case in enumerate(inputs['fairness']):
        w=json.loads((directory/'outputs'/f'fairness-{k:02d}-flow-repair-0'/'Worker.json').read_text())
        probes=[r for r in w['records'] if 'coverage_candidate' in r]
        selected=w['extras']['selected_coverage'];assert admit(case,probes,selected,dep)
        bad=copy.deepcopy(probes);bad[0]['proof']['dependency']='wrong';assert not admit(case,bad,selected,dep)
        missing_rejected=None
        if len(probes)>1:
            assert not admit(case,probes[1:],selected,dep);missing_rejected=True
        scalar_rejected=None
        if selected is not None and Fraction(selected)>0:
            # Grant the scalar proof the correct new model hash; feasibility must
            # still fail, so this control does not rely only on a digest mismatch.
            bad=copy.deepcopy(probes);bad[-1]['proof']=copy.deepcopy(w['records'][0]['proof'])
            bad[-1]['proof']['model']=probes[-1]['proof']['model']
            assert not admit(case,bad,selected,dep);scalar_rejected=True
        results.append({'case':case['id'],'fairness_bundle_accepted':True,'wrong_dependency_rejected':True,'missing_higher_cut_rejected':missing_rejected,'scalar_proof_as_positive_maxmin_rejected':scalar_rejected})
    # Designed answer-stable / proof-inapplicable case, separate from cold solving.
    base=copy.deepcopy(inputs['static'][0]);p,*_=answer(base,'cold',None,dep)
    changed=copy.deepcopy(base);changed['edges'][1]['c']=0
    new,*_=answer(changed,'potential',p,dep)
    assert new['flow']==p['flow'] and new['pi']!=p['pi'] and verify(changed,new,dep)
    results.append({'case':'same-flow-new-potential','old_flow':p['flow'],'new_flow':new['flow'],'old_pi':p['pi'],'new_pi':new['pi'],'accepted':True})
    accepted=rejected=sign_checks=0
    for stream in inputs['heldout']:
        if 'cost' not in stream['id']:continue
        previous=stream['models'][0];proof,*_=answer(previous,'cold',None,dep);cache=Captured(previous,proof,dep)
        for raw in stream['models'][1:]:
            # This complete delta is calculated by the test harness, not assumed
            # to be discoverable in O(k) from an arbitrary full changed model.
            changes=[(i,e['c']) for i,e in enumerate(raw['edges']) if e['c']!=cache.model['edges'][i]['c']]
            ok,count=cache.patch(cache.version,dep,changes);sign_checks+=count
            if ok:
                assert verify(cache.model,cache.proof,dep);accepted+=1
            else:
                proof,*_=answer(raw,'cold',None,dep);cache=Captured(raw,proof,dep);rejected+=1
    assert not cache.patch(cache.version+1,dep,[])[0]
    assert not cache.patch(cache.version,'different-dependency',[])[0]
    results.append({'case':'conditional-cost-patches','accepted':accepted,'rejected_with_recapture':rejected,'changed_edge_sign_checks':sign_checks,'stale_version_rejected':True,'dependency_change_rejected':True,'raw_input_delta_discovery_included_in_O_k_bound':False,'full_export_digest_included_in_O_k_bound':False})
    report={'passed':True,'controls':results,'scope':'Independently checked composition and conditional patch correctness; not a measured O(k) full pipeline or a formal proof.'}
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]))
