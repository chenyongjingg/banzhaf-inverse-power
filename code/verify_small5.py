"""Verify the 5 small closed-form constructions: n=8,10,11,12,15."""
import json
from math import gcd
from functools import reduce

for n, f in [(8,'sol8_cap2.json'),(10,'sol10_cap3.json'),
             (11,'sol11_cap6.json'),(12,'sol12_cap6.json'),
             (15,'sol15_cap6.json')]:
    try:
        d=json.load(open(f))
    except Exception as e:
        print(f'n={n}: no saved json ({e})'); continue
    G=d['G']; F=d['F']; N=n
    Gset=set(tuple(sorted(e)) for e in G); deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))
    mono=all(tuple(sorted((X[a],X[b]))) in Gset for X in F for a in range(3) for b in range(a+1,3))
    # deg+r pattern
    dr=sorted(set(deg[i]+sum(1 for X in F if i in X) for i in range(N-1)))
    print(f'n={n} (≡{n%7}): c={d["c"]} |G|={len(G)} |F|={len(F)} swings_OK={ok} monotone={mono} non-special deg+r set={dr}')
    print(f'   F: {F}')
