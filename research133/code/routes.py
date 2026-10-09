"""Common complete-cost admission paths and invalid controls."""
import copy
import time
from checker import digest, encode, feasible, validate, verify
from producer import certificate, feasibility, networkx_flow, optimize, potentials


METHODS = ['cold', 'warm', 'recheck', 'potential', 'flow-repair', 'nx-cold']


def answer(m, method, previous, dependency):
    timing, counters, attempts = {}, {}, []
    def measured(key, fn):
        t=time.perf_counter()
        try:return fn()
        finally:timing[key]=timing.get(key,0)+time.perf_counter()-t
    if not measured('admission_s', lambda: validate(m)):
        raise ValueError('unsupported model')
    old = previous if previous and previous['kind']=='optimal' else None
    if old and method in ('recheck','flow-repair'):
        candidate=measured('encoding_s',lambda: certificate(m,dependency,flow=old['flow'],pi=old['pi']))
        accepted=measured('probe_s',lambda: verify(m,candidate,dependency))
        attempts.append({'probe':'captured-potential','accepted':accepted})
        if accepted:return candidate,timing,counters,attempts
    if old and method in ('potential','flow-repair'):
        accepted=measured('probe_s',lambda: feasible(m,old['flow']))
        attempts.append({'probe':'old-flow-feasibility','accepted':accepted})
        if accepted:
            pi,cycle=measured('potential_probe_s',lambda: potentials(m,old['flow'],counters))
            attempts.append({'probe':'potential-repair','accepted':cycle is None})
            if cycle is None:
                p=measured('proof_s',lambda:certificate(m,dependency,flow=old['flow'],pi=pi))
                return p,timing,counters,attempts
    if method=='nx-cold':
        value,x=measured('solver_s',lambda:networkx_flow(m))
        if x is None:
            x,cut=measured('completion_s',lambda:feasibility(m,None,counters))
            assert x is None
            p=measured('proof_s',lambda:certificate(m,dependency,cut=cut))
        else:
            pi,cycle=measured('proof_s',lambda:potentials(m,x,counters))
            assert cycle is None
            p=measured('proof_s',lambda:certificate(m,dependency,flow=x,pi=pi))
            assert p['cost_units']==value
        return p,timing,counters,attempts
    seed=old['flow'] if old and method in ('warm','flow-repair') else None
    x,cut=measured('feasibility_s',lambda:feasibility(m,seed,counters))
    if cut is not None:
        p=measured('proof_s',lambda:certificate(m,dependency,cut=cut))
    else:
        p=optimize(m,x,dependency,counters,timing)
    attempts.append({'probe':'seeded-flow-solve' if seed is not None else 'cold-solve','accepted':True})
    return p,timing,counters,attempts


def invalid_controls(m,p,dependency):
    pairs=[]
    def add(name, model, proof):
        pairs.append({'control':name,'rejected':not verify(model,proof,dependency)})
    bad=copy.deepcopy(p);bad['dependency']='different-producer/checker-context'
    add('dependency-change',m,bad)
    mm=copy.deepcopy(m);mm['nonlinear_objective']='unsupported'
    bad=copy.deepcopy(p);bad['model']=digest(mm);add('nonlinear-objective',mm,bad)
    mm=copy.deepcopy(m);mm['edges'][0]['u']=0.5
    bad=copy.deepcopy(p);bad['model']=digest(mm);add('noninteger-domain',mm,bad)
    if p['kind']=='cut':
        bad=copy.deepcopy(p);bad['set']=[];add('false-cut',m,bad)
    else:
        bad=copy.deepcopy(p);bad['cost_units']+=1;add('false-cost',m,bad)
        bad=copy.deepcopy(p);bad['flow'][0]=m['edges'][0]['u']+1;add('false-flow',m,bad)
        bad=copy.deepcopy(p)
        for e,x in zip(m['edges'],p['flow']):
            if e['a']!=e['z'] and (x<e['u'] or x>e['l']):
                bad['pi'][e['z']]=e['c']+bad['pi'][e['a']]+(1 if x<e['u'] else -1)
                break
        else:raise AssertionError('no potential control edge')
        add('false-potential',m,bad)
        mm=copy.deepcopy(m)
        i=next(i for i,x in enumerate(p['flow']) if x>0)
        mm['edges'][i]['u']=p['flow'][i]-1
        bad=copy.deepcopy(p);bad['model']=digest(mm);add('capacity-below-flow',mm,bad)
        mm=copy.deepcopy(m);mm['b'][0]+=1;mm['b'][1]-=1
        bad=copy.deepcopy(p);bad['model']=digest(mm);add('balance-change',mm,bad)
    assert all(z['rejected'] for z in pairs),pairs
    return pairs
