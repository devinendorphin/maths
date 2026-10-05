"""Selective scalar repair with either rescan or cached priority-queue dispatch."""
import copy
import heapq
import time
from shared import E,H,C,common,native,value


def run(row,mode,force_cap=False):
    start=time.process_time(); t=0; serial=0; cells={}; queue=[]; sources=[]; repairs=[]; segments=[]
    counts=dict(horizon_cells=0,horizon_evaluations=0,heap_pushes=0,heap_pops=0,
                failure_events=0,failed_cells=0,packing_changes=0,repair_bound_evaluations=0)
    capped=None; m=0
    def horizon(cell,at):
        shifted=list(cell); shifted[5]=H.numerator(cell,row['weights'],row['profits'],row['slopes'],at)
        q=[a+at*b for a,b in zip(row['profits'],row['slopes'])]
        dt,ct=H.cell_horizon(shifted,row['weights'],q,row['slopes'],m)
        counts['horizon_cells']+=1; counts['horizon_evaluations']+=ct['evaluations']
        return None if dt is None else at+dt
    def install(proof,at,reset=False):
        nonlocal serial
        if reset: cells.clear(); queue.clear()
        for cell in proof:
            ident=serial; serial+=1; cells[ident]=list(cell)
            if mode=='queue':
                loss=horizon(cell,at)
                if loss is not None: heapq.heappush(queue,(loss,ident)); counts['heap_pushes']+=1
    def source(at):
        nonlocal m
        old=m; r=native(row,at); r['time']=at; sources.append(r); m=r['packing']
        if at and value(row['profits'],old)+at*value(row['slopes'],old)<r['objective']:
            counts['packing_changes']+=1
        install(r['proof'],at,reset=True)
    source(0)
    if force_cap:
        try:
            built,ct=C.build(row['weights'],row['profits'],row['slopes'],row['capacity'],'indexed',
                             (0,row['end']),time.perf_counter()+30,common.counters(),{'transitions':1})
            raise AssertionError('forced partial build unexpectedly completed')
        except C.BuildCap as exc:
            capped=exc.partial
            assert not capped['complete']
    while t<=row['end']:
        if time.process_time()-start>60: raise RuntimeError('event sequence CPU cap')
        if mode=='queue':
            expired=[]
            while queue and queue[0][1] not in cells: heapq.heappop(queue); counts['heap_pops']+=1
            loss=queue[0][0] if queue else None
            if loss is not None and loss<=row['end']:
                while queue and queue[0][0]==loss:
                    _,i=heapq.heappop(queue); counts['heap_pops']+=1
                    if i in cells: expired.append(i)
        else:
            failures={i:horizon(cell,t) for i,cell in cells.items()}
            loss=min((x for x in failures.values() if x is not None),default=None)
            expired=[i for i,x in failures.items() if x==loss] if loss is not None else []
        until=row['end'] if loss is None else min(row['end'],loss-1)
        assert until>=t
        segments.append(dict(anchor=t,until=until,packing=m,proof=copy.deepcopy(list(cells.values()))))
        if loss is None or loss>row['end']: break
        t=loss; counts['failure_events']+=1; counts['failed_cells']+=len(expired)
        old_proof=[cells[i] for i in expired]; q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
        work=E.Work(row['weights'],q,m,E.empty_counts(),time.perf_counter()+30)
        result=work.repair(old_proof)
        repairs.append(dict(time=t,packing=m,expired=expired,before=copy.deepcopy(old_proof),
                            calls=work.calls,result=result,counters=work.ct))
        counts['repair_bound_evaluations']+=work.ct['bound_evaluations']
        if not result['success']:
            assert value(q,result['witness'])>value(q,m)
            source(t)
        else:
            for ident in expired: del cells[ident]
            install(result['proof'],t)
    return dict(method='selective_'+mode+('_after_cap' if force_cap else ''),
                algorithm_cpu=time.process_time()-start,sources=sources,repairs=repairs,
                segments=segments,counts=counts,capped_construction=capped,
                capped_active=False,packings=[next(s['packing'] for s in segments if s['anchor']<=x<=s['until'])
                                             for x in range(row['end']+1)])
