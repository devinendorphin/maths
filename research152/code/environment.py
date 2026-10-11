"""Pin the libraries actually mapped by this process, not a different Python wheel."""
import hashlib
import json
import os
from pathlib import Path
import platform
import networkx
import networkx.algorithms.flow.networksimplex as ns
from native import LIB

ROOT=Path(__file__).resolve().parents[1]


def capture():
    build=json.loads((ROOT/'Build.json').read_text());sdk=Path(os.environ.get('MATHS152_SDK',build['sdk_root']));mapped=set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        parts=line.split()
        if len(parts)>=6 and parts[-1].startswith(str(sdk/'lib')+'/'):mapped.add(Path(parts[-1]).resolve())
    assert any(p.name.startswith('libortools.so') for p in mapped)
    libraries={str(p.relative_to(sdk)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(mapped)}
    assert all(build['native_libraries'][p]==h for p,h in libraries.items())
    return {'python':platform.python_version(),'networkx':networkx.__version__,'glibc':list(platform.libc_ver()),
            'network_simplex_sha256':hashlib.sha256(Path(ns.__file__).read_bytes()).hexdigest(),
            'mapped_sdk_libraries':libraries,'adapter_sha256':hashlib.sha256((ROOT/'bridge.so').read_bytes()).hexdigest()}
