import re, sys
p = r"manuscript.tex"
t = open(p, encoding='utf-8').read()
# header fix: minimal preamble (amsmath,amssymb from pandoc + booktabs/geometry optional)
t = t.replace(r'\usepackage{amsmath,amssymb}',
              r'\usepackage{amsmath,amssymb}\usepackage{booktabs}\usepackage{geometry}\geometry{margin=2.5cm}')
# Uncode math -> LaTeX (longest first)
repl = [
    ('ψⁿ', r'$\psi^{n}$'), ('ψ', r'$\psi$'), ('β', r'$\beta$'), ('Σ', r'$\sum$'),
    ('≥', r'$\geq$'), ('≤', r'$\leq$'), ('∈', r'$\in$'), ('∉', r'$\notin$'),
    ('⊆', r'$\subseteq$'), ('⊇', r'$\supseteq$'), ('∪', r'$\cup$'), ('∩', r'$\cap$'),
    ('≠', r'$\neq$'), ('∝', r'$\propto$'), ('⟺', r'$\iff$'), ('×', r'$\times$'),
    ('∞', r'$\infty$'), ('⌊', r'$\lfloor$'), ('⌋', r'$\rfloor$'), ('·', r'$\cdot$'),
    ('−', r'$-$'), ('∅', r'$\varnothing$'), ('∀', r'$\forall$'), ('∃', r'$\exists$'),
    ('…', r'$\ldots$'),
    ('→', r'$\to$'), ('∋', r'$\ni$'), ('∌', r'$\not\ni$'), ('∎', r'$\square$'),
    ('≈', r'$\approx$'), ('≡', r'$\equiv$'),
    # sub/superscripts
    ('ⁿ', r'$^{n}$'), ('₀', r'$_0$'), ('₁', r'$_1$'), ('₂', r'$_2$'), ('₃', r'$_3$'),
    ('₄', r'$_4$'), ('₅', r'$_5$'), ('₆', r'$_6$'), ('₇', r'$_7$'), ('₈', r'$_8$'), ('₉', r'$_9$'),
    ('⁰', r'$^{0}$'), ('¹', r'$^{1}$'), ('²', r'$^{2}$'), ('³', r'$^{3}$'), ('⁴', r'$^{4}$'),
    ('⁵', r'$^{5}$'), ('⁶', r'$^{6}$'), ('⁷', r'$^{7}$'), ('⁸', r'$^{8}$'), ('⁹', r'$^{9}$'),
]
for a, b in repl:
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
# report
import unicodedata
cjk = len(re.findall(r'[\u4e00-\u9fff]', t))
print('post-processed, CJK remaining:', cjk)
for ch in ['ψ','β','∈','∪','≥','≠','∞','·','−','ⁿ']:
    if ch in t:
        print('WARNING remaining char:', ch)
print('done')
