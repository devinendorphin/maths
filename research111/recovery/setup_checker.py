"""Bounded new proof-replay checker, using untouched official rule sources."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
SDK=Path('/workspace/maths-toolchains/veripb2-recovery-source')
SOURCE=next(SDK.glob('VeriPB-*'))
VENV=SDK/'venv'
START=time.monotonic();records=[]


def command(args,cwd=SDK):
    log=SDK/f'setup-{time.time_ns()}-{len(records)}.log';start=time.monotonic()
    with log.open('w') as out:
        env=dict(os.environ,CC='gcc',CXX='g++')
        p=subprocess.run(args,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=max(1,300-(time.monotonic()-START)))
    records.append(dict(command=args,wall=time.monotonic()-start,exit_code=p.returncode,log=log.name))
    assert p.returncode==0,log


try:
    command([sys.executable,'-m','venv',str(VENV)])
    python=str(VENV/'bin/python')
    command([python,'-m','pip','install','--disable-pip-version-check','setuptools==69.5.1','pybind11==2.13.6'])
    script=SDK/'build_core.py'
    script.write_text("from setuptools import setup,Extension\nimport pybind11\nsetup(name='veripb',version='2.3.0',packages=['veripb','veripb.optimized'],ext_modules=[Extension('veripb.optimized.pybindings',sources=['veripb/optimized/'+s for s in ['pybindings.cpp','constraints.cpp','parsing.cpp','gzstream.cpp']],include_dirs=[pybind11.get_include()],extra_compile_args=['--std=c++17','-DPY_BINDINGS','-O3','-DNDEBUG'],libraries=['gmp','gmpxx','z'],language='c++')])\n")
    command([python,str(script),'build_ext','--inplace','egg_info'],cwd=SOURCE)
    binaries={p.relative_to(SOURCE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob('*.so') if 'build' not in p.parts}
    assert list(binaries)==['veripb/optimized/pybindings.cpython-312-x86_64-linux-gnu.so']
    result=dict(status='built',source=str(SOURCE),python=python,binaries=binaries,
                checking_rule_changes=False,interpreted_rule_modules=True,
                build_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
except Exception as e:
    result=dict(status='setup_failed',reason=str(e))
result.update(wall=time.monotonic()-START,wall_cap=300,commands=records)
(ROOT/'Checker-setup.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
