"""Published certifying DP and SCIP proposal paths, with independent exact admission."""
from fractions import Fraction as Q
import json,re,subprocess,pathlib
from support import *
from pyscipopt import Model,SCIP_PARAMSETTING,quicksum
def qvalues(row,t):
 t=Q(t);return [t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
def complete_solution(text,weights,q):
 """Spell out auxiliary flags from their logged threshold/conjunction definitions."""
 line=next(x for x in text.splitlines() if x.startswith('soli '));mask=sum(1<<int(x[1:]) for x in line.split()[1:] if x.startswith('x'))
 names=set(re.findall(r'\b(?:[wp]\d+_-?\d+|c\d+_-?\d+_-?\d+)\b',text));assign=[]
 for name in sorted(names):
  if name[0] in 'wp':
   layer,threshold=map(int,name[1:].split('_'));value=sum((weights[j] if name[0]=='w' else q[j]) for j in range(layer) if mask>>j&1);truth=value>=threshold if name[0]=='w' else value<=threshold
  else:
   layer,weight,profit=map(int,name[1:].split('_'));truth=sum(weights[j] for j in range(layer) if mask>>j&1)>=weight and sum(q[j] for j in range(layer) if mask>>j&1)<=profit
  assign.append(name if truth else '~'+name)
 return text.replace(line,line+' '+' '.join(assign))
def cp_point(row,t):
 t=Q(t);q=qvalues(row,t);key=digest([model(row),[t.numerator,t.denominator]]);folder=ROOT/'evidence/cp'/key;folder.mkdir(parents=True,exist_ok=True)
 inp=folder/'input.txt';inp.write_text(f'{row["n"]} {row["capacity"]}\n'+''.join(f'{w} {p}\n' for w,p in zip(row['weights'],q)))
 p=subprocess.run([str(ROOT/'external/cp2024/knapsack'),str(inp)],cwd=folder,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr
 proof=folder/'knapsack.veripb';formula=folder/'knapsack.opb';assert proof.stat().st_size<=8*1024**2
 raw=proof.read_text();(folder/'producer.veripb').write_text(raw);proof.write_text(complete_solution(raw,row['weights'],q))
 o=subprocess.run(['python3',str(ROOT/'tools/run_veripb.py'),str(formula),str(proof)],capture_output=True,text=True,timeout=15)
 if o.returncode or 'Verification failed' in o.stdout+o.stderr or 'Verification succeeded' not in o.stdout+o.stderr:raise ValueError('VeriPB rejected CP proof: '+(o.stdout+o.stderr)[-500:])
 text=proof.read_text();bounds=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',text);assert bounds and bounds[1]==bounds[2];target=-int(bounds[1])
 solution=next(line for line in text.splitlines() if line.startswith('soli '));mask=sum(1<<int(x[1:]) for x in solution.split()[1:] if x.startswith('x'))
 assert shared.value(q,mask)==target and shared.value(row['weights'],mask)<=row['capacity']
 r=dict(time=[t.numerator,t.denominator],packing=mask,objective=target,proof_path=str(proof.relative_to(ROOT)),formula_path=str(formula.relative_to(ROOT)),proof_sha256=hashfile(proof),formula_sha256=hashfile(formula),bytes=proof.stat().st_size,formula_bytes=formula.stat().st_size,states=[int(x) for x in p.stdout.split()],checker_stdout=o.stdout)
 return r

def scip_model(row,reopt=False,limited=False):
 m=Model();m.hideOutput();m.setParam('limits/time',5);m.setParam('limits/nodes',100000);m.setParam('randomization/randomseedshift',0)
 if reopt:m.enableReoptimization()
 if limited:m.setPresolve(SCIP_PARAMSETTING.OFF);m.setHeuristics(SCIP_PARAMSETTING.OFF)
 xs=[m.addVar('x'+str(j),vtype='B') for j in range(row['n'])];m.addCons(quicksum(w*x for w,x in zip(row['weights'],xs))<=row['capacity']);return m,xs
def extract(m,xs,row,t):
 if m.getNSols()==0:return 0
 sol=m.getBestSol();mask=sum(1<<j for j,x in enumerate(xs) if m.getSolVal(sol,x)>.5)
 assert shared.value(row['weights'],mask)<=row['capacity'];return mask
def scip_sequence(row,reopt=False):
 start=meter();records=[];claims=[];proposals=[];m=xs=None
 for i,t in enumerate(row['observations']):
  q=qvalues(row,t);ss=meter()
  if m is None or not reopt:
   m,xs=scip_model(row,reopt);m.setObjective(quicksum(p*x for p,x in zip(q,xs)),'maximize')
  else:m.freeReoptSolve();m.chgReoptObjective(quicksum(p*x for p,x in zip(q,xs)),sense='maximize')
  m.optimize();mask=extract(m,xs,row,t);solvecost=elapsed(ss)
  # Independent exact bound production still does native work; it is fully charged.
  r=certificates.produce(row,t);assert shared.value(q,mask)==r['objective'];records.append(r)
  claims.append(dict(time=t,packing=mask));proposals.append(dict(status=str(m.getStatus()),packing=mask,**solvecost))
 return dict(status='complete',method='scip_reopt' if reopt else 'scip_cold',records=records,claims=claims,proposals=proposals,certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),**elapsed(start))
