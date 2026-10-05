"""Meaningful proof, mutation, boundary and fallback fixtures before freezing."""
import copy
import random
import tempfile
import time
from pathlib import Path
from common import E, OLD, ROOT, counters, limits, save, SG
import certificates as C
import policy
from audit import Checker, optimum, path_audit


def row(w,p,v,c,end=256,stage=36):
    return dict(case_id='fixture',stage=stage,weights=w,profits=p,slopes=v,capacity=c,end=end)


def checked(r,method,interval=(0,256)):
    cert,ct=C.build(r['weights'],r['profits'],r['slopes'],r['capacity'],method,interval,time.perf_counter()+30,{},limits(r['stage']))
    checker=Checker(r)
    for j in range(len(cert['layers'])): checker.layer(cert,j)
    checker.terminal(cert)
    for t in range(interval[0],interval[1]+1):
        assert C.at(cert,t)==optimum(r['weights'],[P+t*S for P,S in zip(r['profits'],r['slopes'])],r['capacity'])
    return cert,ct


def run():
    reports=[]; mutations=[]
    examples=[row([1,1],[4,7],[0,0],1),row([1,2],[4,7],[2,2],2),
              row([1,2],[4,4],[-1,-1],2),row([1,2],[-5,-2],[-1,0],2),
              row([2,3],[4,5],[0,0],0),row([5,6],[9,9],[1,2],1),
              row([1,1],[10,-246],[0,1],1),row([1,1],[10,-245],[0,1],1),
              row([1,2,2],[0,0,-3],[2,-1,1],3)]
    rng=random.Random(160900)
    examples += [row([rng.randint(1,8) for _ in range(6)], [rng.randint(-12,20) for _ in range(6)], [rng.randint(-4,4) for _ in range(6)],12) for _ in range(12)]
    for i,r in enumerate(examples):
        outputs={m:checked(r,m)[0] for m in ('unpruned','same','naive','indexed')}
        save(ROOT/'fixture-evidence'/f'case-{i:03}.json.gz',dict(input=r,certificates=outputs))
        assert [x['retained'] for x in outputs['naive']['layers']]==[x['retained'] for x in outputs['indexed']['layers']]
        for m in ('naive','indexed'):
            try: C.at(outputs[m],257); raise AssertionError('interval accepted 257')
            except ValueError: pass
        # The unpruned construction retains the frozen recurrence exactly.
        oldct={k:0 for k in OLD.DP_KEYS}; old=OLD.build(r['weights'],r['profits'],r['slopes'],r['capacity'],'slope',time.perf_counter()+30,oldct)
        assert [x['raw'] for x in outputs['unpruned']['layers']]==[x['raw'] for x in old['tables'][0]['layers']]
        reports.append(dict(fixture=i,methods=list(outputs),all_integer_values_checked=True,unpruned_matches_frozen=True))
        if i==0:
            bad=copy.deepcopy(outputs['unpruned']); bad['layers'][1]['raw'][-1][-1]=[99,1]
            try: Checker(r).layer(bad,1); raise RuntimeError('mutation accepted')
            except (AssertionError,IndexError): mutations.append('predecessor')
        for method in ('same','indexed'):
            cert=outputs[method]
            for j,layer in enumerate(cert['layers']):
                if layer['deletions']:
                    bad=copy.deepcopy(cert); bad['layers'][j]['deletions'][0][1]=bad['layers'][j]['deletions'][0][0]
                    try: Checker(r).layer(bad,j); raise RuntimeError('mutation accepted')
                    except AssertionError: mutations.append(method+'_deletion')
                    break
        cert=outputs['indexed']
        if len(cert['layers'])>1 and cert['layers'][1]['index']['coordinates']:
            bad=copy.deepcopy(cert); bad['layers'][1]['index']['coordinates'][0]+=1
            try: Checker(r).layer(bad,1); raise RuntimeError('mutation accepted')
            except AssertionError: mutations.append('coordinate_rank')
            bad=copy.deepcopy(cert); bad['layers'][1]['index']['queries'][0][2]=[999,0,0]
            try: Checker(r).layer(bad,1); raise RuntimeError('mutation accepted')
            except AssertionError: mutations.append('query_aggregate')
            bad=copy.deepcopy(cert)
            node=next(k for k,x in enumerate(bad['layers'][1]['index']['tree']) if x is not None)
            bad['layers'][1]['index']['tree'][node][0]+=999
            try: Checker(r).layer(bad,1); raise RuntimeError('mutation accepted')
            except AssertionError: mutations.append('stored_tree_aggregate')
    boundary=row([1,1],[10,-246],[0,1],1,end=1024,stage=40)
    first,_=checked(boundary,'indexed'); second,_=checked(boundary,'indexed',(256,512))
    assert C.at(first,256)==10 and C.at(second,257)==11
    for r in [boundary,row([1,1],[10,-245],[0,1],1,1024,40),row([1,2],[5,6],[-1,-2],2,1024,40),row([1,1,1],[10,9,0],[0,1,2],1,1024,40)]:
        for method in ('maintain','unpruned','same','rolling'):
            result=policy.run(r,method)
            assert result['status']=='window_complete'
            with tempfile.TemporaryDirectory(dir=ROOT) as d: path_audit(r,result,Path(d))
            if method=='rolling': assert len(result['constructions'])==4
    # The declared memory guard must save an inactive partial proof and charge fallback.
    r=row([1,2,3],[5,-2,4],[1,0,-1],3,24)
    result=policy.run(r,'indexed',forced_caps={'auxiliary':3})
    assert result['status']=='window_complete' and result['constructions'][0]['status']!='complete'
    assert not result['constructions'][0]['active_certificate'] and result['totals']['dp_entries']>0
    with tempfile.TemporaryDirectory(dir=ROOT) as d: path_audit(r,result,Path(d))
    # Zero/negative gate slopes retain exact signed arithmetic and gcd-zero semantics.
    for r in examples:
        ct=counters(); features=C.gate(r['weights'],r['profits'],r['slopes'],r['capacity'],ct)
        cert,_=checked(r,'unpruned')
        assert sum(len(x['raw']) for x in cert['layers'])<=features['E_bound']
    result=dict(passed=True,fixtures=reports,mutation_rejections=mutations,multiple_switches_inside_window=True,
                boundary_deleted_state_restored=True,strict_boundary_loss=True,
                native_optimizer_and_scalar_audits=True,charged_partial_build_fallback=True,
                no_gratuitous_fifth_window=True)
    save(ROOT/'Verification-fixtures.json',result)
    print('FIXTURES PASSED',len(reports),len(mutations),flush=True)
    return result


if __name__=='__main__': run()
