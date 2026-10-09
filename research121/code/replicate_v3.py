"""Exact logical comparison; no exclusions inside logical records."""
import hashlib
import json
from pathlib import Path
import sys


def run(first,second,out):
    a=json.loads((first/'Results.json').read_text())+json.loads((first/'Supplement.json').read_text());b=json.loads((second/'Results.json').read_text())+json.loads((second/'Supplement.json').read_text());assert len(a)==len(b)
    differences=[]
    for index,(x,y) in enumerate(zip(a,b)):
        for key in ['stage','repeat','logical']:
            if x[key]!=y[key]:differences.append(dict(index=index,field=key,first=x[key],second=y[key]))
    for name in ['Freeze.json','Audit-amendment.json','Supplement-freeze.json','Policy.json','Policy-freeze.json','Training.json','Checker-fixtures.json']:
        assert (first/name).read_bytes()==(second/name).read_bytes(),name
    # The training evidence and frozen policy are copied, explicitly not claimed
    # as an independent rerun. Every held-out/control record is rerun.
    report=dict(passed=not differences,records_compared=len(a),differences=differences,comparison='Every stage, repeat and logical field, including original model, proof/raw-proof/formula hashes, witness packing, interval endpoints, policy decisions, invalidation and byte-budget traces.',excluded_fields={'measurements':'All CPU/wall/phases/residual, reachable Python/tracemalloc memory and sampled RSS/process observations are machine measurements, not mathematical or proof identity fields. Reported separately, never used to suppress logical discrepancies.'},shared=['External SDK installation','Frozen policy, original 72-record training evidence and their proof files (not counted as independent replication)' ],fresh=['All 451 campaign plus six separately frozen cap-repair executions, produced proofs, false-bound controls and independent audit'])
    out.write_text(json.dumps(report,indent=2)+'\n');assert report['passed'],differences
    print('Exact logical/proof replication passed for',len(a),'records')


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
