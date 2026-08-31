import random
def swings_brute(E, F, n):
    Em=[(1<<a)|(1<<b) for a,b in E]; Fm=[(1<<a)|(1<<b)|(1<<c) for a,b,c in F]
    def win(S):
        s=bin(S).count('1'); comp=((1<<n)-1)&~S
        if s>=n-1: return True
        if s==n-2: return comp not in Em
        if s==n-3: return comp in Fm
        return False
    return [sum(1 for S in range(1<<n) if not (S&(1<<i)) and (not win(S)) and win(S|(1<<i))) for i in range(n)]
def formula(E,F,n):
    C=(n-1)*(n-2)//2; f=len(F); e=len(E)
    deg=[sum(1 for a,b in E if a==i or b==i) for i in range(n)]
    out=[]
    for i in range(n):
        r=sum(1 for X in F if i in X)
        ee=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) in [tuple(sorted(ed)) for ed in E])
        out.append(C + f - e + 2*deg[i] - 2*r + ee)
    return out
random.seed(7)
for n in (8,10,12):
    for t in range(20):
        Es=[(a,b) for a in range(n) for b in range(a+1,n)]
        Fs=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
        E=random.sample(Es, random.randint(0,len(Es)))
        F=random.sample(Fs, random.randint(0,min(8,len(Fs))))
        b=swings_brute(E,F,n); fm=formula(E,F,n)
        assert b==fm, (n,E,F,b,fm)
print("CORRECTED FORMULA VERIFIED for n=8,10,12 (20 random each)")
