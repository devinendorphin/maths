import time
ORIGIN = time.perf_counter_ns()
from meter import Meter, install
import sys
MODE = sys.argv[4]
meter = Meter(ORIGIN, MODE == 'accounted')
with meter.phase('session.imports'):
    import copy
    import hashlib
    import json
    import resource
    import tempfile
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / 'vendor'))
    from checker import digest, encode
    from engine import Engine
    from environment import capture
meter.label = 'session.bookkeeping'


def run(destination, index, route, mode, rep, development=False):
    assert mode in ('accounted', 'unobserved')
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    cpu = time.process_time_ns()
    with meter.phase('startup.provenance'):
        if development:
            ctx = 'development-accounting-only'
        else:
            freeze = json.loads((ROOT / 'Freeze.json').read_text())
            ctx = freeze['context']
            for name, value in freeze['files'].items():
                assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == value
            assert capture() == freeze['environment']
        install(meter)
    with meter.phase('startup.input'):
        entry = json.loads((ROOT / 'Inputs.json').read_text())['development' if development else 'heldout'][index]
        packets = [None] + [dict(copy.deepcopy(z['message']), context=ctx) for z in entry['updates']]
        out = Path(destination)
        out.mkdir()
        records = []
        nbytes = 0
        queries = []
        legacy = []
    with meter.phase('startup.engine'):
        engine = Engine(entry['model'], ctx, route)
    # Stream into an anonymous file; publish only after closing a complete journal.
    with tempfile.TemporaryFile(mode='w+b') as log:
        for step, packet in enumerate(packets):
            begin = meter.enter('query.control')
            rec = engine.query(packet)
            end = meter.leave()
            queries.append({'start_ns': begin - ORIGIN, 'end_ns': end - ORIGIN})
            with meter.phase('record.prepare'):
                legacy.append({'query_wall_s': rec.pop('query_wall_s'), 'timing': rec.pop('timing')})
                rec['step'] = step
            with meter.phase('record.encode'):
                data = encode(rec) + b'\n'
            with meter.phase('record.write_flush'):
                log.write(data)
                log.flush()
                nbytes += len(data)
            with meter.phase('record.ownership'):
                records.append(copy.deepcopy(rec))
        with meter.phase('record.publish'):
            log.seek(0)
            journal = log.read()
            assert len(journal) == nbytes and list(map(json.loads, journal.splitlines())) == records
            pending = out / 'Evidence.jsonl.pending'
            assert pending.write_bytes(journal) == len(journal)
            pending.replace(out / 'Evidence.jsonl')
            assert (out / 'Evidence.jsonl').read_bytes() == journal
    with meter.phase('worker.cleanup'):
        engine.close()
    with meter.phase('output.digest'):
        result = {'index': index, 'route': route, 'mode': mode, 'repetition': rep,
                  'context': ctx, 'records': records, 'evidence_bytes': nbytes,
                  'final_model': digest(engine.state.model),
                  'final_proof': hashlib.sha256(encode(engine.proof)).hexdigest()}
    with meter.phase('output.worker_json'):
        text = json.dumps(result, sort_keys=True, indent=2) + '\n'
    with meter.phase('output.worker_write'):
        pending = out / 'Worker.json.pending'
        pending.write_text(text)
        pending.replace(out / 'Worker.json')
        assert (out / 'Worker.json').read_text() == text
    receipt = meter.finish()
    receipt.update({'queries': queries, 'legacy': legacy, 'worker_cpu_ns_to_receipt': time.process_time_ns() - cpu,
                    'worker_maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    # Receipt serialization cannot time itself recursively. Parent process clock includes it.
    text = json.dumps(receipt, separators=(',', ':')) + '\n'
    pending = out / 'Accounting.json.pending'
    pending.write_text(text)
    pending.replace(out / 'Accounting.json')
    assert (out / 'Accounting.json').read_text() == text


if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]), sys.argv[3], MODE, int(sys.argv[5]), '--development' in sys.argv)
