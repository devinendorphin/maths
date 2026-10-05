"""Verify the small published package without downloading the proof archive."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from campaign import check_freeze, inputs
from verify import digest
from summarize import main as summarize

def load(name): return json.loads((ROOT/name).read_text())
def main():
    check_freeze(); assert inputs()==load('Inputs.json')
    paths=load('Path-results.json'); builds=load('Construction-results.json')
    assert len(paths)==690 and len(builds)==72
    assert all(p['status']=='window_complete' and p['audit_passed'] for p in paths)
    assert all(b['audit_passed'] for b in builds)
    selection=load('Selection.json'); tuning=[p for p in paths if p['phase'].startswith('tuning')]
    assert digest(tuning)==selection['training_records_hash']
    assert digest(load('Freeze-original.json'))==selection['freeze_hash']
    score=min(enumerate(selection['scores']),key=lambda p:(p[1]['median'],p[0]))[1]
    assert score['candidate']==selection['chosen']
    amend=load('Implementation-amendment.json')
    assert hashlib.sha256((ROOT/'Freeze-original.json').read_bytes()).hexdigest()==amend['original_freeze_sha256']
    assert load('Freeze-original.json')['files']['code/campaign.py']==amend['original_campaign_sha256']
    assert load('Freeze.json')['files']['code/campaign.py']==amend['amended_campaign_sha256']
    summary=(ROOT/'Summary.json').read_bytes(); synthesis=(ROOT/'Synthesis.md').read_bytes()
    summarize()
    assert (ROOT/'Summary.json').read_bytes()==summary
    assert (ROOT/'Synthesis.md').read_bytes()==synthesis
    print(json.dumps(dict(passed=True,unique_inputs=105,path_records=690,construction_records=72,
        integer_time_checks=load('Summary.json')['integer_time_checks'],
        proof_archive_required_for_independent_reaudit=True)))

if __name__=='__main__': main()
