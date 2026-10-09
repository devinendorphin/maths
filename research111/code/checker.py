"""Independent recurrence checker; does not import the DP producer or solver."""
from fractions import Fraction

def verify(row,t,cert):
 try:
  t=Fraction(t);w=row['weights'];c=row['capacity'];n=len(w)
  if cert.get('status')!='complete' or not isinstance(c,int) or c<0 or len(w)!=row['n'] or any(type(x)!=int or x<=0 for x in w):return False
  if any(cert[k]!=row[k] for k in ['weights','capacity','profits','slopes']):return False
  if len(row['profits'])!=n or len(row['slopes'])!=n:return False
  q=[t.denominator*row['profits'][j]+t.numerator*row['slopes'][j] for j in range(n)]
  if cert['time']!=[t.numerator,t.denominator] or cert['coefficients']!=q:return False
  a=cert['table']
  if len(a)!=n+1 or any(len(r)!=c+1 or any(type(v)!=int for v in r) for r in a) or any(a[0]):return False
  for i in range(1,n+1):
   for b in range(c+1):
    expected=a[i-1][b]
    if b>=w[i-1]:expected=max(expected,q[i-1]+a[i-1][b-w[i-1]])
    if a[i][b]!=expected:return False
  mask=cert['packing']
  if type(mask)!=int or not 0<=mask<(1<<n):return False
  if sum(w[j] for j in range(n) if mask>>j&1)>c:return False
  value=sum(q[j] for j in range(n) if mask>>j&1)
  return type(cert['objective'])==int and value==cert['objective']==a[-1][-1]
 except (KeyError,TypeError,ValueError,IndexError,OverflowError):return False
