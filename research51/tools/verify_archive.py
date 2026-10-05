"""Verify every declared archive member, with optional full mathematical re-audit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def run(full=False):
    manifest=json.loads((ROOT/'Archive-members.json').read_text())
    for row in manifest['members']:
        p=ROOT/row['path']
        assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
    if full:
        kernel=ROOT/'dependencies/stage35'
        os.environ['MATHS_BASELINE']=str(kernel)
        sys.path.insert(0,str(kernel));sys.path.insert(0,str(ROOT/'dependencies/research46/code'))
        sys.path.insert(0,str(ROOT/'code'))
        import campaign
        from shared import read
        count=0
        for p in sorted((ROOT/'evidence').glob('[0-9]*.json.gz')):
            record=read(p);stage=record['summary']['stage']
            assert campaign.audit(record['input'],stage,record['result'])['passed'];count+=1
        assert count==422
    print(json.dumps(dict(passed=True,members=len(manifest['members']),full_reaudit=full)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args();run(args.full)
