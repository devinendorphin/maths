"""Create an isolated fresh run from archived source/dependency snapshots."""
import argparse
import json
from pathlib import Path
import platform
import shutil
import sys

SOURCE=Path(__file__).resolve().parents[1]


def run(target):
    if target.exists():raise FileExistsError(target)
    target.mkdir(parents=True)
    shutil.copytree(SOURCE/'code',target/'code',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(SOURCE/'dependencies',target/'dependencies',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(SOURCE/'Roadmap.md',target/'Roadmap.md')
    capability=dict(python=sys.version,platform=platform.platform(),replication_of='experiments-76-85',
                    vipr_commit='30f2951d1e90e47afa821bdd1b12b82246656c42')
    (target/'Capabilities.json').write_text(json.dumps(capability,sort_keys=True,indent=2)+'\n')
    sys.path.insert(0,str(target/'code'))
    import campaign
    campaign.freeze()
    assert json.loads((target/'Inputs.json').read_text())==json.loads((SOURCE/'Inputs.json').read_text())
    campaign.run()
    old=json.loads((SOURCE/'Path-results.json').read_text());new=json.loads((target/'Path-results.json').read_text())
    key=lambda r:(r['case_id'],r['method'],r['phase'],r['repeat'])
    old_complete={key(r):(r['status'],r['signature']) for r in old}
    new_complete={key(r):(r['status'],r['signature']) for r in new}
    assert old_complete==new_complete
    old_proofs=json.loads((SOURCE/'Proof-summary.json').read_text());new_proofs=json.loads((target/'Proof-summary.json').read_text())
    fields=('case_id','reuse','cache_hits','certificates','invalid_rejected','endpoint_references','bundles','rejected_scopes','integer_checks','bytes','derivations')
    assert [{k:r[k] for k in fields} for r in old_proofs]==[{k:r[k] for k in fields} for r in new_proofs]
    assert json.loads((SOURCE/'Cache-tests.json').read_text())==json.loads((target/'Cache-tests.json').read_text())
    print('FRESH REPLICATION PASSED',len(new),'workers; all statuses and logical signatures match')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('target',type=Path);args=parser.parse_args();run(args.target)
