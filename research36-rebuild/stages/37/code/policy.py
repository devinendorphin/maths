"""One isolated policy trajectory, using only input data and certified states."""
import copy
import sys
import time
from collections import defaultdict
from pathlib import Path
from common import ROOT, E, H, SG, OLD, add, counters, limits, read, save, value
import certificates as C


def run(row, method, folder=None, selection=None, forced_caps=None):
    stage=row['stage']; lim=limits(stage); wall=time.perf_counter(); cpu=time.process_time()
    E.LIMITS['evaluations']=lim['scalar_evaluations']
    deadline=wall+lim['wall_seconds']; serialization=[]; ledger=[]; ct=counters()
    constructs=[]; native=[]; events=[]; segments=[]; pending=None; current=0
    native_refs=[]; event_refs=[]; segment_refs=[]
    w,p,v,c=(list(row[k]) if isinstance(row[k],list) else row[k] for k in ('weights','profits','slopes','capacity'))
    m=None; proof=None; proof_anchor=0; cert=None; active_method=method; normalized=False

    def persist(name,data):
        nonlocal deadline
        if folder is None: return None
        record=save(Path(folder)/name,data,immutable=True)
        serialization.append(record); deadline+=record['wall']
        return dict(file=record['path'],sha256=record['sha256'])

    def account(t,kind,counts,elapsed):
        add(ct,counts); ledger.append(dict(time=t,kind=kind,counters=counts,cpu=elapsed))

    def event(record):
        events.append(record)
        event_refs.append(persist(f'event-{len(events)-1:04}.json.gz',record))

    def emit_segment(record):
        segments.append(record)
        segment_refs.append(persist(f'segment-{len(segments)-1:04}.json.gz',record))

    def checkpoint():
        if folder is None: return
        data=dict(time=current,packing=m,proof=proof,proof_anchor=proof_anchor,counters=ct,
                  constructions=constructs,native=native_refs,events=event_refs,segments=segment_refs,
                  ledger=ledger,active_method=active_method,normalized=normalized,
                  active_construction=None if cert is None else len(constructs)-1,
                  gate=selected_gate,
                  algorithm_cpu=time.process_time()-cpu-sum(x['cpu'] for x in serialization),
                  algorithm_wall=time.perf_counter()-wall-sum(x['wall'] for x in serialization))
        persist(f'state-{len(segments):04}.json.gz',data)

    def source(t):
        nonlocal m,proof,proof_anchor
        start=time.process_time(); remaining=lim['cumulative_native']-ct['native_generator_steps']
        if remaining<=0: raise E.Cap('cumulative native generator cap')
        try:
            result=SG.solve(w,[a+t*b for a,b in zip(p,v)],c,deadline=deadline,max_steps=remaining)
        except SG.SourceCap as exc:
            failed=dict(time=t,status='pending_restart',reason=str(exc),**exc.cost)
            native.append(failed); persist(f'native-{len(native)-1:03}.json.gz',failed)
            account(t,'native_aborted',dict(native_generator_steps=exc.cost['construction_steps'],native_cleanup_steps=exc.cost['cleanup_steps'],native_disposal_steps=exc.cost['disposal_steps']),time.process_time()-start-serialization[-1]['cpu'] if folder else time.process_time()-start)
            raise
        measured=time.process_time()-start
        record=dict(time=t,status='complete',**result); native.append(record)
        account(t,'initial_native' if len(native)==1 else 'replacement_native',dict(native_generator_steps=result['construction_steps'],native_cleanup_steps=result['cleanup_steps'],native_disposal_steps=result['disposal_steps']),measured)
        native_refs.append(persist(f'native-{len(native)-1:03}.json.gz',record))
        m=result['packing']; proof=copy.deepcopy(result['proof']); proof_anchor=t
        return result

    def construct(t,a,b,kind):
        nonlocal cert,active_method
        cert=None
        start=time.process_time(); before=ct.copy()
        try:
            built,cc=C.build(w,p,v,c,kind,(a,b),deadline,ct,dict(lim,**(forced_caps or {})))
            status='complete'; reason=None
        except C.BuildCap as exc:
            built=exc.partial; cc=built['counters']; status='incomplete_abandoned_after_guard'; reason=str(exc)
        measured=time.process_time()-start
        account(t,'construction',cc,measured)
        if t>0: account(t,'interval_rebuild',{'interval_rebuilds':1},0)
        ref=persist(f'construction-{len(constructs):03}.json.gz',built)
        record=dict(anchor=t,interval=built['interval'],method=kind,status=status,reason=reason,
                    counters=cc,cpu=measured,record=ref,cursor=built.get('cursor'),
                    raw_rows=sum(len(x['raw']) for x in built['layers'])+len(built.get('current',{}).get('raw',[])),
                    retained_by_prefix=[len(x['retained']) for x in built['layers']],
                    raw_by_prefix=[len(x['raw']) for x in built['layers']],
                    lines=len(built.get('lines',[])),envelope=len(built.get('envelope',[])),
                    proof=built if folder is None else None,active_certificate=status=='complete')
        constructs.append(record)
        if status=='complete': cert=built
        else: cert=None; active_method='maintain'

    try:
        s=source(0)
        if 'generation_source' in row:
            assert m==row['generation_source']['packing'] and s['objective']==row['generation_source']['objective']
        start=time.process_time(); rc=counters(); matched=True
        for a,b in zip(p,v):
            rc['recognition']+=1
            if a!=b: matched=False; break
        normalized=matched and len(p)==len(v)
        if normalized:
            normalization=E.normalized_certificate(w,p,v,c,m,proof)
            rc['normalized_validation_cells']+=len(proof)
            rc['normalized_validation_hinges']+=sum(x[1].bit_count() for x in proof)
        account(0,'recognition',rc,time.process_time()-start)
        selected_gate=None
        if not normalized and method in ('conservative','selected','gate_unpruned','gate_same'):
            start=time.process_time(); gc=counters(); features=C.gate(w,p,v,c,gc)
            chosen=selection if method in ('selected','gate_unpruned','gate_same') and selection else dict(method='unpruned' if method in ('conservative','gate_unpruned') else 'same',threshold=500000)
            if chosen.get('method')=='maintain': accepted=False
            else: accepted=features['E_bound']<=chosen['threshold'] and features['T_bound']<=2000000
            active_method=chosen['method'] if accepted else 'maintain'
            selected_gate=dict(features=features,selection=chosen,accepted=accepted)
            account(0,'gate',gc,time.process_time()-start)
        if normalized:
            status='window_complete'; current=row['end']
            emit_segment(dict(kind='normalized',anchor=0,until=row['end'],packing=m,base_proof=proof,certificate=normalization))
            account(0,'initial_input_and_proof_handling',{},max(0,time.process_time()-cpu-sum(x['cpu'] for x in serialization)-sum(x['cpu'] for x in ledger)))
        else:
            if active_method!='maintain': construct(0,0,256,'indexed' if active_method=='rolling' else active_method)
            account(0,'initial_input_and_proof_handling',{},max(0,time.process_time()-cpu-sum(x['cpu'] for x in serialization)-sum(x['cpu'] for x in ledger)))
            while True:
                iteration_cpu=time.process_time(); ser_before=sum(x['cpu'] for x in serialization); component_before=sum(x['cpu'] for x in ledger); anchor=current
                if time.perf_counter()>=deadline: raise E.Cap('trajectory wall cap')
                if cert is not None:
                    start=time.process_time(); hc=counters(); loss,witness=C.horizon(cert,p,v,m,current,hc)
                    account(current,'frontier_horizon',hc,time.process_time()-start)
                    boundary=cert['interval'][1]
                    stop=min(row['end'],boundary if boundary is not None else row['end'])
                    segment=dict(kind='frontier',anchor=current,until=stop,packing=m,construction=len(constructs)-1,loss=loss,witness=witness)
                    if loss is not None and loss<=stop:
                        segment['until']=loss; segments.append(segment)
                        segment_refs.append(persist(f'segment-{len(segments)-1:04}.json.gz',segment)); current=loss
                        assert C.at(cert,current)>value(p,m)+current*value(v,m)
                        event(dict(kind='strict_loss',time=current,packing=m,witness=witness,construction=len(constructs)-1))
                        source(current)
                        if boundary is not None and current==boundary and current<row['end']:
                            old_value=C.at(cert,current)
                            construct(current,current,min(current+256,row['end']),'indexed')
                            if cert is not None: assert C.at(cert,current)==old_value
                    elif stop==row['end']:
                        segments.append(segment); segment_refs.append(persist(f'segment-{len(segments)-1:04}.json.gz',segment))
                        current=stop; status='window_complete'
                        elapsed=time.process_time()-iteration_cpu-(sum(x['cpu'] for x in serialization)-ser_before)-(sum(x['cpu'] for x in ledger)-component_before)
                        account(anchor,'driver_bookkeeping',{},max(0,elapsed)); break
                    else:
                        segments.append(segment); segment_refs.append(persist(f'segment-{len(segments)-1:04}.json.gz',segment))
                        current=stop; old_value=C.at(cert,current)
                        event(dict(kind='window_join',time=current,packing=m,objective=old_value))
                        construct(current,current,min(current+256,row['end']),'indexed')
                        if cert is not None: assert C.at(cert,current)==old_value
                else:
                    # A saved scalar partition can be stale after frontier phases.
                    q=[a+current*b for a,b in zip(p,v)]
                    if proof_anchor!=current:
                        start=time.process_time(); work=E.Work(w,q,m,ct,deadline)
                        before=copy.deepcopy(proof)
                        try: repaired=work.repair(proof)
                        except E.Cap as exc:
                            repaired=dict(success=False,incomplete=True,reason=str(exc),partial_repair=getattr(work,'partial_repair',None),trace=getattr(work,'repair_trace',[]))
                        account(current,'fallback_reprice',work.ct,time.process_time()-start)
                        event(dict(kind='fallback_reprice',time=current,packing=m,before=before,calls=work.calls,result=repaired,counters=work.ct))
                        if repaired.get('incomplete'): raise E.Cap(repaired['reason'])
                        if not repaired['success']:
                            assert value(w,repaired['witness'])<=c and value(q,repaired['witness'])>value(q,m)
                            source(current)
                        else: proof=repaired['proof']; proof_anchor=current
                    start=time.process_time(); h=H.certificate_horizon(proof,w,q,v,m)
                    account(current,'scalar_horizon',{'horizon_evaluations':h['evaluations']},time.process_time()-start)
                    dt=h['first_failure']; nt=None if dt is None else current+dt
                    segment=dict(kind='scalar',anchor=current,until=row['end'] if nt is None or nt>row['end'] else nt,packing=m,proof=copy.deepcopy(proof),certificate=h)
                    segments.append(segment); segment_refs.append(persist(f'segment-{len(segments)-1:04}.json.gz',segment))
                    if nt is None or nt>row['end']:
                        current=row['end']; status='window_complete'
                        elapsed=time.process_time()-iteration_cpu-(sum(x['cpu'] for x in serialization)-ser_before)-(sum(x['cpu'] for x in ledger)-component_before)
                        account(anchor,'driver_bookkeeping',{},max(0,elapsed)); break
                    current=nt; q=[a+current*b for a,b in zip(p,v)]
                    start=time.process_time(); work=E.Work(w,q,m,ct,deadline); work.ct['maintenance_events']=1
                    try: repaired=work.repair(proof)
                    except E.Cap as exc:
                        repaired=dict(success=False,incomplete=True,reason=str(exc),partial_repair=getattr(work,'partial_repair',None),trace=getattr(work,'repair_trace',[]))
                    account(current,'scalar_expiry',work.ct,time.process_time()-start)
                    event(dict(kind='scalar_expiry',time=current,packing=m,before=proof,calls=work.calls,result=repaired,counters=work.ct))
                    if repaired.get('incomplete'): raise E.Cap(repaired['reason'])
                    if repaired['success']: proof=repaired['proof']; proof_anchor=current
                    else:
                        witness=repaired['witness']
                        assert value(w,witness)<=c and value(q,witness)>value(q,m)
                        event(dict(kind='strict_loss',time=current,packing=m,witness=witness,construction=None))
                        source(current)
                elapsed=time.process_time()-iteration_cpu-(sum(x['cpu'] for x in serialization)-ser_before)-(sum(x['cpu'] for x in ledger)-component_before)
                account(anchor,'driver_bookkeeping',{},max(0,elapsed))
                # Immutable phase checkpoints retain all completed actions.
                checkpoint_cpu=time.process_time(); old_serial=sum(x['cpu'] for x in serialization)
                checkpoint()
                account(current,'checkpoint_bookkeeping',{},max(0,time.process_time()-checkpoint_cpu-(sum(x['cpu'] for x in serialization)-old_serial)))
    except E.Cap as exc:
        status='capped'
        pending=dict(kind='native_pending_restart' if native and native[-1]['status']=='pending_restart' else 'policy_action',
                     reason=str(exc),time=current,packing=m,last_complete_scalar_proof=proof,scalar_anchor=proof_anchor,
                     active_construction=None if cert is None else len(constructs)-1,counters=ct)
        persist('pending.json.gz',pending)
    # Up-front input copying, initial source result handling and final certificate handling.
    measured=time.process_time()-cpu-sum(x['cpu'] for x in serialization)
    allocated=sum(x['cpu'] for x in ledger)
    residual=measured-allocated
    account(current,'final_handling_and_accounting',{},max(0,residual))
    component_cpu=defaultdict(float)
    for x in ledger: component_cpu[x['kind']]+=x['cpu']
    # Final proofs remain retained output. Their disposal is outside every policy's CPU boundary.
    result=dict(stage=stage,case_id=row['case_id'],policy=method,status=status,final_time=current,
                final_packing=m,normalized=normalized,gate=locals().get('selected_gate'),
                totals=ct,ledger=ledger,component_cpu=dict(component_cpu),algorithm_cpu=sum(component_cpu.values()),
                measured_algorithm_cpu=measured,cpu_reconciliation_error=sum(component_cpu.values())-measured,
                algorithm_wall=time.perf_counter()-wall-sum(x['wall'] for x in serialization),
                native=native,constructions=constructs,events=events,segments=segments,pending=pending,
                serialization=serialization,output_proof_disposal_inside_boundary=False,
                switch_times=[x['time'] for x in native[1:] if x['status']=='complete'])
    # Physical machine time is never part of a logical repeat fingerprint.
    import hashlib,json
    signature=dict(totals=ct,switch_times=result['switch_times'],status=status,
                   native=[(x['time'],x.get('objective'),x.get('packing'),x.get('construction_steps'),x.get('proof')) for x in native],
                   builds=[(x['method'],x['status'],x['counters'],x['raw_by_prefix'],x['retained_by_prefix']) for x in constructs])
    result['logical_signature']=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
    return result


if __name__=='__main__':
    start_decode=time.process_time(); row=read(sys.argv[1]); method=sys.argv[2]; folder=Path(sys.argv[3]); selection=read(sys.argv[4]) if len(sys.argv)>4 else None
    decode=time.process_time()-start_decode
    E.LIMITS['evaluations']=limits(row['stage'])['scalar_evaluations']
    result=run(row,method,folder,selection)
    result['input_decoding_cpu']=decode
    save(folder/'Path-result.json.gz',result,immutable=True)
    print(result['case_id'],method,result['status'],result['algorithm_cpu'],flush=True)
