"""ctypes ownership and literal retained-state observations for the credited SDK."""
import ctypes as C
from pathlib import Path
from checker import validate

LIB=C.CDLL(str(Path(__file__).resolve().parents[1]/'bridge.so'))
I=C.c_int64;J=C.c_int;PI=C.POINTER(I);PJ=C.POINTER(J)
FIELDS=[C.c_int,C.c_int,PJ,PJ,PI,PI,PI,PI]
LIB.m152_create.argtypes=FIELDS;LIB.m152_create.restype=C.c_void_p
LIB.m152_patch.argtypes=[C.c_void_p,PI,PI,PI,PI];LIB.m152_patch.restype=C.c_int
LIB.m152_solve.argtypes=[C.c_void_p,PI];LIB.m152_solve.restype=C.c_int
LIB.m152_snapshot.argtypes=[C.c_void_p,PI,PI,PJ];LIB.m152_snapshot.restype=C.c_int
LIB.m152_destroy.argtypes=[C.c_void_p];LIB.m152_destroy.restype=None
LIB.m152_simple.argtypes=FIELDS+[PI];LIB.m152_simple.restype=C.c_int


def arrays(m):
    assert validate(m) and all(abs(b)<=1000000 for b in m['b'])
    es=m['edges'];n=m['n'];e=len(es)
    return [n,e,(J*e)(*(q['a'] for q in es)),(J*e)(*(q['z'] for q in es)),
            (I*e)(*(q['l'] for q in es)),(I*e)(*(q['u'] for q in es)),
            (I*e)(*(q['c'] for q in es)),(I*n)(*m['b'])]


class Native:
    def __init__(self,m):
        self.n,self.e=m['n'],len(m['edges']);self.topology=tuple((e['a'],e['z']) for e in m['edges'])
        self.h=LIB.m152_create(*arrays(m));assert self.h
    def close(self):
        if self.h:LIB.m152_destroy(self.h);self.h=None
    def patch(self,m):
        assert self.n==m['n'] and self.topology==tuple((e['a'],e['z']) for e in m['edges'])
        assert LIB.m152_patch(self.h,*arrays(m)[4:])==0
    def solve(self,witness):
        return LIB.m152_solve(self.h,(I*self.e)(*witness))
    def snapshot(self):
        y=(I*self.e)();excess=(I*self.n)();counts=(J*3)();assert LIB.m152_snapshot(self.h,y,excess,counts)==0
        return {'y':list(y),'excess':list(excess),'updates':counts[0],'solves':counts[1],'identity_stable':bool(counts[2])}


def simple(m):
    a=arrays(m);x=(I*len(m['edges']))();status=LIB.m152_simple(*a,x)
    if status==1:return None
    assert status==0,status
    return list(x)
