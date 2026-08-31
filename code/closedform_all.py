"""Verify: every n in a range has a closed-form construction.
Residues 0,2,3,6: complement-of-edge. Residues 1,4,5: triangle construction (f=5,6,4)."""
import networkx as nx
from math import gcd
from functools import reduce

def comp_edge(n,d):
    num=d*(2*n-8)+4*(n-1)
    if num%7: return None
    c=num//7; ds=d+c//2
    seq=[d]*(n-1)+[ds]
    if not nx.is_graphical(seq): return None
    return c, ds

def triangle(n,f):
    c=(10*(n-1)-2*f-18)//7
    s=(c+6)//2
    Rcount=(n-1)-3*f
    if s>Rcount: return None
    seq=[3]*Rcount+[s]
    if not nx.is_graphical(seq): return None
    return c, s

def method(n):
    r=n%7
    if r in (0,2,3,6):
        c=comp_edge(n,{0:3,2:1,3:4,6:2}[r])
        return ('comp-edge', c)
    elif r==1:
        return ('triangle', triangle(n,5))
    elif r==4:
        return ('triangle', triangle(n,6))
    elif r==5:
        return ('triangle', triangle(n,4))
    return None

covered=0; gaps=[]
for n in range(67, 141):
    m=method(n)
    if m and m[1] is not None:
        covered+=1
    else:
        gaps.append((n, n%7))
print(f'n in [67,140]: {covered}/{len(range(67,141))} closed-form, gaps: {gaps}')
# also show the smallest n for each residue where closed form works
print()
print("Smallest closed-form n per residue:")
for r in range(7):
    for n in range(6, 200):
        if n%7==r:
            m=method(n)
            if m and m[1] is not None:
                print(f"  n≡{r}: smallest={n} ({m[0]})")
                break
