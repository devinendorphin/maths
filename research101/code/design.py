"""Deterministic bounded design, written before headline execution."""
import json,random,pathlib
root=pathlib.Path(__file__).resolve().parents[1];rng=random.Random(101110)
rows=[]
for n in [8,12,16]:
 for seed in range(2):
  w=[rng.randint(1,20) for _ in range(n)]
  rows.append(dict(case_id=f'n{n}-s{seed}',n=n,weights=w,capacity=sum(w)//3,profits=[rng.randint(-12,40) for _ in w],slopes=[rng.randint(-4,4) for _ in w],end=8,observations=list(range(9))))
rows.extend([
 dict(case_id='ties',n=8,weights=[2]*8,capacity=6,profits=[4]*8,slopes=[-1]*8,end=8,observations=list(range(9))),
 dict(case_id='zero-capacity',n=8,weights=list(range(1,9)),capacity=0,profits=[-3,0,3,6,9,12,15,18],slopes=[2,-1,0,1,-2,1,-1,0],end=8,observations=list(range(9)))])
(root/'Inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
protocol=dict(experiments={
 '101':'Exact DP certificate production and independent recurrence validation, eight models at three times.',
 '102':'Production SCIP candidates plus independently checked exact DP upper certificates, same point inputs; exact-mode capability gate.',
 '103':'Weight/capacity scaling 1, 4, 16 with unchanged feasible subsets: pseudopolynomial cost and certificate growth.',
 '104':'Signed, zero and tied objective controls: two declared fixtures over nine integer times.',
 '105':'Rational queries at 1/3, 7/5, 15/2; exact denominator scaling and model binding.',
 '106':'Six certificate corruption controls on every baseline point; original proof still admitted.',
 '107':'Declared DP cell caps: one-cell failure and exactly sufficient completion; charge failed attempt and fresh fallback.',
 '108':'Capacity changes: invalidate old certificates; subset transfer only when the old optimum remains feasible.',
 '109':'Repeated observations: checked point memoization versus fresh DP with same exact point contract.',
 '110':'Full-cost DP, SCIP+DP, VIPR points and VIPR guarded intervals on matched dense/sparse streams, three rotated repetitions.'},
 seed=101110,domain='Fixed positive integer weights; nonnegative capacity; signed integer affine coefficients; rational query. n <= 16.',
 limits=dict(campaign_wall_seconds=300,scip_seconds_per_query=5,dp_cell_cap=200000,weight_scale_max=16),
 repetitions=3,baseline_times=[0,4,8],timing='process CPU plus child user/system CPU; construction, exact admission, serialization and proof I/O included; import/install/audit/package excluded and disclosed separately',
 assurance='DP full table verified independently; SCIP candidate checked for binary/feasible packing and exact DP optimum. VIPR uses inherited original-problem checker. These are different checking paths, no formal verification of Python.',
 stop='Any unexpected failed admission or incomplete required solve aborts headline run. Caps in 107 are expected incompletes, never admitted.',
 nonclaims=['No reproduction of CP 2024 certifying-DP or VeriPB','No SCIP exact-mode result if capability gate fails','No SCIP reoptimization test','No timing significance or general scalability claim'])
(root/'Protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
