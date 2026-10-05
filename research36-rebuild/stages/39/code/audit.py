"""Independent recurrence, index, cover and objective checks. Audit-only oracles."""
from collections import defaultdict
from fractions import Fraction
import math
from pathlib import Path
import time
from common import ROOT, read, save, value
from audit_horizon import rational_horizon


def optimum(w,q,c):
    dp=[0]*(c+1)
    for weight,profit in zip(w,q):
        for r in range(c,weight-1,-1):
            candidate=dp[r-weight]+profit
            if candidate>dp[r]: dp[r]=candidate
    return dp[c]


def count_packings(w,c):
    counts=[0]*(c+1); counts[0]=1
    for wi in w:
        for r in range(c,wi-1,-1): counts[r]+=counts[r-wi]
    return sum(counts)


class Checker:
    def __init__(self,row):
        self.w,self.p,self.v,self.c=[row[k] for k in ('weights','profits','slopes','capacity')]
        self.n=len(self.w); self.cover_cache=set(); self.price_cache=set(); self.checks=defaultdict(int)
        self.deadline=time.perf_counter()+45

    def guard(self):
        if time.perf_counter()>self.deadline: raise TimeoutError('independent audit batch wall cap')

    def witness(self,j,row):
        W,S,P,M,_=row
        assert 0<=M<1<<j and W<=self.c
        assert (W,S,P)==(value(self.w,M),value(self.v,M),value(self.p,M))
        self.checks['predecessor_witnesses']+=1

    def layer(self,cert,j,partial=False):
        lay=cert['current'] if partial else cert['layers'][j]
        raw=lay['raw']; retained=lay['retained']; deletions=lay['deletions']
        assert len({(x[0],x[1]) for x in raw})==len(raw)
        if j==0:
            assert raw==[[0,0,0,0,None]] and retained==[0] and not deletions
            return
        prior=cert['layers'][j-1]; expected={}; cursor=cert.get('cursor') or {}
        for pos,i in enumerate(prior['retained']):
            a=prior['raw'][i]
            for include in (0,1):
                if partial and cursor.get('stage')=='recurrence' and (pos,include)>=(cursor['next_predecessor_position'],cursor['next_include']):
                    continue
                self.guard()
                W=a[0]+include*self.w[j-1]; S=a[1]+include*self.v[j-1]
                P=a[2]+include*self.p[j-1]; M=a[3]|((1<<(j-1)) if include else 0)
                if W>self.c: continue
                key=(W,S)
                if key not in expected or P>expected[key][2]: expected[key]=[W,S,P,M,[i,include]]
        assert raw==list(expected.values()), (j,len(raw),len(expected))
        for row in raw: self.witness(j,row)
        if partial and cursor.get('stage')=='recurrence': return
        if partial and cursor.get('stage')=='pre_sort': return
        method=cert['method']; a,b=cert['interval']
        order=sorted(range(len(raw)),key=lambda i:(raw[i][0],-(raw[i][2]+a*raw[i][1]),-(raw[i][2]+b*raw[i][1]),raw[i][1],raw[i][3])) if method in ('naive','indexed') else sorted(range(len(raw)),key=lambda i:(raw[i][1],raw[i][0],-raw[i][2],raw[i][3],i)) if method=='same' else list(range(len(raw)))
        assert lay['order']==order
        processed=order if not partial else order[:len(retained)+len(deletions)]
        got=set(retained)|{x for x,y in deletions}
        assert got==set(processed) and len(retained)+len(deletions)==len(got)
        assert not set(retained)&{x for x,y in deletions}
        survivors=[]; expected_deletions=[]; best_by_slope={}; witnesses=dict(deletions)
        # Independent descending-coordinate arrays are replayed and also checked
        # against an independently maintained prefix maximum map.
        index=lay['index']; coords=[]; tree=[]; prefix_by_coordinate={}
        if method=='indexed':
            coords=sorted({r[2]+a*r[1] for r in raw},reverse=True)
            assert index['coordinates']==coords
            tree=[None]*(len(coords)+1); ranks={x:i+1 for i,x in enumerate(coords)}
            assert len(index['queries'])>=len(processed)
        for pos,i in enumerate(processed):
            self.guard(); Y=raw[i]; dominator=None
            if method=='same':
                old=best_by_slope.get(Y[1])
                if old is not None and raw[old][2]>=Y[2]: dominator=old
                else: best_by_slope[Y[1]]=i
            elif method=='naive':
                for k in survivors:
                    X=raw[k]
                    if X[2]+a*X[1]>=Y[2]+a*Y[1] and X[2]+b*X[1]>=Y[2]+b*Y[1]:
                        dominator=k; break
            elif method=='indexed':
                rank=ranks[Y[2]+a*Y[1]]; q=rank; aggregates=[]
                while q:
                    if tree[q] is not None: aggregates.append(tree[q])
                    q-=q&-q
                result=max(aggregates,key=lambda z:z[:2]) if aggregates else None
                assert index['queries'][pos]==[i,rank,result]
                # Every visited Fenwick aggregate covers its declared coordinate range.
                q=rank
                while q:
                    candidates=[entry for rr,entry in prefix_by_coordinate.items() if q-(q&-q)<rr<=q]
                    assert tree[q]==(max(candidates,key=lambda z:z[:2]) if candidates else None)
                    q-=q&-q
                if result is not None and result[0]>=Y[2]+b*Y[1]: dominator=result[2]
                if dominator is None:
                    entry=[Y[2]+b*Y[1],-pos,i]; old=prefix_by_coordinate.get(rank)
                    if old is None or entry[:2]>old[:2]: prefix_by_coordinate[rank]=entry
                    q=rank
                    while q<len(tree):
                        if tree[q] is None or entry[:2]>tree[q][:2]: tree[q]=entry
                        q+=q&-q
                self.checks['index_queries_verified']+=1
            if dominator is None:
                survivors.append(i); assert i not in witnesses
            else:
                assert witnesses[i]==dominator and dominator in survivors
                X=raw[dominator]
                assert X[0]<=Y[0]
                if method=='same': assert X[1]==Y[1] and X[2]>=Y[2]
                else: assert X[2]+a*X[1]>=Y[2]+a*Y[1] and X[2]+b*X[1]>=Y[2]+b*Y[1]
                expected_deletions.append([i,dominator]); self.checks['deletions_verified']+=1
        assert survivors==retained and expected_deletions==deletions
        if method=='indexed' and not partial: assert index['tree']==tree and len(index['queries'])==len(order)
        self.checks['raw_rows_verified']+=len(raw)

    def terminal(self,cert):
        assert cert['complete'] and cert['cursor'] is None
        best={}; last=cert['layers'][-1]
        for i in last['retained']:
            W,S,P,M,_=last['raw'][i]
            if S not in best or P>best[S][0]: best[S]=[P,S,M]
        assert cert['lines']==list(best.values())
        envelope=cert['envelope']; starts=cert['envelope_starts']
        assert len(envelope)==len(starts) and starts[0] is None
        for i,line in enumerate(envelope):
            self.guard(); assert line in cert['lines']
            left=Fraction(*starts[i]) if i else None
            right=Fraction(*starts[i+1]) if i+1<len(starts) else None
            if i:
                old=envelope[i-1]; assert old[1]<line[1]
                assert left==Fraction(old[0]-line[0],line[1]-old[1])
                if i>1: assert Fraction(*starts[i-1])<left
            for P,S,M in cert['lines']:
                if left is None: assert S>=line[1]
                else: assert line[0]+left*line[1]>=P+left*S
                if right is None: assert S<=line[1]
                else: assert line[0]+right*line[1]>=P+right*S
        self.checks['terminal_groups']+=len(best)

    def cover(self,proof):
        key=tuple(tuple(x[:3]) for x in proof)
        if key in self.cover_cache: return
        total=0
        for i,(f,u,r,*_) in enumerate(proof):
            self.guard(); assert f&u==0 and (f|u)<1<<self.n
            assert r==self.c-value(self.w,f) and r>=0
            total+=count_packings([wi for j,wi in enumerate(self.w) if u>>j&1],r)
            for g,z,*_ in proof[:i]:
                # The common intersection is feasible iff the union of fixed
                # items is allowed by both domains and fits the capacity.
                if not f&~(g|z) and not g&~(f|u): assert value(self.w,f|g)>self.c
        assert total==count_packings(self.w,self.c)
        self.cover_cache.add(key); self.checks['covers']+=1

    def prices(self,proof,t,m):
        q=[P+t*S for P,S in zip(self.p,self.v)]; target=value(q,m)
        for cell in proof:
            f,u,r,a,b,z=cell; assert a>=0 and b>0
            assert z==b*value(q,f)+a*r+sum(max(0,b*q[j]-a*self.w[j]) for j in range(self.n) if u>>j&1)
            assert z//b<=target
        self.checks['scalar_cells']+=len(proof)

    def repair(self,e):
        t=e['time']; m=e['packing']; q=[P+t*S for P,S in zip(self.p,self.v)]; latest={}
        candidates_count=hinges=0
        for call in e['calls']:
            self.guard(); f,u,r=call['domain']
            assert f&u==0 and r==self.c-value(self.w,f)
            candidates=sorted({Fraction(0)}|{Fraction(q[j],self.w[j]) for j in range(self.n) if u>>j&1 and q[j]>0})
            assert call['candidates']==len(candidates) and 0<=call['evaluated']<=len(candidates)
            candidates_count+=call['evaluated']; hinges+=call['evaluated']*u.bit_count()
            if call['priced'] is None: continue
            assert call['evaluated']==len(candidates)
            scores=[]
            for price in candidates:
                a,b=price.numerator,price.denominator
                z=b*value(q,f)+a*r+sum(max(0,b*q[j]-a*self.w[j]) for j in range(self.n) if u>>j&1)
                scores.append((Fraction(z,b),price,z))
            _,price,z=min(scores)
            assert call['priced']==[f,u,r,price.numerator,price.denominator,z]
            latest[(f,u,r)]=call['priced']
        assert candidates_count==e['counters']['bound_evaluations']
        assert hinges==e['counters']['free_term_evaluations'] and len(e['calls'])==e['counters']['price_calls']
        result=e['result']
        for branch in result.get('trace',[]):
            f,u,r=branch['domain']; remaining=r; fractional=None
            items=sorted([j for j in range(self.n) if u>>j&1 and q[j]>0],key=lambda j:(-Fraction(q[j],self.w[j]),j))
            for j in items:
                if self.w[j]<=remaining: remaining-=self.w[j]
                elif remaining>0: fractional=j; break
                else: break
            assert branch['pivot']==fractional and fractional is not None
            bit=1<<fractional; children=[[f,u^bit,r]]
            if self.w[fractional]<=r: children.append([f|bit,u^bit,r-self.w[fractional]])
            assert branch['children']==children
        if result.get('incomplete'): return
        if result['success']:
            self.cover(result['proof']); self.prices(result['proof'],t,m)
        else:
            witness=result['witness']; assert value(self.w,witness)<=self.c and value(q,witness)>value(q,m)


