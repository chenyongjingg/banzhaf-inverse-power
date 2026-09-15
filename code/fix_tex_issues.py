import re
# 1. Fix markdown source: N\X -> N\setminus X
p_md = r'manuscript.md'
t = open(p_md, encoding='utf-8').read()
t = t.replace(r'N\X', r'N\setminus X')
open(p_md, 'w', encoding='utf-8').write(t)
print('markdown N\\X fixed, remaining:', t.count(r'N\X'))

# 2. Fix postprocess preamble target to actual pandoc output
p_pp = r'code/postprocess_tex.py'
pp = open(p_pp, encoding='utf-8').read()
# ensure the replacement string includes amsthm and targets the actual preamble
pp = pp.replace(r"\usepackage{amsmath,amssymb,amsfonts}",
                r"\usepackage{amsmath,amssymb,amsfonts}")
# Replace the preamble line in the postprocess source robustly
# Find the header-fix block and rewrite it
start = pp.find('# header fix')
end = pp.find('# Uncode math')
if start != -1 and end != -1:
    block = ("# header fix\n"
             "t = t.replace(r'\\usepackage{amsmath,amssymb}',\n"
             "              r'\\usepackage{amsmath,amssymb,amsfonts,amsthm}\\usepackage{bm}'\n"
             "              r'\\usepackage{booktabs}\\usepackage{geometry}\\geometry{margin=2.5cm}')\n")
    pp = pp[:start] + block + pp[end:]
open(p_pp, 'w', encoding='utf-8').write(pp)
print('postprocess preamble fix written')
