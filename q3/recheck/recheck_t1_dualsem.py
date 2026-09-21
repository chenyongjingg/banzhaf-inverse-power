# -*- coding: utf-8 -*-
r"""Is Theorem 1's 100% mismatch rate a misaligned instrument, or a false theorem?

Verdict (see q3/recheck/README.md): misaligned instrument. An earlier re-run
used the *dual* game — a coalition wins iff it meets every edge of G (a vertex
cover) — whereas the manuscript defines v_G by "a coalition is winning iff the
voters outside it are contained in some edge of G". The two differ, and Theorem 1
is stated for the second.

This script is self-contained (no imports from the audit tree). It:
  * [control]  corrupts the formula's sign and requires many mismatches — a
               check that never rejects anything is not evidence;
  * [main]     exhaustively enumerates all 2^15 graphs on n = 6 and compares
               beta_i = |E| + (n-1) - 2*deg_G(i) against the definition.

Observed: 27,443 graphs pass the hypotheses, 0 mismatches; the control reports
27,443 mismatches. The same domain (n = 7, 1,887,277 graphs) gives 100%
mismatches under the vertex-cover game and 0 under the closure game.

Analytic derivation of the formula under the closure semantics, so the result
does not have to be taken on trust: S ∪ {i} wins iff S^c \ {i} is contained in
some edge, and S loses iff S^c is contained in no edge. Let T = S^c \ {i}.
  |T| = 0 : {i} lies in some edge (deg i >= 1) so S does not lose — not counted.
  |T| = 1 : T = {t} lies in an edge; S loses iff {t,i} is not an edge, giving
            (n-1) - deg(i) coalitions.
  |T| = 2 : T must itself be an edge, and S loses automatically (no edge has
            three vertices), giving |E| - deg(i) coalitions.
  |T| >= 3: T is contained in no edge — not counted.
Total: (n-1-deg i) + (|E|-deg i) = |E| + (n-1) - 2*deg_G(i).  QED

(The Chinese notes below are the original audit comments, kept verbatim.)

原注：Theorem 1 的 100% 不匹配，是**仪器错位**还是**定理为假**？—— 判据：换成修正后的 v_G 语义再跑一遍。

背景（不许跳过）：
    `audit_reports/rerun/recheck_t1_u.log` 里，Theorem 1 的复算是
        n=6: 满足前提 27443 个图，**不匹配 27443 个**
        n=7: 抽样 179845 个，**不匹配 179845 个**
    两处都是 **100%**。本项目已登记的判据：**100% 的不匹配率本身就是仪器错位的指纹**
    —— 真定理只会零星反例。所以先怀疑仪器，而不是先宣布定理倒了。

仪器在哪里错位：
    `_recheck_math.py:65` 的 `graph_win(n, E)` 写的是
        w(S) = 1  <=>  S 与**每条**边都相交（即 S 是 E 的顶点覆盖）
    这是 **"a coalition is winning iff it misses no edge of G"** ——
    也就是本轮跨树修复**改掉的那一句**。修正后的 v_G 是它的**对偶**：
        w(S) = 1  <=>  S 之外的那些投票人被**某一条边**包含（S^c ⊆ e）
    两句话不是同义改写，是**两个不同的博弈**。所以 100% 不匹配是预期的，
    只要定理 1 是照着修正后的 v_G 说的。

本脚本做的判定：
    [对照] 对修正后的博弈，把公式的符号改坏（+|E| -> -|E|），**必须**报大量不匹配
           —— 一个从不拒绝任何东西的对照不是证据。
    [主测] 修正后的博弈 + 公式 β_i = |E| + (n−1) − 2·deg_G(i)，穷举 n=6 全部 2^15 个图。

手算一遍为什么公式对（写在这里，好让读的人不必信代码）：
    S ∪ {i} 赢  <=>  S^c ∖ {i} ⊆ 某条边；   S 输  <=>  S^c ⊄ 任何边。
    令 T = S^c ∖ {i}：
      |T| = 0 : {i} ⊆ 某条边（deg i ≥ 1 时成立）⇒ S 不输，不计。
      |T| = 1 : T={t} 总在一条边里；S 输 <=> {t,i} 不是边 ⇒ 计数 (n−1) − deg(i)。
      |T| = 2 : 需要 T 本身是边；而 S 输恒成立（三元素不可能是边的子集）
                ⇒ 计数 |E| − deg(i)。
      |T| ≥ 3 : 不满足 T ⊆ 边，不计。
    合计 β_i = (n−1−deg i) + (|E|−deg i) = |E| + (n−1) − 2·deg_G(i)。∎
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def edges_of(n, mask):
    E, k = [], 0
    for a in range(n):
        for b in range(a + 1, n):
            if (mask >> k) & 1:
                E.append((a, b))
            k += 1
    return E


def degs(n, E):
    d = [0] * n
    for a, b in E:
        d[a] += 1
        d[b] += 1
    return d


def win_corrected(n, E):
    """修正后的 v_G：w(S)=1 <=> S^c ⊆ 某条边 e。"""
    def w(S):
        comp = ((1 << n) - 1) ^ S
        for a, b in E:
            if comp & ~((1 << a) | (1 << b)) == 0:
                return True
        return False
    return w


def win_vertexcover(n, E):
    """旧 semantics（本轮修复改掉的那句）：w(S)=1 <=> S 与每条边都相交。"""
    def w(S):
        for a, b in E:
            if not ((S >> a) & 1 or (S >> b) & 1):
                return False
        return True
    return w


def brute_swings(n, win):
    eta = [0] * n
    for S in range(1 << n):
        vS = win(S)
        for i in range(n):
            if S & (1 << i):
                continue
            if (not vS) and win(S | (1 << i)):
                eta[i] += 1
    return eta


n = 6
ne = n * (n - 1) // 2
bad_correct = bad_control = tested = skip = 0
shown = 0

for mask in range(1 << ne):
    E = edges_of(n, mask)
    d = degs(n, E)
    if any(x == 0 for x in d):                 # 前提：无孤立点
        skip += 1
        continue
    if max(d) == len(E) and len(E) > 0:        # 前提：非星
        skip += 1
        continue
    tested += 1
    pred = [len(E) + (n - 1) - 2 * d[i] for i in range(n)]

    got = brute_swings(n, win_corrected(n, E))
    if got != pred:
        bad_correct += 1
        if shown < 3:
            print("  [主测] ✗ E=%s 实测%s 公式%s" % (E, got, pred))
            shown += 1

    # 阳性对照：符号改坏，必须报错
    ctrl = [-(len(E)) + (n - 1) - 2 * d[i] for i in range(n)]
    if brute_swings(n, win_corrected(n, E)) != ctrl:
        bad_control += 1

    # 旧 semantics 的读数，用来对上日志里的 [21,9,9,3,3,3]
    if mask == 60:   # 边序 (0,1)(0,2)(0,3)(0,4)(0,5)(1,2)… ⇒ bit2,3,4,5 = (0,3),(0,4),(0,5),(1,2)
        print("  [留证] E=[(0,3),(0,4),(0,5),(1,2)] 旧 semantics swings = %s"
              % brute_swings(n, win_vertexcover(n, E)))

print()
print("=" * 74)
print("n=%s 穷举 2^%d = %d 个图；满足前提 %d 个（跳过 %d）" % (n, ne, 1 << ne, tested, skip))
print("  [主测] 修正后 v_G + 公式   不匹配 %d 个   %s"
      % (bad_correct, "✓ 全部匹配" if bad_correct == 0 else "★★ 尚有反例"))
print("  [对照] 公式符号改坏        不匹配 %d 个   %s"
      % (bad_control, "✓ 对照中（仪器能报错）" if bad_control == tested else "★★ 对照不中，仪器作废"))
print("=" * 74)
