#!/usr/bin/env python3
"""Cross-check every c-value claimed in the manuscript against the authoritative
appendix-data-n80.json (the paper's own machine-readable dataset, re-verified by
counting swings directly from the game definition rather than through (U)).

Deterministic, offline. Prints PASS/FAIL per check; exit code 0 iff all pass.

Run from the repository root:  python verify_appendix_manuscript.py
"""
import json
import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]


def _resolve(name):
    """Locate a companion file in the repo layout (PAPER/) or the package layout
    (PAPER/data/), whichever exists; fall back to PAPER/name."""
    for cand in (PAPER / name, PAPER / "data" / name):
        if cand.exists():
            return cand
    return PAPER / name


APPENDIX = _resolve("appendix-data-n80.json")
EN = PAPER / "manuscript.md"
ZH = PAPER / "manuscript_zh.md"
SOLUTIONS = _resolve("appendix-solutions.md")


def load_appendix():
    data = json.loads(APPENDIX.read_text(encoding="utf-8"))
    # accept both {"n": {...}} keyed by int and a bare dict/list
    if isinstance(data, dict) and "c" in data and isinstance(data["c"], (int, float)):
        raise ValueError("appendix-data-n80.json has unexpected top-level shape")
    out = {}
    for k, v in data.items():
        n = int(k)
        c = v["c"] if isinstance(v, dict) and "c" in v else v
        out[n] = int(c)
    return out


def load_games():
    """The full (c, G, F, method) record per n, for checking the appendix file's quotations."""
    raw = json.loads(APPENDIX.read_text(encoding="utf-8"))
    games = {}
    for k, v in raw.items():
        G = {(1 << a) | (1 << b) for a, b in v["G"]}
        F = {(1 << a) | (1 << b) | (1 << c) for a, b, c in v["F"]}
        games[int(k)] = (int(v["c"]), G, F, v.get("method", ""))
    return games


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_solutions_summary(text):
    """(n, c, |G|, |F|, method) from the summary table of `appendix-solutions.md`."""
    rows, lines = [], text.splitlines()
    for idx, ln in enumerate(lines):
        if re.match(r"\s*\|\s*n\s*\|\s*n mod 7\s*\|\s*c\s*\|", ln) and "method" in ln:
            for j in range(idx + 1, len(lines)):
                if not re.match(r"\s*\|", lines[j]):
                    break
                cells = _cells(lines[j])
                if len(cells) != 6:
                    continue
                try:
                    n, c = int(cells[0]), int(cells[2])
                    nG, nF = int(cells[3].strip("|")), int(cells[4].strip("|"))
                except ValueError:
                    continue  # the header row itself, or a separator
                rows.append((n, c, nG, nF, cells[5]))
            break
    return rows


def parse_solutions_listings(text):
    """The explicit games printed for five values of n, as {n: (c, method, G, F)}."""
    out = {}
    for chunk in text.split("### n = ")[1:]:
        head, _, body = chunk.partition("\n")
        m = re.match(r"(\d+) \(c = (\d+), (.+)\)\s*$", head)
        g = re.search(r"^G: (\[.*\])$", body, re.M)
        f = re.search(r"^F: (\[.*\])$", body, re.M)
        if not (m and g and f):
            continue
        G = {(1 << a) | (1 << b) for a, b in json.loads(g.group(1))}
        F = {(1 << a) | (1 << b) | (1 << d) for a, b, d in json.loads(f.group(1))}
        out[int(m.group(1))] = (int(m.group(2)), m.group(3), G, F)
    return out


def check_solutions(games, text):
    """`appendix-solutions.md` against the dataset it prints.

    Both its summary table and its five explicit game listings are quotations of
    appendix-data-n80.json.  Until 2026-09-15 neither was compared to it: this verifier read
    c-values out of the *manuscripts*, so the appendix file could quote a superseded generation
    of the dataset and every gate still passed.  It did -- the n = 11 row printed c = 16,
    |G| = 28 where the dataset has c = 14, |G| = 22, and the n = 11 and n = 22 listings were
    the older games.  The games it printed were real and did realize psi^n, so no number was a
    lie; what was wrong is that two shipped surfaces described different games for the same n.
    """
    bad = []
    rows = parse_solutions_summary(text)
    listings = parse_solutions_listings(text)

    for n, c, nG, nF, method in rows:
        if n not in games:
            bad.append(f"summary table: n={n} is not in the dataset")
            continue
        wc, G, F, wm = games[n]
        if (c, nG, nF, method) != (wc, len(G), len(F), wm):
            bad.append(f"summary table n={n}: prints c={c}, |G|={nG}, |F|={nF}, method={method!r}; "
                       f"dataset has c={wc}, |G|={len(G)}, |F|={len(F)}, method={wm!r}")

    for n, (c, method, G, F) in sorted(listings.items()):
        if n not in games:
            bad.append(f"listing: n={n} is not in the dataset")
            continue
        wc, wG, wF, wm = games[n]
        if G != wG or F != wF:
            extra_g, miss_g = sorted(G - wG)[:4], sorted(wG - G)[:4]
            bad.append(f"listing n={n}: the game printed is not the dataset's -- "
                       f"{len(G - wG)} edge(s) not in the dataset, {len(wG - G)} missing"
                       + (f"; first extra {extra_g}, first missing {miss_g}"
                          if extra_g or miss_g else ""))
        if c != wc or method != wm:
            bad.append(f"listing n={n}: prints c={c}, method={method!r}; dataset has "
                       f"c={wc}, method={wm!r}")

    # Coverage, so that a table quietly reduced to the rows that happen to agree is a failure.
    if rows and {r[0] for r in rows} != set(games):
        missing = sorted(set(games) - {r[0] for r in rows})
        extra = sorted({r[0] for r in rows} - set(games))
        bad.append(f"summary table covers {len(rows)} values of n, the dataset has {len(games)}"
                   f" (missing {missing[:6]}, unexpected {extra[:6]})")
    if not rows:
        bad.append("no summary table found in appendix-solutions.md")
    if not listings:
        bad.append("no explicit game listings found in appendix-solutions.md")

    if bad:
        print(f"[FAIL] appendix-solutions.md vs appendix-data-n80.json: {len(bad)} mismatch(es)")
        for b in bad[:12]:
            print("   ", b)
        return bad
    print(f"[PASS] appendix-solutions.md: summary table ({len(rows)} rows) and "
          f"{len(listings)} game listings all match appendix-data-n80.json")
    return []


