"""Check compact source seal, corrected repeats, summaries and archive-member hashes."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run():
    seal=json.loads((ROOT/'Freeze.json').read_text())
    for name,expected in seal['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    summary=json.loads((ROOT/'Summary.json').read_text());audit=json.loads((ROOT/'Final-audit.json').read_text())
    assert hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()==audit['summary_sha256']
    assert hashlib.sha256((ROOT/'tools/finalize.py').read_bytes()).hexdigest()==summary['correction']['verifier_sha256']
    rows=json.loads((ROOT/'Path-results.json').read_text());assert len(rows)==summary['workers']==422
    groups=defaultdict(set)
    for row in rows:
        assert row['audit']['passed'];groups[(row['stage'],row['case_id'],row['method'])].add(row['signature'])
    assert all(len(v)==1 for v in groups.values())
    assert summary['all_audits_passed'] and audit['passed']
    manifest=json.loads((ROOT/'Archive-members.json').read_text())
    checked=0
    for row in manifest['members']:
        p=ROOT/row['path']
        if p.exists():
            assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
            checked+=1
    print(json.dumps(dict(passed=True,workers=len(rows),logical_groups=len(groups),present_archive_members_checked=checked)))


if __name__=='__main__':run()
