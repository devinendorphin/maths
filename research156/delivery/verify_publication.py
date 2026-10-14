"""Dependency-free custody, exact mathematical/state and timing-ledger replay."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / 'vendor'))
sys.path.insert(0, str(ROOT / 'code'))
from checker import digest, encode, verify
from state_audit import check as state_check
from transaction import Transaction
from ledger import check as ledger_check
from controls_accounting import run as adversaries
from archive_parts import read_archive

ROUTES = ('simple-cold', 'generic-cold', 'generic-warm', 'guard-generic', 'flow-repair', 'guard-repair')


def run():
    seal = json.loads((ROOT / 'Publication-seal.json').read_text())
    for name, item in seal['files'].items():
        data = (REPO / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], name
    old = json.loads((ROOT / 'Old-custody.json').read_text())
    for name, item in old.items():
        data = (REPO / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], name
    receipt = seal['archive']
    data = read_archive(ROOT, receipt)
    assert len(data) == receipt['bytes'] and hashlib.sha256(data).hexdigest() == receipt['sha256']
    manifest = json.loads((ROOT / 'Archive-manifest.json').read_text())
    payloads = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:xz') as tar:
        members = tar.getmembers()
        assert len(members) == len(manifest) == receipt['members'] and len({m.name for m in members}) == len(members)
        for member in members:
            assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
            data = tar.extractfile(member).read()
            item = manifest[member.name]
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'] and member.mode == item['mode']
            payloads[member.name] = data
    scientific = {}
    observations = cuts = accounted = 0
    for label, folder, sessions_file, audit_file, selection, reps in (
        ('primary', 'outputs', 'Sessions.json', 'Audit.json', 'heldout', 2),
        ('replica', 'outputs', 'Sessions.json', 'Audit.json', 'heldout', 2),
        ('reports', 'development-outputs', 'Development-sessions.json', 'Development-Audit.json', 'development', 1),
    ):
        freeze = json.loads(payloads[label + '/Freeze.json'])
        body = copy.deepcopy(freeze)
        ctx = body.pop('context')
        assert hashlib.sha256(encode(body)).hexdigest() == ctx and freeze['headline_not_executed_at_freeze']
        for name, value in freeze['files'].items():
            assert hashlib.sha256(payloads[label + '/' + name]).hexdigest() == value
            assert payloads[label + '/' + name] == (ROOT / name).read_bytes()
        if selection == 'development':
            ctx = 'development-accounting-only'
        inputs = json.loads(payloads[label + '/Inputs.json'])[selection]
        sessions = json.loads(payloads[label + '/' + sessions_file])
        summary_name = 'Development-Accounting-summary.json' if selection == 'development' else 'Accounting-summary.json'
        cost_table = json.loads(payloads[label + '/' + summary_name])
        expected = {(i, r, mode, rep) for i in range(6) for r in ROUTES for mode in ('accounted', 'unobserved') for rep in range(reps)}
        assert len(sessions) == len(expected)
        assert {(s['index'], s['route'], s['mode'], s['repetition']) for s in sessions} == expected
        for session in sessions:
            assert not session['exit_code'] and not session['timed_out']
            prefix = label + '/' + folder + '/' + session['name']
            w = json.loads(payloads[prefix + '/Worker.json'])
            accounting = json.loads(payloads[prefix + '/Accounting.json'])
            assert accounting['enabled'] == (session['mode'] == 'accounted')
            costs = ledger_check(accounting, session['wall_ns'])
            if accounting['enabled']:
                accounted += len(w['records'])
            entry = inputs[w['index']]
            state = Transaction(entry['model'], ctx)
            previous = None
            assert len(w['records']) == 49 and len(accounting['legacy']) == 49
            assert all(w[k] == session[k] for k in ('index', 'route', 'mode', 'repetition'))
            raw = payloads[prefix + '/Evidence.jsonl']
            assert len(raw) == w['evidence_bytes'] and list(map(json.loads, raw.splitlines())) == w['records']
            for step, rec in enumerate(w['records']):
                if step:
                    state.apply(dict(copy.deepcopy(entry['updates'][step - 1]['message']), context=ctx))
                model = state.model
                p = rec['proof']
                assert rec['step'] == step and rec['version'] == step and rec['model'] == digest(model)
                assert verify(model, p, ctx)
                state_check(model, rec, previous, w['route'], step)
                assert rec['native'] is None or not rec['native']['status_forced_control']
                bad = copy.deepcopy(p)
                bad['dependency'] = 'wrong'
                assert not verify(model, bad, ctx)
                bad = copy.deepcopy(p)
                if p['kind'] == 'optimal':
                    bad['cost_units'] += 1
                else:
                    bad['set'] = []
                    cuts += 1
                assert not verify(model, bad, ctx)
                observations += 1
                previous = rec
            assert w['final_model'] == digest(model) and w['final_proof'] == hashlib.sha256(encode(p)).hexdigest()
            identity = hashlib.sha256(encode({k: v for k, v in w.items() if k not in ('mode', 'repetition')})).hexdigest()
            key = (selection, w['index'], w['route'])
            assert key not in scientific or scientific[key] == identity
            scientific[key] = identity
            if accounting['enabled']:
                calls = accounting['calls']
                assert calls['record.prepare'] == calls['record.encode'] == calls['record.write_flush'] == calls['record.ownership'] == 49
                traces = [r['native'] for r in w['records'] if r['native'] is not None]
                if traces:
                    assert calls.get('native.create', 0) == max(t['constructions'] for t in traces)
                    assert calls.get('native.solve_with_witness', 0) == sum(t['solve_called'] for t in traces)
                    assert calls.get('native.patch', 0) == (0 if w['route'] == 'generic-cold' else 48)
            assert costs == cost_table[session['name']]
        audit = json.loads(payloads[label + '/' + audit_file])
        assert audit['passed'] and audit['observations'] == len(sessions) * 49
    for name in ('Inputs.json', 'Freeze.json', 'Logical.json'):
        assert payloads['primary/' + name] == payloads['replica/' + name]
    assert (ROOT / 'Inputs.json').read_bytes() == (REPO / 'research152/Inputs.json').read_bytes()
    for path in (ROOT / 'vendor').glob('*'):
        if path.is_file():
            assert path.read_bytes() == (REPO / 'research152/code' / path.name).read_bytes()
    assert (ROOT / 'bridge.so').read_bytes() == (REPO / 'research152/bridge.so').read_bytes()
    assert len(adversaries()['controls']) == 12
    native = json.loads(payloads['reports/Native-controls.json'])
    assert native['passed'] and native['observer_installed'] and len(set(native['controls'])) == 42
    control_context = native['initial_proof']['dependency']
    assert verify(native['model'], native['initial_proof'], control_context)
    assert verify(native['model'], native['fallback_proof'], control_context)
    assert verify(native['shortage_model'], native['shortage_proof'], control_context)
    assert observations == 17640 and accounted == 8820
    rejection = json.loads(payloads['reports/Rejected-execution.json'])
    assert not rejection['accepted'] and rejection['excluded_from_headline']
    old_context = rejection['old_context']
    for root in ('rejected/primary-1', 'rejected/development-source-1'):
        old_freeze = json.loads(payloads[root + '/Freeze.json'])
        assert old_freeze['context'] == old_context and old_context != json.loads((ROOT / 'Freeze.json').read_text())['context']
        for name, value in old_freeze['files'].items():
            assert hashlib.sha256(payloads[root + '/' + name]).hexdigest() == value
    for bad in rejection['bad_journals']:
        prefix = 'rejected/primary-1/outputs/' + bad['name']
        raw = payloads[prefix + '/Evidence.jsonl']
        worker = json.loads(payloads[prefix + '/Worker.json'])
        assert len(raw) == bad['bytes'] != worker['evidence_bytes'] == bad['declared_bytes']
        assert len(raw.splitlines()) == bad['rows'] < len(worker['records']) == 49
    print('Verified cost accounting:', len(members), 'members;', observations,
          'certified observations including excluded development;', accounted,
          'exact query ledgers;', len(old), 'predecessor files unchanged;', cuts, 'cuts')


if __name__ == '__main__':
    run()
