def cumulative(path,t,key='bound_evaluations'):
    return sum(e['counters'][key] for e in path['events'] if e['time']<=t)

def comparison(base,hybrid,end):
    rebuilds=[e for e in hybrid['events'] if e['action']=='rebuild']
    out=dict(mode=hybrid['mode'],attempted=bool(rebuilds),final_saving=base['totals']['bound_evaluations']-hybrid['totals']['bound_evaluations'])
    if not rebuilds:return out
    assert len(rebuilds)==1;event=rebuilds[0];t=event['time'];r=event['result'];out.update(reconstruction_time=t,successful=r['success'])
    assert cumulative(base,t-1)==cumulative(hybrid,t-1)
    if not r['success']:return out
    savings=[cumulative(base,s)-cumulative(hybrid,s) for s in range(t,end+1)]
    durable=next((t+i for i,z in enumerate(savings) if z>0 and all(x>0 for x in savings[i:])),None)
    out.update(prior_cells=event['prior_cells'],reconstructed_cells=len(r['proof']),compacted=len(r['proof'])<event['prior_cells'],initial_extra_cost=-savings[0],first_advantage_time=next((t+i for i,z in enumerate(savings) if z>0),None),durable_advantage_time=durable,payback_delay=None if durable is None else durable-t,savings_by_time=savings)
    return out

def summarize(rows):
    modes={}
    for i,mode in enumerate(('maintain','once_1','once_4','once_16','rebuild')):
        paths=[x['paths'][i] for x in rows]
        modes[mode]=dict(bound_evaluations=sum(x['totals']['bound_evaluations'] for x in paths),free_term_evaluations=sum(x['totals']['free_term_evaluations'] for x in paths),splits=sum(x['totals']['splits'] for x in paths),events=sum(len(x['events']) for x in paths),core_cpu=sum(x['totals']['core_cpu'] for x in paths),statuses={s:sum(x['status']==s for x in paths) for s in ('packing_lost','forever_certified','window_complete')})
    summaries={};comparisons=[]
    for x in rows:
        comparisons.append(dict(case_id=x['case_id'],regime=x.get('regime','synthetic'),rows=[comparison(x['paths'][0],path,x['end']) for path in x['paths'][1:4]]))
    for mode in ('once_1','once_4','once_16'):
        cases=[z for x in comparisons for z in x['rows'] if z['mode']==mode];successful=[z for z in cases if z.get('successful')]
        summaries[mode]=dict(attempted=sum(z['attempted'] for z in cases),successful=len(successful),compacted=sum(z['compacted'] for z in successful),paid_back=sum(z['durable_advantage_time'] is not None for z in successful),paid_positive_extra_cost=sum(z['initial_extra_cost']>0 and z['durable_advantage_time'] is not None for z in successful),benefited=sum(z['final_saving']>0 for z in cases),harmed=sum(z['final_saving']<0 for z in cases),tied=sum(z['final_saving']==0 for z in cases),payback_delays=[z['payback_delay'] for z in successful if z['payback_delay'] is not None])
    return dict(cases=len(rows),modes=modes,hybrids=summaries,comparisons=comparisons)
