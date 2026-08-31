-- mathfix.lua: convert text-mode Unicode math and ASCII pseudo-math in the
-- manuscript markdown into proper LaTeX inline math at the pandoc AST level.
--
-- The manuscript was written with math as formatted text (Unicode glyphs like
-- ψⁿ ≤ ∈ ∪ and ASCII pseudo-LaTeX like X_i, X_{...}, X^(...)).  XeLaTeX with
-- Latin Modern Roman cannot render those glyphs in text mode, so the symbols
-- came out blank in the PDF.  This filter rewrites such runs as real math.
--
-- Strategy: walk every inline list.  Consecutive "mathy" Str nodes (those
-- containing a mapped Unicode math character or an ASCII math marker) are
-- merged (with interleaved spaces) into a single inline Math node.

-- --- mappings --------------------------------------------------------------

local GREEK = {
  ["α"]="\\alpha", ["β"]="\\beta", ["γ"]="\\gamma", ["δ"]="\\delta",
  ["ε"]="\\varepsilon", ["ζ"]="\\zeta", ["η"]="\\eta", ["θ"]="\\theta",
  ["ι"]="\\iota", ["κ"]="\\kappa", ["λ"]="\\lambda", ["μ"]="\\mu",
  ["ν"]="\\nu", ["ξ"]="\\xi", ["π"]="\\pi", ["ρ"]="\\rho", ["σ"]="\\sigma",
  ["τ"]="\\tau", ["φ"]="\\varphi", ["χ"]="\\chi", ["ψ"]="\\psi", ["ω"]="\\omega",
  ["Γ"]="\\Gamma", ["Δ"]="\\Delta", ["Θ"]="\\Theta", ["Λ"]="\\Lambda",
  ["Ξ"]="\\Xi", ["Π"]="\\Pi", ["Σ"]="\\sum", ["Φ"]="\\Phi", ["Ψ"]="\\Psi",
  ["Ω"]="\\Omega",
}

local REL = {
  ["≤"]="\\le", ["≥"]="\\ge", ["≠"]="\\ne", ["≡"]="\\equiv", ["≅"]="\\cong",
  ["⌈"]="\\lceil", ["⌉"]="\\rceil",
  ["∈"]="\\in", ["∉"]="\\notin", ["∋"]="\\ni",
  ["⊆"]="\\subseteq", ["⊇"]="\\supseteq", ["⊂"]="\\subset", ["⊃"]="\\supset",
  ["∪"]="\\cup", ["∩"]="\\cap", ["×"]="\\times", ["÷"]="\\div",
  ["≈"]="\\approx", ["∼"]="\\sim", ["∝"]="\\propto",
  ["⟺"]="\\iff", ["⟹"]="\\implies", ["→"]="\\to", ["↦"]="\\mapsto",
  ["⋅"]="\\cdot", ["·"]="\\cdot", ["−"]="-", ["−"]="-",
  ["∞"]="\\infty", ["∅"]="\\varnothing", ["∎"]="\\blacksquare",
  ["‖"]="\\|", ["…"]="\\dots", ["⋯"]="\\cdots", ["∑"]="\\sum",
  ["∌"]="\\not\\ni", ["⊔"]="\\sqcup", ["′"]="'",
}

local SUB = {
  ["₀"]="_0", ["₁"]="_1", ["₂"]="_2", ["₃"]="_3", ["₄"]="_4",
  ["₅"]="_5", ["₆"]="_6", ["₇"]="_7", ["₈"]="_8", ["₉"]="_9",
  ["ᵢ"]="_i", ["ⱼ"]="_j", ["ₖ"]="_k", ["ₗ"]="_l", ["ₘ"]="_m",
  ["ₙ"]="_n", ["ₚ"]="_p", ["ᵣ"]="_r", ["ₛ"]="_s", ["ₜ"]="_t", ["ₓ"]="_x",
}

local SUP = {
  ["⁰"]="^0", ["¹"]="^1", ["²"]="^2", ["³"]="^3", ["⁴"]="^4",
  ["⁵"]="^5", ["⁶"]="^6", ["⁷"]="^7", ["⁸"]="^8", ["⁹"]="^9",
  ["ⁿ"]="^n", ["⁻"]="^-", ["⁺"]="^+", ["ᵀ"]="^T",
}

-- common word tokens that should be roman operators
local WORDS = {
  deg="\\deg", max="\\max", min="\\min", arg="\\arg", sup="\\sup",
  inf="\\inf", lim="\\lim", Bz="\\mathrm{Bz}", Pz="\\mathrm{Pz}",
}

