"""Paired analysis: success by strategy and type, exact McNemar vs B2, task-clustered bootstrap CI, cost columns."""
import json, os, random
from math import comb
from collections import defaultdict
from .env import OrderDesk, replay

READ_ONLY = ("view_state", "list_products")


def components(state):
    """State as {component: value}; a component is one cart line, the shipping choice, the coupon or the gift note."""
    c = {("cart", sku): q for sku, q in state["cart"].items()}
    if state["shipping"]: c[("ship",)] = tuple(sorted(state["shipping"].items()))
    if state["coupon"]: c[("coupon",)] = state["coupon"]
    if state["note"]: c[("note",)] = state["note"]
    return c


def touched(tool, args):
    if tool in ("add_to_cart", "remove_from_cart"): return ("cart", args.get("sku"))
    if tool == "set_shipping": return ("ship",)
    if tool in ("apply_coupon", "remove_coupon"): return ("coupon",)
    if tool in ("set_gift_note", "clear_gift_note"): return ("note",)
    return None


def episode_metrics(rec, prefix, expected):
    """Plan-reuse and efficiency metrics, computed from the stored prefix, cut point K and post-cut actions (no model needed).
    reuse     = share of components that were already correct at the cut and that the strategy never touched afterwards.
    wasted    = post-cut mutating actions that touched a component that was already correct at the cut (undo / redo of good work).
    min_acts  = number of components that differ between the state at the cut and the final goal, plus 1 for checkout
                (a lower-bound proxy for the cheapest repair, not a proven optimum).
    overhead  = mutating post-cut actions minus min_acts."""
    env = OrderDesk(); replay(env, prefix[:rec["K"]])
    at_k, goal = components(env.state()), components(expected)
    correct = {c for c, v in at_k.items() if goal.get(c) == v}
    post = [(t, a) for t, a in rec["post_actions"] if t not in READ_ONLY and t != "checkout"]
    hit = {touched(t, a) for t, a in post}
    min_acts = len({c for c in set(at_k) | set(goal) if at_k.get(c) != goal.get(c)}) + 1
    return {"reuse": (len(correct - hit) / len(correct)) if correct else None,
            "wasted": sum(1 for t, a in post if touched(t, a) in correct),
            "overhead": len(post) + 1 - min_acts}


def mcnemar_p(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def boot_ci(diffs, reps=5000, seed=0):
    if not diffs: return (float("nan"),) * 2
    rng = random.Random(seed); n = len(diffs)
    ms = sorted(sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(reps))
    return ms[int(0.025 * reps)], ms[int(0.975 * reps) - 1]


def report(path, baseline="B2"):
    rows = [json.loads(l) for l in open(path)]
    root = os.path.dirname(path); tasks = {t["id"]: t for t in json.load(open(os.path.join(root, "tasks.json")))}
    for r in rows:
        pre = [tuple(a) for a in json.load(open(os.path.join(root, "stageA", r["task_id"] + ".json")))["actions"]]
        r["m"] = episode_metrics(r, pre, tasks[r["task_id"]]["expected"])
    by = defaultdict(dict)                                   # (task) -> strategy -> record
    for r in rows: by[r["task_id"]][r["strategy"]] = r
    strategies = sorted({r["strategy"] for r in rows}); types = sorted({r["type"] for r in rows}) + ["ALL"]
    print(f"episodes: {len(rows)}  errors: {sum(1 for r in rows if r['error'])}\n")
    print(f"{'strategy':8} {'type':11} {'n':>3} {'success':>8} {'calls':>6} {'tok_in':>8} {'post_act':>8} {'repeat':>6} {'reuse':>6} {'wasted':>6} {'overhd':>6}")
    for s in strategies:
        for ty in types:
            rs = [r for r in rows if r["strategy"] == s and (ty == "ALL" or r["type"] == ty)]
            if not rs: continue
            m = lambda f: sum(f(r) for r in rs) / len(rs)
            print(f"{s:8} {ty:11} {len(rs):3} {100*m(lambda r: r['success']):7.1f}% {m(lambda r: r['llm']['calls']):6.1f} "
                  f"{m(lambda r: r['llm']['tokens_in']):8.0f} {m(lambda r: r['n_post_actions']):8.1f} {m(lambda r: r['repeated_actions']):6.2f} "
                  f"{(lambda v: sum(v)/len(v) if v else float('nan'))([r['m']['reuse'] for r in rs if r['m']['reuse'] is not None]):6.2f} "
                  f"{m(lambda r: r['m']['wasted']):6.2f} {m(lambda r: r['m']['overhead']):6.2f}")
    print(f"\nPaired difference vs {baseline} (strategy minus {baseline}; exact McNemar p; 95% task-bootstrap CI)")
    for s in strategies:
        if s == baseline: continue
        for ty in types:
            pairs = [(t[s]["success"], t[baseline]["success"]) for t in by.values()
                     if s in t and baseline in t and (ty == "ALL" or t[s]["type"] == ty)]
            if not pairs: continue
            b = sum(1 for x, y in pairs if x and not y); c = sum(1 for x, y in pairs if y and not x)
            lo, hi = boot_ci([int(x) - int(y) for x, y in pairs])
            print(f"{s:8} {ty:11} n={len(pairs):3} wins={b:2} losses={c:2} diff={100*(b-c)/len(pairs):+6.1f} pts  p={mcnemar_p(b, c):.3f}  CI=[{100*lo:+.1f}, {100*hi:+.1f}]")
