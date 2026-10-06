"""Disjoint small exhaustive fixtures for implementations and hard cap recovery."""
import random
from fractions import Fraction
from shared import value
import oracles as O
import curves
import audit


def run():
    checks=0
    for seed in range(12):
        rng=random.Random(2766000+seed);n=7
        row=dict(case_id='smoke-'+str(seed),n=n,weights=[rng.randint(1,9)*3 for _ in range(n)],
                 profits=[rng.randint(-9,14) for _ in range(n)],slopes=[rng.randint(-5,5) for _ in range(n)],capacity=41,end=19)
        checker=audit.Auditor(row)
        for kernel in ('dense','sparse','bb','bb_lean','gate','gate_bb','gate_lean'):
            for t in (Fraction(0),Fraction(3,7),Fraction(19)):
                q=O.solve(row,t,kernel,1,True);checker.check_query(q)
                best=max((t.denominator*value(row['profits'],m)+t.numerator*value(row['slopes'],m),
                          value(row['slopes'],m),-m) for m in range(1<<n) if value(row['weights'],m)<=row['capacity'])
                assert (q['scaled_objective'],q['slope'],-q['packing'])==best;checks+=1
        for kind in ('real','integer','cross','balanced','points'):checker.check(curves.run(row,kind,'dense',True));checks+=1
        for mode in ('cold','incumbent','tree','small_tree','lean_cold','lean_incumbent'):checker.check(curves.sequence(row,mode));checks+=1
        for kernel in ('dense','sparse','bb'):
            result=curves.run(row,'real',kernel,forced=True)
            assert result['aborted_calls']==result['oracle_calls'];checker.check(result);checks+=1
        for kernel in ('portfolio','forcedportfolio','deadportfolio'):
            result=curves.run(row,'real',kernel);checker.check(result)
            if kernel=='forcedportfolio':assert result['aborted_calls']==2*result['oracle_calls']
            if kernel=='deadportfolio':assert result['status']=='capped' and result['aborted_calls']==3 and not result['packings'] and not result['intervals']
            checks+=1
        result=curves.sequence(row,'tree',force_cells=0)
        assert result['aborted_calls']>=1;checker.check(result);checks+=1
    # Original-unit large capacities exercise the new B&B gate branch.
    for seed in range(3):
        row=dict(case_id='large-smoke-'+str(seed),n=6,weights=[10001+777*j for j in range(6)],profits=[5*j-8 for j in range(6)],slopes=[(-1)**j*j for j in range(6)],capacity=33001,end=13)
        checker=audit.Auditor(row)
        for kind in ('real','integer','cross','balanced'):
            r=curves.run(row,kind,'gate_lean');checker.check(r);assert {q['kernel'] for q in r['queries']}=={'bb'};checks+=1
    return dict(passed=True,fixtures=15,checks=checks,exhaustive_masks=True,selection_use=False)


if __name__=='__main__':print(run())
