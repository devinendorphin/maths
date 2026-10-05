"""Persistence and unchanged exact source/proof dependencies for 56–65."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
DEPS=ROOT/'dependencies'
KERNEL=DEPS/'stage35'
if not KERNEL.exists():KERNEL=REPO/'baseline/code'
ADAPTER=DEPS/'adapter'
if not ADAPTER.exists():ADAPTER=REPO/'research51/code'
sys.path.append(str(KERNEL));sys.path.append(str(ADAPTER))
import source_guarded as SG


def value(xs,mask):return sum(x for i,x in enumerate(xs) if mask>>i&1)


def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def read(path):
    p=Path(path)
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as stream:return json.load(stream)


def save(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise FileExistsError(p)
    data=json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
    if p.suffix=='.gz':data=gzip.compress(data,mtime=0)
    p.write_bytes(data)


def frac(x):return [x.numerator,x.denominator]


def logical(obj):
    if isinstance(obj,dict):return {k:logical(v) for k,v in obj.items() if not k.endswith(('_cpu','_wall')) and k not in ('cpu','wall','deadline')}
    if isinstance(obj,list):return [logical(v) for v in obj]
    return obj


import vipr_adapter
