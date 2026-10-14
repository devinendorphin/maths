"""Exact proofs, state transitions, independent references and interval closure."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
from ledger import check as ledger_check

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from audit import independent, references
from checker import digest, encode, verify
from state_audit import check as state_check
from transaction import Transaction
from engine import ROUTES


def run(development=False):
    tick = time.perf_counter_ns()
    folder = ROOT / ('development-outputs' if development else 'outputs')
    sessions = json.loads((ROOT / ('Development-sessions.json' if development else 'Sessions.json')).read_text())
    ctx = 'development-accounting-only' if development else json.loads((ROOT / 'Freeze.json').read_text())['context']
    entries = json.loads((ROOT / 'Inputs.json').read_text())['development' if development else 'heldout']
    reps = 1 if development else 2
    assert len(sessions) == 6 * 6 * 2 * reps
    assert {(s['index'], s['route'], s['mode'], s['repetition']) for s in sessions} == {
        (i, r, mode, rep) for i in range(6) for r in ROUTES for mode in ('accounted', 'unobserved') for rep in range(reps)}
    answers = {}
    proofs = set()
    identities = {}
    logical = {}
    costs = {}
    observations = cuts = 0
    for s in sessions:
        assert not s['exit_code'] and not s['timed_out']
        out = folder / s['name']
        w = json.loads((out / 'Worker.json').read_text())
        receipt = json.loads((out / 'Accounting.json').read_text())
        assert receipt['enabled'] == (s['mode'] == 'accounted')
        costs[s['name']] = ledger_check(receipt, s['wall_ns'])
        entry = entries[w['index']]
        state = Transaction(entry['model'], ctx)
        previous = None
        assert len(w['records']) == 49 and len(receipt['legacy']) == 49
        assert all(w[k] == s[k] for k in ('index', 'route', 'mode', 'repetition'))
        raw = (out / 'Evidence.jsonl').read_bytes()
        assert len(raw) == w['evidence_bytes'] and list(map(json.loads, raw.splitlines())) == w['records']
        for step, rec in enumerate(w['records']):
            if step:
                state.apply(dict(copy.deepcopy(entry['updates'][step - 1]['message']), context=ctx))
            model = state.model
            proof = rec['proof']
            assert rec['step'] == step and rec['version'] == step and rec['model'] == digest(model)
            assert verify(model, proof, ctx)
            value = independent(model, proof, ctx)
            state_check(model, rec, previous, w['route'], step)
            assert rec['native'] is None or not rec['native']['status_forced_control']
            key = digest(model)
            if key not in answers:
                answers[key] = references(model)
            assert value == answers[key]
            proofs.add(hashlib.sha256(encode(proof)).hexdigest())
            observations += 1
            cuts += proof['kind'] == 'cut'
            previous = rec
        assert w['final_model'] == digest(model) and w['final_proof'] == hashlib.sha256(encode(proof)).hexdigest()
        if receipt['enabled']:
            calls = receipt['calls']
            assert calls['record.prepare'] == calls['record.encode'] == calls['record.write_flush'] == calls['record.ownership'] == 49
            traces = [r['native'] for r in w['records'] if r['native'] is not None]
            if traces:
                assert calls.get('native.create', 0) == max(t['constructions'] for t in traces)
                assert calls.get('native.solve_with_witness', 0) == sum(t['solve_called'] for t in traces)
                assert calls.get('native.patch', 0) == (0 if w['route'] == 'generic-cold' else 48)
            else:
                assert not calls.get('native.create', 0) and not calls.get('native.patch', 0)
        scientific = {k: v for k, v in w.items() if k not in ('mode', 'repetition')}
        identity = hashlib.sha256(encode(scientific)).hexdigest()
        key = (w['index'], w['route'])
        if key in identities:
            assert identities[key] == identity
        else:
            identities[key] = identity
        logical[s['name']] = {'scientific_sha256': identity, 'journal_sha256': hashlib.sha256(raw).hexdigest()}
    report = {'passed': True, 'development_excluded': development, 'workers': len(sessions), 'observations': observations,
              'cuts': cuts, 'distinct_models': len(answers), 'distinct_proofs': len(proofs),
              'accounted_sessions': sum(s['mode'] == 'accounted' for s in sessions),
              'all_query_and_worker_interval_sums_exact': True,
              'observer_modes_and_repetitions_scientifically_identical': True,
              'audit_wall_ns': time.perf_counter_ns() - tick}
    prefix = 'Development-' if development else ''
    for name, value in (('Audit.json', report), ('Logical.json', logical), ('Accounting-summary.json', costs)):
        (ROOT / (prefix + name)).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    run('--development' in sys.argv)
