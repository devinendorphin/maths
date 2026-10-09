"""Sample simultaneous descendant RSS via PPid, without holding checker state."""
import os
from pathlib import Path
import sys
import threading
import time


def status(pid):
    try:
        fields={}
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith(('PPid:','VmRSS:')):
                k,v=line.split(':',1);fields[k]=int(v.split()[0])
        return fields
    except (FileNotFoundError,ProcessLookupError):return {}


def observe():
    rows={int(p.name):status(int(p.name)) for p in Path('/proc').iterdir() if p.name.isdigit()};ids={os.getpid()}
    while True:
        expanded=ids|{pid for pid,s in rows.items() if s.get('PPid') in ids}
        if expanded==ids:break
        ids=expanded
    values={pid:status(pid).get('VmRSS',0) for pid in ids}
    return dict(rss_kib=sum(values.values()),processes=len(ids),positive_processes=sum(v>0 for v in values.values()))


class Sampler:
    def __enter__(self):
        self.samples=[];self.stop=threading.Event()
        def sample():
            while not self.stop.is_set():
                self.samples.append(observe());self.stop.wait(0.002)
        self.thread=threading.Thread(target=sample,daemon=True);self.thread.start();return self
    def __exit__(self,*args):self.stop.set();self.thread.join()
    def report(self):
        return dict(observed_peak_tree_rss_kib=max(s['rss_kib'] for s in self.samples),max_processes=max(s['processes'] for s in self.samples),
            max_positive_processes=max(s['positive_processes'] for s in self.samples),samples=len(self.samples),interval_seconds=0.002,
            note='PPid discovery; unmodified checker exit; sampled simultaneous RSS can double-count shared pages and miss short peaks. Observer overhead included only in these memory workers.')


def reachable(value):
    seen=set()
    def walk(x):
        if id(x) in seen:return 0
        seen.add(id(x));size=sys.getsizeof(x)
        if isinstance(x,dict):size+=sum(walk(k)+walk(v) for k,v in x.items())
        elif isinstance(x,(tuple,list,set)):size+=sum(walk(v) for v in x)
        return size
    return walk(value)
