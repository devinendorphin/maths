"""Bounded official VIPR completion/checker installation after the development gate."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

SDK=Path('/workspace/maths-toolchains/repair-sdk');start=time.monotonic();records=[]
cmake=str(SDK/'checker-venv/bin/cmake');build=SDK/'vipr-build-compatible'
commands=[
 [cmake,'-S',str(SDK/'vipr-current/code'),'-B',str(build),f'-DSOPLEX_DIR={SDK}/prefix/lib/cmake/soplex',f'-DCMAKE_PREFIX_PATH={SDK}/prefix/usr'],
 [cmake,'--build',str(build),'--target','viprcomp','viprchk','--parallel','4']]
try:
 for i,cmd in enumerate(commands):
  t=time.monotonic();log=SDK/f'completion-setup-{i}.log'
  with log.open('w') as out:p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=max(1,180-(time.monotonic()-start)))
  records.append(dict(command=cmd,exit_code=p.returncode,wall=time.monotonic()-t,log=log.name))
  if p.returncode:raise RuntimeError(f'completion command {i} failed')
 result=dict(status='built',binaries={name:dict(path=str(build/name),sha256=hashlib.sha256((build/name).read_bytes()).hexdigest()) for name in ['viprcomp','viprchk']})
except Exception as e:result=dict(status='attempt_failed',reason=str(e))
result.update(total_wall=time.monotonic()-start,wall_cap=180,commands=records)
(SDK/'Completion-setup.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
