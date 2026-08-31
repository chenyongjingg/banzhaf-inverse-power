"""Batch-run W-family MILP for n in range. Prints solvable n."""
import subprocess, sys, time
lo=int(sys.argv[1]); hi=int(sys.argv[2]); tl=int(sys.argv[3]) if len(sys.argv)>3 else 60
covered=[]; failed=[]
for n in range(lo, hi+1):
    t0=time.time()
    try:
        out=subprocess.run(['python','code/milp_ufamily.py',str(n),str(tl)],capture_output=True,text=True,timeout=tl+20)
        txt=out.stdout
        c=None
        for l in txt.splitlines():
            l=l.strip()
            if l.startswith('c='):
                c=l.split(',')[0].replace('c=','').strip(); break
        if c is not None:
            covered.append((n,c)); print(f"n={n}: SOLVED c={c} [{time.time()-t0:.0f}s]", flush=True)
        else:
            failed.append(n); print(f"n={n}: FAIL [{time.time()-t0:.0f}s]", flush=True)
    except Exception as ex:
        failed.append(n); print(f"n={n}: ERROR {ex} [{time.time()-t0:.0f}s]", flush=True)
print(f"\nSOLVED n: {[n for n,_ in covered]}")
print(f"FAILED n: {failed}")
