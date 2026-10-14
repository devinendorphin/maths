"""Adversarial interval checks and clock calibration, excluded from headline costs."""
import copy
import json
from pathlib import Path
import statistics
import time
from ledger import check


def run():
    queries = [{'start_ns': 2 * i + 1, 'end_ns': 2 * i + 2} for i in range(49)]
    receipt = {'origin_ns': 1000, 'end_ns': 1100, 'enabled': True, 'queries': queries,
               'intervals': [[0, 100, 'query.control']], 'calls': {'query.control': 49}}
    assert check(receipt, 200)['query_ns'] == 49
    controls = []

    def reject(name, mutate, parent=200):
        bad = copy.deepcopy(receipt)
        mutate(bad)
        try:
            check(bad, parent)
        except (AssertionError, KeyError, ValueError):
            controls.append(name)
        else:
            raise AssertionError('Accepted invalid accounting: ' + name)

    reject('missing-interval', lambda r: r.update(intervals=[]))
    reject('one-nanosecond-gap', lambda r: r['intervals'][0].__setitem__(0, 1))
    reject('negative-interval', lambda r: r['intervals'][0].__setitem__(1, -1))
    reject('unknown-category', lambda r: r['intervals'][0].__setitem__(2, 'unclaimed-proof-work'))
    reject('wrong-enclosing-end', lambda r: r.__setitem__('end_ns', 1101))
    reject('query-outside-session', lambda r: r['queries'][-1].__setitem__('end_ns', 101))
    reject('overlapping-queries', lambda r: r['queries'][1].__setitem__('start_ns', 1))
    reject('missing-query', lambda r: r['queries'].pop())
    reject('wrong-observer-mode', lambda r: r.__setitem__('enabled', False))
    reject('wrong-query-call-count', lambda r: r['calls'].__setitem__('query.control', 48))
    reject('parent-smaller-than-worker', lambda r: None, 99)
    reject('duplicated-interval', lambda r: r['intervals'].append([0, 100, 'query.control']))
    deltas = []
    for _ in range(10000):
        start = time.perf_counter_ns()
        deltas.append(time.perf_counter_ns() - start)
    return {'passed': True, 'excluded_from_headline': True, 'controls': controls,
            'clock': vars(time.get_clock_info('perf_counter')),
            'paired_reads_ns': {'samples': len(deltas), 'min': min(deltas), 'median': statistics.median(deltas), 'max': max(deltas)},
            'calibration_is_not_subtracted': True}


if __name__ == '__main__':
    p = Path(__file__).resolve().parents[1] / 'Accounting-controls.json'
    p.write_text(json.dumps(run(), sort_keys=True, indent=2) + '\n')
    print('Passed 12 adversarial accounting controls and retained clock calibration')
