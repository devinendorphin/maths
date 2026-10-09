"""Standalone exact certificate admission. No optimizer/reference imports."""
import hashlib
import json


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(model):
    return hashlib.sha256(encode(model)).hexdigest()


def validate(m):
    def integer(x): return type(x) is int
    if not isinstance(m, dict) or set(m) != {'id', 'n', 'b', 'denominator', 'edges'}:
        return False
    if not isinstance(m['id'], str) or not integer(m['n']) or not 1 <= m['n'] <= 10:
        return False
    if not integer(m['denominator']) or m['denominator'] <= 0:
        return False
    if len(m['b']) != m['n'] or not all(integer(x) for x in m['b']) or sum(m['b']) != 0:
        return False
    if len(m['edges']) > 25:
        return False
    for e in m['edges']:
        if set(e) != {'a', 'z', 'l', 'u', 'c'} or not all(integer(x) for x in e.values()):
            return False
        if not 0 <= e['a'] < m['n'] or not 0 <= e['z'] < m['n']:
            return False
        if not 0 <= e['l'] <= e['u'] <= 5 or abs(e['c']) > 100:
            return False
    return True


def feasible(m, x):
    if len(x) != len(m['edges']) or any(type(v) is not int for v in x):
        return False
    balance = [0] * m['n']
    for e, v in zip(m['edges'], x):
        if not e['l'] <= v <= e['u']:
            return False
        balance[e['a']] += v
        balance[e['z']] -= v
    return balance == m['b']


def verify(m, p, dependency):
    try:
        if not validate(m) or p['model'] != digest(m) or p['dependency'] != dependency:
            return False
        if p['kind'] == 'cut':
            s = p['set']
            if any(type(v) is not int or not 0 <= v < m['n'] for v in s) or len(s) != len(set(s)):
                return False
            s = set(s)
            supply = sum(m['b'][v] for v in s)
            upper = sum(e['u'] for e in m['edges'] if e['a'] in s and e['z'] not in s)
            lower = sum(e['l'] for e in m['edges'] if e['a'] not in s and e['z'] in s)
            return supply > upper - lower
        if p['kind'] != 'optimal' or not feasible(m, p['flow']):
            return False
        pi = p['pi']
        if len(pi) != m['n'] or any(type(v) is not int for v in pi):
            return False
        if type(p['cost_units']) is not int or p['cost_units'] != sum(e['c'] * x for e, x in zip(m['edges'], p['flow'])):
            return False
        for e, x in zip(m['edges'], p['flow']):
            r = e['c'] + pi[e['a']] - pi[e['z']]
            if x < e['u'] and r < 0 or x > e['l'] and r > 0:
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False
