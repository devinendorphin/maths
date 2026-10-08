"""Frozen ten-experiment batch, immutable workers and independent checks."""
import argparse,hashlib,json,platform,statistics,time,resource
from collections import defaultdict
from shared import ROOT,DEPS,save,read,digest,logical
import design,oracles,economy,theories
from checker import Checker

def protocol():
 rows=design.inputs();timings=[(r['case_id'],m) for r in rows if r['timing'] for m in design.timing_methods(r['stage'])]
 return dict(version=1,previous_commit='649e3afb0ac730d7ed639cff97bdfe9fa8926ea9',inputs=len(rows),headline_workers=sum(len(design.METHODS[r['stage']]) for r in rows),timing_workers=3*len(timings),repeats=3,methods=design.METHODS,timing_subset=timings,batch_wall_seconds=900,oracle_limits=oracles.LIMITS,native_proof_limits=dict(steps=500000,cells=4096,wall_seconds=30),checker_timeout_seconds=30,
 guarantees='Elementary conditional proofs in Mathematical-guarantees.md; tests validate implementations and assumptions, not general theorems or novelty.',
 model='Fixed-feasible binary knapsack and signed affine profits, except explicit capacity-subset controls88, polynomial curvature controls89 and finite model epochs94. These use separately labeled contracts.',
 economy='Integrated parent process CPU plus child VIPR CPU: curve discovery, native solve/disposal, adapter, required proof-file I/O, checker, cache hashing, primal feasibility/value, coefficient recognition, output selection included. Independent audits, worker JSON, deliberately false-proof trials and archive work excluded. Cold state per worker; method order rotated over three declared repeats. Counts and observed costs do not establish a universal speedup.',
 proof_storage='Proof files deduplicated by content SHA256 for archive space. Each required new proof is nevertheless regenerated, written and checked during its worker. There is no shared algorithm cache between workers.',
 integrity='Guarded receipts bind canonical original-problem prefix, full model/time, objective, accepted primal, proof bytes and frozen checker binary. Receipt seals are unsalted hashes, not signatures. Trust admission/immutable snapshots and truthful model; concurrent/adversarial system compromise not studied.',
 dependencies='92 observation-stride variants share each seed input;90 profiles share baseweights/profits; all explicitly constructed controls are not independent draws. No tuning or outcome-based selection.',
 audit='Independent MITM/layers for affine queries, objectives and intervals; exact polynomial optima and analytic quadratic extrema; scalar disjoint covers, all-time true-loss lines and boundary repricing; original-problem proof regeneration and unique VIPR accepted/false-bound checks; explicit cache controls replayed read-only.',
 scope='No novel arithmetic, recovered unpublished mathematics, formal verification, production SCIP comparison, measured peak RSS or generic complexity improvement claimed.')
def freeze():
 save(ROOT/'Inputs.json',design.inputs());save(ROOT/'Protocol.json',protocol());paths=list((ROOT/'code').glob('*.py'))+[ROOT/'Inputs.json',ROOT/'Protocol.json',ROOT/'Roadmap.md',ROOT/'Mathematical-guarantees.md']
 files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};deps={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS.rglob('*') if p.is_file() and '__pycache__' not in p.parts};save(ROOT/'Freeze.json',dict(files=files,dependencies=deps,capabilities=read(ROOT/'Capabilities.json')));print('FROZEN',len(design.inputs()),digest(files),flush=True)
def check_freeze():
 s=read(ROOT/'Freeze.json')
 for p,h in {**s['files'],**s['dependencies']}.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p

def execute(row,method):
 start=time.process_time()
 if method in theories.DISPATCH:
  before=resource.getrusage(resource.RUSAGE_CHILDREN);r=theories.DISPATCH[method](row);after=resource.getrusage(resource.RUSAGE_CHILDREN);r['algorithm_cpu']=time.process_time()-start+after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
 else:r=economy.run(row,method)
 r['method']=method;return r

