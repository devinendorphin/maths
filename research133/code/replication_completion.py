"""Post-run comparison of duplicate logs, preflights and non-timing metadata."""
import json
from pathlib import Path
import sys


def run(a,b,output):
    audits=[]
    for root in (a,b):
        audit=json.loads((root/'Audit.json').read_text())
        audits.append({k:v for k,v in audit.items() if k not in ['audit_wall_s','audit_cpu_s']})
    assert audits[0]==audits[1]
    sessions=json.loads((a/'Sessions.json').read_text())['sessions']
    for s in sessions:
        left=a/'outputs'/s['name'];right=b/'outputs'/s['name']
        assert (left/'stderr.txt').read_bytes()==(right/'stderr.txt').read_bytes()==b''
        logs=[json.loads((root/'stdout.txt').read_text()) for root in (left,right)]
        assert {k:v for k,v in logs[0].items() if k!='worker_wall_s'}=={k:v for k,v in logs[1].items() if k!='worker_wall_s'}
    for name in ['Freeze.json','Maintenance-freeze.json','Deployment-check.json','Inputs.json','Protocol.md','Setup.json','Development.json','Primary-source-receipts.json']:
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
    report={'passed':True,'workers':len(sessions),'duplicate_stdout_counts_match':True,'stderr_empty_in_both_runs':True,'all_nontiming_audit_metadata_matches':True,'frozen_configuration_and_preflights_match':True,'additional_excluded_field':'stdout.worker_wall_s: duplicate of the explicitly excluded worker measurement; both original logs retained','setup_timing_not_excluded':'Setup.json is the same recorded shared installation receipt in both directories; it is not a second installation observation'}
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
