"""Immutable content-addressed evidence; unchanged storage semantics from 41–45."""
import gzip
import hashlib
import json
from common import ROOT

def objectify(data):
    if isinstance(data,list): node=[objectify(x) for x in data]
    elif isinstance(data,dict): node={k:objectify(v) for k,v in data.items()}
    else: return data
    b=json.dumps(node,sort_keys=True,separators=(',',':')).encode()
    if len(b)<2048: return node
    h=hashlib.sha256(b).hexdigest(); p=ROOT/'evidence/objects'/f'{h}.json.gz'
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_suffix('.tmp'); tmp.write_bytes(gzip.compress(b,compresslevel=6,mtime=0)); tmp.replace(p)
    return {'$object':h}

def hydrate(data):
    if isinstance(data,list): return [hydrate(x) for x in data]
    if not isinstance(data,dict): return data
    if set(data)=={'$object'}:
        h=data['$object']; b=gzip.decompress((ROOT/'evidence/objects'/f'{h}.json.gz').read_bytes())
        assert hashlib.sha256(b).hexdigest()==h
        return hydrate(json.loads(b))
    return {k:hydrate(v) for k,v in data.items()}

