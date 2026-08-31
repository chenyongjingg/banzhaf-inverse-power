p = r'code/postprocess_tex.py'
t = open(p, encoding='utf-8').read()
# Replace the header-fix block: keep minimal (amsmath,amssymb) + booktabs/geometry optional;
# do NOT add amsthm (avoid package install). \qed will become \square.
start = t.find('# header fix')
end = t.find('# Uncode math')
block = ("# header fix: minimal preamble (amsmath,amssymb from pandoc + booktabs/geometry optional)\n"
         "t = t.replace(r'\\usepackage{amsmath,amssymb}',\n"
         "              r'\\usepackage{amsmath,amssymb}\\usepackage{booktabs}\\usepackage{geometry}\\geometry{margin=2.5cm}')\n")
t = t[:start] + block + t[end:]
# Add \qed -> \square replacement (amssymb provides \square)
t = t.replace("('∎', r'$\\qed$'),", "('∎', r'$\\square$'),")
open(p, 'w', encoding='utf-8').write(t)
print('postprocess updated: minimal preamble, \\qed -> \\square')
