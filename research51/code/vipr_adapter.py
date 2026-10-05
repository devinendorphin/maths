"""Translate native scalar covers to VIPR 1.0, with no presolve transformation."""
from fractions import Fraction
from shared import value


def certificate(row,t,packing,proof):
    t=Fraction(t); n=len(row['weights']); full=(1<<n)-1
    w=row['weights']; q=[t.denominator*p+t.numerator*v for p,v in zip(row['profits'],row['slopes'])]
    target=value(q,packing); constraints=[]; derived=[]
    def terms(xs):
        return str(len(xs))+' '+ ' '.join(str(i)+' '+str(v) for i,v in xs)
    for i in range(n):
        constraints.extend([f'lb{i} G 0 1 {i} 1',f'ub{i} L 1 1 {i} 1'])
    constraints.append('capacity L '+str(row['capacity'])+' '+terms(list(enumerate(w))))
    def emit(sense,rhs,lhs,reason):
        index=len(constraints)+len(derived)
        derived.append(f'd{index} {sense} {rhs} {lhs} {{ {reason} }} -1')
        return index
    def combine(f,u,path,cell=None):
        if cell is None:
            # Infeasible fixed items: capacity minus all lower bounds is 0 <= negative.
            # For assigned-zero variables use their original lower bounds, not x<=0.
            mult=[(2*n,Fraction(1))]+[(path[j] if f>>j&1 else 2*j,Fraction(-w[j])) for j in range(n)]
            return emit('L',target,'OBJ','lin '+terms(mult))
        lam=Fraction(cell[3],cell[4]); mult=[]
        if lam: mult.append((2*n,lam))
        rhs=lam*row['capacity']
        for j in range(n):
            z=Fraction(q[j])-lam*w[j]
            if not z: continue
            if u>>j&1:
                idx=2*j+1 if z>0 else 2*j
                rhs+=max(Fraction(0),z)
            elif f>>j&1:
                idx=2*j+1 if z>0 else path[j]
                rhs+=z
            else:
                idx=path[j] if z>0 else 2*j
            mult.append((idx,z))
        assert rhs.numerator//rhs.denominator<=target
        return emit('L',target,'OBJ','rnd '+terms(mult))
    def intersects(f,u,cell):
        a,b=cell[:2]
        return not (f&~(a|b) or a&~(f|u))
    def recurse(f,u,path,candidates):
        if value(w,f)>row['capacity']: return combine(f,u,path)
        candidates=[cell for cell in candidates if intersects(f,u,cell)]
        assert candidates
        covering=[cell for cell in candidates if cell[0]&f==cell[0] and not (f|u)&~(cell[0]|cell[1])]
        if covering: return combine(f,u,path,covering[0])
        possible=u&~candidates[0][1]; assert possible
        j=(possible&-possible).bit_length()-1; bit=1<<j
        left_asm=emit('L',0,f'1 {j} 1','asm')
        left=recurse(f,u^bit,{**path,j:left_asm},candidates)
        right_asm=emit('G',1,f'1 {j} 1','asm')
        right=recurse(f|bit,u^bit,{**path,j:right_asm},candidates)
        return emit('L',target,'OBJ',f'uns {left} {left_asm} {right} {right_asm}')
    recurse(0,full,{},proof)
    lines=['VER 1.0',f'VAR {n}',' '.join('x'+str(i) for i in range(n)),f'INT {n}',
           ' '.join(map(str,range(n))),'OBJ max',terms([(i,x) for i,x in enumerate(q) if x]),
           f'CON {len(constraints)} {2*n}',*constraints,f'RTP range {target} {target}','SOL 1',
           'packing '+terms([(i,1) for i in range(n) if packing>>i&1]),f'DER {len(derived)}',*derived]
    return '\n'.join(lines)+'\n',dict(derivations=len(derived),original_constraints=len(constraints),
                                     scaled_objective=target,scale=t.denominator)
