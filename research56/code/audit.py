"""Independent MITM enumeration / immutable-layer DP; no policy imports."""
from bisect import bisect_right
from collections import Counter
from fractions import Fraction
import math
import time
from shared import value,digest


class Auditor:
    def __init__(self,row):
        self.row=row;self.cache={};self.checks=0;self.sparse_work={}
        n=row['n'];c=row['capacity']
        self.halves=None
        if n<=24:
            halves=[]
            for start,stop in ((0,n//2),(n//2,n)):
                entries=[(0,0,0,0)]
                for j in range(start,stop):
                    additions=[(w+row['weights'][j],p+row['profits'][j],s+row['slopes'][j],m|1<<j)
                               for w,p,s,m in entries if w+row['weights'][j]<=c]
                    entries+=additions
                halves.append(sorted(entries))
            self.halves=halves;self.right_weights=[x[0] for x in halves[1]]
        else:assert c<=4096,'Large-n audit requires a bounded dense capacity'

    def optimum(self,t,side=1):
        t=Fraction(t);key=(t,side)
        if key in self.cache:return self.cache[key]
        row=self.row;a,b=t.numerator,t.denominator
        if self.halves is not None:
            left,right=self.halves;prefix=[];best=None
            for w,p,s,m in right:
                score=(b*p+a*s,side*s,-m)
                if best is None or score>best:best=score
                prefix.append(best)
            result=None
            for w,p,s,m in left:
                index=bisect_right(self.right_weights,row['capacity']-w)-1
                if index<0:continue
                rhs=prefix[index];candidate=(b*p+a*s+rhs[0],side*s+rhs[1],-m+rhs[2])
                if result is None or candidate>result:result=candidate
        else:
            # New immutable layer for each item, exact occupied weights.
            states={0:(0,0,0)}
            for j in range(row['n']):
                layer={}
                for occupied,score in states.items():
                    choices=[(occupied,score)]
                    target=occupied+row['weights'][j]
                    if target<=row['capacity']:
                        choices.append((target,(score[0]+b*row['profits'][j]+a*row['slopes'][j],
                                                score[1]+side*row['slopes'][j],score[2]-(1<<j))))
                    for weight,option in choices:
                        if weight not in layer or option>layer[weight]:layer[weight]=option
                states=layer
            result=max(states.values())
        self.cache[key]=result;return result

    def check_query(self,q):
        assert q['complete'];t=Fraction(*q['time']);mask=q['packing'];row=self.row
        assert value(row['weights'],mask)<=row['capacity']
        expected=self.optimum(t,q['side'])
        assert (q['scaled_objective'],q['side']*q['slope'],-mask)==expected
        assert q['intercept']==value(row['profits'],mask) and q['slope']==value(row['slopes'],mask)
        features=q['normalization']
        if features['gcd_terms']:
            assert features['gcd']==math.gcd(*row['weights']) and features['gcd_terms']==row['n']
        else:assert features['gcd']==1
        self.checks+=1

    def check(self,r):
        before=time.process_time();integer=0;rational=0;row=self.row
        previous_domains=None
        for q in r['queries']:
            self.check_query(q);rational+=1;g=q['normalization']['gcd'];w=[x//g for x in row['weights']];c=row['capacity']//g
            if q['kernel']=='dense':assert q['counts']['transitions']==sum(max(0,c-wi+1) for wi in w)
            elif q['kernel']=='sparse':
                if g not in self.sparse_work:
                    weights={0};work=0;peak=1
                    for wi in w:
                        work+=len(weights);weights=weights|{x+wi for x in weights if x+wi<=c};peak=max(peak,len(weights))
                    self.sparse_work[g]=(work,peak)
                assert (q['counts']['transitions'],q['counts']['states_peak'])==self.sparse_work[g]
            else:
                initial=previous_domains if q['retained_start'] else [[0,(1<<row['n'])-1,c]]
                if q['retained_start']:assert digest(initial)==q['start_domains_hash']
                pending=Counter(tuple(x) for x in initial)
                for split in q['trace']:
                    domain=tuple(split['domain']);assert pending[domain]>0;pending[domain]-=1
                    pending.update(tuple(x) for x in split['children'])
                assert +pending==Counter(tuple(x) for x in q['domains'])
                assert q['counts']['nodes']==1+len(q['trace'])+len(q['domains'])
                t=Fraction(*q['time']);side=q['side'];positive=0
                for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])):
                    profit=t.denominator*p+t.numerator*v
                    if profit>0 or profit==0 and side*v>0:positive|=1<<j
                assert q['counts']['sorted_terms']==positive.bit_count()+sum((x['domain'][1]&positive).bit_count() for x in q['trace'])+sum((x[1]&positive).bit_count() for x in q['domains'])
                previous_domains=q['domains']
        for q in r['incomplete_attempts']:
            assert not q['complete'] and not q['active'];ct=q['counts']
            if q.get('reason')=='dp_transitions cap':assert ct['transitions'] in (1,1500000)
            if q.get('reason')=='bb_nodes cap':assert ct['nodes'] in (1,30000)
        if r['status']=='complete':assert len(r['packings'])==row['end']+1
        elif not r['kind'].startswith('warm_'):assert not r['packings'] and not r['intervals']
        for t,mask in enumerate(r['packings']):
            profit=value(row['profits'],mask)+t*value(row['slopes'],mask)
            assert value(row['weights'],mask)<=row['capacity'] and profit==self.optimum(t)[0]
            integer+=1
        for segment in r['intervals']:
            l=segment['left'];h=segment['right'];l=Fraction(*l) if isinstance(l,list) else Fraction(l);h=Fraction(*h) if isinstance(h,list) else Fraction(h)
            p,s,mask=segment['line'];assert p==value(row['profits'],mask) and s==value(row['slopes'],mask)
            assert 0<=l<=h<=row['end']
            for t in (l,h):
                assert t.denominator*p+t.numerator*s==self.optimum(t)[0];rational+=1
        for q in r['queries']:
            for split in q.get('trace',[]):
                f,u,res=split['domain'];j=split['pivot'];assert u>>j&1
                g=q['normalization']['gcd'];wi=row['weights'][j]//g;bit=1<<j
                expected=[[f,u^bit,res]]
                if wi<=res:expected.append([f|bit,u^bit,res-wi])
                assert split['children']==expected
        return dict(passed=True,complete=r['status']=='complete',integer_checks=integer,rational_checks=rational,
                    checker='MITM enumeration' if self.halves is not None else 'immutable exact-weight DP',audit_cpu=time.process_time()-before)
