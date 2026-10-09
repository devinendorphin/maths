"""Capacity-indexed 0/1 DP producer; certificates bind original integer coefficients."""
import json,time
from fractions import Fraction

def coefficients(row,t):
 t=Fraction(t);return [t.denominator*p+t.numerator*s for p,s in zip(row['profits'],row['slopes'])]
def produce(row,t,cell_cap=200000):
 t=Fraction(t);q=coefficients(row,t);w=row['weights'];c=row['capacity'];cells=(len(w)+1)*(c+1)
 if cells>cell_cap:return {'status':'incomplete','required_cells':cells,'cell_cap':cell_cap}
 table=[[0]*(c+1)]
 for wi,qi in zip(w,q):
  prev=table[-1];table.append([max(prev[b],prev[b-wi]+qi) if b>=wi else prev[b] for b in range(c+1)])
 b=c;mask=0
 for i in range(len(w),0,-1):
  if table[i][b]!=table[i-1][b]:mask|=1<<(i-1);b-=w[i-1]
 return {'status':'complete','weights':w,'capacity':c,'profits':row['profits'],'slopes':row['slopes'],'time':[t.numerator,t.denominator],'coefficients':q,'table':table,'packing':mask,'objective':table[-1][-1],'cells':cells}
