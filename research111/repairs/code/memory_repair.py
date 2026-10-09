"""Supplement failed short-process sampling without repeating valid experiments."""
import json
from pathlib import Path
import subprocess
from core import ROOT,clock,elapsed,produce,sha
from memory_observer import observe

BINARY=Path('/workspace/maths-toolchains/repair-sdk/vipr_hold')


def run():
    frozen=json.loads((ROOT/'Memory-freeze.json').read_text())
    for name,digest in frozen['files'].items():assert sha((ROOT/name).read_bytes())==digest,name
    assert sha(BINARY.read_bytes())==frozen['binary_sha256']
    rows={r['case_id']:r for r in json.loads((ROOT/'Inputs.json').read_text())};records=[]
    for case in ['heldout-n18-0','heldout-factor']:
        row=rows[case];start=clock();fact,_=produce(row,4)
        process=subprocess.Popen([str(BINARY),str(ROOT/fact.path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        status=None
        while True:
            line=process.stdout.readline()
            if not line:raise RuntimeError('memory observer child ended before checkpoint')
            if line.startswith('MEMORY_CHECKPOINT '):status=int(line.split()[1]);break
        assert status==0
        import os
        own=os.getpid();ids,values=observe(own,process.pid)
        logical=dict(case_id=case,row=row,time=[4,1],fact=fact.record(),verification_status=status,checkpoint='after verification, retained parsed proof state')
        measured=dict(simultaneous_tree_rss_kib=sum(values.values()),runner_rss_kib=values[own],checker_rss_kib=values[process.pid],observed_processes=len(ids))
        pss=[]
        for pid in ids:
            for line in Path(f'/proc/{pid}/smaps_rollup').read_text().splitlines():
                if line.startswith('Pss:'):pss.append(int(line.split()[1]))
        measured['simultaneous_proportional_set_kib']=sum(pss)
        process.stdin.write('\n');process.stdin.flush();process.stdin.close();process.wait(timeout=10);assert process.returncode==0
        measured['total']=elapsed(start);records.append(dict(logical=logical,measurements=measured))
    (ROOT/'Memory-repair.json').write_text(json.dumps(records,indent=2)+'\n');print('Verified retained-state memory checkpoints:',len(records),flush=True)

if __name__=='__main__':run()
