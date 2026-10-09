"""Generate deployment identities and a complete source/input freeze before execution."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SDK=Path('/workspace/maths-toolchains/repair-sdk')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(destination):
    binaries={name:dict(path=str(path),sha256=digest(path)) for name,path in {
        'exact_scip':SDK/'scip-build/bin/scip',
        'official_completion':SDK/'vipr-build-compatible/viprcomp',
        'official_checker':SDK/'vipr-build-compatible/viprchk',
        'fork_wrapper':SDK/'vipr_fork',
    }.items()}
    manifest=dict(binaries=binaries,ordinary_scip_python=dict(pyscipopt='6.0.0',scip='10.0.0',exact_support=False),
                  original_checker_sha256=digest(ROOT/'dependencies/research86/dependencies/vipr/viprchk'),
                  inherited_checker_source_sha256=digest(ROOT/'dependencies/research86/dependencies/vipr/viprchk.cpp'),
                  wrapper_source_sha256=digest(ROOT/'code/vipr_fork.cpp'),
                  compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
                  source_commits=dict(scip='0c80fdd8e91d7d9f23c0c7a55b68884209d5f27c',soplex='2207cfb274dbce5c2644911dd621438535733607',vipr='30f2951d1e90e47afa821bdd1b12b82246656c42'),
                  independent_sdk_installation=False)
    (ROOT/'SDK-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='Freeze.json' and '__pycache__' not in p.parts}
    (ROOT/'Freeze.json').write_text(json.dumps(dict(headline_started=False,files=files),indent=2)+'\n')
    copy_to(destination)


def copy_to(destination):
    destination=Path(destination);destination.mkdir(exist_ok=False)
    files=json.loads((ROOT/'Freeze.json').read_text())['files']
    for name,digest_expected in files.items():
        assert digest(ROOT/name)==digest_expected,name
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    shutil.copy2(ROOT/'Freeze.json',destination/'Freeze.json')
    print('Prepared fresh repair directory:',destination,flush=True)


if __name__=='__main__':
    if sys.argv[1]=='freeze':prepare(sys.argv[2])
    else:copy_to(sys.argv[2])
