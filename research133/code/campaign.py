"""Sequential isolated workers with wait4 lifetime CPU/peak RSS and wall limits."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from routes import METHODS

ROOT=Path(__file__).resolve().parents[1]


def save(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def run():
    start=time.perf_counter();cpu=time.process_time()
    jobs=[('static',0,'cold',0,4096)]
    jobs += [('updates',i,method,rep,4096) for i in range(12) for rep in range(3) for method in METHODS]
    jobs += [('fairness',i,'flow-repair',0,4096) for i in range(8)]
    jobs += [('counterexample',0,'recheck',0,4096)]
    jobs += [('budget',2,method,0,64) for method in METHODS]
    outputs=ROOT/'outputs';outputs.mkdir(exist_ok=True)
    sessions=[]
    for mode,index,method,repetition,limit in jobs:
        name=f'{mode}-{index:02d}-{method}-{repetition}'
        out=outputs/name;out.mkdir()
        command=[sys.executable,str(ROOT/'code/worker.py'),mode,str(index),method,str(repetition),str(out),str(limit)]
        tick=time.perf_counter()
        with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            proc=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            expired=False
            while True:
                pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
                if pid:break
                if time.perf_counter()-tick>30:
                    proc.kill();expired=True
                    pid,status,usage=os.wait4(proc.pid,0);break
                time.sleep(.005)
            proc.returncode=os.waitstatus_to_exitcode(status)
        session={'name':name,'mode':mode,'index':index,'method':method,'repetition':repetition,'cache_limit':limit,
                 'exit_code':proc.returncode,'timed_out':expired,'session_wall_s':time.perf_counter()-tick,
                 'wait4_user_cpu_s':usage.ru_utime,'wait4_system_cpu_s':usage.ru_stime,'wait4_maxrss_kib':usage.ru_maxrss}
        sessions.append(session)
        save(ROOT/'Sessions-progress.json',sessions)
        if proc.returncode:
            print('Preserved failed worker',name,(out/'stderr.txt').read_text(),flush=True)
            raise RuntimeError('worker failure; no silent skip')
    save(ROOT/'Sessions.json',{'sessions':sessions,'launcher_wall_s':time.perf_counter()-start,'launcher_cpu_s':time.process_time()-cpu,'session_count':len(sessions)})
    print('Completed',len(sessions),'isolated workers',flush=True)


if __name__=='__main__':run()
