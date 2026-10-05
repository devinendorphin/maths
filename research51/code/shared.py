"""Batch utilities and access to frozen, unchanged earlier kernels."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
KERNEL = REPO / 'campaigns/experiments-31-35/research/stages/35/code'
if not KERNEL.exists():
    KERNEL = REPO / 'baseline/code'
sys.path.append(str(REPO / 'research46/code'))
sys.path.append(str(KERNEL))
import common
import engine as E
import horizon as H
import source_guarded as SG
import certificates as C


def value(xs, mask):
    return sum(x for i, x in enumerate(xs) if mask >> i & 1)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        return json.load(stream)


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    data = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    if path.suffix == '.gz':
        data = gzip.compress(data, mtime=0)
    path.write_bytes(data)


def native(row, t):
    q = [p + t*v for p, v in zip(row['profits'], row['slopes'])]
    return SG.solve(row['weights'], q, row['capacity'], deadline=time.perf_counter()+30)


def encode_fraction(x):
    return [x.numerator, x.denominator]
