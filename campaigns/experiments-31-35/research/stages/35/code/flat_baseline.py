"""Supporting flat immutable-sharing baseline, extracted from the prior experiment.
Used by proof_price_experiment.py; see Proof-price-protocol.md.
Standard library only. Solver/storage logic is unchanged.
"""

import argparse

import hashlib

import itertools

import json

import platform

import random

import statistics

import time

from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Cell:
    fixed: int
    free: int
    residual: int
    a: int
    b: int
    num: int

def metered_value(p,mask):
    total=0
    while mask:
        bit=mask & -mask
        mask-=bit
        total+=p[bit.bit_length()-1]
        yield
    return total

def metered_order(w,p,arena):
    rank=yield from arena.buffer()
    for i in range(len(w)):
        rank.append(i)
        yield
        j=len(rank)-1
        while j:
            left=rank[j-1]
            before=p[i]*w[left]>p[left]*w[i]
            yield
            if not before:
                break
            rank[j]=left
            rank[j-1]=i
            j-=1
            yield
    return rank

def metered_lp(w,p,residual,free,rank):
    chosen=profit=0
    room=residual
    for i in rank:
        bit=1<<i
        eligible=bool(free & bit) and p[i]>0
        yield
        if not eligible:
            continue
        if w[i]<=room:
            room-=w[i]
            chosen|=bit
            profit+=p[i]
            yield
        else:
            result=(profit*w[i]+p[i]*room,w[i],i,chosen,p[i],w[i])
            yield
            return result
    return profit,1,None,chosen,0,1

def run_to_completion(gen):
    steps=0
    while True:
        steps+=1
        try:
            next(gen)
        except StopIteration as done:
            return done.value,steps

B = 16

MODES = ('flat_copy', 'flat_share', 'block_copy', 'block_share')

class Store:
    def __init__(self):
        self.cells = {}
        self.blocks = {}
        self.next_id = 0
        self.stats = dict(cells_allocated=0, cells_freed=0, blocks_allocated=0,
                          blocks_freed=0, retains=0, releases=0,
                          cells_reused=0, blocks_reused=0,
                          input_cells=0, input_blocks=0,
                          peak_cells=0, peak_blocks=0)

    def ident(self):
        self.next_id += 1
        return self.next_id

    def cell(self, cell, arena):
        ident = self.ident()
        self.cells[ident] = [cell, 1]
        arena.newcells.append(ident)
        self.stats['cells_allocated'] += 1
        self.stats['peak_cells'] = max(self.stats['peak_cells'], len(self.cells))
        yield
        return ident

    def retain(self, ident, block=False):
        (self.blocks if block else self.cells)[ident][1] += 1
        self.stats['retains'] += 1

    def block(self, ids, arena):
        assert 0 < len(ids) <= B
        owned = []
        arena.owned_builders.append(owned)
        yield
        for ident in ids:
            self.retain(ident)
            owned.append(ident)
            yield
        ident = self.ident()
        # Transfer the bounded builder's ownership; no suspended ownership gap.
        self.blocks[ident] = [tuple(owned), 1]
        owned.clear()
        arena.newblocks.append(ident)
        self.stats['blocks_allocated'] += 1
        self.stats['peak_blocks'] = max(self.stats['peak_blocks'], len(self.blocks))
        yield
        return ident

    def release(self, ident, block=False):
        table = self.blocks if block else self.cells
        record = table[ident]
        record[1] -= 1
        self.stats['releases'] += 1
        yield
        if record[1] == 0:
            del table[ident]
            self.stats['blocks_freed' if block else 'cells_freed'] += 1
            yield
            if block:
                for child in record[0]:
                    yield from self.release(child)

    def empty(self):
        assert not self.cells and not self.blocks
        assert self.stats['cells_allocated'] == self.stats['cells_freed']
        assert self.stats['blocks_allocated'] == self.stats['blocks_freed']

class Proof:
    def __init__(self, store, blocked):
        self.store, self.blocked = store, blocked
        self.ids = []

    def append(self, ident):
        self.store.retain(ident, self.blocked)
        self.ids.append(ident)
        yield

    def release(self):
        while self.ids:
            ident = self.ids.pop()
            yield
            yield from self.store.release(ident, self.blocked)

    def cell_ids(self):
        for ident in self.ids:
            if self.blocked:
                yield from self.store.blocks[ident][0]
            else:
                yield ident

    def fields(self):
        return [tuple(asdict(self.store.cells[i][0]).values()) for i in self.cell_ids()]

