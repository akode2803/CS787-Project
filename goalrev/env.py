"""Order-desk environment: a small stateful tool environment (no Docker, no browser).

State: cart, shipping, coupon, gift note, checked_out. `checkout` is the only irreversible action.
Every other mutation can be undone with another tool call, which is what makes stale state testable.
"""
import json

ITEMS = ["notebook", "pen set", "backpack", "mug", "lamp"]
COLORS = ["red", "blue", "green", "black"]
CITIES = ["Delhi", "Mumbai", "Pune", "Kanpur", "Chennai"]
SPEEDS = ["standard", "express"]
COUPONS = ["SAVE10", "WELCOME5"]


def sku(color, item):
    return f"{color} {item}"


CATALOG = [sku(c, i) for i in ITEMS for c in COLORS]

TOOLS_DOC = """- list_products(): list available SKUs (format "<color> <item>").
- view_state(): show cart, shipping, coupon, gift note, order status.
- add_to_cart(sku, qty): add qty (default 1) of a SKU.
- remove_from_cart(sku, qty): remove qty of a SKU (omit qty to remove all of it).
- set_shipping(city, speed): set destination city and speed ("standard" or "express"; default "standard"). Replaces any earlier shipping setting.
- apply_coupon(code): apply a coupon code (needs a non-empty cart).
- remove_coupon(): remove the applied coupon.
- set_gift_note(text): attach a gift note.
- clear_gift_note(): remove the gift note.
- checkout(): place the order. IRREVERSIBLE; requires shipping to be set and a non-empty cart.
- finish(message): end the session when the request is fully handled."""

MUTATING = {"add_to_cart", "remove_from_cart", "set_shipping", "apply_coupon", "remove_coupon",
            "set_gift_note", "clear_gift_note", "checkout"}


class OrderDesk:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cart, self.shipping, self.coupon, self.note, self.checked_out = {}, None, None, None, False

    def state(self):
        return {"cart": dict(sorted(self.cart.items())), "shipping": dict(self.shipping) if self.shipping else None,
                "coupon": self.coupon, "note": self.note, "checked_out": self.checked_out}

    def apply(self, tool, args):
        """Execute one tool call; returns an observation string (errors are strings, never exceptions)."""
        args = args or {}
        if tool not in MUTATING and tool not in ("list_products", "view_state"):
            return f"ERROR: unknown tool '{tool}'."
        if self.checked_out and tool in MUTATING:
            return "ERROR: the order has already been placed."
        try:
            return getattr(self, "_" + tool)(**args)
        except TypeError as e:
            return f"ERROR: bad arguments for {tool}: {e}"

    # ---- read-only
    def _list_products(self):
        return "SKUs: " + ", ".join(CATALOG)

    def _view_state(self):
        return json.dumps(self.state())

    # ---- mutating
    def _add_to_cart(self, sku, qty=1):
        qty = int(qty)
        if sku not in CATALOG or qty < 1:
            return f"ERROR: invalid sku or qty ({sku!r}, {qty})."
        self.cart[sku] = self.cart.get(sku, 0) + qty
        return f"OK: cart now has {self.cart[sku]} x {sku}."

    def _remove_from_cart(self, sku, qty=None):
        if sku not in self.cart:
            return f"ERROR: {sku!r} is not in the cart."
        if qty is None or int(qty) >= self.cart[sku]:
            del self.cart[sku]
            if not self.cart:
                self.coupon = None   # a coupon cannot outlive an empty cart
            return f"OK: removed {sku} from the cart."
        self.cart[sku] -= int(qty)
        return f"OK: cart now has {self.cart[sku]} x {sku}."

    def _set_shipping(self, city, speed="standard"):
        if city not in CITIES or speed not in SPEEDS:
            return f"ERROR: city must be one of {CITIES}; speed one of {SPEEDS}."
        self.shipping = {"city": city, "speed": speed}
        return f"OK: shipping set to {city}, {speed}."

    def _apply_coupon(self, code):
        if not self.cart:
            return "ERROR: coupon needs a non-empty cart."
        if code not in COUPONS:
            return f"ERROR: invalid coupon {code!r}."
        self.coupon = code
        return f"OK: coupon {code} applied."

    def _remove_coupon(self):
        self.coupon = None
        return "OK: coupon removed."

    def _set_gift_note(self, text):
        self.note = str(text)
        return "OK: gift note set."

    def _clear_gift_note(self):
        self.note = None
        return "OK: gift note cleared."

    def _checkout(self):
        if not self.cart:
            return "ERROR: cart is empty."
        if not self.shipping:
            return "ERROR: shipping is not set."
        self.checked_out = True
        return "OK: order placed."


def replay(env, actions):
    """Apply recorded (tool, args) actions to env; returns history entries with observations (no LLM calls)."""
    hist = []
    for tool, args in actions:
        hist.append({"tool": tool, "args": args, "obs": env.apply(tool, args)})
    return hist