local function is_letter(ch)
  return ch ~= nil and ch ~= "" and ch:find("%a") ~= nil
end
local function is_letter_or_digit(ch)
  return ch ~= nil and ch ~= "" and ch:find("[%a%d]") ~= nil
end

-- split a string into UTF-8 characters (Lua strings are byte arrays)
local function uchars(s)
  local t = {}
  for c in s:gmatch(utf8.charpattern) do
    t[#t + 1] = c
  end
  return t
end

-- UTF-8 3-byte codepoint, or nil
local function utf8_codepoint(ch)
  if #ch == 3 then
    local b1, b2, b3 = ch:byte(1, 3)
    return ((b1 - 0xE0) * 0x40 + (b2 - 0x80)) * 0x40 + (b3 - 0x80)
  end
  return nil
end

-- Han ideographs + CJK/fullwidth punctuation (，。（）：；、？ etc.). Used to
-- keep Chinese prose OUT of math nodes: in the ZH manuscript Chinese text runs
-- directly against math glyphs (当ψⁿ, ≤等) with no spaces, and pandoc lumps
-- them into one Str node. mathfix must split at these prose boundaries so
-- Chinese stays in text mode (CJKmainfont) instead of being pulled into
-- latinmodern-math (which has no CJK glyphs).
local function is_cjk(ch)
  local cp = utf8_codepoint(ch)
  if not cp then return false end
  return (cp >= 0x4E00 and cp <= 0x9FFF)      -- CJK unified ideographs
      or (cp >= 0x3400 and cp <= 0x4DBF)      -- extension A
      or (cp >= 0xF900 and cp <= 0xFAFF)      -- compat ideographs
      or (cp >= 0x3000 and cp <= 0x303F)      -- CJK symbols & punctuation 《》「」、。
      or (cp >= 0xFF00 and cp <= 0xFFEF)      -- fullwidth forms ，。（）：；？
end

local function contains_cjk(s)
  for _, ch in ipairs(uchars(s)) do
    if is_cjk(ch) then return true end
  end
  return false
end

-- --- mathy detection ---------------------------------------------------------

local function contains_math_marker(s)
  if s:find("[%^_{}|]") then return true end
  for _, c in ipairs(uchars(s)) do
    if GREEK[c] or REL[c] or SUB[c] or SUP[c] then return true end
  end
  return false
end

-- split a Str's text into alternating text/math runs, cutting ONLY at CJK
-- boundaries. Non-CJK runs are kept atomic: a run containing any math marker
-- (Unicode math char or ASCII pseudo-math like _ ^ { }) is math, otherwise
-- text. CJK chars are always text. This preserves EN ASCII-math runs
-- (2^(n-1), X_i) while keeping Chinese prose in text mode.
local function split_cjk(s)
  local raw, current, curcjk = {}, "", nil
  for _, ch in ipairs(uchars(s)) do
    local c = is_cjk(ch)
    if curcjk == nil then
      current, curcjk = ch, c
    elseif c == curcjk then
      current = current .. ch
    else
      raw[#raw + 1] = { cjk = curcjk, text = current }
      current, curcjk = ch, c
    end
  end
  if current ~= "" then raw[#raw + 1] = { cjk = curcjk, text = current } end
  local runs = {}
  for _, r in ipairs(raw) do
    runs[#runs + 1] = { isMath = (not r.cjk) and contains_math_marker(r.text),
                        text = r.text }
  end
  return runs
end

-- set of known LaTeX command names emitted by this filter
local CMD = {}
for _, tbl in ipairs({ GREEK, REL, SUB, SUP }) do
  for _, v in pairs(tbl) do
    local name = v:match("^\\([%a]+)")
    if name then CMD[name] = true end
  end
end
for _, v in pairs(WORDS) do
  local name = v:match("^\\([%a]+)")
  if name then CMD[name] = true end
end
-- commands hardcoded in the scanner (not in the mapping tables)
CMD.vert = true
CMD.setminus = true
CMD["not"] = true   -- \not is a LaTeX primitive (used by ∌ → \not\ni)
CMD.allowbreak = true   -- emitted after top-level \}, in math

-- insert a space between a LaTeX command and a following letter, so that
-- \vertE / \leN / \inN never parse as a single (undefined) control word.
-- Match the LONGEST known command prefix of each letter run; whatever letters
-- remain are variables and need a separating space.
local function fix_cmd_gluing(tex)
  local out, i, n = {}, 1, #tex
  while i <= n do
    local c = tex:sub(i, i)
    if c == "\\" then
      local j = i + 1
      while tex:sub(j, j):match("%a") do j = j + 1 end
      local run = tex:sub(i + 1, j - 1)      -- letter run after the backslash
      local best = 0
      for k = #run, 1, -1 do
        if CMD[run:sub(1, k)] then best = k; break end
      end
      out[#out + 1] = "\\" .. run:sub(1, best)
      local rest = run:sub(best + 1)
      if rest ~= "" then
        out[#out + 1] = " " .. rest
      end
      i = j
    else
      out[#out + 1] = c
      i = i + 1
    end
  end
  return table.concat(out)
end

-- --- character-level scanner -------------------------------------------------

local function find_matching(cs, open_idx, open)
  -- cs is a UTF-8 character array. open_idx is the (char) index of the
  -- opening char in cs.  Returns the char index of the matching closing
  -- char, or nil.  Works on chars, not bytes, so multi-byte characters
  -- (β, −, ψ, …) inside the group do not shift the returned index.
  local depth = 1
  local close = (open == "{") and "}" or ")"
  local i = open_idx + 1
  local n = #cs
  while i <= n do
    local c = cs[i]
    if c == open then
      depth = depth + 1
    elseif c == close then
      depth = depth - 1
      if depth == 0 then return i end
    end
    i = i + 1
  end
  return nil
end

local function convert_to_math(s)
  local cs = uchars(s)           -- UTF-8 character array
  local out, i, n = {}, 1, #cs
  local function subat(k)
    return cs[k] or ""
  end
  local function concat_range(a, b)
    if a > b then return "" end
    local sub = {}
    for k = a, math.min(b, n) do sub[#sub + 1] = cs[k] end
    return table.concat(sub)
  end
  while i <= n do
    local c = cs[i]
    -- word tokens (3 letters, then 2 letters), only on a word boundary
    local w3 = concat_range(i, i + 2)
    if WORDS[w3] and not is_letter(subat(i + 3)) then
      table.insert(out, WORDS[w3]); i = i + 3
    else
      local w2 = concat_range(i, i + 1)
      if WORDS[w2] and not is_letter(subat(i + 2)) then
        table.insert(out, WORDS[w2]); i = i + 2
      elseif GREEK[c] then
        table.insert(out, GREEK[c]); i = i + 1
      elseif REL[c] then
        table.insert(out, REL[c]); i = i + 1
      elseif SUB[c] or SUP[c] then
        -- merge consecutive Unicode sub/superscript chars into one group,
        -- so C₁₃ becomes C_{13}, not the invalid C_1_3
        local tbl = SUB[c] and SUB or SUP
        local parts, k = {}, i
        while k <= n and tbl[cs[k]] do
          parts[#parts + 1] = tbl[cs[k]]:sub(2)   -- strip leading _ or ^
          k = k + 1
        end
        local sep = (tbl == SUB) and "_" or "^"
        if #parts == 1 then
          table.insert(out, sep .. parts[1])
        else
          table.insert(out, sep .. "{" .. table.concat(parts) .. "}")
        end
        i = k
      elseif c == "_" then
        local nx = subat(i + 1)
        if nx == "{" then
          local j = find_matching(cs, i + 1, "{")
          if j then
            local inner = concat_range(i + 2, j - 1)
            table.insert(out, "_{" .. convert_to_math(inner) .. "}")
            i = j + 1
          else
            table.insert(out, "_"); i = i + 1
          end
        elseif nx ~= "" then
          table.insert(out, "_" .. nx); i = i + 2
        else
          table.insert(out, "_"); i = i + 1
        end
      elseif c == "^" then
        local nx = subat(i + 1)
        if nx == "(" then
          local j = find_matching(cs, i + 1, "(")
          if j then
            local inner = concat_range(i + 2, j - 1)
            table.insert(out, "^{" .. convert_to_math(inner) .. "}")
            i = j + 1
          else
            table.insert(out, "^"); i = i + 1
          end
        elseif nx ~= "" then
          table.insert(out, "^" .. nx); i = i + 2
        else
          table.insert(out, "^"); i = i + 1
        end
      elseif c == "{" then
        -- set-difference if immediately preceded by a letter/digit, else a set literal
        if is_letter_or_digit(subat(i - 1)) then
          table.insert(out, "\\setminus\\{")
        else
          table.insert(out, "\\{")
        end
        i = i + 1
      elseif c == "}" then
        table.insert(out, "\\}"); i = i + 1
      elseif c == "%" then
        table.insert(out, "\\%"); i = i + 1
      elseif c == "&" then
        table.insert(out, "\\&"); i = i + 1
      elseif c == "#" then
        table.insert(out, "\\#"); i = i + 1
      elseif c == "$" then
        table.insert(out, "\\$"); i = i + 1
      elseif c == "|" then
        table.insert(out, "\\vert"); i = i + 1
      elseif c == " " then
        table.insert(out, "\\ "); i = i + 1
      else
        table.insert(out, c); i = i + 1
      end
    end
  end
  local tex = table.concat(out)
  -- Permit a line break after each top-level set-closer + comma (e.g. the
  -- long enumerations {1,2,3,4}, {1,2,3,5}, ... in Section 6), which would
  -- otherwise stay one unbreakable run and overflow the line.
  tex = tex:gsub("\\},", "\\},\\allowbreak")
  return fix_cmd_gluing(tex)
end

-- --- inline-list walker -------------------------------------------------------

local function fix_inlines(inlines)
  local result, buf, mathing, pending = {}, {}, false, false
  local function flush()
    if mathing then
      local tex = table.concat(buf)
      tex = tex:gsub("%s+$", "")       -- trim trailing space
      -- Convert the whole merged span at once, so that braces/parens
      -- matched by ^(...) / _{...} can span the Space nodes pandoc
      -- inserts between Str runs (e.g. "Σ_{S ∌ i}" is three Strs).
      table.insert(result, pandoc.Math("InlineMath", convert_to_math(tex)))
      buf = {}; mathing = false
    end
  end
  for _, inl in ipairs(inlines) do
    if inl.t == "Str" then
      if contains_math_marker(inl.text) then
        if contains_cjk(inl.text) then
          -- CJK text mixed with math in one Str (ZH doc): keep the Chinese
          -- prose out of math mode, send only the non-CJK math runs to buf.
          for _, r in ipairs(split_cjk(inl.text)) do
            if r.isMath then
              if pending then table.insert(buf, " "); pending = false end
              if not mathing then mathing = true end
              table.insert(buf, r.text)
            else
              flush()
              if pending then table.insert(result, pandoc.Space()); pending = false end
              table.insert(result, pandoc.Str(r.text))
            end
          end
        else
          if pending then table.insert(buf, " "); pending = false end
          if not mathing then mathing = true end
          table.insert(buf, inl.text)
        end
      else
        flush()
        if pending then table.insert(result, pandoc.Space()); pending = false end
        table.insert(result, inl)
      end
    elseif inl.t == "Space" then
      if mathing then
        pending = true
      else
        table.insert(result, inl)
      end
    else
      flush()
      if pending then table.insert(result, pandoc.Space()); pending = false end
      table.insert(result, inl)
    end
  end
  flush()
  return result
end

-- --- filter handlers ----------------------------------------------------------

-- --- code spans (script names) ----------------------------------------------

-- Inline code like `conj15_feas.py` renders as \texttt{...}, whose single
-- unbreakable word can overflow a line. Make script names breakable after
-- underscores and dots so long names (conj15_l1_range.py) wrap cleanly.
local function fix_code(el)
  local s = el.text
  if s:match("%.py$") or s:match("%.json$") or s:match("%.csv$") then
    local tex = s:gsub("_", "\\_\\allowbreak "):gsub("%.", ".\\allowbreak ")
    return pandoc.RawInline("tex", "\\texttt{" .. tex .. "}")
  end
  return el
end

local handlers = {}
for _, t in ipairs({ "Para", "Plain", "Header", "Emph", "Strong", "Quoted",
                     "Superscript", "Subscript", "SmallCaps", "Span",
                     "Link", "Cite" }) do
  handlers[t] = function(el)
    el.content = fix_inlines(el.content)
    return el
  end
end
handlers["Code"] = fix_code

-- --- EJOR technical check: 1.5-line spacing --------------------------------
-- Inject \usepackage{setspace} + \onehalfspacing into the generated preamble
-- so that regenerating the manuscript from the markdown preserves the
-- journal's required 1.5-line spacing (setspace's \onehalfspacing yields a
-- true 1.5 line height for 10/11/12 pt).  Applied via the pandoc
-- 'header-includes' meta variable, which the default LaTeX template emits in
-- the preamble before \begin{document}.
function handlers.Pandoc(doc)
  local inc = pandoc.RawInline("latex", "\\usepackage{setspace}\n\\onehalfspacing")
  local hdrs = doc.meta["header-includes"]
  if hdrs == nil then
    doc.meta["header-includes"] = pandoc.List{inc}
  else
    hdrs:insert(inc)
  end
  return doc
end

return handlers
