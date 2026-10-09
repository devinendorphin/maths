"""Independent original-model enumeration, certificate binding and cache-trace audit.

Imports no campaign, cache, adapter, native producer, or SCIP Python API.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import time
import collections
import os
import re
import statistics

ROOT=Path(__file__).resolve().parents[1]
CHECKER=ROOT/'dependencies/research86/dependencies/vipr/viprchk'
ORACLES={}; COUNTS={'answers':0,'proof_bindings':0,'valid_external':0,'false_external_rejected':0}


def optimum(row,t):
    t=Fraction(t);key=json.dumps([row['weights'],row['capacity'],row['profits'],row['slopes'],str(t)])
    if key not in ORACLES:
        q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
        weights=[0]*(1<<row['n']);profits=[0]*(1<<row['n']);best=0
        for mask in range(1,1<<row['n']):
            bit=mask&-mask;j=bit.bit_length()-1;old=mask^bit
            weights[mask]=weights[old]+row['weights'][j];profits[mask]=profits[old]+q[j]
            if weights[mask]<=row['capacity']:best=max(best,profits[mask])
        ORACLES[key]=best
    return ORACLES[key]


def answer(row,t,mask,objective):
    t=Fraction(t);assert type(mask)==int and 0<=mask<(1<<row['n'])
    assert sum(w for j,w in enumerate(row['weights']) if mask>>j&1)<=row['capacity']
    exact=sum((t.denominator*p+t.numerator*v) for j,(p,v) in enumerate(zip(row['profits'],row['slopes'])) if mask>>j&1)
    assert exact==objective==optimum(row,t);COUNTS['answers']+=1


def header_binding(path,row,t):
    """Check the original feasible set and positive objective normalization exactly."""
    text=path.read_text().split();pos=0
    def take():
        nonlocal pos
        result=text[pos];pos+=1;return result
    def expect(token):assert take()==token
    def vector():
        k=int(take());out={}
        for _ in range(k):
            j=int(take());v=Fraction(take());out[j]=out.get(j,Fraction(0))+v
        return {j:v for j,v in out.items() if v}
    expect('VER');assert take() in ['1.0','1.1'];expect('VAR');n=int(take());assert n==row['n'];names=[take() for _ in range(n)]
    # Native adapter uses x0 labels; native SCIP uses t_x0.
    def original(name):
        name=name.removeprefix('t_').removeprefix('x');return int(name)
    mapping={j:original(name) for j,name in enumerate(names)}
    assert set(mapping.values())==set(range(n))
    expect('INT');assert int(take())==n;assert set(int(take()) for _ in range(n))==set(range(n))
    expect('OBJ');sense=take();assert sense in ['max','min'];coef=vector();t=Fraction(t)
    q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
    sign=1 if sense=='max' else -1;ratios=[]
    for j in range(n):
        v=coef.get(j,0);wanted=sign*q[mapping[j]]
        if wanted:assert v!=0;ratios.append(Fraction(wanted,v))
        else:assert v==0
    scale=ratios[0] if ratios else Fraction(1)
    assert scale>0 and all(x==scale for x in ratios)
    expect('CON');m=int(take());take();assert m==2*n+1
    expected=[]
    for j in range(n):expected.extend([('G',Fraction(0),((j,Fraction(1)),)),('L',Fraction(1),((j,Fraction(1)),))])
    expected.append(('L',Fraction(row['capacity']),tuple((j,Fraction(row['weights'][j])) for j in range(n))))
    observed=[]
    for _ in range(m):
        take();relation=take();rhs=Fraction(take());v=vector();v={mapping[j]:x for j,x in v.items()}
        observed.append((relation,rhs,tuple(sorted(v.items()))))
    assert sorted(observed)==sorted(expected)
    expect('RTP');expect('range');lo=Fraction(take());hi=Fraction(take());assert lo==hi
    assert (lo*scale*sign)==optimum(row,t)
    COUNTS['proof_bindings']+=1
    return dict(objective_scale=[scale.numerator,scale.denominator],sense=sense)
