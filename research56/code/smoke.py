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
        rng=random.Random(956000+seed);n=7
        row=dict(case_id='smoke-'+str(seed),n=n,weights=[rng.randint(1,9)*3 for _ in range(n)],
                 profits=[rng.randint(-9,14) for _ in range(n)],slopes=[rng.randint(-5,5) for _ in range(n)],capacity=41,end=19)
        checker=audit.Auditor(row)
        for kernel in ('dense','sparse','bb','gate'):
            for t in (Fraction(0),Fraction(3,7),Fraction(19)):
                q=O.solve(row,t,kernel,1,True);checker.check_query(q)
                best=max((t.denominator*value(row['profits'],m)+t.numerator*value(row['slopes'],m),
                          value(row['slopes'],m),-m) for m in range(1<<n) if value(row['weights'],m)<=row['capacity'])
                assert (q['scaled_objective'],q['slope'],-q['packing'])==best;checks+=1
        for kind in ('real','integer','points'):checker.check(curves.run(row,kind,'dense',True));checks+=1
        for mode in ('cold','incumbent','tree'):checker.check(curves.sequence(row,mode));checks+=1
        for kernel in ('dense','sparse','bb'):
            result=curves.run(row,'real',kernel,forced=True)
            assert result['aborted_calls']==result['oracle_calls'];checker.check(result);checks+=1
        result=curves.sequence(row,'tree',force_cells=0)
        assert result['aborted_calls']>=1;checker.check(result);checks+=1
    return dict(passed=True,fixtures=12,checks=checks,exhaustive_masks=True,selection_use=False)


if __name__=='__main__':print(run())
