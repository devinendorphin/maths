"""Matched credited cold/warm state, full proof admission and charged fallbacks."""
import copy
import time
import networkx
from checker import digest, feasible, verify
from native import Native, simple
from producer import Budget, certificate, feasibility, networkx_flow, optimize, potentials
from transaction import Transaction

ROUTES=('simple-cold','generic-cold','generic-warm','guard-generic','flow-repair','guard-repair')


def completion(m,x,ctx):
    if x is None:
        _,cut=feasibility(m);assert cut is not None
        return certificate(m,ctx,cut=cut)
    pi,cycle=potentials(m,x);assert cycle is None
    return certificate(m,ctx,flow=x,pi=pi)


class Engine:
    def __init__(self,model,context,route):
        assert route in ROUTES
        self.state=Transaction(model,context);self.context,self.route=context,route
        self.last_flow,self.proof,self.native=None,None,None;self.constructions=0
    def close(self):
        if self.native:self.native.close();self.native=None
    def query(self,message=None,force_budget=False,force_native_failure=False):
        tick=time.perf_counter();m=self.state.model if message is None else self.state.apply(message)
        assert all(abs(b)<=1000000 for b in m['b'])
        stats={'guard_attempt':False,'guard_accepted':False,'flow_hint':False,'budget_fallback':False,
               'native_failure':False,'augmentations':0,'cycles':0,'relaxations':0}
        p=None;trace=None;solver_s=0.0;feasibility_s=0.0;proof_s=0.0
        if self.route in ('generic-cold','generic-warm','guard-generic'):
            start=time.perf_counter()
            if self.route=='generic-cold' or self.native is None:
                self.native=Native(m);self.constructions+=1;before=None
            else:
                before=self.native.snapshot();self.native.patch(m)
            patched=self.native.snapshot();solver_s+=time.perf_counter()-start
            trace={'before':before,'patched':patched,'after':None,'constructions':self.constructions,
                   'solve_called':False,'solve_status':None,'feasible_witness':None,'failure_after':None,'status_forced_control':False}
        if self.route in ('guard-generic','guard-repair') and self.proof is not None and self.proof['kind']=='optimal':
            start=time.perf_counter();stats['guard_attempt']=True;candidate=copy.deepcopy(self.proof)
            candidate['model']=digest(m);candidate['cost_units']=sum(e['c']*x for e,x in zip(m['edges'],candidate['flow']))
            if verify(m,candidate,self.context):p=candidate;stats['guard_accepted']=True
            proof_s+=time.perf_counter()-start
        if p is not None:
            action='certificate-admission'
        elif self.route=='simple-cold':
            start=time.perf_counter();x=simple(m);solver_s+=time.perf_counter()-start
            start=time.perf_counter();p=completion(m,x,self.context);proof_s+=time.perf_counter()-start;action='simple-cold'
        elif trace is not None:
            start=time.perf_counter();witness,cut=feasibility(m);feasibility_s+=time.perf_counter()-start
            if cut is not None:p=certificate(m,self.context,cut=cut);action='generic-shortage'
            else:
                assert feasible(m,witness);trace['feasible_witness']=witness.copy()
                start=time.perf_counter();trace['solve_called']=not force_native_failure;trace['status_forced_control']=force_native_failure
                # The deliberate control exercises the checked nonoptimal-status path.
                status=-99 if force_native_failure else self.native.solve(witness)
                trace['solve_status']=status;solver_s+=time.perf_counter()-start
                if status:
                    stats['native_failure']=True;stats['budget_fallback']=True;trace['failure_after']=self.native.snapshot()
                    start=time.perf_counter();p=completion(m,simple(m),self.context);proof_s+=time.perf_counter()-start
                    action='charged-native-fallback'
                else:
                    snap=self.native.snapshot();assert not any(snap['excess'])
                    x=[e['l']+y for e,y in zip(m['edges'],snap['y'])]
                    start=time.perf_counter();p=completion(m,x,self.context);proof_s+=time.perf_counter()-start
                    action=self.route
        else:
            stats['flow_hint']=self.last_flow is not None
            try:
                start=time.perf_counter();x,cut=feasibility(m,self.last_flow,stats);feasibility_s+=time.perf_counter()-start
                if cut is not None:p=certificate(m,self.context,cut=cut);action='repair-shortage'
                else:
                    if force_budget:raise Budget('deliberately forced control')
                    start=time.perf_counter();p=optimize(m,x,self.context,stats);solver_s+=time.perf_counter()-start;action='flow-repair'
            except Budget:
                stats['budget_fallback']=True
                start=time.perf_counter();p=completion(m,simple(m),self.context);proof_s+=time.perf_counter()-start;action='charged-cold-fallback'
        start=time.perf_counter();assert verify(m,p,self.context);proof_s+=time.perf_counter()-start
        if trace is not None:
            trace['after']=self.native.snapshot()
            if stats['native_failure']:
                # Failed native state is preserved in the record, then discarded/charged.
                self.native.close();self.native=None
            elif self.route=='generic-cold':self.native.close();self.native=None
        if p['kind']=='optimal':self.last_flow=p['flow'].copy()
        self.proof=copy.deepcopy(p)
        return {'model':digest(m),'version':self.state.version,'action':action,'stats':stats,'native':trace,
                'proof':copy.deepcopy(p),'query_wall_s':time.perf_counter()-tick,
                'timing':{'native_or_optimizer_s':solver_s,'feasibility_s':feasibility_s,'completion_admission_s':proof_s}}
