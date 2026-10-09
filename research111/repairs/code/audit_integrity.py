"""Additional independent artifact, deployment and LRU-trace checks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    counts = {}
    for seal in ['Freeze.json', 'Memory-freeze.json']:
        frozen = json.loads((ROOT/seal).read_text())
        for name, expected in frozen['files'].items():
            assert digest(ROOT/name) == expected, name
        counts[seal] = len(frozen['files'])
    sdk = json.loads((ROOT/'SDK-manifest.json').read_text())
    for binary in sdk['binaries'].values():
        assert digest(Path(binary['path'])) == binary['sha256']
    assert digest(ROOT/'dependencies/research86/dependencies/vipr/viprchk') == sdk['original_checker_sha256']
    rows = json.loads((ROOT/'Results.json').read_text())
    native = [r for r in rows if r['kind'] == 'R112-native']
    assert len(native) == 9
    for r in native:
        d = r['logical']
        assert d['status'] == 'verified_native_scip'
        assert digest(ROOT/d['raw_proof']) == d['raw_sha256']
        assert digest(ROOT/d['proof']) == d['sha256']
        assert (ROOT/d['proof']).stat().st_size <= 1048576
        assert r['measurements']['completion_cpu'] >= 0
    for r in rows:
        if r['kind'] != 'R119-120':
            continue
        d = r['logical']; lru = []; evictions = 0; changes = set()
        for event in d['events']:
            if event['kind'] == 'point':
                t = event['time']; hit = t in lru
                assert event['hit'] == hit
                if hit:
                    lru.remove(t)
                lru.append(t)
                if len(lru) > 2:
                    lru.pop(0); evictions += 1
                assert event['entries'] == len(lru) and event['evictions'] == evictions
            if event['kind'] == 'context-change':
                changes.add(event['change'])
                expected = sdk['binaries']['fork_wrapper']['sha256'] if event['change'] == 'dependency' else sdk['original_checker_sha256']
                assert event['epoch'] == expected
                if event['new_fact']:
                    f = event['new_fact']; row = event['changed_model']
                    model = {k: row[k] for k in ['n','weights','capacity','profits','slopes']}
                    assert f['model'] == hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    assert f['epoch'] == expected
                    assert digest(ROOT/f['path']) == f['proof_sha256']
        assert changes == {'capacity','weight','objective','domain','nonlinear','dependency'}
    report = dict(passed=True, frozen_files_checked=counts, native_certificates=9,
                  raw_and_final_proof_hashes_checked=True, independent_lru_traces=2,
                  actual_checker_binary_epoch_checked=True)
    (ROOT/'Integrity-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    run()
