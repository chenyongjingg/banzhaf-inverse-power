from math import gcd
from functools import reduce

# validated swing: standard Banzhaf
def swings_bf(ac, n):
    def win(m): return any((m & c) == c for c in ac)
    eta = [0]*n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit: continue
            if (not win(m)) and win(m | bit): eta[i] += 1
    return eta

# search_n6 version
def swings_of(pT, F, n):
    pbit = 1<<(n-1)
    def win(m):
        if (m & pbit)==pbit and (m & pT)==pT: return True
        for f in F:
            if (m & f)==f: return True
        return False
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for mm in range(1<<n):
            if mm & bit: continue
            if (not win(mm)) and win(mm|bit): eta[i]+=1
    return eta

n=6; pbit=1<<(n-1)
T=0b11; F=[0b111]
ac = [T|pbit] + F
print("brute:", swings_bf(ac, n))
print("struct:", swings_of(T|pbit, F, n))
print("MATCH:", swings_bf(ac,n)==swings_of(T|pbit,F,n))
print("unanimity bf:", swings_bf([(1<<n)-1], n))
