"""Pinned public SDK; deterministic local adapter build, no vendored solver binary."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SDK=Path(os.environ.get('MATHS152_SDK','/workspace/scratch/fa22180e3e2d/ortools-cpp-9.14/or-tools_x86_64_Ubuntu-22.04_cpp_v9.14.6206'))


def run():
    lib=SDK/'lib';out=ROOT/'bridge.so'
    command=['g++','-O2','-DNDEBUG','-std=c++17','-fPIC','-shared','-Wl,--build-id=none',str(ROOT/'code/bridge.cc'),
             '-I'+str(SDK/'include'),'-L'+str(lib),'-lortools','-Wl,-rpath,'+str(lib),'-o',str(out)]
    subprocess.run(command,check=True)
    deps={str(p.relative_to(SDK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(lib.glob('*.so*')) if p.is_file() and not p.is_symlink()}
    report={'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
            'sdk_release_url':'https://github.com/google/or-tools/releases/download/v9.14/or-tools_amd64_ubuntu-22.04_cpp_v9.14.6206.tar.gz',
            'sdk_release_sha256':'127a82bbbf304d26721bb9b41ecce2d66f21c757204ab5aa2cc37eaa6ffb7eb6',
            'sdk_root':str(SDK),'command':command,'native_libraries':deps,'adapter_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'adapter_bytes':out.stat().st_size}
    (ROOT/'Build.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('Built adapter:',out.stat().st_size,'bytes')


if __name__=='__main__':run()
