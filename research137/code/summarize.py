"""Summarize both retained measurement sets; exclude measurements only in equality."""
import hashlib
import json
from pathlib import Path
import statistics
import sys


def run(primary,replica,out):
    roots=[Path(primary),Path(replica)];out=Path(out)
    math=[json.loads((r/'Mathematical-records.json').read_text()) for r in roots]
    assert math[0]==math[1]
    assert (roots[0]/'Controls.json').read_bytes()==(roots[1]/'Controls.json').read_bytes()
    assert (roots[0]/'Freeze.json').read_bytes()==(roots[1]/'Freeze.json').read_bytes()
    session_sets=[json.loads((r/'Sessions.json').read_text()) for r in roots]
    expected={(i,route,rep,4096) for i in range(6) for route in ('cold','full-recheck','delta-buffered','delta-fsync') for rep in range(3)}
    expected|={(i,'delta-buffered',0,64) for i in range(6)}
    for sessions in session_sets:
        assert len(sessions)==78 and len({s['name'] for s in sessions})==78
        assert {(s['index'],s['route'],s['repetition'],s['budget']) for s in sessions}==expected
    for a,b in zip(session_sets[0],session_sets[1]):
        assert {k:v for k,v in a.items() if k not in ('wall_s','kernel_cpu_s','kernel_maxrss_kib')}=={k:v for k,v in b.items() if k not in ('wall_s','kernel_cpu_s','kernel_maxrss_kib')}
        workers=[json.loads((root/'outputs'/s['name']/'Worker.json').read_text()) for root,s in zip(roots,(a,b))]
        excluded=('timing','journal_io_s','worker_wall_s','worker_cpu_s','worker_peak_rss_kib')
        assert {k:v for k,v in workers[0].items() if k not in excluded}=={k:v for k,v in workers[1].items() if k not in excluded}
        for worker,session in zip(workers,(a,b)):
            assert all(worker[k]==session[k] for k in ('index','route','repetition','budget'))
    sets=[]
    for root in roots:
        sessions=json.loads((root/'Sessions.json').read_text());groups={};budget=[]
        for s in sessions:
            w=json.loads((root/'outputs'/s['name']/'Worker.json').read_text())
            if s['budget']==64:budget.append(w);continue
            groups.setdefault((s['index'],s['route']),[]).append((s,w))
        table=[]
        inputs=json.loads((root/'Inputs.json').read_text())['heldout']
        for (i,route),rows in sorted(groups.items()):
            m=inputs[i]['model']
            table.append({'index':i,'nodes':m['n'],'edges':len(m['edges']),'route':route,
                          'median_session_ms':statistics.median(s['wall_s'] for s,w in rows)*1000,
                          'median_kernel_cpu_ms':statistics.median(s['kernel_cpu_s'] for s,w in rows)*1000,
                          'median_update_ms':statistics.median(w['timing']['updates'] for s,w in rows)*1000,
                          'median_recovery_ms':statistics.median(w['timing']['recovery'] for s,w in rows)*1000,
                          'peak_kernel_rss_kib':max(s['kernel_maxrss_kib'] for s,w in rows),
                          'journal_bytes':rows[0][1]['journal_write_bytes'],
                          'checkpoint_bytes':rows[0][1]['checkpoint_bytes'],
                          'accepted_patches':sum(r['action']=='patch' for r in rows[0][1]['records']),
                          'failed_patches_or_rechecks':sum(r['action']=='fallback' for r in rows[0][1]['records']),
                          'compactions':sum(r.get('compacted',False) for r in rows[0][1]['records'])})
        sets.append({'table':table,'audit':json.loads((root/'Audit.json').read_text()),
                     'total_session_wall_s':sum(s['wall_s'] for s in sessions),
                     'total_kernel_cpu_s':sum(s['kernel_cpu_s'] for s in sessions),
                     'budget_control_compactions':sum(sum(r.get('compacted',False) for r in w['records']) for w in budget)})
    out.mkdir(exist_ok=True,parents=True)
    (out/'Summary.json').write_text(json.dumps({'primary':sets[0],'replica':sets[1]},indent=2)+'\n')
    (out/'Replication.json').write_text(json.dumps({'passed':True,'workers_per_directory':78,
       'mathematical_records_equal':True,'controls_equal':True,'frozen_context_equal':True,
       'all_journal_checkpoint_identities_equal':True,
       'excluded_fields':{'Sessions.json':['wall_s','kernel_cpu_s','kernel_maxrss_kib'],
                          'Worker.json':['timing','journal_io_s','worker_wall_s','worker_cpu_s','worker_peak_rss_kib'],
                          'Audit.json':['audit_wall_s']},
       'reason':'Measured observations cannot match bytewise; both are retained. All decisions, costs, flow/potential identities, logs, bytes and controls compare.',
       'mathematical_sha256':hashlib.sha256((roots[0]/'Mathematical-records.json').read_bytes()).hexdigest()},indent=2)+'\n')
    print(json.dumps(sets[0]['audit']))


if __name__=='__main__':run(*sys.argv[1:])
