"""Exact relevant optimizer bytes pinned for local campaign and replica."""
import hashlib
from pathlib import Path
import platform
import networkx
import networkx.algorithms.flow.networksimplex as ns
import ortools
from ortools.graph.python import min_cost_flow


def capture():
    root=Path(ortools.__file__).parent
    native=[Path(min_cost_flow.__file__)]+sorted(root.rglob('libortools.so*'))
    return {'python':platform.python_version(),'networkx':networkx.__version__,'ortools':ortools.__version__,
            'network_simplex_sha256':hashlib.sha256(Path(ns.__file__).read_bytes()).hexdigest(),
            'native':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in native}}
