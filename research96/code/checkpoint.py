"""Small exhaustive branch-tree with certified partial bounds and safe resumption.

This is an intentionally simple reference mechanism, not a faster optimizer.
"""
from fractions import Fraction as Q
import time
from support import digest,model,dependencies

def setup(row,t):
 return dict(schema=1,model=digest(model(row)),time=[Q(t).numerator,Q(t).denominator],dependencies=dependencies(),
  todo=[[0,0]],processed=[],packing=0,nodes=0,status='incomplete')
def qvalues(row,t):return [Q(t).denominator*p+Q(t).numerator*v for p,v in zip(row['profits'],row['slopes'])]
def value(xs,m):return sum(v for j,v in enumerate(xs) if m>>j&1)
def replay(row,t,s,expected=None):
 if s['schema']!=1 or s['model']!=digest(model(row)) or s['time']!=[Q(t).numerator,Q(t).denominator] or s['dependencies']!=(expected if expected is not None else dependencies()):raise ValueError('checkpoint context')
 q=qvalues(row,t);todo=[[0,0]];best=0;packing=0
 for recorded in s['processed']:
  if not todo:raise ValueError('extra progress')
  depth,m=todo.pop()
  if recorded!=[depth,m]:raise ValueError('progress transcript')
  if value(row['weights'],m)>row['capacity']:continue
  if depth==row['n']:
   score=value(q,m)
   if score>best or score==best and m<packing:best=score;packing=m
  else:todo.extend([[depth+1,m|(1<<depth)],[depth+1,m]])
 if todo!=s['todo'] or packing!=s['packing'] or len(s['processed'])!=s['nodes']:raise ValueError('checkpoint state')
 upper=max([best]+[value(q,m)+sum(max(0,q[j]) for j in range(d,row['n'])) for d,m in todo if value(row['weights'],m)<=row['capacity']])
 return best,upper
def advance(row,t,s,budget,expected=None):
 replay(row,t,s,expected);q=qvalues(row,t);start=time.perf_counter()
 for _ in range(budget):
  if not s['todo']:break
  if s['nodes']>=8191 or time.perf_counter()-start>=10:break
  d,m=s['todo'].pop();s['processed'].append([d,m]);s['nodes']+=1
  if value(row['weights'],m)>row['capacity']:continue
  if d==row['n']:
   score=value(q,m);best=value(q,s['packing'])
   if score>best or score==best and m<s['packing']:s['packing']=m
  else:s['todo'].extend([[d+1,m|(1<<d)],[d+1,m]])
 lo,hi=replay(row,t,s,expected)
 s['lower']=lo;s['upper']=hi;s['gap']=hi-lo
 s['status']='optimal' if hi==lo else 'bounded-gap' if s['processed'] else 'incomplete'
 return s
