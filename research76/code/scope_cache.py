"""Model-scoped optimal bound cache; trusted checked proofs plus packing checks."""
from fractions import Fraction
from shared import digest,value
class BoundCache:
 def __init__(self):self.entries={}
 @staticmethod
 def key(row,t):return (digest([row['n'],row['weights'],row['capacity']]),digest([row['profits'],row['slopes']]),Fraction(t))
 def put(self,row,t,index,objective,accepted):
  key=self.key(row,t);self.entries[key]=dict(key=key,index=index,objective=objective,accepted=accepted)
 def get(self,row,t,packing=None):
  key=self.key(row,t);r=self.entries.get(key)
  if r is None or r['key']!=key or not r['accepted']:return None
  if packing is not None:
   if packing<0 or packing>=1<<row['n'] or value(row['weights'],packing)>row['capacity']:return None
   t=Fraction(t);objective=sum((t.denominator*p+t.numerator*v) for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])) if packing>>j&1)
   if objective!=r['objective']:return None
  return r['index']
