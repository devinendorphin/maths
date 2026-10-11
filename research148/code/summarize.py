"""Predeclared median complete-session and sum-of-query accounting, no tuning."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
from engine import ROUTES


def run(primary,replica,destination):
    roots=[Path(primary),Path(replica)];out=Path(destination);out.mkdir(exist_ok=True)
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):
        assert (roots[0]/name).read_bytes()==(roots[1]/name).read_bytes(),name
    rows=[]
    for root in roots:
        sessions=json.loads((root/'Sessions.json').read_text());inputs=json.loads((root/'Inputs.json').read_text())['heldout']
        for i,entry in enumerate(inputs):
            routes={}
            for route in ROUTES:
                group=[s for s in sessions if s['index']==i and s['route']==route]
                assert len(group)==2
                workers=[json.loads((root/'outputs'/s['name']/'Worker.json').read_text()) for s in group]
                routes[route]={'session_ms':1000*statistics.median(s['wall_s'] for s in group),
                               'queries_ms':1000*statistics.median(sum(w['query_wall_s']) for w in workers),
                               'kernel_cpu_ms':1000*statistics.median(s['kernel_cpu_s'] for s in group),
                               'peak_rss_kib':max(s['kernel_maxrss_kib'] for s in group),
                               'evidence_bytes':workers[0]['evidence_bytes']}
            rows.append({'run':root.name,'index':i,'family':entry['family'],'nodes':entry['model']['n'],'edges':len(entry['model']['edges']),'routes':routes})
    result={'exact_logical_replication':True,'rows':rows,'runs':{r.name:json.loads((r/'Audit.json').read_text()) for r in roots},
            'freeze_sha256':hashlib.sha256((roots[0]/'Freeze.json').read_bytes()).hexdigest()}
    (out/'Results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('All logical, proof, control and raw journal identities reproduced')


if __name__=='__main__':run(*sys.argv[1:])
