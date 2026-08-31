import time
def antichains(n):
    masks = list(range(1 << n))
    results = []
    def rec(chosen, start):
        results.append(chosen)  # just count, store minimal
        for idx in range(start, len(masks)):
            m = masks[idx]
            ok=True
            for c in chosen:
                if (c & m)==c: ok=False; break
            if ok:
                chosen.append(m); rec(chosen, idx+1); chosen.pop()
    rec([], 0)
    return len(results)
t0=time.time()
c=antichains(6)
print("antichains:", c, " time:", time.time()-t0)
