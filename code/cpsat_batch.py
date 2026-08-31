"""CP-SAT batch for W-family: n in range, residues given. Saves solutions to file."""
import subprocess, sys, time, re, ast, os
lo=int(sys.argv[1]); hi=int(sys.argv[2]); tl=int(sys.argv[3]) if len(sys.argv)>3 else 120
residues=set(int(x) for x in sys.argv[4].split(',')) if len(sys.argv)>4 else {1,4,5}
outpath=sys.argv[5] if len(sys.argv)>5 else 'paper-raw/cpsat_batch.txt'
results=[]
for n in range(lo, hi+1):
    if n%7 not in residues:
        print(f"n={n}: (closed-form residue, skip)", flush=True)
        continue
    t0=time.time()
    try:
        out=subprocess.run(['python','code/cpsat_wfamily.py',str(n),str(tl)],capture_output=True,text=True,timeout=tl+30)
        txt=out.stdout
        m=re.search(r'c=(\d+) \|G\|=(\d+) \|F\|=(\d+)', txt)
        if m:
            c,g,f = int(m.group(1)),int(m.group(2)),int(m.group(3))
            results.append((n,c))
            print(f"n={n}: SOLVED c={c} |G|={g} |F|={f} [{time.time()-t0:.0f}s]", flush=True)
        else:
            results.append((n,None))
            print(f"n={n}: FAIL [{time.time()-t0:.0f}s] {txt.strip()[:80]}", flush=True)
    except Exception as ex:
        results.append((n,None))
        print(f"n={n}: ERR {ex} [{time.time()-t0:.0f}s]", flush=True)
print(f"\n=== SOLVED:", [n for n,c in results if c])
print(f"=== FAILED:", [n for n,c in results if c is None])
