"""Owned admitted state, transactional cost deltas and bounded replay journal.

The caller supplies a COMPLETE delta from a trusted sequenced source. Hashes
detect edits/order mistakes; they do not authenticate the source or find omissions.
"""
import copy
import hashlib
import json
from checker import digest, encode, verify


class Refused(ValueError):
    pass


def chain(previous, event):
    return hashlib.sha256(previous.encode() + encode(event)).hexdigest()


class Captured:
    def __init__(self, model, proof, context, version=0, budget=4096):
        if not verify(model, proof, context) or proof['kind'] != 'optimal':
            raise Refused('initial admission')
        if type(version) is not int or version < 0 or type(budget) is not int or budget < 0:
            raise Refused('state contract')
        self._m, self._p = copy.deepcopy(model), copy.deepcopy(proof)
        self.context, self.version, self.budget = context, version, budget
        self._events, self.bytes = [], 0
        self._snapshot()

    def _snapshot(self):
        self.base = {'model': copy.deepcopy(self._m), 'proof': copy.deepcopy(self._p),
                     'context': self.context, 'version': self.version, 'budget': self.budget}
        self.head = hashlib.sha256(encode(self.base)).hexdigest()
        self._events, self.bytes = [], 0

    def patch(self, message):
        """Inspect just k edges. No full model encode/hash/copy on accepted path."""
        try:
            if set(message) != {'version', 'context', 'changes'}:
                raise Refused('message schema')
            if type(message['version']) is not int or message['version'] != self.version:
                raise Refused('stale version')
            if message['context'] != self.context:
                raise Refused('dependency context')
            changes = message['changes']
            if not isinstance(changes, list) or len(changes) > 4096:
                raise Refused('changes schema')
            seen, offset, checked = set(), 0, 0
            for z in changes:
                if set(z) != {'edge', 'old', 'new'} or any(type(v) is not int for v in z.values()):
                    raise Refused('integer cost changes only')
                i = z['edge']
                if i in seen or not 0 <= i < len(self._m['edges']):
                    raise Refused('duplicate/outside edge')
                seen.add(i)
                e, x = self._m['edges'][i], self._p['flow'][i]
                if z['old'] != e['c'] or abs(z['new']) > 1000000:
                    raise Refused('old value/domain')
                r = z['new'] + self._p['pi'][e['a']] - self._p['pi'][e['z']]
                checked += 1
                if (x < e['u'] and r < 0) or (x > e['l'] and r > 0):
                    return {'accepted': False, 'edge_checks': checked, 'reason': 'residual sign'}
                offset += (z['new'] - e['c']) * x
            event = {'message': copy.deepcopy(message), 'cost_units': self._p['cost_units'] + offset}
            new_head = chain(self.head, event)
            record = dict(event, previous=self.head, head=new_head)
            size = len(encode(record)) + 1
            # Commit occurs only after all validation and journal preparation.
            for z in changes:
                self._m['edges'][z['edge']]['c'] = z['new']
            self._p['cost_units'] += offset
            self.version += 1
            self.head = new_head
            compact = self.bytes + size > self.budget
            if compact:
                # Full recapture is deliberately visible and charged to caller.
                self._p['model'] = digest(self._m)
                if not verify(self._m, self._p, self.context):
                    raise RuntimeError('internal recapture failure')
                self._snapshot()
            else:
                self._events.append(record)
                self.bytes += size
            return {'accepted': True, 'edge_checks': checked, 'record': record,
                    'compacted': compact, 'journal_bytes': self.bytes, 'head': self.head}
        except (KeyError, TypeError, AttributeError) as error:
            raise Refused('malformed message') from error

    def export(self):
        """Explicit O(V+E) output, outside the sparse patch interface."""
        m, p = copy.deepcopy(self._m), copy.deepcopy(self._p)
        p['model'] = digest(m)
        return m, p

    def checkpoint(self):
        return {'base': copy.deepcopy(self.base), 'events': copy.deepcopy(self._events),
                'head': self.head, 'version': self.version}

    @classmethod
    def restore(cls, bundle, context, expected_anchor=None):
        try:
            if set(bundle) != {'base', 'events', 'head', 'version'}:
                raise Refused('checkpoint schema')
            if expected_anchor is not None and (bundle['version'], bundle['head']) != expected_anchor:
                raise Refused('trusted terminal anchor')
            b = bundle['base']
            if b['context'] != context:
                raise Refused('checkpoint context')
            state = cls(b['model'], b['proof'], context, b['version'], b['budget'])
            for event in bundle['events']:
                if event['previous'] != state.head or chain(state.head, {'message': event['message'], 'cost_units': event['cost_units']}) != event['head']:
                    raise Refused('journal chain')
                result = state.patch(event['message'])
                if not result['accepted'] or result['compacted'] or result['record'] != event:
                    raise Refused('journal replay')
            if state.head != bundle['head'] or state.version != bundle['version']:
                raise Refused('checkpoint head/version')
            m, p = state.export()
            if not verify(m, p, context):
                raise Refused('restored certificate')
            return state
        except (KeyError, TypeError, AttributeError) as error:
            raise Refused('malformed checkpoint') from error
