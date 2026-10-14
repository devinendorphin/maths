"""Measured medians only; no synthetic subtraction of causal observer cost."""
import json
from pathlib import Path
import statistics
import sys


def summarize(root):
    root = Path(root)
    sessions = json.loads((root / 'Sessions.json').read_text())
    costs = json.loads((root / 'Accounting-summary.json').read_text())
    rows = []
    for index in range(6):
        for route in ('simple-cold', 'generic-cold', 'generic-warm', 'guard-generic', 'flow-repair', 'guard-repair'):
            row = {'index': index, 'route': route}
            for mode in ('accounted', 'unobserved'):
                selected = [s for s in sessions if s['index'] == index and s['route'] == route and s['mode'] == mode]
                assert len(selected) == 2
                def median(fn):
                    return statistics.median(fn(s, costs[s['name']]) for s in selected) / 1e6
                value = {'complete_ms': median(lambda s, c: s['wall_ns']),
                         'ledger_ms': median(lambda s, c: c['worker_ns']),
                         'query_ms': median(lambda s, c: c['query_ns']),
                         'envelope_gap_ms': median(lambda s, c: c['process_envelope_gap_ns'])}
                for group in ('worker', 'query'):
                    key = group + '_categories_ns'
                    labels = sorted({label for s in selected for label in costs[s['name']][key]})
                    value[group + '_categories_ms'] = {label: median(lambda s, c: c[key].get(label, 0)) for label in labels}
                row[mode] = value
            row['observer_complete_ratio'] = row['accounted']['complete_ms'] / row['unobserved']['complete_ms']
            row['observer_query_ratio'] = row['accounted']['query_ms'] / row['unobserved']['query_ms']
            rows.append(row)
    return rows


if __name__ == '__main__':
    value = {label: summarize(path) for label, path in zip(('primary', 'replica'), sys.argv[1:])}
    print(json.dumps(value, sort_keys=True, indent=2))