def worker(row,method,phase,repeat,checker):
 p=ROOT/'evidence'/f'{row["case_id"]}--{method}--{phase}--{repeat}.json.gz'
 if p.exists():return read(p)['summary']
 r=execute(row,method);checked=checker.run(row,r)
 s=dict(stage=row['stage'],case_id=row['case_id'],method=method,phase=phase,repeat=repeat,status=r['status'],algorithm_cpu=r['algorithm_cpu'],certificates=r.get('certificates',len(r.get('records',[]))),certificate_bytes=r.get('certificate_bytes',sum(x['bytes'] for x in r.get('records',[]))),cache_hits=r.get('cache_hits',0),factor_used=r.get('factor_used',False),intervals=len(r.get('bundles',r.get('blocks',[]))),audit=checked,signature=digest(logical(r)))
 save(p,dict(input=row,result=r,audit=checked,summary=s));print('PATH',row['case_id'],method,phase,repeat,f'cpu={r["algorithm_cpu"]:.6f}',flush=True);return s

def finish():
 rows=[read(p)['summary'] for p in sorted((ROOT/'evidence').glob('*--*.json.gz'))];expected=protocol();assert len(rows)==expected['headline_workers']+expected['timing_workers'];groups=defaultdict(list)
 for r in rows:assert r['audit']['passed'];groups[(r['case_id'],r['method'])].append(r)
 for key,samples in groups.items():assert len({r['signature'] for r in samples})==1,key
 timing=[]
 for stage in range(86,96):
  for method in design.timing_methods(stage):
   selected=[r for r in rows if r['stage']==stage and r['method']==method and r['phase']=='timing'];sums=[sum(r['algorithm_cpu'] for r in selected if r['repeat']==rep) for rep in range(3)];cases={r['case_id'] for r in selected}
   timing.append(dict(stage=stage,method=method,repeated_sums=sums,median=statistics.median(sums),eligible=True,runs=len(selected),per_case_medians={case:statistics.median(r['algorithm_cpu'] for r in selected if r['case_id']==case) for case in sorted(cases)}))
 summary=dict(inputs=len(read(ROOT/'Inputs.json')),workers=len(rows),complete_workers=len(rows),integer_checks=sum(r['audit']['integer_checks'] for r in rows),numerical_checks=sum(r['audit']['numerical_checks'] for r in rows),bound_checks=sum(r['audit']['bound_checks'] for r in rows),all_audits_passed=True,all_logical_repeats_match=True,repeated_groups=sum(len(s)>1 for s in groups.values()),timing=timing)
 save(ROOT/'Path-results.json',rows);save(ROOT/'Summary.json',summary);save(ROOT/'Final-audit.json',dict(passed=True,workers=len(rows),freeze_intact=True,summary_sha256=hashlib.sha256((ROOT/'Summary.json').read_bytes()).hexdigest()));print('COMPLETED',json.dumps({k:summary[k] for k in ('inputs','workers','integer_checks','numerical_checks','bound_checks')}),flush=True)
def run():
 check_freeze();start=time.perf_counter();rows=read(ROOT/'Inputs.json')
 for stage in range(86,96):
  subset=[r for r in rows if r['stage']==stage];checkers={r['case_id']:Checker(r) for r in subset}
  for row in subset:
   if time.perf_counter()-start>900:raise RuntimeError('batch wall cap')
   for method in design.METHODS[stage]:worker(row,method,'headline',0,checkers[row['case_id']])
  methods=design.timing_methods(stage)
  for repeat in range(3):
   for row in subset:
    if not row['timing']:continue
    for j in range(len(methods)):
     if time.perf_counter()-start>900:raise RuntimeError('batch wall cap')
     worker(row,methods[(j+repeat)%len(methods)],'timing',repeat,checkers[row['case_id']])
  check_freeze()
 finish();check_freeze();save(ROOT/'Execution.json',dict(completed=True,wall_seconds=time.perf_counter()-start,batch_limit_seconds=900))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run']);a=p.parse_args();freeze() if a.action=='freeze' else run()
