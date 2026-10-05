import time
import horizon as H
import renewal as R
import refine as F

def kernel(proof,w,q,m):
    original=R.reprice;old_refine=F.reprice;counts=dict(price_calls=0,bound_evaluations=0,free_term_evaluations=0)
    def counted(cell,w,q):
        result,n=original(cell,w,q);counts['price_calls']+=1;counts['bound_evaluations']+=n;counts['free_term_evaluations']+=n*cell[1].bit_count();return result,n
    R.reprice=F.reprice=counted
    try:
        start=time.process_time();renewed=R.renew(proof,w,q,m);result=F.repair(renewed['proof'],w,q,m);cpu=time.process_time()-start
    finally:R.reprice=original;F.reprice=old_refine
    return result,counts,cpu

def run(w,p,v,c,m,initial,mode,end=64):
    proof=[list(x) for x in initial];t=0;events=[];peak=len(proof);total=dict(price_calls=0,bound_evaluations=0,free_term_evaluations=0,splits=0,core_cpu=0.0)
    while True:
        q=[a+t*b for a,b in zip(p,v)];cert=H.certificate_horizon(proof,w,q,v,m);dt=cert['first_failure']
        if dt is None:return dict(mode=mode,status='forever_certified',final_time=t,events=events,final_proof=proof,final_certificate=cert,peak_cells=peak,totals=total)
        next_time=t+dt
        if next_time>end:return dict(mode=mode,status='window_complete',final_time=end,last_renewal_time=t,events=events,final_proof=proof,final_certificate=cert,peak_cells=peak,totals=total)
        q=[a+next_time*b for a,b in zip(p,v)];domain=proof if mode=='maintain' else [[0,(1<<len(w))-1,c,0,1,0]]
        result,counts,cpu=kernel(domain,w,q,m)
        event=dict(time=next_time,previous_time=t,previous_certificate=cert,input_cells=len(domain),result=result,counters=counts,core_cpu=cpu)
        events.append(event)
        for key in counts:total[key]+=counts[key]
        total['splits']+=result['splits'];total['core_cpu']+=cpu
        if not result['success']:return dict(mode=mode,status='packing_lost',final_time=next_time,events=events,final_proof=proof,peak_cells=peak,totals=total)
        proof=result['proof'];peak=max(peak,len(proof));t=next_time
        assert len(events)<=end