class Arena:
    def __init__(self, store):
        self.store = store
        self.buffers, self.roots = [], []
        self.newcells, self.newblocks, self.owned_builders = [], [], []
        self.refreshes = self.splits = 0

    def buffer(self):
        buf = []
        self.buffers.append(buf)
        yield
        return buf

    def root(self, blocked):
        root = Proof(self.store, blocked)
        self.roots.append(root)
        yield
        return root

    def cleanup(self, keep=None):
        while self.roots:
            root = self.roots.pop()
            yield
            if root is not keep:
                yield from root.release()
        while self.newblocks:
            ident = self.newblocks.pop()
            yield
            yield from self.store.release(ident, True)
        while self.owned_builders:
            owned = self.owned_builders.pop()
            yield
            while owned:
                ident = owned.pop()
                yield
                yield from self.store.release(ident)
        while self.newcells:
            ident = self.newcells.pop()
            yield
            yield from self.store.release(ident)
        while self.buffers:
            buf = self.buffers.pop()
            yield
            while buf:
                buf.pop()
                yield

def solve(w, p, c, incumbent, old, anchor, mode, arena):
    store = arena.store
    sharing = mode.endswith('share')
    blocked = mode.startswith('block')
    output = yield from arena.root(blocked)
    changes = yield from arena.buffer()
    leaves = yield from arena.buffer()
    stack = yield from arena.buffer()
    group = yield from arena.buffer()
    best = yield from metered_value(p, incumbent)
    chosen = incumbent
    if best < 0:
        best = chosen = 0
    yield
    rank = None
    if old is not None:
        for i in range(len(w)):
            delta = p[i] - anchor[i]
            yield
            if delta:
                changes.append((i, delta))
                yield
        # Borrow bounded old groups; old root remains alive through commit/cancel.
        groups = ((ident, store.blocks[ident][0]) for ident in old.ids) if blocked else (
            (None, old.ids[start:start+B]) for start in range(0, len(old.ids), B))
    else:
        groups = ((None, (None,)),)
    for oldblock, ids in groups:
        yield
        if old is not None:
            store.stats['input_blocks'] += int(blocked)
        for ident in ids:
            group.append(ident)
            yield
        for ident in group:
            if ident is None:
                stack.append((0, (1 << len(w))-1, c))
                yield
            else:
                cell = store.cells[ident][0]
                num = cell.num
                store.stats['input_cells'] += 1
                yield
                for i, delta in changes:
                    bit = 1 << i
                    if cell.fixed & bit:
                        num += cell.b * delta
                    elif cell.free & bit:
                        num += (max(0, cell.b*p[i]-cell.a*w[i])
                                - max(0, cell.b*anchor[i]-cell.a*w[i]))
                    yield
                reuse = sharing and num == cell.num
                yield
                if reuse:
                    synced = ident
                    store.stats['cells_reused'] += 1
                else:
                    synced = yield from store.cell(Cell(cell.fixed, cell.free,
                        cell.residual, cell.a, cell.b, num), arena)
                if num // cell.b <= best:
                    leaves.append(synced)
                    yield
                else:
                    stack.append((cell.fixed, cell.free, cell.residual))
                    yield
            while stack:
                fixed, free, residual = stack.pop()
                arena.refreshes += 1
                yield
                if rank is None:
                    rank = yield from metered_order(w, p, arena)
                fixed_value = yield from metered_value(p, fixed)
                num, den, split, filled, a, b = yield from metered_lp(w, p, residual, free, rank)
                candidate_value = fixed_value + (yield from metered_value(p, filled))
                if candidate_value > best:
                    best, chosen = candidate_value, fixed | filled
                upper = fixed_value + num // den
                yield
                if upper <= best or split is None:
                    new = yield from store.cell(Cell(fixed, free, residual, a, b,
                                                     fixed_value*den+num), arena)
                    leaves.append(new)
                    yield
                else:
                    arena.splits += 1
                    bit = 1 << split
                    rest = free ^ bit
                    stack.append((fixed, rest, residual))
                    yield
                    if residual >= w[split]:
                        stack.append((fixed | bit, rest, residual-w[split]))
                        yield
        if blocked:
            same = sharing and oldblock is not None and len(leaves) == len(group)
            yield
            if same:
                for left, right in zip(leaves, group):
                    same = same and left == right
                    yield
            if same:
                store.stats['blocks_reused'] += 1
                yield from output.append(oldblock)
            else:
                # Each bounded chunk formation is charged per slot.
                chunk = yield from arena.buffer()
                for ident in leaves:
                    chunk.append(ident)
                    yield
                    if len(chunk) == B:
                        newblock = yield from store.block(chunk, arena)
                        yield from output.append(newblock)
                        while chunk:
                            chunk.pop()
                            yield
                if chunk:
                    newblock = yield from store.block(chunk, arena)
                    yield from output.append(newblock)
                    while chunk:
                        chunk.pop()
                        yield
        else:
            for ident in leaves:
                yield from output.append(ident)
        while leaves:
            leaves.pop()
            yield
        while group:
            group.pop()
            yield
    return best, chosen, output

