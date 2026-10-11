"""Sequential bounded workers; kernel lifetime resource accounting."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from controls import run as controls

ROOT=Path(__file__).resolve().parents[1]


def run():
    if (ROOT/'Sessions.json').exists() or (ROOT/'outputs').exists():
        raise RuntimeError('use an empty run directory')
    (ROOT/'outputs').mkdir()
    routes=['cold','full-recheck','delta-buffered','delta-fsync']
    jobs=[(i,r,j,4096) for i in range(6) for j in range(3) for r in routes]
    jobs += [(i,'delta-buffered',0,64) for i in range(6)]
    sessions=[]
    for i,route,rep,budget in jobs:
        name=f'{i}-{route}-{rep}-{budget}'
        out=ROOT/'outputs'/name
        start=time.perf_counter()
        proc=subprocess.Popen([sys.executable,str(ROOT/'code/worker.py'),str(out),str(i),route,str(rep),str(budget)],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        # Worker emits no stdout; stderr is small. wait4 owns the child reap.
        timed=False
        while True:
            pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
            if pid:break
            if time.perf_counter()-start>60:
                proc.kill();timed=True;pid,status,usage=os.wait4(proc.pid,0);break
            time.sleep(.005)
        proc.returncode=os.waitstatus_to_exitcode(status)
        stderr=proc.stderr.read().decode();stdout=proc.stdout.read().decode()
        (ROOT/'outputs'/(name+'.stderr')).write_text(stderr)
        (ROOT/'outputs'/(name+'.stdout')).write_text(stdout)
        sessions.append({'name':name,'index':i,'route':route,'repetition':rep,'budget':budget,
                         'exit_code':proc.returncode,'timed_out':timed,'wall_s':time.perf_counter()-start,
                         'kernel_cpu_s':usage.ru_utime+usage.ru_stime,'kernel_maxrss_kib':usage.ru_maxrss})
        (ROOT/'Sessions-progress.json').write_text(json.dumps(sessions,indent=2)+'\n')
        if proc.returncode:raise RuntimeError(f'Preserved incomplete {name}: {stderr}')
    freeze=json.loads((ROOT/'Freeze.json').read_text())
    (ROOT/'Controls.json').write_text(json.dumps(controls(freeze['context']),indent=2,sort_keys=True)+'\n')
    (ROOT/'Sessions.json').write_text(json.dumps(sessions,indent=2)+'\n')
    print('Completed',len(sessions),'workers')


if __name__=='__main__':run()
