"""Compose cost/cut certificates into an exact discrete max-min certificate."""
import copy
from fractions import Fraction
from checker import digest, verify


def coverage_model(case,rate):
    m=copy.deepcopy(case['model']);m['id']=m['id']+'/coverage/'+str(rate)
    for r,d in enumerate(case['demands']):
        m['edges'][6+r]['l']=max(case['floors'][r],(rate.numerator*d+rate.denominator-1)//rate.denominator)
    return m


def admit(case,probes,selected,dependency):
    candidates=sorted({Fraction(i,d) for d in case['demands'] for i in range(d+1)},reverse=True)
    expected=candidates if selected is None else candidates[:candidates.index(Fraction(selected))+1]
    if len(probes)!=len(expected):return False
    for k,(r,rate) in enumerate(zip(probes,expected)):
        if r['coverage_candidate']!=str(rate):return False
        m=coverage_model(case,rate)
        if digest(r['model'])!=digest(m) or not verify(m,r['proof'],dependency):return False
        kind='optimal' if selected is not None and k==len(expected)-1 else 'cut'
        if r['proof']['kind']!=kind:return False
    return True
