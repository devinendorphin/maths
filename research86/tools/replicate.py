"""Run every frozen worker from fresh algorithm/proof state and compare logical results."""
import argparse,json,shutil,sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]
def run(target):
 if target.exists():raise FileExistsError(target)
 target.mkdir(parents=True)
 for folder in ('code','dependencies'):shutil.copytree(SOURCE/folder,target/folder,ignore=shutil.ignore_patterns('__pycache__'))
 for name in ('Roadmap.md','Mathematical-guarantees.md','Capabilities.json'):shutil.copy(SOURCE/name,target/name)
 sys.path.insert(0,str(target/'code'));import campaign
 campaign.freeze();assert json.loads((target/'Inputs.json').read_text())==json.loads((SOURCE/'Inputs.json').read_text());campaign.run()
 old=json.loads((SOURCE/'Path-results.json').read_text());new=json.loads((target/'Path-results.json').read_text());key=lambda r:(r['case_id'],r['method'],r['phase'],r['repeat'])
 assert {key(r):(r['status'],r['signature']) for r in old}=={key(r):(r['status'],r['signature']) for r in new}
 receipt=dict(passed=True,workers=len(new),all_statuses_and_logical_signatures_match=True,original_timings_preserved=True,replica_timings_not_pooled=True)
 (target/'Replication.json').write_text(json.dumps(receipt,sort_keys=True));print('FRESH REPLICATION PASSED',len(new),'workers',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('target',type=Path);run(p.parse_args().target)
