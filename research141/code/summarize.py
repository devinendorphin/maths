"""Post-run summaries; no source or parameter selection from timing outcomes."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1]


def run(primary,replica):
    roots=[Path(primary),Path(replica)];storage=ROOT.name=='research141';reports={};cells={}
    for name in ('Freeze.json','Inputs.json','Logical.json','Controls.json'):
        assert (roots[0]/name).read_bytes()==(roots[1]/name).read_bytes(),name
    for label,root in zip(('primary','replica'),roots):
        audit=json.loads((root/'Audit.json').read_text());reports[label]=audit
        (ROOT/('Audit-'+label+'.json')).write_bytes((root/'Audit.json').read_bytes())
        sessions=json.loads((root/'Sessions.json').read_text());groups={}
        for s in sessions:
            key=(s['index'],s['format'],s['policy']) if storage else (s['index'],s['route'])
            groups.setdefault(key,[]).append(s)
        table=[]
        for key,ss in sorted(groups.items()):
            ws=[json.loads((root/'outputs'/s['name']/'Worker.json').read_text()) for s in ss];assert len(ss)==2
            record={'index':key[0],'format':key[1],'policy':key[2]} if storage else {'index':key[0],'route':key[1]}
            record.update(wall_mean_s=statistics.mean(s['wall_s'] for s in ss),wall_range_s=[min(s['wall_s'] for s in ss),max(s['wall_s'] for s in ss)],
                          kernel_cpu_mean_s=statistics.mean(s['kernel_cpu_s'] for s in ss),kernel_maxrss_kib=max(s['kernel_maxrss_kib'] for s in ss),
                          worker_wall_mean_s=statistics.mean(w['worker_wall_s'] for w in ws),session_samples=ss)
            names=('active_peak_bytes','active_final_bytes','active_written_bytes','raw_evidence_bytes','snapshots','recovery_checks') if storage else ('evidence_bytes',)
            for name in names:assert ws[0][name]==ws[1][name];record[name]=ws[0][name]
            record['actions']={a:sum(r['action']==a for r in ws[0]['records']) for a in sorted({r['action'] for r in ws[0]['records']})}
            if not storage:record['pivots']=sum(r['pivots'] for r in ws[0]['records'])
            table.append(record)
        cells[label]=table
    assert {k:v for k,v in reports['primary'].items() if k!='audit_wall_s'}=={k:v for k,v in reports['replica'].items() if k!='audit_wall_s'}
    receipt={'passed':True,'exact_files':{n:hashlib.sha256((roots[0]/n).read_bytes()).hexdigest() for n in ('Freeze.json','Inputs.json','Logical.json','Controls.json')},
             'audits':reports,'scope':'fresh directories in shared pinned installation; resource measurements intentionally differ'}
    (ROOT/'Replication.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    (ROOT/'Summary.json').write_text(json.dumps(cells,sort_keys=True,indent=2)+'\n')
    print('Exact replication and full cost summaries written:',ROOT.name)


if __name__=='__main__':run(*sys.argv[1:])
