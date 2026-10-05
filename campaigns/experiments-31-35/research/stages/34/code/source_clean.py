"""Native exact optimizer with bounded construction, unconditional disposal, separate audit."""
import time
import flat_baseline as F
import proof_slack_experiment as P
from engine import Cap,LIMITS

def solve(w,p,c):
 store=F.Store();ar=F.Arena(store);gen=P.SOLVERS['slack_branch'](w,p,c,0,None,None,'flat_share',ar);steps=0;start=time.process_time();wall=time.perf_counter();root=None
 try:
  while True:
   if steps%128==0:
    if steps>=LIMITS['source_steps'] or len(store.cells)>LIMITS['source_cells'] or time.perf_counter()-wall>LIMITS['source_seconds']:raise Cap('source construction cap')
   steps+=1
   try:next(gen)
   except StopIteration as done:best,chosen,root=done.value;break
  gen.close();_,clean=F.run_to_completion(ar.cleanup(root));proof=root.fields();_,dispose=F.run_to_completion(root.release());store.empty()
  if len(proof)>LIMITS['cells']:raise Cap('source returned cell cap')
  return dict(objective=best,packing=chosen,proof=proof,construction_steps=steps,cleanup_steps=clean,disposal_steps=dispose,algorithm_cpu=time.process_time()-start,wall=time.perf_counter()-wall,stats=store.stats,empty=True)
 except BaseException:
  gen.close();F.run_to_completion(ar.cleanup())
  if root and root.ids:F.run_to_completion(root.release())
  store.empty();raise
