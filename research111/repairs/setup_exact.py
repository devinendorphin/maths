"""Timed, trust-preserving exact SCIP setup; all installation state stays outside Git."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SDK = Path('/workspace/maths-toolchains/repair-sdk')
START = time.monotonic()
CAP = 600
SDK.mkdir(exist_ok=True)
records = []
env = dict(os.environ)
env['PATH'] = '/workspace/maths-toolchains/scip-venv/bin:' + env['PATH']


def command(args, cwd=SDK, extra_env=None):
    remaining = CAP - (time.monotonic() - START)
    if remaining <= 0:
        raise TimeoutError('entire exact deployment wall cap')
    index = len(records)
    output = SDK / f'setup-{index:02d}.log'
    started = time.monotonic()
    with output.open('w') as log:
        p = subprocess.run(args, cwd=cwd, env=extra_env or env, stdout=log,
                           stderr=subprocess.STDOUT, timeout=remaining)
    records.append(dict(command=args, exit_code=p.returncode,
                        wall=time.monotonic()-started, log=output.name))
    if p.returncode:
        raise RuntimeError(f'command {index} failed: {output}')


try:
    apt = SDK / 'apt'
    for sub in ['lists/partial', 'cache/archives/partial', 'log', 'etc']:
        (apt/sub).mkdir(parents=True, exist_ok=True)
    options = ['-o', f'Dir::State::lists={apt}/lists', '-o', f'Dir::Cache={apt}/cache',
               '-o', f'Dir::Log={apt}/log', '-o', 'Dir::Etc::main=/dev/null',
               '-o', f'Dir::Etc::parts={apt}/etc', '-o', f'Dir::Etc::sourcelist={ROOT}/apt.sources',
               '-o', f'Dir::Etc::sourceparts={apt}/etc', '-o', 'APT::Sandbox::User=agent']
    command(['apt-get', *options, 'update'])
    command(['apt-get', *options, 'download', 'libmpfr-dev', 'libmpfr6', 'libboost1.83-dev'])
    prefix = SDK / 'prefix'
    prefix.mkdir(exist_ok=True)
    package_hashes = {}
    for p in sorted(SDK.glob('*.deb')):
        package_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        command(['dpkg-deb', '-x', str(p), str(prefix)])
    soplex = SDK / 'soplex'
    if not soplex.exists():
        command(['git', 'clone', '--depth', '1', '--branch', 'v8.0.0',
                 'https://github.com/scipopt/soplex.git', str(soplex)])
    actual = subprocess.check_output(['git', '-C', str(soplex), 'rev-parse', 'HEAD'], text=True).strip()
    assert actual == '2207cfb274dbce5c2644911dd621438535733607'
    scip = Path('/workspace/maths-toolchains/scip-v10.0.0')
    assert subprocess.check_output(['git', '-C', str(scip), 'rev-parse', 'HEAD'], text=True).strip() == '0c80fdd8e91d7d9f23c0c7a55b68884209d5f27c'
    hints = [f'-DCMAKE_PREFIX_PATH={prefix}/usr', f'-DCMAKE_INSTALL_PREFIX={prefix}',
             f'-DCMAKE_INCLUDE_PATH={prefix}/usr/include', f'-DCMAKE_LIBRARY_PATH={prefix}/usr/lib/x86_64-linux-gnu']
    command(['cmake', '-S', str(soplex), '-B', str(SDK/'soplex-build'), *hints,
             '-DPAPILO=OFF', '-DMPFR=ON', '-DGMP=ON', '-DCMAKE_BUILD_TYPE=Release'])
    command(['cmake', '--build', str(SDK/'soplex-build'), '--parallel', '4'])
    command(['cmake', '--install', str(SDK/'soplex-build')])
    command(['cmake', '-S', str(scip), '-B', str(SDK/'scip-build'), *hints,
             f'-DSOPLEX_DIR={prefix}/lib/cmake/soplex', '-DEXACTSOLVE=ON',
             '-DLPSEXACT=spx', '-DPAPILO=OFF', '-DZIMPL=OFF', '-DIPOPT=OFF',
             '-DREADLINE=OFF', '-DAMPL=OFF', '-DCMAKE_BUILD_TYPE=Release'])
    command(['cmake', '--build', str(SDK/'scip-build'), '--target', 'scip', '--parallel', '4'])
    binary = SDK/'scip-build/bin/scip'
    status = dict(status='built', binary=str(binary), binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), packages=package_hashes)
except Exception as e:
    status = dict(status='attempt_failed', reason=str(e))
finally:
    status.update(total_wall=time.monotonic()-START, total_wall_cap=CAP, commands=records)
    (SDK/'Setup.json').write_text(json.dumps(status, indent=2)+'\n')
    print(json.dumps(status), flush=True)
