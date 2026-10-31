# Check: in a simple game symmetric in the n-1 non-special players (one special s),
# can the special player's swing count be exactly half of the others'?
# Game encoded by monotone h,g on k=0..n-1: h(k)=v(k non-special, s absent),
# g(k)=v(k non-special, s present), h<=g, h(0)=0, g(n-1)=1.
from itertools import product
from math import comb

def check(n):
    seqs = [s for s in product([0,1], repeat=n) if all(s[i] <= s[i+1] for i in range(n-1))]
    bad = []   # ratio exactly 1/2 (eta_s * 2 == eta_i)
    viol = []  # eta_s strictly between 0 and eta_i
    for h in seqs:
        if h[0] != 0: continue
        for g in seqs:
            if any(g[k] < h[k] for k in range(n)): continue
            if g[n-1] != 1: continue
            eta_s = sum(comb(n-1,k) for k in range(n) if h[k]==0 and g[k]==1)
            A = sum(comb(n-2,k) for k in range(n-1) if h[k]==0 and h[k+1]==1)
            B = sum(comb(n-2,k) for k in range(n-1) if g[k]==0 and g[k+1]==1)
            eta_i = A+B
            if eta_s > 0 and 2*eta_s == eta_i:
                bad.append((h,g,eta_s,eta_i))
            if 0 < eta_s < eta_i:
                viol.append((h,g,eta_s,eta_i))
    return bad, viol

for n in range(2,10):
    bad, viol = check(n)
    print(f"n={n}: ratio=1/2 cases: {len(bad)}   strictly-between cases: {len(viol)}")
    for b in bad[:3]:
        print("   BAD", b)
    for b in viol[:3]:
        print("   BETWEEN", b)
