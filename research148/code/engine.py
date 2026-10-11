"""Credited established algorithms; retained primal flows, no retained tree claim."""
import copy
import time
import networkx  # Equal module startup charged to every route.
from ortools.graph.python import min_cost_flow
from checker import digest, verify
from producer import Budget, certificate, feasibility, networkx_flow, optimize, potentials
from transaction import Transaction

ROUTES = ('networkx-cold', 'ortools-cold', 'flow-repair', 'guard-repair')


def native_flow(m):
    solver = min_cost_flow.SimpleMinCostFlow()  # Fresh for each query, explicitly cold.
    balances = m['b'].copy()
    for e in m['edges']:
        balances[e['a']] -= e['l']; balances[e['z']] += e['l']
        solver.add_arc_with_capacity_and_unit_cost(e['a'], e['z'], e['u']-e['l'], e['c'])
    for v, b in enumerate(balances):
        solver.set_node_supply(v, b)
    status = solver.solve()
    if status == solver.INFEASIBLE:
        return None
    if status != solver.OPTIMAL:
        raise RuntimeError('OR-Tools status ' + str(status))
    x = [e['l'] + solver.flow(i) for i, e in enumerate(m['edges'])]
    assert sum(e['c']*(v-e['l']) for e, v in zip(m['edges'], x)) == solver.optimal_cost()
    return x


def completion(m, x, context):
    if x is None:
        _, cut = feasibility(m)
        assert cut is not None
        return certificate(m, context, cut=cut)
    pi, cycle = potentials(m, x)
    assert cycle is None
    return certificate(m, context, flow=x, pi=pi)


class Engine:
    def __init__(self, model, context, route):
        assert route in ROUTES
        self.state = Transaction(model, context)
        self.context, self.route = context, route
        self.last_flow, self.proof = None, None

    def query(self, message=None, force_budget=False):
        tick = time.perf_counter()
        m = self.state.model if message is None else self.state.apply(message)
        stats = {'guard_attempt': False, 'guard_accepted': False, 'flow_hint': False,
                 'budget_fallback': False, 'augmentations': 0, 'cycles': 0, 'relaxations': 0}
        p = None
        if self.route == 'guard-repair' and self.proof is not None and self.proof['kind'] == 'optimal':
            stats['guard_attempt'] = True
            candidate = copy.deepcopy(self.proof)
            candidate['model'] = digest(m)
            candidate['cost_units'] = sum(e['c']*x for e, x in zip(m['edges'], candidate['flow']))
            if verify(m, candidate, self.context):
                p = candidate; stats['guard_accepted'] = True
        if p is not None:
            action = 'certificate-admission'
        elif self.route in ('networkx-cold', 'ortools-cold'):
            x = networkx_flow(m)[1] if self.route == 'networkx-cold' else native_flow(m)
            p = completion(m, x, self.context); action = self.route
        else:
            # Even a stale hint after a cut is only input to clamping + complete repair.
            stats['flow_hint'] = self.last_flow is not None
            try:
                x, cut = feasibility(m, self.last_flow, stats)
                if cut is not None:
                    p = certificate(m, self.context, cut=cut); action = 'repair-shortage'
                else:
                    if force_budget:
                        raise Budget('deliberately forced control')
                    p = optimize(m, x, self.context, stats); action = 'flow-repair'
            except Budget:
                stats['budget_fallback'] = True
                p = completion(m, networkx_flow(m)[1], self.context); action = 'charged-cold-fallback'
        assert verify(m, p, self.context)
        if p['kind'] == 'optimal':
            self.last_flow = p['flow'].copy()
        self.proof = copy.deepcopy(p)
        return {'model': digest(m), 'version': self.state.version, 'action': action,
                'stats': stats, 'proof': copy.deepcopy(p), 'query_wall_s': time.perf_counter()-tick}
