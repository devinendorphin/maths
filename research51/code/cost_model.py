"""Classical fixed-price rent-or-buy model and an explicit failed generalization."""


def classical(price,horizon):
    # Pay one per service day; after renting price days, buy before the next day.
    return horizon if horizon<=price else 2*price


def run():
    rows=[]
    for price in range(1,33):
        for horizon in range(129):
            alg=classical(price,horizon); offline=min(price,horizon); maintain=horizon
            assert alg<=2*offline
            rows.append(dict(price=price,horizon=horizon,online=alg,offline=offline,maintain=maintain))
    # If an initial quoted price 1 becomes M at the buy decision, the same
    # unmodified threshold pays 1+M for two days; hindsight can simply rent twice.
    counterexamples=[dict(quoted_price=1,actual_price=m,horizon=2,online=1+m,offline=2,
                          ratio=[1+m,2]) for m in (2,4,16,256,65536)]
    return dict(model='Unit rental cost, fixed known integer price, free permanent service after buying, unknown horizon',
                grid=rows,counterexamples=counterexamples,
                theorem='For all B>=1 and T>=0: A(T)=T if T<=B else 2B, OPT(T)=min(T,B), so A<=2*OPT.',
                scope='Not a competitive bound for expiring/renewable proofs or CPU costs')