def check(name, pairs, appendix):
    bad = []
    for n, c in pairs:
        if n not in appendix:
            bad.append(f"n={n}: c={c} claimed but n not in appendix")
        elif appendix[n] != c:
            bad.append(f"n={n}: claimed c={c}, appendix c={appendix[n]}")
    if bad:
        print(f"[FAIL] {name}: {len(bad)} mismatch(es)")
        for b in bad[:12]:
            print("   ", b)
        return bad
    print(f"[PASS] {name}: {len(pairs)} values all match appendix")
    return []


def parse_table_rows(text):
    """Return (n, c) pairs from tables whose header contains '| n |' and a
    '| c |' data row following an 'n mod 7' row."""
    pairs = []
    lines = text.splitlines()
    for idx, ln in enumerate(lines):
        if re.match(r"\s*\| n \|", ln):
            heads = [h.strip() for h in ln.strip().strip("|").split("|")]
            # find a following row with matching col count and a 'c' entry
            for j in range(idx + 1, min(idx + 6, len(lines))):
                row = lines[j]
                if not re.match(r"\s*\|", row):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) != len(heads):
                    continue
                if cells[0] in {"c", "c 值"}:
                    # align the value row with the numeric header columns only;
                    # pairing heads[1:] with cells[1:] fixes an off-by-one that
                    # previously shifted every c onto the next n.
                    for h, cell in zip(heads[1:], cells[1:], strict=False):
                        try:
                            pairs.append((int(h), int(cell)))
                        except ValueError:
                            pass
                    break
    return pairs


def parse_column_tables(text):
    """Return (n, c) pairs from tables whose header is '| n | n mod 7 | c | ... |'
    and whose data rows put n in col 0 and c in col 2 (e.g. §7 / Prop 11 tables)."""
    pairs = []
    lines = text.splitlines()
    for idx, ln in enumerate(lines):
        if not re.match(r"\s*\| n \| n mod 7 \| c \|", ln):
            continue
        for j in range(idx + 1, len(lines)):
            row = lines[j]
            if not re.match(r"\s*\|", row):
                break
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            try:
                n = int(cells[0])
                c = int(cells[2])
            except ValueError:
                continue
            pairs.append((n, c))
    return pairs


def parse_narrative_claims(text):
    """Parse 'n = 67 (≡4) c = 90'-style and 'n=39 (≡4) c=50'-style claims."""
    pairs = []
    pat = re.compile(r"n\s*=\s*(\d+)\s*(?:\([^)]*\))?\s*[c,]?\s*c\s*=\s*(\d+)")
    for m in pat.finditer(text):
        pairs.append((int(m.group(1)), int(m.group(2))))
    return pairs


def main():
    # An explicit path is accepted for the appendix file so that the self-test can run this
    # checker over a deliberately corrupted copy; the gate calls it with no argument.
    sol_path = SOLUTIONS
    if "--solutions" in sys.argv:
        sol_path = Path(sys.argv[sys.argv.index("--solutions") + 1])

    appendix = load_appendix()
    en = EN.read_text(encoding="utf-8")
    zh = ZH.read_text(encoding="utf-8") if ZH.exists() else None

    all_bad = []

    # --- EN: §10.1 representative table + Prop 10 tables -------------------
    all_bad += check("EN §10.1 representative table", parse_table_rows(en), appendix)
    all_bad += check("EN Prop 10 tables", parse_table_rows(en), appendix)
    all_bad += check("EN §7/Prop 11 column tables", parse_column_tables(en), appendix)
    all_bad += check("EN narrative c= claims", parse_narrative_claims(en), appendix)

    # --- ZH mirrors (present only if manuscript_zh.md ships in the package) ---
    if zh is not None:
        all_bad += check("ZH §10.1/Prop 10 tables", parse_table_rows(zh), appendix)
        all_bad += check("ZH §7/Prop 11 column tables", parse_column_tables(zh), appendix)
        all_bad += check("ZH narrative c= claims", parse_narrative_claims(zh), appendix)
    else:
        print("[SKIP] ZH mirrors: manuscript_zh.md not present (EN-only package)")

    # --- the appendix prose file against the dataset it prints --------------
    if sol_path.exists():
        all_bad += check_solutions(load_games(), sol_path.read_text(encoding="utf-8"))
    else:
        all_bad.append(f"appendix-solutions.md not found at {sol_path}")

    # --- reported range sanity ---------------------------------------------
    vals = sorted(appendix)
    print(f"appendix covers n = {vals[0]}..{vals[-1]} ({len(vals)} values)")

    if all_bad:
        print(f"\nTOTAL: {len(all_bad)} mismatching claims")
        sys.exit(1)
    print("\nTOTAL: all claims consistent with appendix-data-n80.json")
    sys.exit(0)


if __name__ == "__main__":
    main()
