"""Strict atomic fixed-topology updates. Model commits include infeasible states."""
import copy
from checker import digest, validate


class Rejected(ValueError):
    pass


class Transaction:
    def __init__(self, model, context):
        assert validate(model)
        self.model = copy.deepcopy(model)
        self.context = context
        self.version = 0

    def apply(self, message):
        try:
            if type(message) is not dict or set(message) != {'version', 'context', 'old_model', 'edges', 'balances'}:
                raise Rejected('message shape')
            if type(message['version']) is not int or message['version'] != self.version:
                raise Rejected('version')
            if message['context'] != self.context or message['old_model'] != digest(self.model):
                raise Rejected('binding')
            edges, balances = message['edges'], message['balances']
            if type(edges) is not list or type(balances) is not list or len(edges) > 32 or len(balances) > 256:
                raise Rejected('patch limits')
            if not edges and not balances:
                raise Rejected('empty patch')
            m = copy.deepcopy(self.model)
            seen = set()
            for change in edges:
                if type(change) is not dict or set(change) != {'edge', 'field', 'old', 'new'}:
                    raise Rejected('edge shape')
                i, field = change['edge'], change['field']
                if type(i) is not int or not 0 <= i < len(m['edges']) or type(field) is not str or field not in ('l', 'u', 'c'):
                    raise Rejected('edge identity')
                if (i, field) in seen or any(type(change[k]) is not int for k in ('old', 'new')):
                    raise Rejected('duplicate or noninteger')
                if self.model['edges'][i][field] != change['old'] or change['old'] == change['new']:
                    raise Rejected('old value or no change')
                seen.add((i, field)); m['edges'][i][field] = change['new']
            seen = set()
            for change in balances:
                if type(change) is not dict or set(change) != {'node', 'old', 'new'}:
                    raise Rejected('balance shape')
                v = change['node']
                if type(v) is not int or not 0 <= v < m['n'] or v in seen or any(type(change[k]) is not int for k in ('old', 'new')):
                    raise Rejected('balance identity')
                if self.model['b'][v] != change['old'] or change['old'] == change['new']:
                    raise Rejected('balance old value')
                seen.add(v); m['b'][v] = change['new']
            if not validate(m):
                raise Rejected('invalid candidate model')
        except (KeyError, TypeError, IndexError, AttributeError) as error:
            raise Rejected('malformed patch') from error
        # No caller-owned references are retained, and invalid messages never commit.
        self.model = m
        self.version += 1
        return copy.deepcopy(m)
