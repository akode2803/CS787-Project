"""Task generator. Each task = initial request q0, one update u, oracle final request, and the exact expected end state.

Types mirror InterruptBench: addition (q0 incomplete), revision (q0 contains a mistake), retraction (q0 over-specified).
Scoring is exact match on the final environment state; no LLM judge.
"""
import random
from .env import ITEMS, COLORS, CITIES, SPEEDS, COUPONS, sku

NOTES = ["Happy birthday!", "Congratulations", "Thank you for everything", "Welcome to the team"]


def _state(cart, city, speed, coupon=None, note=None):
    return {"cart": dict(sorted(cart.items())), "shipping": {"city": city, "speed": speed},
            "coupon": coupon, "note": note, "checked_out": True}


def _order(q, color, item, city, speed=None, coupon=None, note=None):
    s = f"Order {q} {color} {item}" + ("s" if q > 1 and not item.endswith("set") else "")
    s += f" and ship to {city}"
    if speed: s += f" with {speed} shipping"
    if coupon: s += f", use coupon {coupon}"
    if note: s += f", with the gift note \"{note}\""
    return s + "."


def _pick2(rng, seq):
    a, b = rng.sample(seq, 2)
    return a, b


def make_addition(rng, i):
    item, item2 = _pick2(rng, ITEMS); color, color2 = rng.choice(COLORS), rng.choice(COLORS)
    q, q2 = rng.randint(1, 3), rng.randint(1, 3); city = rng.choice(CITIES)
    variant = rng.choice(["item_speed", "coupon_note"])
    if variant == "item_speed":
        q0 = _order(q, color, item, city)
        u = rng.choice([f"Also add {q2} {color2} {item2}, and make the shipping express.",
                        f"I forgot: please include {q2} {color2} {item2} too, and I need express shipping."])
        cart = {sku(color, item): q}; cart[sku(color2, item2)] = cart.get(sku(color2, item2), 0) + q2
        exp = _state(cart, city, "express")
        final = _order(q, color, item, city, "express") + f" Also {q2} {color2} {item2}."
    else:
        code, note = rng.choice(COUPONS), rng.choice(NOTES)
        q0 = _order(q, color, item, city, "standard")
        u = rng.choice([f"One more thing: apply coupon {code} and add the gift note \"{note}\".",
                        f"Please also use coupon {code}, and attach a gift note saying \"{note}\"."])
        exp = _state({sku(color, item): q}, city, "standard", code, note)
        final = _order(q, color, item, city, "standard", code, note)
    return dict(id=f"add-{i:02d}", type="addition", variant=variant, q0=q0, update=u, final_request=final, expected=exp)


def make_revision(rng, i):
    item, item2 = _pick2(rng, ITEMS); color1, color2 = _pick2(rng, COLORS)
    city1, city2 = _pick2(rng, CITIES); speed1, speed2 = _pick2(rng, SPEEDS)
    q = rng.randint(1, 3); q_new = q + rng.randint(1, 2)
    variant = rng.choice(["color_city", "qty_speed", "item_swap"])
    if variant == "color_city":
        q0 = _order(q, color1, item, city1, speed1)
        u = f"Sorry, I meant {color2}, not {color1}, and ship it to {city2} instead of {city1}."
        exp = _state({sku(color2, item): q}, city2, speed1); final = _order(q, color2, item, city2, speed1)
    elif variant == "qty_speed":
        q0 = _order(q, color1, item, city1, speed1)
        u = f"Correction: I need {q_new} of them, not {q}, and the shipping should be {speed2}."
        exp = _state({sku(color1, item): q_new}, city1, speed2); final = _order(q_new, color1, item, city1, speed2)
    else:
        q0 = _order(q, color1, item, city1, speed1)
        u = f"Wait, wrong product. I wanted the {color1} {item2}, not the {item}."
        exp = _state({sku(color1, item2): q}, city1, speed1); final = _order(q, color1, item2, city1, speed1)
    return dict(id=f"rev-{i:02d}", type="revision", variant=variant, q0=q0, update=u, final_request=final, expected=exp)


def make_retraction(rng, i):
    item, item2 = _pick2(rng, ITEMS); color, color2 = rng.choice(COLORS), rng.choice(COLORS)
    q, q2 = rng.randint(1, 3), rng.randint(1, 2); city = rng.choice(CITIES)
    variant = rng.choice(["extras", "item"])
    if variant == "extras":
        code, note = rng.choice(COUPONS), rng.choice(NOTES)
        q0 = _order(q, color, item, city, "express", code, note)
        u = rng.choice(["Forget the gift note and the coupon, and standard shipping is fine.",
                        "Actually, skip the gift note and coupon; regular shipping is okay."])
        exp = _state({sku(color, item): q}, city, "standard"); final = _order(q, color, item, city, "standard")
    else:
        q0 = _order(q, color, item, city, "standard") + f" Also add {q2} {color2} {item2}."
        u = f"Actually, drop the {color2} {item2}; I don't need it."
        exp = _state({sku(color, item): q}, city, "standard"); final = _order(q, color, item, city, "standard")
    return dict(id=f"ret-{i:02d}", type="retraction", variant=variant, q0=q0, update=u, final_request=final, expected=exp)


def generate(n_per_type=12, seed=0):
    tasks = []
    for maker in (make_addition, make_revision, make_retraction):
        for i in range(n_per_type):
            tasks.append(maker(random.Random(f"{seed}-{maker.__name__}-{i}"), i))   # task i does not depend on n_per_type
    return tasks
