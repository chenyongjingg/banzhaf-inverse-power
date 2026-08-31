"""For Family A n=6 solution, list the exact swing coalitions per player."""
n=6
ac_sets=[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,6],[3,5],[4,5],[5,6]]
ac=[sum(1<<(x-1) for x in c) for c in ac_sets]
def win(m): return any((m&c)==c for c in ac)
for i in range(n):
    bit=1<<i
    swings=[]
    for m in range(1<<n):
        if m&bit: continue
        if (not win(m)) and win(m|bit):
            swings.append(sorted(j+1 for j in range(n) if (m>>j)&1))
    print(f"player {i+1}: {len(swings)} swings")
    print("   ", swings)
