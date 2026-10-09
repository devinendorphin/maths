"""Post-run descriptive aggregation; no significance or scalability inference."""
import collections
import json
from pathlib import Path
import statistics
import sys
from checker import verify
from producer import certificate


def describe(values):
    return dict(min=min(values),median=statistics.median(values),max=max(values),sum=sum(values))


def one(root):
    sessions=json.loads((root/'Sessions.json').read_text());groups={};phases=collections.Counter();failed=collections.Counter();memory=[];proofsizes=[];fair=[]
    stability=collections.Counter()
    for s in sessions['sessions']:
        w=json.loads((root/'outputs'/s['name']/'Worker.json').read_text());memory.append(s['wait4_maxrss_kib'])
        if s['mode']=='updates':
            key=s['method'];g=groups.setdefault(key,dict(session_wall_s=[],session_cpu_s=[],query_wall_s=[],query_cpu_s=[],peak_rss_kib=[],cache_bytes=[],phase_s=collections.Counter(),failed_probes=0))
            g['session_wall_s'].append(s['session_wall_s']);g['session_cpu_s'].append(s['wait4_user_cpu_s']+s['wait4_system_cpu_s']);g['peak_rss_kib'].append(s['wait4_maxrss_kib']);g['cache_bytes'].append(w['cache_peak_bytes'])
            for r in w['records']:
                g['query_wall_s'].append(r['query_wall_s']);g['query_cpu_s'].append(r['query_cpu_s']);g['phase_s'].update(r['timing']);g['failed_probes']+=sum(not p['accepted'] for p in r['attempts'])
            if s['method']=='cold' and s['repetition']==0:
                for old,new in zip(w['records'],w['records'][1:]):
                    if old['proof']['kind']!='optimal':stability['previously_infeasible']+=1;continue
                    if new['proof']['kind']!='optimal':stability['newly_infeasible']+=1;continue
                    from checker import feasible
                    if not feasible(new['model'],old['proof']['flow']):stability['old_flow_now_infeasible']+=1;continue
                    value=sum(e['c']*x for e,x in zip(new['model']['edges'],old['proof']['flow']))
                    if value==new['proof']['cost_units']:
                        stability['old_flow_still_optimal']+=1
                        p=certificate(new['model'],w['dependency'],flow=old['proof']['flow'],pi=old['proof']['pi'])
                        stability['old_potential_still_applies' if verify(new['model'],p,w['dependency']) else 'old_flow_optimal_but_old_potential_fails']+=1
                    else:stability['old_flow_feasible_but_suboptimal']+=1
        if s['mode']=='fairness':fair.append(dict(case=s['index'],**w['extras'],session_wall_s=s['session_wall_s'],session_cpu_s=s['wait4_user_cpu_s']+s['wait4_system_cpu_s'],peak_rss_kib=s['wait4_maxrss_kib'],candidate_probes=len(w['records'])-1,failed_probes=sum(r['proof']['kind']=='cut' for r in w['records'][1:])))
        for r in w['records']:proofsizes.append(r['proof_bytes']);phases.update(r['timing']);failed.update(p['probe'] for p in r['attempts'] if not p['accepted'])
    for g in groups.values():
        for k in ['session_wall_s','session_cpu_s','query_wall_s','query_cpu_s','peak_rss_kib','cache_bytes']:g[k]=describe(g[k])
        g['phase_s']=dict(g['phase_s'])
    return {'audit':json.loads((root/'Audit.json').read_text()),'workers':len(sessions['sessions']),'queries':sum(json.loads((root/'outputs'/s['name']/'Worker.json').read_text())['records'].__len__() for s in sessions['sessions']),
            'launcher_wall_s':sessions['launcher_wall_s'],'launcher_cpu_s':sessions['launcher_cpu_s'],'all_session_wall_s':sum(s['session_wall_s'] for s in sessions['sessions']),
            'all_worker_cpu_s':sum(s['wait4_user_cpu_s']+s['wait4_system_cpu_s'] for s in sessions['sessions']),
            'peak_worker_rss_kib':describe(memory),'certificate_bytes':describe(proofsizes),'phase_totals_s':dict(phases),'failed_probes':dict(failed),
            'update_methods':groups,'cold_plan_transition_diagnostics':dict(stability),'fairness':fair}


if __name__=='__main__':
    result={'primary':one(Path(sys.argv[1])),'replica':one(Path(sys.argv[2])),'counts_per_run':'4 heldout base networks, 3 streams, 9 observations, 6 routes, 3 repetitions =1944 update queries; 11 static, 84 fairness probe/scalar, 6 counterexample and54 binding-budget queries; 10 supplemental assurance groups separate.'}
    Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n')
    for name in ['primary','replica']:
        r=result[name];print(name,'session wall',r['all_session_wall_s'],'worker CPU',r['all_worker_cpu_s'],'RSS',r['peak_worker_rss_kib'],'proof bytes',r['certificate_bytes'])
        for method,g in r['update_methods'].items():print(method,'session wall median ms',g['session_wall_s']['median']*1000,'CPU sum',g['session_cpu_s']['sum'],'failed probes',g['failed_probes'])
        print('Stability',r['cold_plan_transition_diagnostics']);print('Fairness',r['fairness'])
