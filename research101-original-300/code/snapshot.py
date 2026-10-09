"""Admit exact endpoint facts once, then query immutable in-memory intervals."""
from dataclasses import dataclass
from fractions import Fraction as Q
from support import *
import witness as W

@dataclass(frozen=True)
class Snapshot:
 key: tuple
 epoch: tuple
 intervals: tuple
 def query(self,row,t,epoch):
  if identity(row)!=self.key or tuple(sorted(epoch.items()))!=self.epoch:raise ValueError('snapshot context changed')
  if row.get('feasible_type','constant')!='constant' or row.get('objective_type','affine')!='affine' or any(row.get('quadratic',[])):raise ValueError('snapshot model class')
  t=Q(t)
  interval=next((s for s in self.intervals if Q(*s[0])<=t<=Q(*s[1])),None)
  if interval is None:raise ValueError('outside admitted interval')
  mask=interval[2]
  if shared.value(row['weights'],mask)>row['capacity']:raise ValueError('candidate feasibility')
  return mask

def build(row,route='native'):
 curve=curves.run(row,'real','dense',True);assert curve['status']=='complete';cache={};records=[];blocks=[];epoch=dependencies()
 for part in curve['intervals']:
  a,b=Q(*part['left']),Q(*part['right']);mask=part['line'][2]
  for t in [a,b]:
   if t not in cache:
    if route=='cp':
     from external import cp_point
     rec=cp_point(row,t)
    else:rec=W.produce(row,t);assert W.valid(row,t,rec)
    cache[t]=rec;records.append(rec)
   q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
   assert shared.value(q,mask)==cache[t]['objective'] and shared.value(row['weights'],mask)<=row['capacity']
  blocks.append((tuple(part['left']),tuple(part['right']),mask))
 assert blocks and Q(*blocks[0][0])==0 and Q(*blocks[-1][1])==row['end']
 assert all(x[1]==y[0] for x,y in zip(blocks,blocks[1:]))
 return Snapshot(identity(row),tuple(sorted(epoch.items())),tuple(blocks)),records,curve

def run(row,repeat=False,route='native'):
 start=meter();snap,records,curve=build(row,route);epoch=dependencies();claims=[];validations=0
 for t in row['observations']:
  if repeat:
   part=next(p for p in snap.intervals if Q(*p[0])<=t<=Q(*p[1]))
   for time in [Q(*part[0]),Q(*part[1])]:
    rec=next(r for r in records if Q(*r['time'])==time);assert W.valid(row,time,rec);validations+=1
  claims.append(dict(time=t,packing=snap.query(row,t,epoch)))
 return dict(status='complete',records=records,claims=claims,curve=curve,intervals=snap.intervals,
  certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),repeat_validations=validations,
  captured_facts='fixed admitted model, endpoint bounds and candidate intervals; no disk read needed after admission',**elapsed(start))

def window(row,width):
 start=meter();cache={};blocks=[];records=[];claims=[];successful=0;failed=0
 def point(t):
  if t not in cache:cache[t]=W.produce(row,t);assert W.valid(row,t,cache[t]);records.append(cache[t])
  return cache[t]
 for time in row['observations']:
  t=Q(time);block=next((s for s in blocks if s[0]<=t<=s[1]),None)
  if block is None:
   r=point(t);mask=r['packing'];end=min(Q(row['end']),t+width)
   if end>t:
    endpoint=point(end);q=[end.denominator*p+end.numerator*v for p,v in zip(row['profits'],row['slopes'])]
    if shared.value(q,mask)==endpoint['objective']:blocks.append((t,end,mask));successful+=1
    else:failed+=1
  else:mask=block[2]
  claims.append(dict(time=time,packing=mask))
 return dict(status='complete',records=records,claims=claims,certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),
  successful_probes=successful,failed_probes=failed,intervals=[([a.numerator,a.denominator],[b.numerator,b.denominator],m) for a,b,m in blocks],**elapsed(start))

def lru(row,limit):
 from collections import OrderedDict
 start=meter();cache=OrderedDict();records=[];claims=[];hits=evictions=peak=0;epoch=dependencies()
 for t in row['observations']:
  key=Q(t)
  if key in cache:r=cache.pop(key);hits+=1
  else:r=W.produce(row,key);assert W.valid(row,key,r);records.append(r)
  # Store only immutable admitted facts, not mutable source diagnostics.
  cache[key]=(r if isinstance(r,tuple) else (r['packing'],r['objective'],r['proof_sha256']))
  mask=cache[key][0];claims.append(dict(time=t,packing=mask))
  if limit is not None and len(cache)>limit:cache.popitem(last=False);evictions+=1
  peak=max(peak,len(cache))
 return dict(status='complete',records=records,claims=claims,hits=hits,evictions=evictions,peak_entries=peak,
  certificates=len(records),certificate_bytes=sum(r['bytes'] for r in records),**elapsed(start))
