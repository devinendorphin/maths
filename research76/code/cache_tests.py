"""Explicit invalidation and poisoned-metadata controls for a bound cache."""
from fractions import Fraction
from shared import ROOT,save,digest,value
from scope_cache import BoundCache

def run(row,proof,checker):
 r=proof['records'][0];t=Fraction(*r['time']);mask=r['packing'];bound=r['info']['scaled_objective'];cache=BoundCache();cache.put(row,t,0,bound,r['valid']);assert cache.get(row,t,mask)==0
 tests=[]
 def reject(label,changed,t2=t,packing=mask):
  accepted=cache.get(changed,t2,packing);assert accepted is None,label;tests.append(dict(label=label,rejected=True,context=digest([changed,t2.numerator,t2.denominator,packing])))
 for name,changed in [('capacity',dict(row,capacity=row['capacity']+1)),('weights',dict(row,weights=[row['weights'][0]+1]+row['weights'][1:])),('profits',dict(row,profits=[row['profits'][0]+1]+row['profits'][1:])),('slopes',dict(row,slopes=[row['slopes'][0]+1]+row['slopes'][1:])),('n',dict(row,n=row['n']+1))]:reject(name,changed)
 reject('time',row,t+1);reject('mask_negative',row,packing=-1);reject('mask_out_of_range',row,packing=1<<row['n']);reject('infeasible_packing',row,packing=(1<<row['n'])-1)
 bad=next(m for m in range(1<<row['n']) if value(row['weights'],m)<=row['capacity'] and value(row['profits'],m)*t.denominator+t.numerator*value(row['slopes'],m)!=bound)
 reject('suboptimal_packing',row,packing=bad)
 entry=cache.entries[cache.key(row,t)];entry['accepted']=False;reject('unchecked_entry',row);entry['accepted']=True
 entry['key']=('wrong','wrong',t);reject('mismatched_entry_metadata',row)
 cache.put(row,t,0,bound,True);assert cache.get(dict(row,case_id='alias-label'),t,mask)==0
 result=dict(case_id=row['case_id'],passed=True,accepted_same_model=2,rejected=len(tests),tests=tests,limitations='Explicit model/key/packing controls; no adversarial corruption of an accepted objective bound, formal verification, signed provenance or concurrent cache study.')
 save(ROOT/'evidence'/('cache-tests-'+row['case_id']+'.json.gz'),result);return result
