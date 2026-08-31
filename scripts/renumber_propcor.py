#!/usr/bin/env python3
"""Renumber Proposition/Corollary labels to sequential document order.

The EJOR reframing moved the "extended explorations" section (§11) after the
weighted-obstruction section (§9), so Proposition/Corollary numbers were no
longer sequential.  This maps every Proposition/Corollary label (definitions
and cross-references alike) to its new sequential number in one pass, so no
intermediate value can collide with a later source label.

    Old (document order)          New
    -------------------           ---
    Prop 17  (§9)             ->  Prop 4
    Cor 18   (§9)             ->  Cor 5
    Cor 19   (§9)             ->  Cor 6
    Cor 20   (§9)             ->  Cor 7
    Prop 4   (§11)            ->  Prop 8
    Cor 5    (§11)            ->  Cor 9
    Prop 6   (§11)            ->  Prop 10
    Prop 8   (§11)            ->  Prop 11
    Prop 10  (§11)            ->  Prop 12
    Prop 11  (§11)            ->  Prop 13
    Cor 12   (§11)            ->  Cor 14
    Cor 13   (§11)            ->  Cor 15
    Cor 14   (§11)            ->  Cor 16
    Cor 15   (§11)            ->  Cor 17

Theorem 1/2, Corollary 2/3 (Section 1-7) and Lemma A already appear in order
and are left untouched.
"""

import re
import sys
from collections import Counter

MAPPING = {
    ("Proposition", "17"): "4",
    ("Corollary", "18"): "5",
    ("Corollary", "19"): "6",
    ("Corollary", "20"): "7",
    ("Proposition", "4"): "8",
    ("Corollary", "5"): "9",
    ("Proposition", "6"): "10",
    ("Proposition", "8"): "11",
    ("Proposition", "10"): "12",
    ("Proposition", "11"): "13",
    ("Corollary", "12"): "14",
    ("Corollary", "13"): "15",
    ("Corollary", "14"): "16",
    ("Corollary", "15"): "17",
}

PATTERN = re.compile(r"\b(Proposition|Corollary)\s+(\d+)\b")
counts = Counter()


def repl(m):
    kind, num = m.group(1), m.group(2)
    new = MAPPING.get((kind, num))
    if new is not None:
        counts[(kind, num, new)] += 1
        return f"{kind} {new}"
    return m.group(0)


def main(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    out = PATTERN.sub(repl, text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"Renumbered {path}:")
    for (kind, num, new), c in sorted(counts.items()):
        print(f"  {kind} {num} -> {kind} {new}  ({c}x)")
    print(f"  total substitutions: {sum(counts.values())}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manuscript.md")
