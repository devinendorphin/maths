import horizon as H
from repeated import kernel

POLICIES=('maintain','once_1','once_4','once_16','rebuild')

def run(w,p,v,c,m,initial,mode,end=64):
    proof=[list(x) for x in initial];t=0;events=[];peak=len(proof);total=dict(price_calls=0,bound_evaluations=0,free_term_evaluations=0,splits=0,core_cpu=0.0)
    trigger=int(mode.split('_')[1]) if mode.startswith('once_') else None
    while True:
        q=[a+t*b for a,b in zip(p,v)];cert=H.certificate_horizon(proof,w,q,v,m);dt=cert['first_failure']
        if dt is None:return dict(mode=mode,status='forever_certified',final_time=t,events=events,final_proof=proof,final_certificate=cert,peak_cells=peak,totals=total)
        next_time=t+dt
        if next_time>end:return dict(mode=mode,status='window_complete',final_time=end,last_renewal_time=t,events=events,final_proof=proof,final_certificate=cert,peak_cells=peak,totals=total)
        ordinal=len(events)+1;action='rebuild' if mode=='rebuild' or ordinal==trigger else 'repair'
        q=[a+next_time*b for a,b in zip(p,v)];domain=proof if action=='repair' else [[0,(1<<len(w))-1,c,0,1,0]]
        result,counts,cpu=kernel(domain,w,q,m)
        events.append(dict(time=next_time,ordinal=ordinal,action=action,previous_time=t,previous_certificate=cert,prior_cells=len(proof),input_cells=len(domain),result=result,counters=counts,core_cpu=cpu))
        for key in counts:total[key]+=counts[key]
        total['splits']+=result['splits'];total['core_cpu']+=cpu
        if not result['success']:return dict(mode=mode,status='packing_lost',final_time=next_time,events=events,final_proof=proof,peak_cells=peak,totals=total)
        proof=result['proof'];peak=max(peak,len(proof));t=next_time
        assert len(events)<=end