def advance(w, p, c, chosen, old, anchor, mode, store):
    arena = Arena(store)
    gen = solve(w, p, c, chosen, old, anchor, mode, arena)
    answer, steps = run_to_completion(gen)
    gen.close()
    steps += 1
    _, cleanup = run_to_completion(arena.cleanup(answer[2]))
    steps += cleanup
    if old is not None:
        _, retirement = run_to_completion(old.release())
        steps += retirement
    return answer, steps, arena.refreshes, arena.splits

def dp(w, p, c):
    values = [0]*(c+1)
    for weight, profit in zip(w, p):
        for room in range(c, weight-1, -1):
            values[room] = max(values[room], values[room-weight]+profit)
    return max(values)

def audit(w, p, c, best, chosen, proof):
    assert sum(w[i] for i in range(len(w)) if chosen >> i & 1) <= c
    assert sum(p[i] for i in range(len(w)) if chosen >> i & 1) == best == dp(w, p, c)
    fields = proof.fields()
    for fixed, free, residual, a, b, num in fields:
        assert fixed & free == 0 and a >= 0 and b > 0
        assert residual == c - sum(w[i] for i in range(len(w)) if fixed >> i & 1)
        expected = b*sum(p[i] for i in range(len(w)) if fixed >> i & 1) + a*residual
        expected += sum(max(0, b*p[i]-a*w[i]) for i in range(len(w)) if free >> i & 1)
        assert expected == num and num//b <= best
    for mask in range(1 << len(w)):
        if sum(w[i] for i in range(len(w)) if mask >> i & 1) <= c:
            assert sum(mask & fixed == fixed and mask & ~(fixed | free) == 0
                       for fixed, free, *_ in fields) == 1
    return len(fields)

def ownership(store, roots, arenas=()):
    expected_cells = {i: 0 for i in store.cells}
    expected_blocks = {i: 0 for i in store.blocks}
    for root in roots:
        target = expected_blocks if root.blocked else expected_cells
        for ident in root.ids:
            target[ident] += 1
    for arena in arenas:
        for ident in arena.newcells:
            expected_cells[ident] += 1
        for ident in arena.newblocks:
            expected_blocks[ident] += 1
        for builder in arena.owned_builders:
            for ident in builder:
                expected_cells[ident] += 1
        for root in arena.roots:
            target = expected_blocks if root.blocked else expected_cells
            for ident in root.ids:
                target[ident] += 1
    for ids, refs in store.blocks.values():
        for ident in ids:
            expected_cells[ident] += 1
    assert {i: r[1] for i, r in store.cells.items()} == expected_cells
    assert {i: r[1] for i, r in store.blocks.items()} == expected_blocks
    assert all(expected_cells.values()) and all(expected_blocks.values())

def workload(seed, family, regime):
    rng = random.Random(seed)
    w = [rng.randint(5,70) for _ in range(24)]
    c = sum(w)//3
    p = ([rng.randint(10,150) for _ in w] if family == 'uncorrelated'
         else [weight+40+rng.randint(-3,3) for weight in w])
    stream = [p]
    for t in range(1,80):
        k = {'sparse1':1, 'sparse6':6, 'dense24':24,
             'alternating':24 if t%2 else 1,
             'pulse10':24 if t%10==0 else 1,
             'mixed':24 if 25<=t<50 else 1}[regime]
        q = p.copy()
        for i in rng.sample(range(24),k):
            q[i] = max(1,q[i]+rng.choice((-1,1))*rng.randint(1,20))
        stream.append(q)
        p = q
    return w,c,stream
