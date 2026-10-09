from fractions import Fraction as Q
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import native as N
ROOT=Path(__file__).resolve().parents[1]


def point(row,observation):
    t,s=map(lambda x:Q(*x),observation);d=math.lcm(t.denominator,s.denominator)
    profits=[int(d*(p+t*v+s*u)) for p,v,u in zip(row['profits'],row['v'],row['u'])]
    encoded=dict(n=row['n'],weights=row['weights'],capacity=row['capacity'],profits=profits,slopes=[0]*row['n'],end=1)
    f,cost=N.produce(encoded,0,'two-parameter-original-model-binding')
    return dict(parameter=observation,scale=d,encoded_row=encoded,fact=f.record()),cost


def value(row,mask,observation):
    t,s=map(lambda x:Q(*x),observation)
    return sum(p+t*v+s*u for j,(p,v,u) in enumerate(zip(row['profits'],row['v'],row['u'])) if mask>>j&1)


def inside(vertices,query):
    # Exact convex-hull membership through triangles (Caratheodory in R^2).
    import itertools
    points=[tuple(Q(*x) for x in a) for a in vertices];q=tuple(Q(*x) for x in query)
    if q in points:return True
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    for a,b,c in itertools.combinations(points,3):
        ab=(b[0]-a[0],b[1]-a[1]);ac=(c[0]-a[0],c[1]-a[1]);aq=(q[0]-a[0],q[1]-a[1]);det=cross(ab,ac)
        if det:
            x=cross(aq,ac)/det;y=cross(ab,aq)/det
            if x>=0 and y>=0 and x+y<=1:return True
    return False


def run():
    for name,sha in json.loads((ROOT/'Freeze.json').read_text())['files'].items():assert N.sha((ROOT/name).read_bytes())==sha,name
    for name,sha in json.loads((ROOT/'SDK.json').read_text())['files'].items():assert N.sha(Path(name).read_bytes())==sha,name
    start=time.monotonic();results=[]
    for repeat in range(3):
        order=[(i,o) for i in range(4) for o in ['off','on']];rot=repeat%8;order=order[rot:]+order[:rot]
        for index,observer in order:
            p=subprocess.run([sys.executable,str(ROOT/'code/memory_worker.py'),str(index),observer],capture_output=True,text=True,timeout=40);assert p.returncode==0,p.stderr
            r=json.loads(p.stdout);r['repeat']=repeat;results.append(r)
    for row in json.loads((ROOT/'Inputs.json').read_text()):
        begin=N.clock();facts=[];vertices=[]
        for q in row['vertices']:
            f,cost=point(row,q);facts.append(f);vertices.append(dict(parameter=q,candidate_optimal=value(row,row['candidate'],q)==Q(f['fact']['objective'],f['scale'])))
        admitted=all(v['candidate_optimal'] for v in vertices);partial_vertices=row['vertices'][:3]
        partial_admitted=all(v['candidate_optimal'] for v in vertices[:3]);outputs=[]
        for q in row['queries']:
            applicable=admitted and inside(row['vertices'],q)
            if applicable:mask=row['candidate']
            else:
                f,cost=point(row,q);facts.append(f);mask=f['fact']['packing']
            outputs.append(dict(parameter=q,packing=mask,value=[value(row,mask,q).numerator,value(row,mask,q).denominator],reused=applicable,partial_hull_applicable=partial_admitted and inside(partial_vertices,q)))
        # The first old certificate is valid for its own point. Its objective
        # header is not rebound to a changed point merely because a packing is stable.
        first=facts[0];different=[[1,1],[0,1]];t,s=Q(1),Q(0)
        current=[p+t*v+s*u for p,v,u in zip(row['profits'],row['v'],row['u'])]
        old_point_binding=current==first['encoded_row']['profits']
        d=dict(row=row,vertices=vertices,admitted=admitted,partial_admitted=partial_admitted,partial_vertices=partial_vertices,outputs=outputs,facts=facts,old_point_binding_at_1_0=old_point_binding,old_point_proof_valid_for_original=True,candidate_stable_at_1_0=next(o for o in outputs if o['parameter']==different)['packing']==row['candidate'])
        results.append(dict(stage=132,repeat=0,logical=d,measurements=dict(total=N.elapsed(begin))))
    assert time.monotonic()-start<120 and sum(p.stat().st_size for p in (ROOT/'evidence').rglob('*') if p.is_file())<=33554432
    (ROOT/'Results.json').write_text(json.dumps(results,indent=2)+'\n');print('Completed closing experiments:',len(results),'records')


if __name__=='__main__':run()
