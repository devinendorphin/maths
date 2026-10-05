from fractions import Fraction
import horizon as H

def reprice(cell,w,q):
    fixed,free,residual,_,_,_=cell
    candidates={Fraction(0)}
    for i in range(len(w)):
        if free>>i&1 and q[i]>0:candidates.add(Fraction(q[i],w[i]))
    scored=[]
    for price in sorted(candidates):
        a,b=price.numerator,price.denominator
        num=b*H.value(q,fixed)+a*residual+sum(max(0,b*q[i]-a*w[i]) for i in range(len(w)) if free>>i&1)
        scored.append((Fraction(num,b),price,num))
    bound,price,num=min(scored)
    return [fixed,free,residual,price.numerator,price.denominator,num],len(scored)

def renew(proof,w,q,chosen):
    cells=[];evaluations=0
    for cell in proof:
        new,n=reprice(cell,w,q);cells.append(new);evaluations+=n
    value=H.value(q,chosen)
    failed=[i for i,x in enumerate(cells) if x[5]//x[4]>value]
    return dict(success=not failed,proof=cells,failed_cells=failed,evaluations=evaluations,value=value)
