"""Compare complete mathematical records and explicit session outcomes."""
import json
from pathlib import Path
import sys


def run(a,b,output):
    left=json.loads((a/'Mathematical-records.json').read_text());right=json.loads((b/'Mathematical-records.json').read_text())
    assert left==right,'meaningful replication disagreement'
    aa=json.loads((a/'Sessions.json').read_text())['sessions'];bb=json.loads((b/'Sessions.json').read_text())['sessions']
    excluded=['session_wall_s','wait4_user_cpu_s','wait4_system_cpu_s','wait4_maxrss_kib']
    assert [{k:v for k,v in s.items() if k not in excluded} for s in aa]==[{k:v for k,v in s.items() if k not in excluded} for s in bb]
    for name in ['Proof-controls.json']:
        assert json.loads((a/name).read_text())==json.loads((b/name).read_text())
    report={'passed':True,'mathematical_records_including_session_summaries':len(left),'query_records':len(left)-len(aa),'workers':len(aa),'exact_proof_and_control_identity_match':True,'excluded_measurements':{'query':['timing','query_wall_s','query_cpu_s'],'worker':['worker_wall_s','worker_cpu_s','kernel_self_maxrss_kib'],'session':excluded,'campaign':['launcher_wall_s','launcher_cpu_s'],'audit':['audit_wall_s','audit_cpu_s']},'reason':'Elapsed time, CPU and kernel peak RSS are independent observations and are retained in both runs. No mathematical outcomes, model/proof/dependency hashes, operation counters, cache/eviction decisions, failed probes or exit states are excluded. Relative record labels are identical; no paths occur in logical records.','shared_dependency_installation':True}
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
