"""Run W-family MILP only for n in given residues (the ones needing MILP)."""
import subprocess, sys, time
lo=int(sys.argv[1]); hi=int(sys.argv[2]); tl=int(sys.argv[3]) if len(sys.argv)>3 else 500
residues=set(int(x) for x in sys.argv[4].split(',')) if len(sys.argv)>4 else {1,4,5}
covered=[]; failed=[]
for n in range(lo, hi+1):
    if n%7 not in residues: 
        print(f"n={n}: (closed form residue n%7={n%7}, skip)", flush=True)
        continue
    t0=time.time()
    try:
        out=subprocess.run(['python','code/milp_ufamily.py',str(n),str(tl)],capture_output=True,text=True,timeout=tl+30)
        txt=out.stdout
        c=None
        for l in txt.splitlines():
            l=l.strip()
            if l.startswith('c='): c=l.split(',')[0].replace('c=','').strip(); break
        if c is not None:
            covered.append((n,c)); print(f"n={n}: SOLVED c={c} [{time.time()-t0:.0f}s]", flush=True)
        else:
            failed.append(n); print(f"n={n}: FAIL [{time.time()-t0:.0f}s]", flush=True)
    except Exception as ex:
        failed.append(n); print(f"n={n}: ERR [{time.time()-t0:.0f}s]", flush=True)
print(f"\n=== residues {sorted(residues)} SOLVED:", [n for n,_ in covered])
print(f"=== FAILED:", failed)
