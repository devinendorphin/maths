"""Fresh seeds, cost streams and a separate development model."""
import copy
import random
from predecessor_suite import model


def stream(m,seed,steps=48):
    rng=random.Random(seed);cur=copy.deepcopy(m);result=[];n=m['n']//2
    off=[i for i,e in enumerate(m['edges']) if e['a']+n!=e['z']]
    diag=[i for i,e in enumerate(m['edges']) if e['a']+n==e['z']]
    for step in range(steps):
        ids=rng.sample(off,min([1,4,8][step%3],len(off)))
        if step%8==7:ids[0]=diag[(step//8)%len(diag)]
        changes=[]
        for i in ids:
            old=cur['edges'][i]['c']
            new=(30 if old<10 else -5) if i in diag else old+1
            changes.append({'edge':i,'old':old,'new':new});cur['edges'][i]['c']=new
        result.append(changes)
    return result


def make():
    held=[]
    for dense in (False,True):
        for n in (8,24,64):
            seed=141000+n+int(dense)*1000;m=model(n,dense,seed)
            held.append({'model':m,'changes':stream(m,seed+63)})
    m=model(6,False,912141)
    return {'heldout':held,'development':{'model':m,'changes':stream(m,912145,16)},
            'policies':[{'budget':1024,'cadence':8},{'budget':8192,'cadence':8},{'budget':65536,'cadence':24}]}
