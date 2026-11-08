"""Smallest paired difference (b-c)/n reaching two-sided exact McNemar p<0.05, given n tasks and discordance rate d."""
from math import comb
def p_two_sided(b, c):
    n = b + c
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)
def min_diff(n_disc):
    for diff in range(0, n_disc + 1):
        if (n_disc + diff) % 2: continue
        b = (n_disc + diff) // 2; c = n_disc - b
        if p_two_sided(b, c) < 0.05:
            return diff
    return None
rows = []
for n in (60, 100, 129, 165):
    r = [n]
    for d in (0.15, 0.25, 0.35):
        nd = round(n * d); diff = min_diff(nd)
        r.append((nd, diff, 100 * diff / n if diff is not None else None))
    rows.append(r)
for r in rows:
    print(r[0], [(nd, df, round(pc, 1)) for nd, df, pc in r[1:]])
