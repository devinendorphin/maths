"""Fresh 48-update mixed streams: two full capacity/need/floor/shortage cycles."""
import copy
import random
from checker import digest
from predecessor_suite import model


def stream(n,family,seed):
    base=model(n,family,seed);m=copy.deepcopy(base);rng=random.Random(seed+65537);updates=[]
    for step in range(1,49):
        phase=(step-1)%24+1;new=copy.deepcopy(m);kind='cost'
        if phase in (3,9):new['edges'][0 if phase==3 else 1]['u']=1;kind='capacity-reduction'
        elif phase in (5,11):
            a,z=(0,n//2) if family=='transport' else (0,1)
            new['b'][a]+=2;new['b'][z]-=2;kind='balanced-needs'
        elif phase in (7,13):new['edges'][2 if phase==7 else 3]['l']=1;kind='lower-bound'
        elif phase==15:new['b'][0]+=10000;new['b'][1]-=10000;kind='forced-shortage'
        elif phase==17:new['b'][0]-=10000;new['b'][1]+=10000;kind='restore-needs'
        elif phase==19:
            for e in new['edges'][:4]:e['u']=14
            kind='capacity-increase'
        elif phase==21:
            for e in new['edges'][:4]:e['l']=0
            kind='restore-lower'
        else:
            for i in rng.sample(range(len(m['edges'])),4):new['edges'][i]['c']+=rng.choice([-4,-2,2,4])
        changes=[{'edge':i,'field':field,'old':e[field],'new':new['edges'][i][field]}
                 for i,e in enumerate(m['edges']) for field in ('l','u','c') if e[field]!=new['edges'][i][field]]
        balances=[{'node':v,'old':old,'new':new['b'][v]} for v,old in enumerate(m['b']) if old!=new['b'][v]]
        assert changes or balances
        updates.append({'kind':kind,'message':{'version':step-1,'old_model':digest(m),'edges':changes,'balances':balances}});m=new
    return {'model':base,'family':family,'updates':updates}


def make():
    return {'heldout':[stream(n,f,152000+n+(1000 if f=='cyclic' else 0)) for f in ('transport','cyclic') for n in (32,64,128)],
            'development':[stream(n,f,915152+n+(1000 if f=='cyclic' else 0)) for f in ('transport','cyclic') for n in (6,10,20)]}
