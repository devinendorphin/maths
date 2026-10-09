import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import native as N
from memory import Sampler

ROOT=Path(__file__).resolve().parents[1]
fixtures=json.loads((ROOT/'Fixtures.json').read_text());index=int(sys.argv[1]);observer=sys.argv[2]=='on';f=fixtures[index]
sdk=json.loads((ROOT/'SDK.json').read_text());folder=ROOT/'evidence/memory';folder.mkdir(parents=True,exist_ok=True);log=folder/f'{index}-{sys.argv[2]}.log'
env=dict(os.environ,PYTHONPATH=sdk['pb_source'],PYTHONDONTWRITEBYTECODE='1')
cmd=[str(N.NATIVE_CHECKER),str(ROOT/f['proof'])] if f['producer']=='native' else [sdk['pb_python'],'-m','veripb',str(ROOT/f['formula']),str(ROOT/f['proof'])]
begin=N.clock();sampler=Sampler() if observer else None
if sampler:sampler.__enter__()
p=subprocess.run([str(ROOT/'code/wait_account'),str(log)]+cmd,env=env,capture_output=True,text=True,timeout=35)
if sampler:sampler.__exit__()
assert p.returncode==0,p.stderr;usage=json.loads(p.stdout);text=log.read_text()
accepted=usage['exit']==0 and ('Successfully verified optimal value range' in text if f['producer']=='native' else 'Verification succeeded' in text)
assert accepted
measurement=dict(total=N.elapsed(begin),kernel_child=usage,parent_lifetime_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,sampling=sampler.report() if sampler else None)
assert measurement['total']['child_cpu']+0.002>=usage['child_cpu']
print(json.dumps(dict(stage=131,logical=dict(fixture=index,observer=observer,accepted=accepted,proof_sha256=f['proof_sha256'],formula_sha256=f.get('formula_sha256')),measurements=measurement)))
