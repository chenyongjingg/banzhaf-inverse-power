# -*- coding: utf-8 -*-
"""Independent check of the n=8 L1 upper bound: game [q=4; w=2,3,3,3,3,3,3,1].
Special = position 7 (target 1/15). Verify swing counts and L1 distance to psi^8."""
w = [2,3,3,3,3,3,3,1]
q = 4
n = len(w); N = 1 << n
SW = [0]*N
for mm in range(1, N):
    lb = mm & (-mm); SW[mm] = SW[mm ^ lb] + w[lb.bit_length()-1]
eta = [0]*n
for i in range(n):
    for mm in range(N):
        if mm & (1 << i): continue
        if SW[mm] >= q - w[i] and SW[mm] < q:
            eta[i] += 1
T = sum(eta)
print(f"eta={eta}  T={T}")
# L1 to psi^8 = (2,...,2,1)/15
L1 = 0.0
for i in range(n):
    p = 1/15 if i == n-1 else 2/15
    L1 += abs(eta[i]/T - p)
print(f"L1 = {L1:.8f}   n*L1 = {n*L1:.8f}")
print(f"claimed: L1 = 0.066667, n*L1 = 0.5333")
