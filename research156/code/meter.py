"""Exclusive interval ledger; observer intervals and coarse control remain explicit."""
from contextlib import contextmanager
import functools
import time
from types import SimpleNamespace

LABELS = (
    'session.imports', 'session.bookkeeping', 'startup.provenance', 'startup.input',
    'startup.engine', 'query.control', 'transaction.apply', 'transaction.copy',
    'model.validation', 'model.digest', 'encoding.canonical', 'native.marshal',
    'native.snapshot_materialize', 'native.create', 'native.patch',
    'native.solve_with_witness', 'native.snapshot', 'native.destroy', 'native.simple',
    'feasibility.production', 'feasibility.witness_admission', 'proof.potentials',
    'proof.production', 'proof.admission', 'repair.optimize', 'query.copy',
    'record.prepare', 'record.encode', 'record.write_flush', 'record.ownership', 'record.publish',
    'worker.cleanup', 'output.digest', 'output.worker_json', 'output.worker_write',
    'observer',
)


class Meter:
    def __init__(self, origin, enabled):
        self.origin = self.last = origin
        self.enabled = enabled
        self.label = 'session.imports'
        self.stack = []
        self.intervals = []
        self.calls = {}

    def charge(self, end, label):
        assert end >= self.last and label in LABELS
        if end > self.last:
            self.intervals.append([self.last - self.origin, end - self.origin, label])
        self.last = end

    def enter(self, label):
        start = time.perf_counter_ns()
        if self.enabled:
            self.charge(start, self.label)
            assert label in LABELS
            self.stack.append(self.label)
            self.label = label
            self.calls[label] = self.calls.get(label, 0) + 1
            self.charge(time.perf_counter_ns(), 'observer')
        return start

    def leave(self):
        end = time.perf_counter_ns()
        if self.enabled:
            self.charge(end, self.label)
            assert self.stack
            self.label = self.stack.pop()
            self.charge(time.perf_counter_ns(), 'observer')
        return end

    @contextmanager
    def phase(self, label):
        self.enter(label)
        try:
            yield
        finally:
            self.leave()

    def wrap(self, label, function):
        @functools.wraps(function)
        def observed(*args, **kwargs):
            if self.label == label:
                return function(*args, **kwargs)
            with self.phase(label):
                return function(*args, **kwargs)
        return observed

    def finish(self):
        end = time.perf_counter_ns()
        if self.enabled:
            assert not self.stack
            self.charge(end, self.label)
        return {'origin_ns': self.origin, 'end_ns': end, 'enabled': self.enabled,
                'intervals': self.intervals, 'calls': self.calls}


def install(meter):
    """Original functions remain unchanged; replace only their call boundaries."""
    if not meter.enabled:
        return
    import checker, engine, native, producer, transaction
    modules = (checker, engine, native, producer, transaction)

    def bind(label, original):
        wrapped = meter.wrap(label, original)
        for module in modules:
            for key, value in list(vars(module).items()):
                if value is original:
                    setattr(module, key, wrapped)

    for label, function in (
        ('model.validation', checker.validate), ('model.digest', checker.digest),
        ('encoding.canonical', checker.encode), ('proof.admission', checker.verify),
        ('feasibility.witness_admission', checker.feasible),
        ('feasibility.production', producer.feasibility),
        ('proof.potentials', producer.potentials), ('proof.production', producer.certificate),
        ('repair.optimize', producer.optimize), ('native.marshal', native.arrays),
    ):
        bind(label, function)
    transaction.Transaction.apply = meter.wrap('transaction.apply', transaction.Transaction.apply)
    for method, label in (
        ('__init__', 'native.marshal'), ('patch', 'native.marshal'),
        ('solve', 'native.marshal'), ('snapshot', 'native.snapshot_materialize'),
        ('close', 'worker.cleanup'),
    ):
        setattr(native.Native, method, meter.wrap(label, getattr(native.Native, method)))
    original_lib = native.LIB
    native.LIB = SimpleNamespace(**{
        name: meter.wrap(label, getattr(original_lib, name)) for name, label in (
            ('m152_create', 'native.create'), ('m152_patch', 'native.patch'),
            ('m152_solve', 'native.solve_with_witness'), ('m152_snapshot', 'native.snapshot'),
            ('m152_destroy', 'native.destroy'), ('m152_simple', 'native.simple'),
        )
    })
    for module, label in ((engine, 'query.copy'), (transaction, 'transaction.copy')):
        module.copy = SimpleNamespace(deepcopy=meter.wrap(label, module.copy.deepcopy))
