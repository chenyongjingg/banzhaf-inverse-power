import random
def swings(w,q,n):
    eta=[0]*n
    for S in range(1<<n):
        W=sum(w[i] for i in range(n) if S>>i&1)
        win=W>=q
        for i in range(n):
            if not (S>>i&1) and (not win) and W+w[i]>=q:
                eta[i]+=1
    return eta

# 1) identity (K)
random.seed(7); bad=0; tested=0
for t in range(3000):
    n=random.randint(3,8); w=[random.randint(1,20) for _ in range(n)]; q=random.randint(1,sum(w))
    eta=swings(w,q,n)
    for i in range(n):
        for j in range(n):
            if i==j or w[i]<w[j]: continue
            rest=[k for k in range(n) if k not in (i,j)]
            cnt=sum(1 for T in range(1<<len(rest))
                    if q-w[i] <= sum(w[rest[k]] for k in range(len(rest)) if T>>k&1) < q-w[j])
            tested+=1
            if eta[i]-eta[j]!=2*cnt: bad+=1
print("(K):",bad,"failures /",tested,"pairs")

# 2) equal counts => interchangeable; and no weighted game with n-1 equal counts and an odd player strictly between 0 and theirs
random.seed(11); eq=0; noninter=0; between=0
for t in range(30000):
    n=random.randint(3,7); w=[random.randint(1,30) for _ in range(n)]; q=random.randint(1,sum(w)+2)
    eta=swings(w,q,n)
    coal=[sum(w[i] for i in range(n) if S>>i&1)>=q for S in range(1<<n)]
    groups={}
    for i in range(n): groups.setdefault(eta[i],[]).append(i)
    for val,g in groups.items():
        for a in range(len(g)):
            for b in range(a+1,len(g)):
                i,j=g[a],g[b]; eq+=1
                if not all(coal[S]==coal[(S&~(1<<i)&~(1<<j))|(((S>>j)&1)<<i)|(((S>>i)&1)<<j)] for S in range(1<<n)):
                    noninter+=1
    # odd-player-between check: if n-1 players share a count, the last one is 0 or >= 
    for s in range(n):
        others=[x for x in range(n) if x!=s]
        if len(set(eta[x] for x in others))==1:
            h=eta[others[0]]
            if 0 < eta[s] < h:
                between+=1; print("BETWEEN",n,w,q,eta,s)
print("equal-count pairs:",eq,"non-interchangeable:",noninter,"odd-player-strictly-between:",between)