def construction(path, row, cert, out):
    completed=read(out)['records'] if out.exists() else []
    done={x['key'] for x in completed}; checker=Checker(row)
    keys=[f'layer:{j}' for j in range(len(cert['layers']))]
    if cert.get('current'): keys.append('partial_current')
    if cert['complete']: keys.append('terminal')
    for key in keys:
        if key in done: continue
        checker.deadline=time.perf_counter()+45; start=time.process_time()
        if key=='terminal': checker.terminal(cert)
        elif key=='partial_current': checker.layer(cert,cert['current']['prefix'],partial=True)
        else: checker.layer(cert,int(key.split(':')[1]))
        completed.append(dict(key=key,cpu=time.process_time()-start,checks=dict(checker.checks)))
        save(out,dict(passed=False,records=completed,required=keys,pending=[k for k in keys if k not in {r['key'] for r in completed}]))
    assert set(keys)=={x['key'] for x in completed}
    save(out,dict(passed=True,records=completed,required=keys,pending=[]))


def path_audit(row,result,folder):
    folder=Path(folder); summary_file=folder/'Audit.json'
    if summary_file.exists() and read(summary_file).get('passed'): return read(summary_file)
    checker=Checker(row); start=time.process_time(); constructions=[]
    for i,record in enumerate(result['constructions']):
        cert=read(ROOT/record['record']['file']) if record['record'] else record['proof']
        af=folder/f'construction-audit-{i:03}.json'
        construction(folder,row,cert,af); constructions.append(read(af))
    # Scalar ranges are committed separately; completed ranges survive retries.
    for i,native in enumerate(result['native']):
        if native['status']!='complete': assert native['empty']; continue
        af=folder/f'native-audit-{i:03}.json'
        if af.exists(): continue
        checker.deadline=time.perf_counter()+45
        t=native['time']; q=[P+t*S for P,S in zip(checker.p,checker.v)]
        assert native['empty'] and value(checker.w,native['packing'])<=checker.c
        assert native['objective']==value(q,native['packing'])==optimum(checker.w,q,checker.c)
        checker.cover(native['proof']); checker.prices(native['proof'],t,native['packing'])
        save(af,dict(passed=True,time=t,objective=native['objective'],checks=dict(checker.checks)),immutable=True)
    for i,e in enumerate(result['events']):
        if e['kind'] not in ('scalar_expiry','fallback_reprice'): continue
        af=folder/f'event-audit-{i:04}.json'
        if af.exists(): continue
        checker.deadline=time.perf_counter()+45; checker.repair(e)
        save(af,dict(passed=True,event=i,checks=dict(checker.checks)),immutable=True)
    loaded={}
    for i,segment in enumerate(result['segments']):
        af=folder/f'segment-audit-{i:04}.json'
        if af.exists(): continue
        checker.deadline=time.perf_counter()+45; t=segment['anchor']; m=segment['packing']
        if segment['kind']=='scalar':
            checker.cover(segment['proof']); checker.prices(segment['proof'],t,m)
            shifted=[P+t*S for P,S in zip(checker.p,checker.v)]
            hs=[rational_horizon(cell,checker.w,shifted,checker.v,m) for cell in segment['proof']]
            assert hs==segment['certificate']['cell_horizons']
            assert segment['certificate']['first_failure']==min((h for h in hs if h is not None),default=None)
        elif segment['kind']=='normalized':
            assert checker.p==checker.v and segment['certificate']['factor']==dict(intercept=1,slope=1,interval=[0,None])
            checker.cover(segment['base_proof']); checker.prices(segment['base_proof'],0,m)
        else:
            ci=segment['construction']
            if ci not in loaded:
                record=result['constructions'][ci]; loaded[ci]=read(ROOT/record['record']['file']) if record['record'] else record['proof']
            cert=loaded[ci]; assert cert['complete']; a,b=cert['interval']
            assert a<=t and (b is None or segment['until']<=b)
            target=value(checker.p,m)+t*value(checker.v,m)
            assert max(P+t*S for P,S,M in cert['lines'])==target
            candidates=[t+(target-P-t*S)//(S-value(checker.v,m))+1 for P,S,M in cert['lines'] if S>value(checker.v,m)]
            assert segment['loss']==min(candidates,default=None)
        save(af,dict(passed=True,segment=i,checks=dict(checker.checks)),immutable=True)
    if result.get('gate'):
        features=result['gate']['features']; bounds=[]
        for j in range(checker.n+1):
            xs=checker.v[:j]; g=math.gcd(*[abs(x) for x in xs]) if xs else 0
            bins=1 if not g else 1+(sum(x for x in xs if x>0)-sum(x for x in xs if x<0))//g
            bounds.append((checker.c+1)*bins)
        assert bounds==features['prefix_bounds'] and sum(bounds)==features['E_bound'] and 2*sum(bounds[:-1])==features['T_bound']
    # Each integer-time objective is checked independently, including window joins.
    # Chunking allows saved range coverage to survive an interrupted audit.
    native=[x for x in result['native'] if x['status']=='complete']
    end=row['end'] if result['status']=='window_complete' else max(0,result['final_time']-1)
    for begin in range(0,end+1,64):
        af=folder/f'objective-audit-{begin:04}.json'
        if af.exists(): continue
        checker.deadline=time.perf_counter()+45; values=[]
        for t in range(begin,min(end+1,begin+64)):
            checker.guard(); m=next(x['packing'] for x in reversed(native) if x['time']<=t)
            q=[P+t*S for P,S in zip(checker.p,checker.v)]; target=optimum(checker.w,q,checker.c)
            assert target==value(q,m), (row['case_id'],result['policy'],t,target,value(q,m))
            for segment in result['segments']:
                if segment['kind']=='frontier' and segment['anchor']<=t<=segment['until']:
                    ci=segment['construction']
                    if ci not in loaded:
                        record=result['constructions'][ci]; loaded[ci]=read(ROOT/record['record']['file']) if record['record'] else record['proof']
                    assert max(P+t*S for P,S,M in loaded[ci]['lines'])==target
            values.append([t,target])
        save(af,dict(passed=True,range=[begin,min(end,begin+63)],values=values),immutable=True)
    assert abs(result['cpu_reconciliation_error'])<0.001
    expected_counts=defaultdict(int)
    for event in result['ledger']:
        assert 0<=event['time']<=row['end']
        for k,v in event['counters'].items():
            if not k.endswith('cpu') and isinstance(v,(int,float)):
                expected_counts[k]=max(expected_counts[k],v) if k.endswith('_peak') else expected_counts[k]+v
    assert all(expected_counts[k]==v for k,v in result['totals'].items())
    summary=dict(passed=True,policy=result['policy'],case_id=row['case_id'],constructions=len(constructions),
                 incomplete_constructions=sum(x['status']!='complete' for x in result['constructions']),
                 integer_time_checks=end+1,audit_cpu=time.process_time()-start,checks=dict(checker.checks),
                 coverage_files=sorted(p.name for p in folder.glob('*-audit-*.json')))
    save(summary_file,summary,immutable=True); return summary


def stream_domain(row,out):
    """Audit-only Gray-code traversal; no giant full-domain arrays or bitsets."""
    if out.exists(): return read(out)
    w,p,v,c=[row[k] for k in ('weights','profits','slopes','capacity')]
    W=P=S=0; previous=0; feasible=0; slopes=set(); weight_slopes=set(); counts_by_weight=defaultdict(int)
    batches=[]; last=0; start=time.process_time(); deadline=time.perf_counter()+45
    for k in range(1<<len(w)):
        if k:
            mask=k^(k>>1); bit=mask^previous; i=bit.bit_length()-1; sign=1 if mask&bit else -1
            W+=sign*w[i]; P+=sign*p[i]; S+=sign*v[i]; previous=mask
        if W<=c: feasible+=1; slopes.add(S); weight_slopes.add((W,S)); counts_by_weight[W]+=1
        if (k+1)%65536==0:
            assert time.perf_counter()<deadline
            batches.append([last,k]); last=k+1; deadline=time.perf_counter()+45
    if last<(1<<len(w)): batches.append([last,(1<<len(w))-1])
    result=dict(passed=True,feasible_packings=feasible,distinct_feasible_slopes=len(slopes),
                repeated_slope_collisions=feasible-len(slopes),distinct_weight_slope_states=len(weight_slopes),numerical_slope_span=sum(abs(x) for x in v),
                feasible_counts_by_weight=dict(counts_by_weight),audit_mask_ranges=batches,audit_cpu=time.process_time()-start)
    save(out,result,immutable=True); return result
