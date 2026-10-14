"""Balanced observer order, fresh processes, full records, bounded execution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from engine import ROUTES


def run(development=False):
    folder = ROOT / ('development-outputs' if development else 'outputs')
    assert not folder.exists()
    folder.mkdir()
    sessions = []
    for index in range(6):
        for rep in range(1 if development else 2):
            for position, route in enumerate(ROUTES):
                modes = ('unobserved', 'accounted') if (index + rep + position) % 2 else ('accounted', 'unobserved')
                for mode in modes:
                    name = f'{index}-{route}-{mode}-{rep}'
                    args = [sys.executable, str(ROOT / 'code/account_worker.py'), str(folder / name), str(index), route, mode, str(rep)]
                    if development:
                        args.append('--development')
                    with (folder / (name + '.stdout')).open('wb') as stdout, (folder / (name + '.stderr')).open('wb') as stderr:
                        tick = time.perf_counter_ns()
                        process = subprocess.Popen(args, stdout=stdout, stderr=stderr,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
                        timed_out = False
                        while True:
                            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                            if pid:
                                break
                            if time.perf_counter_ns() - tick > 90_000_000_000:
                                process.kill()
                                timed_out = True
                                pid, status, usage = os.wait4(process.pid, 0)
                                break
                            time.sleep(.001)
                        wall = time.perf_counter_ns() - tick
                    process.returncode = os.waitstatus_to_exitcode(status)
                    sessions.append({'name': name, 'index': index, 'route': route, 'mode': mode, 'repetition': rep,
                        'exit_code': process.returncode, 'timed_out': timed_out, 'wall_ns': wall,
                        'kernel_cpu_ns': int((usage.ru_utime + usage.ru_stime) * 1e9), 'kernel_maxrss_kib': usage.ru_maxrss})
                    (ROOT / ('Development-sessions-progress.json' if development else 'Sessions-progress.json')).write_text(json.dumps(sessions, indent=2) + '\n')
                    if process.returncode:
                        raise RuntimeError('Preserved failed worker: ' + name)
                    out = folder / name
                    w = json.loads((out / 'Worker.json').read_text())
                    raw = (out / 'Evidence.jsonl').read_bytes()
                    if len(raw) != w['evidence_bytes'] or list(map(json.loads, raw.splitlines())) != w['records']:
                        raise RuntimeError('Preserved incomplete journal: ' + name)
    path = ROOT / ('Development-sessions.json' if development else 'Sessions.json')
    path.write_text(json.dumps(sessions, indent=2) + '\n')
    print('Completed', len(sessions), 'development' if development else 'headline', 'workers', flush=True)


if __name__ == '__main__':
    run('--development' in sys.argv)
