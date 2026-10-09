from collections import OrderedDict
import copy
from fractions import Fraction as Q
import gc
import json
from pathlib import Path
import re
import tracemalloc
import backend as B
import native as N
from memory import Sampler,reachable
from routes import pair

ROOT=Path(__file__).resolve().parents[1]


class BufferCache:
    def __init__(self,row,route,budget):
        self.row=copy.deepcopy(row);self.route=route;self.budget=budget;self.key=N.scope(row);self.epoch=B.epoch(route)
        self.items=OrderedDict();self.retained=0;self.evictions=0;self.blocked=False
    def switch(self,row=None,route=None):
        self.items.clear();self.retained=0
        try:self.key=N.scope(row or self.row)
        except ValueError:self.blocked=True;raise
        self.row=copy.deepcopy(row or self.row);self.route=route or self.route;self.epoch=B.epoch(self.route);self.blocked=False
    def get(self,t):
        if self.blocked:raise ValueError('unsupported model context')
        key=(self.key,self.epoch,Q(t))
        if key not in self.items:return None
        item=self.items.pop(key);self.items[key]=item;return item[0]
    def put(self,fact):
        proof=(ROOT/fact['proof']).read_bytes();formula=(ROOT/fact['formula']).read_bytes() if fact['producer']=='cp' else b''
        size=len(N.encode(fact))+len(proof)+len(formula)
        if size>self.budget:return False,size
        while self.retained+size>self.budget:
            _,(_,p,f,s)=self.items.popitem(last=False);self.retained-=s;self.evictions+=1
        self.items[(self.key,self.epoch,Q(*fact['time']))]=(copy.deepcopy(fact),proof,formula,size);self.retained+=size;return True,size


def memory_trial(row,route,budget):
    start=N.clock();facts=[];events=[];cache=BufferCache(row,route,budget);tracemalloc.start();gc.collect();baseline=tracemalloc.get_traced_memory()[0]
    session=B.Session('process') if route.startswith('cp-') else None
    with Sampler() as sampler:
        for t in [0,2,0,4,2,6,0]:
            fact=cache.get(t);hit=fact is not None;admitted=None;size=None
            if not hit:
                fact,_=B.produce(row,t,route,session);facts.append(dict(row=row,fact=fact));admitted,size=cache.put(fact)
            events.append(dict(time=pair(t),hit=hit,admitted=admitted,entry_payload_bytes=size,retained_payload_bytes=cache.retained,evictions=cache.evictions,entries=len(cache.items),packing=fact['packing'],objective=fact['objective']))
        measured=dict(reachable_cache_bytes=reachable(cache.items),retained_payload_bytes=cache.retained,serialized_fact_bytes=sum(len(N.encode(v[0])) for v in cache.items.values()),traced_scenario_above_baseline=tracemalloc.get_traced_memory()[0]-baseline,traced_scenario_peak=tracemalloc.get_traced_memory()[1])
        cache.items.clear();cache.retained=0;gc.collect();measured['reachable_after_clear']=reachable(cache.items)
    tracemalloc.stop()
    if session:session.close()
    measured.update(total=N.elapsed(start),process_tree=sampler.report())
    return dict(row=row,route=route,budget=budget,facts=facts,events=events),measured


def invalidation(row,route):
    start=N.clock();facts=[];events=[];cache=BufferCache(row,route,16777216)
    for change in ['capacity','weight','objective','domain','nonlinear','dependency']:
        cache.switch(row,route);session=B.Session('process') if route.startswith('cp-') else None
        old,_=B.produce(row,0,route,session);admitted,size=cache.put(old);assert admitted and len(cache.items)==1;facts.append(dict(row=row,fact=old))
        changed=copy.deepcopy(row);target=route
        if change=='capacity':changed['capacity']+=1
        if change=='weight':changed['weights'][0]+=1
        if change=='objective':changed['profits'][0]+=1
        if change=='domain':changed['domain']='continuous'
        if change=='nonlinear':changed['objective_class']='quadratic';changed['quadratic']=[1]*row['n']
        if change=='dependency':target='cp-fork' if route.startswith('cp-') else 'native-alt'
        rejected=False
        try:cache.switch(changed,target)
        except ValueError:rejected=True
        assert not cache.items and cache.retained==0
        fresh=None
        if not rejected:
            if session:session.close()
            session=B.Session('fork') if target=='cp-fork' else (B.Session('process') if target.startswith('cp-') else None)
            fresh,_=B.produce(changed,0,target,session);facts.append(dict(row=changed,fact=fresh));cache.put(fresh)
            assert fresh['model']==cache.key and fresh['epoch']==cache.epoch
        if session:session.close()
        events.append(dict(change=change,changed_row=changed,rejected=rejected,old_context=[old['model'],old['epoch']],new_context=[cache.key,cache.epoch],old_retained_bytes=size,old_entries_evicted=True,new_fact=fresh))
    return dict(row=row,route=route,events=events,facts=facts),dict(total=N.elapsed(start))


def fault_trial(row,route):
    start=N.clock();facts=[];events=[];session=B.Session('process') if route.startswith('cp-') else None
    basis,_=B.produce(row,0,route,session);facts.append(dict(row=row,fact=basis))
    for corruption in ['appended-bytes','malformed','false-bound']:
        f=copy.deepcopy(basis);original=(ROOT/basis['proof']).read_text();folder=ROOT/'evidence/faults'/N.sha(N.encode([N.scope(row),route,corruption]));folder.mkdir(parents=True,exist_ok=True);p=folder/('copy.veripb' if basis['producer']=='cp' else 'copy.vipr')
        if corruption=='appended-bytes':text=original+'\n'
        elif corruption=='malformed':text='INVALID\n'
        elif basis['producer']=='cp':
            m=re.search(r'conclusion BOUNDS (-?\d+) (-?\d+)',original);v=int(m[1])-1;text=original[:m.start()]+f'conclusion BOUNDS {v} {v}'+original[m.end():]
        else:
            lines=original.splitlines();last=lines[-1].split();last[2]=str(Q(last[2])-1);lines[-1]=' '.join(last);text='\n'.join(lines)+'\n'
        p.write_text(text);f['proof']=str(p.relative_to(ROOT));captured=basis['packing']
        accepted=B.refresh(row,f,session);assert not accepted
        renewed=f.copy();renewed['proof_sha256']=N.sha(p.read_bytes())
        checked_with_new_hash=B.refresh(row,renewed,session)
        assert checked_with_new_hash==(corruption=='appended-bytes')
        fallback,_=B.produce(row,0,route,session);facts.append(dict(row=row,fact=fallback))
        events.append(dict(corruption=corruption,immutable_captured_packing=captured,explicit_refresh_accepted=accepted,redeclared_hash_checker_accepted=checked_with_new_hash,copy_proof=f['proof'],fallback=fallback))
    if session:session.close()
    return dict(row=row,route=route,basis=basis,events=events,facts=facts),dict(total=N.elapsed(start))
