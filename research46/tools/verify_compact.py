"""Verify sources, declared counts, seals, summaries and logical repeats."""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from campaign import check_freeze, inputs, protocol, GATES, BUDGETS
from verify import digest
from summarize import main as summarize

def load(name):return json.loads((ROOT/name).read_text())
def main():
    check_freeze();assert inputs()==load('Inputs.json') and digest(protocol())==digest(load('Protocol.json'))
    rows=load('Path-results.json');assert len(rows)==1020
    assert all(r['audit_passed'] and r['status']=='window_complete' and r['integer_time_checks']==r['end']+1 for r in rows)
    for phase,count in (('headline',444),('timing',360)):
        assert sum(r['phase']==phase for r in rows)==count
    for stage,candidates in ((47,GATES),(48,BUDGETS)):
        training=[r for r in rows if r['phase'].startswith(f'tuning{stage}_')]
        seal=load(f'Selection-{stage}.json')
        assert all(r['stage']==stage and r['split']=='development' for r in training)
        assert digest(training)==seal['training_records_hash']
        assert digest(load('Freeze.json'))==seal['freeze_hash']
        assert [r['candidate'] for r in seal['scores']]==candidates
        for ix,s in enumerate(seal['scores']):
            totals=[sum(r['algorithm_cpu'] for r in training if r['phase']==f'tuning{stage}_{ix}' and r['repeat']==rep) for rep in range(3)]
            assert totals==s['repeat_totals'] and statistics.median(totals)==s['median']
        winner=min(enumerate(seal['scores']),key=lambda p:(p[1]['median'],p[0]))[1]
        assert winner['candidate']==seal['chosen']
    groups=defaultdict(set)
    for r in rows:
        groups[(r['case_id'],r['policy'],r['phase'] if r['phase'].startswith('tuning') else 'normal')].add(r['signature'])
    assert all(len(s)==1 for s in groups.values())
    audit=load('Audit-summary.json');assert audit['passed'] and audit['integer_time_checks']==sum(r['integer_time_checks'] for r in rows)
    for r in rows:
        if r['policy'].startswith('forced_'):
            index=int(r['policy'].split('_')[2])
            assert r['builds'][index]['status']!='complete'
    summary=(ROOT/'Summary.json').read_bytes();synthesis=(ROOT/'Synthesis.md').read_bytes()
    summarize();assert (ROOT/'Summary.json').read_bytes()==summary and (ROOT/'Synthesis.md').read_bytes()==synthesis
    print(json.dumps(dict(passed=True,unique_inputs=110,workers=1020,integer_time_checks=audit['integer_time_checks'],
        source_and_selection_seals_verified=True,proof_archive_required_for_independent_reaudit=True)))

if __name__=='__main__':main()
