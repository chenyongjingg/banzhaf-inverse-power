# Independent verification of Kurz-Napel footnote 19 example
sets = [[2,4,5,6],[2,3,4,5],[1,3,5,6],[1,3,4,5],[1,2,4,6],[1,2,3,5]]
n=6
# convert 1-indexed -> mask
def mask(cc):
    m=0
    for x in cc: m |= 1<<(x-1)
    return m
ac=[mask(c) for c in sets]
print("antichain masks:", ac)
win=[False]*(1<<n)
for m in range(1<<n):
    win[m]=any((m&c)==c for c in ac)
print("winning 4-sets (should be exactly the 6):")
for m in range(1<<n):
    if bin(m).count('1')==4 and win[m]:
        print("  ", [i+1 for i in range(n) if m>>i&1])
eta=[0]*n
for i in range(n):
    bit=1<<i
    for m in range(1<<n):
        if m&bit: continue
        if (not win[m]) and win[m|bit]: eta[i]+=1
print("swings:", eta, "total:", sum(eta))
print("expected: (8,8,8,8,8,4) total 44")
