"""Same native optimizer, full guarded costs including aborted construction."""
import time
import flat_baseline as F
import proof_slack_experiment as P
import engine as E
class SourceCap(E.Cap):
 def __init__(self,reason,cost):super().__init__(reason);self.cost=cost
def solve(w,p,c,deadline=None,max_steps=500000):
 start=time.process_time();wall=time.perf_counter();store=F.Store();ar=F.Arena(store);gen=P.SOLVERS['slack_branch'](w,p,c,0,None,None,'flat_share',ar);steps=0;root=None;clean=dispose=0;reason=None
 try:
  while True:
   if steps>=min(max_steps,500000) or len(store.cells)>4096 or time.perf_counter()-wall>=30 or deadline is not None and time.perf_counter()>=deadline:raise E.Cap('source construction cap')
   steps+=1
   try:next(gen)
   except StopIteration as done:best,chosen,root=done.value;break
  gen.close();_,clean=F.run_to_completion(ar.cleanup(root));proof=root.fields();_,dispose=F.run_to_completion(root.release());store.empty()
  if len(proof)>4096:raise E.Cap('source returned cell cap')
  return dict(objective=best,packing=chosen,proof=proof,construction_steps=steps,cleanup_steps=clean,disposal_steps=dispose,algorithm_cpu=time.process_time()-start,wall=time.perf_counter()-wall,stats=store.stats,empty=True)
 except BaseException as exc:
  gen.close();_,clean=F.run_to_completion(ar.cleanup())
  if root and root.ids:_,dispose=F.run_to_completion(root.release())
  store.empty();cost=dict(construction_steps=steps,cleanup_steps=clean,disposal_steps=dispose,algorithm_cpu=time.process_time()-start,wall=time.perf_counter()-wall,stats=store.stats,empty=True)
  if isinstance(exc,E.Cap):raise SourceCap(str(exc),cost)
  raise
