"""Compact seals; optionally replay every mathematical worker and VIPR check."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def run(full=False):
    seal=json.loads((ROOT/'Freeze.json').read_text())
    for name,h in seal['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    summary=json.loads((ROOT/'Summary.json').read_text());audit=json.loads((ROOT/'Final-audit.json').read_text())
    assert hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()==audit['summary_sha256']
    rows=json.loads((ROOT/'Path-results.json').read_text());assert len(rows)==420==summary['workers']
    groups=defaultdict(list)
    for s in rows:
        assert s['audit']['passed'];groups[(s['case_id'],s['method'])].append(s)
    for key,samples in groups.items():
        if all(s['status']=='complete' for s in samples):assert len({s['signature'] for s in samples})==1,key
    complete_cases={s['case_id'] for s in rows if s['status']=='complete'}
    assert len(complete_cases)==70
    manifest_path=ROOT/'Archive-members.json'
    present=0
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        for member in manifest['members']:
            p=ROOT/member['path']
            if p.exists():
                assert p.stat().st_size==member['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==member['sha256'],str(p);present+=1
            elif full:raise FileNotFoundError(p)
    result=dict(passed=True,workers=420,complete_workers=summary['complete_workers'],capped_workers=summary['capped_workers'],
                all_inputs_have_complete_answers=True,present_member_hashes=present,full_reaudit=full)
    if full:
        for name,h in seal['dependencies'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
        sys.path.insert(0,str(ROOT/'code'))
        from shared import read,logical,digest
        import audit as independent
        checkers={};count=0
        for p in sorted((ROOT/'evidence').glob('*--*.json.gz')):
            r=read(p);row=r['input'];key=row['case_id']
            if key not in checkers:checkers[key]=independent.Auditor(row)
            assert checkers[key].check(r['result'])['passed']
            assert digest(logical(r['result']))==r['summary']['signature'];count+=1
        assert count==420
        valid=invalid=0
        for p in sorted((ROOT/'evidence/vipr').glob('*.vipr')):
            checked=subprocess.run([str(ROOT/'dependencies/vipr/viprchk'),str(p)],capture_output=True,text=True,timeout=30)
            if p.name.endswith('-invalid.vipr'):assert checked.returncode!=0;invalid+=1
            else:assert checked.returncode==0;valid+=1
        assert valid==invalid==24;result.update(vipr_valid=valid,vipr_invalid_rejected=invalid)
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args();run(args.full)
