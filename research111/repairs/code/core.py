"""Compatible original-problem VIPR paths with explicit accounting and cache scope."""
from collections import OrderedDict
from dataclasses import dataclass
from fractions import Fraction
import copy
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'dependencies/research86/code'))
import shared
import certificates

NATIVE_CHECKER = ROOT/'dependencies/research86/dependencies/vipr/viprchk'
WRAPPER = Path('/workspace/maths-toolchains/repair-sdk/vipr_fork')


def encode(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scope(row):
    if row.get('domain', 'binary') != 'binary' or row.get('objective_class', 'affine') != 'affine' or any(row.get('quadratic', [])):
        raise ValueError('unsupported model class')
    if type(row['capacity']) != int or row['capacity'] < 0 or row['n'] != len(row['weights']):
        raise ValueError('unsupported shape/capacity')
    if any(type(w) != int or w <= 0 for w in row['weights']):
        raise ValueError('unsupported weights')
    if len(row['profits']) != row['n'] or len(row['slopes']) != row['n']:
        raise ValueError('unsupported coefficient shape')
    if any(type(q) != int for q in row['profits'] + row['slopes']):
        raise ValueError('unsupported coefficient type')
    return sha(encode({k: row[k] for k in ['n','weights','capacity','profits','slopes']}))


def clock():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time(), r.ru_utime+r.ru_stime, time.perf_counter()


def elapsed(start):
    p, c, w = clock()
    return dict(parent_cpu=p-start[0], child_cpu=c-start[1], cpu=p-start[0]+c-start[1], wall=w-start[2])


def scaled(row, t):
    t = Fraction(t)
    return [t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]


def value(coefficients, mask):
    return sum(v for j,v in enumerate(coefficients) if mask >> j & 1)


@dataclass(frozen=True)
class Fact:
    model: str
    epoch: str
    time: tuple
    packing: int
    objective: int
    proof_sha256: str
    checker_sha256: str
    path: str

    def record(self):
        return dict(self.__dict__)


def verify_file(path, checker=NATIVE_CHECKER):
    checked = subprocess.run([str(checker), str(path)], capture_output=True, text=True, timeout=10)
    return checked.returncode == 0 and 'Successfully verified optimal value range' in checked.stdout


def produce(row, t, epoch='initial', checker=NATIVE_CHECKER, candidate=None):
    """Produce native evidence; candidate solve is separate when supplied by SCIP."""
    begin = clock(); phases = {}
    scope(row); t = Fraction(t); q = scaled(row,t)
    start = clock()
    source = shared.SG.solve(row['weights'], q, row['capacity'], deadline=time.perf_counter()+20)
    assert source['empty']
    phases['native_exact_solve_and_witness'] = elapsed(start)['cpu']
    mask = source['packing'] if candidate is None else candidate
    assert 0 <= mask < (1 << row['n']) and value(row['weights'],mask) <= row['capacity']
    assert value(q,mask) == source['objective']
    start = clock()
    text, info = shared.vipr_adapter.certificate(row,t,source['packing'],source['proof'])
    payload = text.encode()
    phases['vipr_proof_encoding'] = elapsed(start)['cpu']
    assert len(payload) <= 1048576
    start = clock()
    identity = sha(payload)
    folder = ROOT/'evidence/vipr'; folder.mkdir(parents=True, exist_ok=True)
    path = folder/(identity+'.vipr'); path.write_bytes(payload)
    phases['proof_hash_and_write_io'] = elapsed(start)['cpu']
    start = clock(); assert verify_file(path,checker)
    phases['external_checker_including_child_cpu'] = elapsed(start)['cpu']
    start = clock()
    data = path.read_bytes()
    assert sha(data)==identity and data.decode().startswith(certificates.prefix(row,t,source['objective']))
    assert value(q,mask)==source['objective'] and value(row['weights'],mask)<=row['capacity']
    fact = Fact(scope(row),epoch,(t.numerator,t.denominator),mask,source['objective'],identity,
                sha(checker.read_bytes()),str(path.relative_to(ROOT)))
    phases['model_primal_hash_admission'] = elapsed(start)['cpu']
    total = elapsed(begin)
    return fact, dict(phases=phases, measured_phase_sum=sum(phases.values()), residual_cpu=total['cpu']-sum(phases.values()),
                      total=total, bytes=len(payload), derivations=info['derivations'])


def replay(row, fact, checker=NATIVE_CHECKER):
    t = Fraction(*fact.time)
    if scope(row)!=fact.model or sha(checker.read_bytes())!=fact.checker_sha256:
        return False
    path = ROOT/fact.path
    if sha(path.read_bytes())!=fact.proof_sha256 or not verify_file(path,checker):
        return False
    return value(scaled(row,t),fact.packing)==fact.objective and value(row['weights'],fact.packing)<=row['capacity']


class Cache:
    """Explicit model/dependency context; immutable admitted facts are never file watchers."""
    def __init__(self, row, checker=NATIVE_CHECKER):
        self.row = copy.deepcopy(row); self.model = scope(row); self.checker = checker
        self.epoch = sha(checker.read_bytes()); self.points = OrderedDict(); self.snapshots = []
        self.evictions = 0; self.blocked = False

    def switch(self, row=None, checker=None):
        target = self.row if row is None else row
        try:
            model_id = scope(target)
        except ValueError:
            self.evictions += len(self.points)+len(self.snapshots)
            self.points.clear(); self.snapshots.clear(); self.blocked=True
            raise
        new_checker = self.checker if checker is None else checker
        epoch = sha(new_checker.read_bytes())
        if model_id!=self.model or epoch!=self.epoch:
            self.evictions += len(self.points)+len(self.snapshots)
            self.points.clear(); self.snapshots.clear()
        self.row = copy.deepcopy(target); self.model = model_id; self.checker = new_checker; self.epoch = epoch; self.blocked=False

    def point(self, t):
        if self.blocked:
            raise ValueError('unsupported current model context')
        t = Fraction(t); key = (self.model,self.epoch,t)
        if key in self.points:
            fact = self.points.pop(key); self.points[key] = fact
            assert fact.model==self.model and fact.epoch==self.epoch
            return fact, True, None
        fact, cost = produce(self.row,t,self.epoch,self.checker)
        self.points[key] = fact
        if len(self.points)>2:
            self.points.popitem(last=False); self.evictions += 1
        return fact, False, cost

    def snapshot(self, lo, hi):
        lo, hi = Fraction(lo), Fraction(hi)
        assert lo<=hi
        a,_,_ = self.point(lo); b,_,_ = self.point(hi)
        if a.packing!=b.packing:
            return None
        entry=(self.model,self.epoch,lo,hi,a.packing,a,b)
        self.snapshots.append(entry)
        return entry

    def lookup(self, t):
        if self.blocked:
            return None
        t=Fraction(t)
        for model_id,epoch,lo,hi,packing,a,b in self.snapshots:
            if (model_id,epoch)==(self.model,self.epoch) and lo<=t<=hi:
                return packing
        return None

    def refresh(self, fact):
        """Explicit external refresh evicts captured facts before re-admission."""
        self.evictions += len(self.points)+len(self.snapshots)
        self.points.clear(); self.snapshots.clear()
        return fact.model==self.model and fact.epoch==self.epoch and replay(self.row,fact,self.checker)
