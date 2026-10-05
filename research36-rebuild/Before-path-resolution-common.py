"""Atomic immutable persistence and access to the unchanged stage-35 kernels."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(os.environ.get('MATHS_RESEARCH_ROOT', Path(__file__).resolve().parents[1]))
REPO = ROOT.parent
BASELINE = REPO / 'campaigns/experiments-31-35/research/stages/35/code'
if not BASELINE.exists():
    BASELINE = REPO / 'baseline/code'
sys.path.insert(0, str(BASELINE))
import engine as E
import horizon as H
import source_guarded as SG
import frontier as OLD


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    p = Path(path)
    with (gzip.open(p, 'rt') if p.suffix == '.gz' else p.open()) as f:
        return json.load(f)


def save(path, data, immutable=False):
    start = time.process_time(); wall = time.perf_counter()
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    if immutable and p.exists():
        raise FileExistsError(p)
    payload = json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode()
    if p.suffix == '.gz':
        payload = gzip.compress(payload, compresslevel=6, mtime=0)
    q = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    with q.open('xb') as f:
        f.write(payload); f.flush(); os.fsync(f.fileno())
    q.replace(p)
    assert p.read_bytes() == payload
    return dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                sha256=sha(p), bytes=len(payload), cpu=time.process_time()-start,
                wall=time.perf_counter()-wall)


def value(xs, mask):
    return sum(x for i, x in enumerate(xs) if mask >> i & 1)


def counters():
    keys = set(E.COUNT_KEYS) | set(OLD.DP_KEYS) | {
        'same_slope_checks', 'compression_work', 'index_queries', 'index_visits',
        'index_updates', 'witness_records', 'auxiliary_peak', 'proof_peak',
        'interval_rebuilds', 'gcd_operations', 'gate_arithmetic',
        'native_generator_steps', 'native_cleanup_steps', 'native_disposal_steps'}
    return {k: 0 for k in keys}


def add(a, b):
    for k, v in b.items():
        if isinstance(v, (int, float)) and not k.endswith('cpu'):
            if k.endswith('_peak'):
                a[k] = max(a.get(k, 0), v)
            else:
                a[k] = a.get(k, 0) + v


LIMITS = dict(entries=500000, transitions=2000000, dominance=5000000,
              index=5000000, auxiliary=500000, native_per_solve=500000,
              scalar_cells=4096, native_cells=4096, native_seconds=30,
              audit_seconds=45, batch_seconds=900)


def limits(stage):
    f = 4 if stage == 40 else 1
    return dict(LIMITS, cumulative_entries=500000*f,
                cumulative_transitions=2000000*f, cumulative_dominance=5000000*f,
                cumulative_index=5000000*f, scalar_evaluations=2000000*f,
                cumulative_native=2000000*f, wall_seconds=240 if stage == 40 else 120)
