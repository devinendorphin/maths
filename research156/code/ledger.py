"""Independent arithmetic over retained exclusive intervals and query boundaries."""
from collections import Counter
from meter import LABELS


def check(receipt, parent_ns):
    start, end = receipt['origin_ns'], receipt['end_ns']
    assert type(start) is int and type(end) is int and 0 < end - start <= parent_ns
    duration = end - start
    queries = receipt['queries']
    assert len(queries) == 49
    previous = 0
    for q in queries:
        assert type(q['start_ns']) is int and type(q['end_ns']) is int
        assert previous <= q['start_ns'] < q['end_ns'] <= duration
        previous = q['end_ns']
    totals = Counter()
    query_totals = Counter()
    per_query = []
    if receipt['enabled']:
        cursor = 0
        buckets = [Counter() for _ in queries]
        qi = 0
        for a, b, label in receipt['intervals']:
            assert type(a) is int and type(b) is int and a == cursor and b > a and label in LABELS
            totals[label] += b - a
            cursor = b
            while qi < len(queries) and queries[qi]['end_ns'] <= a:
                qi += 1
            j = qi
            while j < len(queries) and queries[j]['start_ns'] < b:
                q = queries[j]
                overlap = min(b, q['end_ns']) - max(a, q['start_ns'])
                if overlap > 0:
                    buckets[j][label] += overlap
                j += 1
        assert cursor == duration and sum(totals.values()) == duration
        for q, parts in zip(queries, buckets):
            assert sum(parts.values()) == q['end_ns'] - q['start_ns']
            per_query.append(dict(parts))
            query_totals.update(parts)
        assert receipt['calls']['query.control'] == 49
    else:
        assert not receipt['intervals'] and not receipt['calls']
    return {'worker_ns': duration, 'process_envelope_gap_ns': parent_ns - duration,
            'query_ns': sum(q['end_ns'] - q['start_ns'] for q in queries),
            'worker_categories_ns': dict(totals), 'query_categories_ns': dict(query_totals),
            'per_query_ns': per_query}
