"""Fixed isolated jobs and preserved progress; all work must complete."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from controls import run as controls

ROOT=Path(__file__).resolve().parents[1]


def run():
    if (ROOT/'outputs').exists():raise RuntimeError('empty destination required')
    (ROOT/'outputs').mkdir();sessions=[]
    jobs=[(i,fmt,policy,rep) for i in range(6) for rep in range(2) for policy in range(3) for fmt in ('full','compact')]
    for i,fmt,policy,rep in jobs:
        name=f'{i}-{fmt}-{policy}-{rep}';out=ROOT/'outputs'/name;t=time.perf_counter()
        with (ROOT/'outputs'/(name+'.stdout')).open('w') as stdout,(ROOT/'outputs'/(name+'.stderr')).open('w') as stderr:
            p=subprocess.Popen([sys.executable,str(ROOT/'code/worker.py'),str(out),str(i),fmt,str(policy),str(rep)],stdout=stdout,stderr=stderr,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            timed=False
            while True:
                pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                if pid:break
                if time.perf_counter()-t>90:
                    p.kill();timed=True;pid,status,usage=os.wait4(p.pid,0);break
                time.sleep(.005)
            p.returncode=os.waitstatus_to_exitcode(status)
        sessions.append({'name':name,'index':i,'format':fmt,'policy':policy,'repetition':rep,'exit_code':p.returncode,'timed_out':timed,
                         'wall_s':time.perf_counter()-t,'kernel_cpu_s':usage.ru_utime+usage.ru_stime,'kernel_maxrss_kib':usage.ru_maxrss})
        (ROOT/'Sessions-progress.json').write_text(json.dumps(sessions,indent=2)+'\n')
        if p.returncode:raise RuntimeError('Preserved failed '+name)
    context=json.loads((ROOT/'Freeze.json').read_text())['context']
    (ROOT/'Controls.json').write_text(json.dumps(controls(context),indent=2,sort_keys=True)+'\n')
    (ROOT/'Sessions.json').write_text(json.dumps(sessions,indent=2)+'\n')
    print('Completed',len(sessions),'storage workers',flush=True)


if __name__=='__main__':run()
