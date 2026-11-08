"""Task set v2: harder families with several cart lines and/or several edits (design in docs/TASKS_V2.md).

long      4 cart lines + shipping + coupon + gift note; the update changes ONE thing deep in the order (tests preserving the rest)
compound  2-3 lines; one update message contains THREE edits
relative  3 lines; the update refers to items by position ("the second item") and by relative amounts ("two more", "double")
null      the update changes nothing (confirmation / chatter); expected state = the q0 state (tests needless repair)
Late/early interruption is not a task family: it is the `--cut` option of the runner.
Every task has exactly one correct end state; scoring is exact match on the final environment state (no LLM judge).
"""
import random
from .env import ITEMS, COLORS, CITIES, SPEEDS, COUPONS, sku
from .tasks import NOTES, _state

ORD = {0: "first", 1: "second", 2: "third", 3: "fourth"}


def _np(q, color, item):
    return f"{q} {color} {item}" + ("s" if q > 1 and not item.endswith("set") else "")


def _text(sp):
    lines = [_np(l["q"], l["color"], l["item"]) for l in sp["lines"]]
    body = lines[0] if len(lines) == 1 else ", ".join(lines[:-1]) + f" and {lines[-1]}"
    s = f"Order {body} and ship to {sp['city']} with {sp['speed']} shipping"
    if sp["coupon"]: s += f", use coupon {sp['coupon']}"
    if sp["note"]: s += f", with the gift note \"{sp['note']}\""
    return s + "."


def _expected(sp):
    cart = {}
    for l in sp["lines"]: cart[sku(l["color"], l["item"])] = cart.get(sku(l["color"], l["item"]), 0) + l["q"]
    return _state(cart, sp["city"], sp["speed"], sp["coupon"], sp["note"])


def _base(rng, n_lines, with_coupon=True, with_note=True):
    items = rng.sample(ITEMS, n_lines)
    return {"lines": [{"item": it, "color": rng.choice(COLORS), "q": rng.randint(1, 3)} for it in items],
            "city": rng.choice(CITIES), "speed": rng.choice(SPEEDS),
            "coupon": rng.choice(COUPONS) if with_coupon else None, "note": rng.choice(NOTES) if with_note else None}


# --- edit operations: each returns (phrase, new_spec); `sp` is never mutated
def _copy(sp):
    return {**sp, "lines": [dict(l) for l in sp["lines"]]}


def op_color(rng, sp, j, rel=False):
    n = _copy(sp); l = n["lines"][j]; c2 = rng.choice([c for c in COLORS if c != l["color"]])
    ph = (f"swap the {ORD[j]} item for the same thing in {c2}" if rel else f"the {l['item']} should be {c2}, not {l['color']}")
    l["color"] = c2; return ph, n


def op_qty(rng, sp, j):
    n = _copy(sp); l = n["lines"][j]; q2 = rng.choice([q for q in (1, 2, 3, 4) if q != l["q"]])
    ph = f"I need {q2} of the {l['color']} {l['item']}, not {l['q']}"; l["q"] = q2; return ph, n


def op_more(rng, sp, j):
    n = _copy(sp); l = n["lines"][j]; k = rng.randint(1, 2)
    ph = f"make the {ORD[j]} item {k} more"; l["q"] += k; return ph, n


def op_double(rng, sp, j):
    n = _copy(sp); l = n["lines"][j]; ph = f"double the quantity of the {ORD[j]} item"; l["q"] *= 2; return ph, n


def op_drop(rng, sp, j):
    n = _copy(sp); l = n["lines"].pop(j); return f"drop the {l['color']} {l['item']}", n


def op_add(rng, sp, j=None):
    n = _copy(sp); used = {l["item"] for l in n["lines"]}; it = rng.choice([i for i in ITEMS if i not in used])
    l = {"item": it, "color": rng.choice(COLORS), "q": rng.randint(1, 3)}; n["lines"].append(l)
    return f"also add {_np(l['q'], l['color'], l['item'])}", n


def op_city(rng, sp, j=None):
    n = _copy(sp); c2 = rng.choice([c for c in CITIES if c != sp["city"]])
    ph = f"ship to {c2} instead of {sp['city']}"; n["city"] = c2; return ph, n


def op_speed(rng, sp, j=None):
    n = _copy(sp); s2 = "standard" if sp["speed"] == "express" else "express"
    ph = f"make the shipping {s2}"; n["speed"] = s2; return ph, n


def op_no_coupon(rng, sp, j=None):
    n = _copy(sp); n["coupon"] = None; return "skip the coupon", n


def op_no_note(rng, sp, j=None):
    n = _copy(sp); n["note"] = None; return "forget the gift note", n


def _apply(rng, sp, ops):
    phrases = []
    for fn, j in ops:
        ph, sp = fn(rng, sp, j); phrases.append(ph)
    return phrases, sp


def _task(tid, typ, variant, sp0, sp1, update):
    return dict(id=tid, type=typ, variant=variant, q0=_text(sp0), update=update,
                final_request=_text(sp1), expected=_expected(sp1))


def make_long(rng, i):
    sp0 = _base(rng, 4); j = rng.randrange(4)
    fn = rng.choice([op_color, op_qty, op_drop, op_add]); ph, sp1 = _apply(rng, sp0, [(fn, j)])
    return _task(f"lng-{i:02d}", "long", fn.__name__, sp0, sp1, f"Small change: {ph[0]}.")


def make_compound(rng, i):
    sp0 = _base(rng, rng.choice([2, 3]))
    combos = [[(op_qty, 0), (op_no_coupon, None), (op_add, None)],
              [(op_color, 0), (op_no_note, None), (op_speed, None)],
              [(op_city, None), (op_drop, 1), (op_no_coupon, None)],
              [(op_speed, None), (op_qty, 1), (op_no_note, None)]]
    ops = rng.choice(combos); ph, sp1 = _apply(rng, sp0, ops)
    return _task(f"cmp-{i:02d}", "compound", "+".join(f.__name__ for f, _ in ops), sp0, sp1,
                 f"Three changes: {ph[0]}; {ph[1]}; and {ph[2]}.")


def make_relative(rng, i):
    sp0 = _base(rng, 3); j = rng.randrange(3)
    fn = rng.choice([op_more, op_double, lambda r, s, k: op_color(r, s, k, rel=True)])
    ph, sp1 = _apply(rng, sp0, [(fn, j)])
    return _task(f"rel-{i:02d}", "relative", {op_more: "more", op_double: "double"}.get(fn, "same_item_new_color"), sp0, sp1,
                 ph[0][0].upper() + ph[0][1:] + ".")


NULL_UPDATES = ["Actually, nothing changes. Please keep the order exactly as I described it.",
                "Thanks! Please go ahead with the order as it is.",
                "One note: I'm travelling next week, but the order itself stays the same.",
                "Just confirming that the order is exactly what I wrote."]


def make_null(rng, i):
    sp0 = _base(rng, rng.choice([2, 3])); u = rng.choice(NULL_UPDATES)
    return _task(f"nul-{i:02d}", "null", "no_change", sp0, sp0, u)


def generate(n_per_type=12, seed=0):
    tasks = []
    for maker in (make_long, make_compound, make_relative, make_null):
        for i in range(n_per_type):
            tasks.append(maker(random.Random(f"v2-{seed}-{maker.__name__}-{i}"), i))   # task i does not depend on n_per_type
    return tasks
