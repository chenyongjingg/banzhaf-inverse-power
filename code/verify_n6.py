from math import gcd
from functools import reduce

def swings(ac, n):
    def win(m): return any((m & c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m & bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

# n=6 example from Kurz-Napel footnote 19, 0-indexed
ac = [[1,3,4,5],[1,2,3,4],[0,2,4,5],[0,2,3,4],[0,1,3,5],[0,1,2,4]]  # {2,4,5,6}->[1,3,4,5] etc
n=6
masks=[]
for c in ac:
    m=0
    for x in c: m|=1<<x
    masks.append(m)
eta=swings(masks, n)
print("swings eta =", eta, " total =", sum(eta))
g=reduce(gcd,eta); print("gcd =", g, " normalized =", [e//g for e in eta])
print("target (2..,2,1) matches:", sorted(e//g for e in eta)==[1,2,2,2,2,2])
print("PBI (normalized Banzhaf) =", [f"{e/sum(eta):.6f}" for e in eta], " should be", [f"{v/11:.6f}" for v in [2,2,2,2,2,1]])
