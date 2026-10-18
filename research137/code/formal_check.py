"""Compile the proofs in a new build directory and retain false controls.
Use --preload only for the documented /proc namespace compatibility library.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def run(binary,destination,preload):
    assert not destination.exists(),'Never overwrite formal evidence'
    destination.mkdir(parents=True)
    env=os.environ.copy();env['LEAN_PATH']=str(destination.resolve())
    if preload:env['LD_PRELOAD']=str(preload.resolve())
    reports=[]
    for file in ('Flow.lean','Spec.lean','RejectedStatement.lean'):
        args=[str(binary),'-j','1']
        if file=='Flow.lean':args+=['-o',str(destination/'Flow.olean')]
        args+=[str(ROOT/'formal'/file)]
        p=subprocess.run(args,env=env,text=True,capture_output=True,timeout=90,cwd=ROOT.parent)
        expected=file!='RejectedStatement.lean'
        assert (p.returncode==0)==expected,(file,p.stdout,p.stderr)
        if expected:assert 'sorryAx' not in p.stdout+p.stderr and 'warning:' not in p.stdout+p.stderr
        else:assert p.stdout.count('error:')>=2
        reports.append({'source':file,'expected_success':expected,'returncode':p.returncode,
                        'stdout':p.stdout,'stderr':p.stderr})
    version=subprocess.check_output([str(binary),'--version'],env=env,text=True).strip()
    report={'passed':True,'version':version,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
            'preload_sha256':None if not preload else hashlib.sha256(preload.read_bytes()).hexdigest(),
            'checks':reports,'no_sorryAx_in_successful_proofs':True}
    (destination/'Formal-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'compiled':['Flow.lean','Spec.lean'],'false_statements_rejected':True}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('destination',type=Path);p.add_argument('--preload',type=Path)
    a=p.parse_args();run(a.binary.resolve(),a.destination.resolve(),a.preload)
