#!/usr/bin/env python3
"""Cross-check every c-value claimed in the manuscript against the authoritative
appendix-data-n80.json (the paper's own machine-readable dataset, re-verified by
direct swing enumeration).

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
