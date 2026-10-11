"""Fresh larger cost streams and three explicitly mixed changing-model streams."""
import copy
from checker import digest
from predecessor_suite import model
from recovery_suite import stream


def entry(size,dense,seed,mixed=False,steps=24):
    base=model(size,dense,seed);base['id']='larger-'+base['id'];m=copy.deepcopy(base)
    costs=stream(base,seed+171,steps);updates=[]
    for step,changes in enumerate(costs,1):
        old=digest(m)
        if mixed and step in (6,12,18,20):
            if step==6:
                for e in m['edges']:
                    if e['a']==0 and e['z']==size:e['u']=1
                kind='capacity'
            elif step==12:
                m['b'][1]+=1;m['b'][size+1]-=1;kind='needs'
            elif step==18:
                for e in m['edges']:
                    if e['a']==0:e['u']=0
                kind='shortage'
            else:
                for e in m['edges']:
                    if e['a']==0:e['u']=3
                kind='restore-capacity'
            updates.append({'kind':kind,'old_model':old,'model':copy.deepcopy(m)})
        else:
            # Some scheduled cost steps are replaced by mixed changes, so rebuild old.
            changes=copy.deepcopy(changes)
            for z in changes:z['old']=m['edges'][z['edge']]['c'];m['edges'][z['edge']]['c']=z['new']
            updates.append({'kind':'cost','old_model':old,'changes':changes})
    return {'model':base,'updates':updates,'mixed':mixed}


def make():
    held=[entry(n,d,145000+n+int(d)*1000) for d in (False,True) for n in (16,64,128)]
    held += [entry(n,False,146000+n,True) for n in (8,24,64)]
    return {'heldout':held,'development':entry(6,False,915145,True)}
