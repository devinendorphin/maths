"""54 isolated predeclared workers, retained failures and fixed guards."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from controls import run as controls
ROOT=Path(__file__).resolve().parents[1]


def run():
    assert not (ROOT/'outputs').exists();(ROOT/'outputs').mkdir();sessions=[]
    for i in range(9):
        for rep in range(2):
            for route in ('cold','basis','guard'):
                name=f'{i}-{route}-{rep}';tick=time.perf_counter()
                with (ROOT/'outputs'/(name+'.stdout')).open('w') as stdout,(ROOT/'outputs'/(name+'.stderr')).open('w') as stderr:
                    p=subprocess.Popen([sys.executable,str(ROOT/'code/worker.py'),str(ROOT/'outputs'/name),str(i),route,str(rep)],stdout=stdout,stderr=stderr,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
                    timed=False
                    while True:
                        pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                        if pid:break
                        if time.perf_counter()-tick>90:
                            p.kill();timed=True;pid,status,usage=os.wait4(p.pid,0);break
                        time.sleep(.005)
                    p.returncode=os.waitstatus_to_exitcode(status)
                sessions.append({'name':name,'index':i,'route':route,'repetition':rep,'exit_code':p.returncode,'timed_out':timed,
                                 'wall_s':time.perf_counter()-tick,'kernel_cpu_s':usage.ru_utime+usage.ru_stime,'kernel_maxrss_kib':usage.ru_maxrss})
                (ROOT/'Sessions-progress.json').write_text(json.dumps(sessions,indent=2)+'\n')
                if p.returncode:raise RuntimeError('preserved failed '+name)
    ctx=json.loads((ROOT/'Freeze.json').read_text())['context']
    (ROOT/'Controls.json').write_text(json.dumps(controls(ctx),sort_keys=True,indent=2)+'\n')
    (ROOT/'Sessions.json').write_text(json.dumps(sessions,indent=2)+'\n');print('Completed',len(sessions),'larger-inquiry workers',flush=True)


if __name__=='__main__':run()
