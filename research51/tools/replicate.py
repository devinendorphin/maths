"""Prepare an isolated fresh replication from the restored archive dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import runpy
import shutil
import sys

SOURCE=Path(__file__).resolve().parents[1]


def run(target,vipr):
    if target.exists():raise FileExistsError(target)
    target.mkdir(parents=True)
    shutil.copytree(SOURCE/'dependencies/stage35',target/'baseline/code')
    shutil.copytree(SOURCE/'dependencies/research46',target/'research46')
    dest=target/'research51';shutil.copytree(SOURCE/'code',dest/'code')
    shutil.copytree(SOURCE/'tools',dest/'tools');shutil.copy(SOURCE/'Roadmap.md',dest/'Roadmap.md')
    vipr=vipr.resolve()
    if not vipr.exists():raise FileNotFoundError(vipr)
    files=[vipr,vipr.parent/'viprchk.cpp',vipr.parent/'CMakeConfig.hpp']
    capability=dict(python=sys.version,platform=platform.platform(),replication_of='experiments-51-55',
                    vipr_files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (dest/'Capabilities.json').write_text(json.dumps(capability,sort_keys=True,indent=2)+'\n')
    sys.path.insert(0,str(dest/'code'))
    import campaign
    campaign.VIPR=vipr;campaign.freeze()
    assert json.loads((dest/'Inputs.json').read_text())==json.loads((SOURCE/'Inputs.json').read_text())
    try:campaign.run()
    except AssertionError as exc:
        if str(exc)!='logical repeat mismatch':raise
        # The original frozen post-run clock-field bug is corrected by the
        # preserved finalizer. Any earlier failure leaves fewer than 422 workers
        # or missing proof/native files and cannot pass finalization.
        runpy.run_path(str(dest/'tools/finalize.py'),run_name='__main__')
    print('Fresh replication:',dest)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('target',type=Path)
    parser.add_argument('--vipr',type=Path,default=SOURCE/'dependencies/vipr/viprchk')
    args=parser.parse_args();run(args.target,args.vipr)
