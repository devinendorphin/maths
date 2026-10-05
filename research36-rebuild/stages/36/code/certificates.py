"""Algorithm-side complete sparse proofs. No audit or prior-result imports."""
from collections import defaultdict
import math
import time
from common import E, OLD, counters, value, LIMITS


class BuildCap(E.Cap):
    def __init__(self, reason, partial):
        super().__init__(reason); self.partial = partial


def gate(w, p, v, c, ct):
    L = U = g = 0; bounds = [c+1]
    for x in v:
        ct['recognition'] += 1; ct['gcd_operations'] += 1; ct['gate_arithmetic'] += 4
        L += min(0, x); U += max(0, x); g = math.gcd(g, abs(x))
        bounds.append((c+1) * (1 if not g else 1+(U-L)//g))
    ct['gate_arithmetic'] += len(bounds)*2
    return dict(prefix_bounds=bounds, E_bound=sum(bounds), T_bound=2*sum(bounds[:-1]),
                final_lower=L, final_upper=U, final_gcd=g)


def build(w, p, v, c, method, interval, deadline, prior, caps=None):
    caps = dict(LIMITS, **(caps or {})); ct = counters()
    layers = [dict(raw=[[0,0,0,0,None]], retained=[0], deletions=[], order=[0], index=None)]
    ct['dp_entries'] = 1; ct['proof_peak'] = 1
    cert = dict(format='sparse-proof-v2', method=method,
                interval=list(interval) if method in ('naive','indexed') else [0,None],
                layers=layers, complete=False, cursor={})
    cursor = cert['cursor']; aux_retained = 1

    def guard(extra=0):
        reason = None
        checks = [('dp_entries','entries','cumulative_entries'),
                  ('dp_transitions','transitions','cumulative_transitions'),
                  ('dominance_comparisons','dominance','cumulative_dominance')]
        for k, per, cumulative in checks:
            if ct[k] > caps[per] or ct[k] + prior.get(k,0) > caps.get(cumulative, caps[per]):
                reason = per+' cap'; break
        visits = ct['index_visits'] + ct['index_updates']
        if visits > caps['index'] or visits + prior.get('index_visits',0)+prior.get('index_updates',0) > caps.get('cumulative_index',caps['index']):
            reason = 'index visit cap'
        if aux_retained + extra > caps['auxiliary']:
            reason = 'auxiliary record cap'
        ct['auxiliary_peak'] = max(ct['auxiliary_peak'], aux_retained+extra)
        ct['proof_peak'] = max(ct['proof_peak'], ct['dp_entries'])
        if time.perf_counter() >= deadline:
            reason = 'algorithm wall cap'
        if reason:
            raise BuildCap(reason, cert)

    # Reserve before a new proof row, transition or auxiliary allocation.
    def reserve(k, n=1):
        per = {'dp_entries':'entries','dp_transitions':'transitions',
               'dominance_comparisons':'dominance','index_visits':'index','index_updates':'index'}[k]
        if ct[k]+n > caps[per]:
            raise BuildCap(per+' cap', cert)
        cumulative = {'dp_entries':'cumulative_entries','dp_transitions':'cumulative_transitions',
                      'dominance_comparisons':'cumulative_dominance'}
        if k in cumulative and prior.get(k,0)+ct[k]+n > caps.get(cumulative[k],caps[per]):
            raise BuildCap(cumulative[k]+' cap', cert)
        if k.startswith('index_') and ct['index_visits']+ct['index_updates']+n > caps['index']:
            raise BuildCap('index visit cap',cert)
        if k.startswith('index_') and prior.get('index_visits',0)+prior.get('index_updates',0)+ct['index_visits']+ct['index_updates']+n > caps.get('cumulative_index',caps['index']):
            raise BuildCap('cumulative index visit cap',cert)
        ct[k] += n

    try:
        guard()
        for j, (wi,pi,vi) in enumerate(zip(w,p,v),1):
            prev = layers[-1]; data = {}; cert['current'] = dict(prefix=j, raw=[], retained=[], deletions=[], order=[], index=None)
            for pos, ident in enumerate(prev['retained']):
                W,S,P,M,_ = prev['raw'][ident]
                for inc in (0,1):
                    cursor.update(stage='recurrence',prefix=j,next_predecessor_position=pos,next_include=inc)
                    guard(len(data)); reserve('dp_transitions')
                    WW,SS,PP,MM = (W+wi,S+vi,P+pi,M|1<<(j-1)) if inc else (W,S,P,M)
                    if WW > c: continue
                    key=(WW,SS)
                    if key not in data:
                        reserve('dp_entries'); data[key]=[WW,SS,PP,MM,[ident,inc]]; ct['backpointer_work']+=1
                    elif PP > data[key][2]:
                        data[key]=[WW,SS,PP,MM,[ident,inc]]; ct['backpointer_work']+=1
                cert['current']['raw'] = list(data.values()) if pos == len(prev['retained'])-1 else []
            raw=list(data.values()); current=cert['current']; current['raw']=raw
            del data
            cursor.update(stage='pre_sort',prefix=j,next_predecessor_position=len(prev['retained']),next_include=0)
            # One order record per raw row, plus sorter keys/scratch, bounded prospectively.
            guard(3*len(raw))
            a,b=interval
            if method in ('naive','indexed'):
                order=OLD.ordered(list(range(len(raw))),lambda i:(raw[i][0],-(raw[i][2]+a*raw[i][1]),-(raw[i][2]+b*raw[i][1]),raw[i][1],raw[i][3]),ct)
            elif method=='same':
                order=OLD.ordered(list(range(len(raw))),lambda i:(raw[i][1],raw[i][0],-raw[i][2],raw[i][3],i),ct)
            else:
                order=list(range(len(raw)))
            current['order']=order; retained=current['retained']; deletions=current['deletions']
            best={}; coords=[]; ranks={}; tree=[]; queries=[]
            if method=='indexed':
                guard(5*len(raw))
                endpoint_values=[r[2]+a*r[1] for r in raw]; ct['compression_work']+=len(raw)
                coords=OLD.ordered(list(set(endpoint_values)),lambda x:-x,ct)
                ranks={x:i+1 for i,x in enumerate(coords)}; tree=[None]*(len(coords)+1)
                ct['compression_work']+=len(coords)*2
                current['index']=dict(coordinates=coords,tree=tree,queries=queries)
                del endpoint_values
            for position,i in enumerate(order):
                cursor.update(stage='pruning',prefix=j,candidate_position=position,candidate=i)
                guard(2+len(order)+len(retained)+len(deletions)+len(coords)*3+len(queries)+len(best))
                Y=raw[i]; dom=None
                if method=='same':
                    ct['same_slope_checks']+=1
                    old=best.get(Y[1])
                    if old is not None and raw[old][2]>=Y[2]:
                        dom=old
                    else:
                        best[Y[1]]=i
                elif method=='naive':
                    for dpos,k in enumerate(retained):
                        cursor.update(dominator_position=dpos); guard(len(order)+len(retained)+len(deletions)); reserve('dominance_comparisons')
                        X=raw[k]
                        if X[2]+a*X[1]>=Y[2]+a*Y[1] and X[2]+b*X[1]>=Y[2]+b*Y[1]:
                            dom=k; break
                elif method=='indexed':
                    rank=ranks[Y[2]+a*Y[1]]; q=rank; result=None; ct['index_queries']+=1
                    while q:
                        cursor.update(index_action='query',index_position=q,query_result=result,rank=rank); guard(len(order)+len(retained)+len(deletions)+len(coords)*3+len(queries)); reserve('index_visits')
                        candidate=tree[q]
                        if candidate is not None and (result is None or candidate[:2]>result[:2]):
                            result=candidate
                        q-=q&-q
                    if result is not None and result[0]>=Y[2]+b*Y[1]: dom=result[2]
                    queries.append([i,rank,None if result is None else list(result)])
                    if dom is None:
                        entry=[Y[2]+b*Y[1],-position,i]; q=rank
                        while q<len(tree):
                            cursor.update(index_action='update',index_position=q); guard(len(order)+len(retained)+len(deletions)+len(coords)*3+len(queries)); reserve('index_updates')
                            if tree[q] is None or entry[:2]>tree[q][:2]: tree[q]=entry
                            q+=q&-q
                if dom is None:
                    retained.append(i)
                else:
                    deletions.append([i,dom]); ct['dominance_deletions']+=1; ct['dominance_witness_work']+=1; ct['witness_records']+=1
            layer=dict(raw=raw,retained=retained,deletions=deletions,order=order,index=current['index'])
            layers.append(layer)
            aux_retained+=len(order)+len(retained)+len(deletions)+len(coords)+len(tree)+len(queries)
            del ranks,best
            del cert['current']; cursor.clear(); cursor.update(stage='layer_complete',prefix=j,next_prefix=j+1); guard()
        best={}
        cursor.update(stage='terminal',prefix=len(w),terminal_position=0)
        last=layers[-1]
        for pos,i in enumerate(last['retained']):
            cursor['terminal_position']=pos; guard(len(best))
            W,S,P,M,_=last['raw'][i]
            if S not in best or P>best[S][0]: best[S]=[P,S,M]
        lines=list(best.values()); ct['frontier_lines']+=len(lines)
        guard(3*len(lines)); cert['lines']=lines
        cert['envelope'],cert['envelope_starts']=OLD.hull(lines,ct)
        cert['complete']=True; cert['cursor']=None
        return cert,ct
    except BuildCap as exc:
        if 'current' in cert and cursor.get('stage')=='recurrence':
            cert['current']['raw']=list(data.values())
        exc.partial['reason']=str(exc); exc.partial['counters']=ct
        raise


def at(cert,t):
    a,b=cert['interval']
    if not cert['complete'] or t<a or b is not None and t>b:
        raise ValueError('incomplete or outside certificate interval')
    return max(P+t*S for P,S,M in cert['lines'])


def horizon(cert,p,v,m,t,ct):
    target=value(p,m)+t*value(v,m)
    ct['envelope_evaluations']+=len(cert['lines'])
    if at(cert,t)!=target: raise ValueError('incumbent not optimal at anchor')
    A=value(p,m); S=value(v,m); answer=None
    for P,s,M in cert['envelope']:
        ct['envelope_evaluations']+=1
        margin=A+t*S-P-t*s
        if s>S:
            candidate=(t+margin//(s-S)+1,M)
            if answer is None or candidate<answer: answer=candidate
    return answer if answer is not None else (None,None)
