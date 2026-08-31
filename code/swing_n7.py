"""Swing decomposition of a canonical n=7 solution (C6+star7 complement)."""
n=7
# complement graph: C6 on {1..6} + star at 7
edges=[(1,2),(2,3),(3,4),(4,5),(5,6),(6,1),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7)]
# winning 5-sets = complements of edges
ac=[sorted(set(range(1,n+1))-set(e)) for e in edges]
acm=[sum(1<<(x-1) for x in c) for c in ac]
def win(m): return any((m&c)==c for c in acm)
for i in range(n):
    bit=1<<i; swings=[]
    for m in range(1<<n):
        if m&bit: continue
        if (not win(m)) and win(m|bit):
            swings.append(sorted(j+1 for j in range(n) if (m>>j)&1))
    print(f"player {i+1}: {len(swings)} swings")
    print("   ", swings)
