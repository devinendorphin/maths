"""Observed simultaneous process-tree RSS and live reachable Python bytes."""
import os
from pathlib import Path
import sys
import threading
import time


def resident(pid):
    try:
        text = Path(f'/proc/{pid}/status').read_text()
        for line in text.splitlines():
            if line.startswith('VmRSS:'):
                return int(line.split()[1])
    except (FileNotFoundError, ProcessLookupError):
        pass
    return 0


def tree(pid):
    ids = {pid}; pending = [pid]
    while pending:
        parent = pending.pop()
        try:
            for task in Path(f'/proc/{parent}/task').iterdir():
                for value in (task/'children').read_text().split():
                    child = int(value)
                    if child not in ids:
                        ids.add(child); pending.append(child)
        except (FileNotFoundError, ProcessLookupError):
            pass
    return ids


class Sampler:
    def __init__(self):
        self.stop = threading.Event(); self.samples = []; self.thread = None

    def __enter__(self):
        def sample():
            while not self.stop.is_set():
                ids = tree(os.getpid())
                self.samples.append(dict(rss_kib=sum(resident(pid) for pid in ids), processes=len(ids)))
                self.stop.wait(0.002)
        self.thread = threading.Thread(target=sample, daemon=True); self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set(); self.thread.join()

    def report(self):
        return dict(observed_peak_tree_rss_kib=max(s['rss_kib'] for s in self.samples),
                    max_observed_processes=max(s['processes'] for s in self.samples),
                    samples=len(self.samples), interval_seconds=0.002,
                    note='Simultaneous RSS sum can double-count shared pages; sampled peak may miss brief peaks. Monitor overhead included in this memory scenario only.')


def reachable_bytes(value):
    seen = set()
    def visit(item):
        if id(item) in seen:
            return 0
        seen.add(id(item)); total = sys.getsizeof(item)
        if isinstance(item, dict):
            total += sum(visit(k)+visit(v) for k,v in item.items())
        elif isinstance(item, (tuple,list,set)) or item.__class__.__name__=='OrderedDict':
            total += sum(visit(x) for x in item)
        elif hasattr(item, '__dict__'):
            total += visit(item.__dict__)
        return total
    return visit(value)
