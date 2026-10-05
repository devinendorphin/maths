"""Disjoint implementation fixtures, never used to select a campaign policy."""
import random
import subprocess
from pathlib import Path
from shared import SG,value
import parametric,reopt,events,audit_batch as A,vipr_adapter


def run():
    tested=0; split_proofs=0
    for seed in range(12):
        rng=random.Random(951000+seed); n=6
        row=dict(case_id='disjoint-smoke-'+str(seed),n=n,weights=[rng.randint(1,7) for _ in range(n)],
                 profits=[rng.randint(-8,15) for _ in range(n)],slopes=[rng.randint(-4,4) for _ in range(n)],
                 capacity=10,end=17,stage=51,solve_times=[0,1,4,9,17])
        for fn in (parametric.curve,parametric.points):
            result=fn(row); A.parametric(row,result)
            for t,m in enumerate(result['packings']):
                q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
                brute=max(value(q,k) for k in range(1<<n) if value(row['weights'],k)<=row['capacity'])
                assert value(q,m)==brute
            tested+=1
        for mode in ('cold','incumbent','tree'):A.reoptimization(row,reopt.sequence(row,mode));tested+=1
        scan=events.run(row,'scan'); queue=events.run(row,'queue'); A.event_path(row,scan);A.event_path(row,queue)
        assert scan['packings']==queue['packings'];tested+=2
        t=3; q=[a+t*b for a,b in zip(row['profits'],row['slopes'])]
        source=SG.solve(row['weights'],q,row['capacity']); text,meta=vipr_adapter.certificate(row,t,source['packing'],source['proof'])
        path=Path('/tmp/maths-vipr-disjoint.vipr');path.write_text(text)
        result=subprocess.run(['/workspace/maths-tools/vipr/viprchk',str(path)],capture_output=True,text=True)
        assert result.returncode==0,(seed,result.stdout)
        split_proofs+=meta['derivations']>1; tested+=1
    capped=events.run(row,'queue',force_cap=True);A.event_path(row,capped);tested+=1
    assert split_proofs>0
    return dict(passed=True,fixtures=12,checks=tested,branching_vipr_proofs=split_proofs,
                cap_recovery=True,selection_use=False)


if __name__=='__main__':print(run())
