"""All fixed inputs, method lists and repeat subsets; no performance-based tuning."""
import random


METHODS={56:['real_dense','real_dense_gcd','real_bb'],57:['real_dense_gcd','real_sparse_gcd','real_bb'],
         58:['real_dense_gcd','integer_dense_gcd'],59:['real_dense','real_dense_gcd'],
         60:['real_dense_gcd','real_sparse_gcd','real_bb'],61:['real_dense_gcd','real_sparse_gcd','real_bb','real_gate'],
         62:['force_dense','force_sparse','force_bb','real_dense_gcd'],
         63:['point_bb_cold','point_bb_incumbent','point_bb_tree','points_dense_gcd','real_dense_gcd'],
         64:['real_gate'],65:['real_gate','integer_gate','real_dense_gcd']}


def make(stage,label,n,seed,regime='bounded',end=64,weight_scale=1,capacity=None):
    rng=random.Random(856000+10000*(stage-56)+n*100+seed)
    w=[rng.randint(2,20)*weight_scale for _ in range(n)]
    p=[rng.randint(-12,48) for _ in range(n)]
    if regime=='bounded':v=[rng.randint(-3,3) for _ in range(n)]
    elif regime=='wide':v=[rng.randint(-32,32) for _ in range(n)]
    elif regime=='powers':v=[rng.choice((-1,1))*2**j for j in range(n)]
    else:raise ValueError(regime)
    return dict(stage=stage,case_id=f'{stage}-{label}',n=n,seed=seed,regime=regime,weights=w,profits=p,slopes=v,
                capacity=sum(w)//2 if capacity is None else capacity,end=end,split='held',timing=False)


def inputs():
    rows=[]
    for seed in (0,1):
        base=make(56,'base',12,seed,'wide')
        for scale in (1,16,256,4096):
            rows.append(dict(base,case_id=f'56-seed{seed}-scale{scale}',weights=[x*scale for x in base['weights']],
                             capacity=base['capacity']*scale,scale=scale,matched_group=f'56-seed{seed}',timing=seed==1 and scale in (1,256)))
    for n in (12,24,48,64):
        for seed in (0,1):rows.append(dict(make(57,f'n{n}-seed{seed}',n,seed,'wide',capacity=96),timing=seed==1 and n in (24,48)))
    for seed in (0,1):
        base=make(58,'base',12,seed,'wide')
        for end in (64,256,1024):rows.append(dict(base,case_id=f'58-seed{seed}-H{end}',end=end,matched_group=f'58-seed{seed}',timing=seed==1 and end==256))
    for n,p,v in [(4,[50,49,45,36],[0,10,30,60]),(6,[100,99,97,94,90,85],[0,20,40,60,80,100])]:
        rows.append(dict(stage=58,case_id=f'58-subinteger-n{n}',n=n,seed=-1,regime='subinteger',weights=[1]*n,
                         profits=p,slopes=v,capacity=1,end=64,split='boundary',timing=n==6))
    for seed in (0,1):
        base=make(59,'base',12,seed,'wide')
        for scale in (16,256):
            for offset in (0,scale-1):rows.append(dict(base,case_id=f'59-seed{seed}-g{scale}-offset{offset}',
                weights=[x*scale for x in base['weights']],capacity=base['capacity']*scale+offset,
                scale=scale,offset=offset,matched_group=f'59-seed{seed}',timing=seed==1 and scale==256))
    for n in (12,16):
        for k,regime in enumerate(('small','gapped','wide_integer')):
            r=make(60,f'n{n}-{regime}',n,20+k,'wide');rng=random.Random(960000+100*n+k)
            if regime=='gapped':r['weights']=[2**j*1000+1 for j in range(n)]
            elif regime=='wide_integer':r['weights']=[rng.randint(100000,1000000) for _ in range(n)]
            r['capacity']=sum(r['weights'])//2;r['weight_regime']=regime;r['timing']=n==12 and regime!='small';rows.append(r)
    for n in (12,20):
        for k,regime in enumerate(('small','large')):
            for seed in (0,1):
                r=make(61,f'n{n}-{regime}-seed{seed}',n,100*k+seed,'wide')
                if regime=='large':r['weights']=[wi*10001+j+1 for j,wi in enumerate(r['weights'])];r['capacity']=sum(r['weights'])//2
                r['weight_regime']=regime;r['timing']=seed==1;rows.append(r)
    for seed in (0,1,2):rows.append(dict(make(62,f'seed{seed}',10,seed,'wide',end=32),timing=seed in (1,2)))
    rows.append(dict(stage=62,case_id='62-tie-chain',n=4,seed=-1,regime='boundary',weights=[2]*4,
                     profits=[48,41,26,3],slopes=[0,1,2,3],capacity=2,end=32,split='boundary',timing=False))
    for n in (10,14,18):
        for seed in (0,1):rows.append(dict(make(63,f'n{n}-seed{seed}',n,seed,'wide'),timing=seed==1 and n in (14,18)))
    for seed in (0,1):rows.append(make(63,f'n14-seed{seed}-H256',14,seed,'wide',end=256))
    for seed in (0,1,2,3):
        r=make(64,f'seed{seed}-large',12,seed,'wide',weight_scale=257)
        r['weights']=[wi+(j%3) for j,wi in enumerate(r['weights'])];r['capacity']=sum(r['weights'])//2;rows.append(r)
    for n,regime,scale in [(16,'wide',257),(24,'wide',1),(40,'bounded',1),(24,'powers',101)]:
        for seed in (0,1):
            r=make(65,f'n{n}-{regime}-seed{seed}',n,100*n+seed,regime,end=256 if seed==0 else 1024,weight_scale=scale)
            if scale>1:r['weights']=[x+j+1 for j,x in enumerate(r['weights'])];r['capacity']=sum(r['weights'])//2
            if n==40:r['capacity']=96
            r['timing']=seed==0;rows.append(r)
    return rows


def timing_methods(stage):
    if stage==57:return ['real_dense_gcd','real_sparse_gcd']
    if stage==60:return ['real_sparse_gcd','real_bb']
    return METHODS[stage]
