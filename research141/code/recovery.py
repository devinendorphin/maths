"""Shared immutable base, checkpoint images and checked proof-change events."""
import copy
import hashlib
from checker import digest, encode, verify
from delta import Captured, Refused


def hashed(previous,payload):return hashlib.sha256(previous.encode()+encode(payload)).hexdigest()


def proof_change(old,new):
    return {'model':new['model'],'dependency':new['dependency'],'kind':'optimal',
            'cost_units':new['cost_units'],
            'flow':[[i,v] for i,v in enumerate(new['flow']) if v!=old['flow'][i]],
            'pi':[[i,v] for i,v in enumerate(new['pi']) if v!=old['pi'][i]]}


def apply_proof(old,difference):
    if set(difference)!= {'model','dependency','kind','cost_units','flow','pi'} or difference['kind']!='optimal':
        raise Refused('proof change schema')
    p=copy.deepcopy(old)
    for field in ('model','dependency','kind','cost_units'):p[field]=difference[field]
    for field in ('flow','pi'):
        seen=set()
        for i,v in difference[field]:
            if type(i) is not int or type(v) is not int or i in seen or not 0<=i<len(p[field]):
                raise Refused('proof change indices')
            seen.add(i);p[field][i]=v
    return p


def image(base,m,p,version,head,fmt,context):
    if not verify(m,p,context):raise Refused('snapshot certificate')
    result={'base':digest(base),'version':version,'head':head,'context':context,'format':fmt,'proof':p}
    if fmt=='compact':result['costs']=[e['c'] for e in m['edges']]
    elif fmt=='full':result['model']=m
    else:raise Refused('snapshot format')
    return result


def replay(base,snapshot,events,context,anchor):
    """Recover a concrete exact proof, checking every retained event."""
    try:
        if snapshot['base']!=digest(base) or snapshot['context']!=context:
            raise Refused('base/context')
        if type(snapshot['version']) is not int or snapshot['version']<0:
            raise Refused('version')
        if snapshot['format']=='compact':
            m=copy.deepcopy(base)
            if len(snapshot['costs'])!=len(m['edges']):raise Refused('cost vector')
            for e,c in zip(m['edges'],snapshot['costs']):e['c']=c
        elif snapshot['format']=='full':
            m=copy.deepcopy(snapshot['model'])
            fixed=copy.deepcopy(m)
            for a,b in zip(fixed['edges'],base['edges']):a['c']=b['c']
            if fixed!=base:raise Refused('fixed model')
        else:raise Refused('format')
        p=copy.deepcopy(snapshot['proof']);version=snapshot['version'];head=snapshot['head']
        if not verify(m,p,context):raise Refused('base certificate')
        state=Captured(m,p,context,version,10**9)
        for event in events:
            payload=event['payload']
            if event['previous']!=head or hashed(head,payload)!=event['head']:
                raise Refused('event chain')
            msg=payload['message']
            if set(msg)!= {'version','context','changes'} or type(msg['version']) is not int or msg['version']!=version or msg['context']!=context or not isinstance(msg['changes'],list):raise Refused('message scope')
            if payload['action']=='patch':
                decision=state.patch(msg)
                if not decision['accepted']:raise Refused('patch proof')
                m,p=state.export()
            elif payload['action']=='recertify':
                m,previous=state.export()
                seen=set()
                for z in msg['changes']:
                    if set(z)!= {'edge','old','new'} or any(type(v) is not int for v in z.values()):raise Refused('cost change schema')
                    i=z['edge']
                    if type(i) is not int or i in seen or not 0<=i<len(m['edges']):raise Refused('recert edge')
                    seen.add(i)
                    if m['edges'][i]['c']!=z['old'] or type(z['new']) is not int:raise Refused('old/new cost')
                    m['edges'][i]['c']=z['new']
                if 'difference' in payload:p=apply_proof(previous,payload['difference'])
                else:
                    if payload['model']!=m:raise Refused('recert model')
                    p=copy.deepcopy(payload['proof'])
                if not verify(m,p,context):raise Refused('recert certificate')
                state=Captured(m,p,context,version+1,10**9)
            else:raise Refused('action')
            if p['cost_units']!=payload['cost_units']:raise Refused('value')
            version+=1;head=event['head']
        if (version,head)!=tuple(anchor):raise Refused('terminal anchor')
        m,p=state.export()
        if not verify(m,p,context):raise Refused('terminal certificate')
        return m,p
    except (KeyError,TypeError,IndexError,ValueError) as error:
        if isinstance(error,Refused):raise
        raise Refused('malformed recovery') from error
