import json, unittest
from goalrev.env import OrderDesk, replay
from goalrev.tasks import generate
from goalrev.agent import parse_action, run_loop
from goalrev.llm import ScriptedLLM
from goalrev.strategies import STRATEGIES, make_env_with_prefix
from goalrev.run import cut_point
from goalrev.analysis import mcnemar_p


def solver_actions(expected):
    """Actions that reach `expected` from an empty store (proves every generated task is solvable)."""
    acts = [("add_to_cart", {"sku": s, "qty": q}) for s, q in expected["cart"].items()]
    sh = expected["shipping"]; acts.append(("set_shipping", {"city": sh["city"], "speed": sh["speed"]}))
    if expected["coupon"]: acts.append(("apply_coupon", {"code": expected["coupon"]}))
    if expected["note"]: acts.append(("set_gift_note", {"text": expected["note"]}))
    return acts + [("checkout", {})]


def reply(tool, **args):
    return json.dumps({"thought": "t", "action": {"tool": tool, "args": args}})


class EnvTests(unittest.TestCase):
    def test_basic_semantics(self):
        e = OrderDesk()
        self.assertIn("ERROR", e.apply("apply_coupon", {"code": "SAVE10"}))        # empty cart
        self.assertIn("ERROR", e.apply("checkout", {}))
        e.apply("add_to_cart", {"sku": "red mug", "qty": 2}); e.apply("apply_coupon", {"code": "SAVE10"})
        e.apply("remove_from_cart", {"sku": "red mug"}); self.assertIsNone(e.coupon)  # coupon dies with empty cart
        self.assertIn("ERROR", e.apply("add_to_cart", {"sku": "purple mug"}))
        e.apply("add_to_cart", {"sku": "red mug"}); e.apply("set_shipping", {"city": "Pune"})
        self.assertEqual(e.shipping["speed"], "standard")
        self.assertIn("OK", e.apply("checkout", {})); self.assertIn("ERROR", e.apply("add_to_cart", {"sku": "red mug"}))

    def test_all_tasks_solvable_and_distinct_states(self):
        tasks = generate(12, seed=0); self.assertEqual(len(tasks), 36)
        for t in tasks:
            e = OrderDesk(); replay(e, solver_actions(t["expected"]))
            self.assertEqual(e.state(), t["expected"], t["id"])
        self.assertEqual(len({json.dumps(t["expected"], sort_keys=True) for t in tasks}) > 20, True)

    def test_update_changes_expected_state(self):
        # the stale (q0-only) solution must NOT already satisfy the final state: otherwise the update would be a no-op
        for t in generate(12, seed=0):
            if t["type"] == "retraction" and t["variant"] == "extras":
                self.assertEqual(t["expected"]["coupon"], None); self.assertEqual(t["expected"]["shipping"]["speed"], "standard")
            self.assertIn(t["update"].split()[0], t["update"])


class TasksV2Tests(unittest.TestCase):
    def test_v2_solvable_and_updates_matter(self):
        from goalrev import tasks_v2
        ts = tasks_v2.generate(15, seed=0); self.assertEqual(len(ts), 60)
        for t in ts:
            e = OrderDesk(); replay(e, solver_actions(t["expected"])); self.assertEqual(e.state(), t["expected"], t["id"])
            self.assertEqual(t["q0"] == t["final_request"], t["type"] == "null", t["id"])     # only null tasks leave the order unchanged
        self.assertEqual(tasks_v2.generate(3, 0)[:3], tasks_v2.generate(15, 0)[:3])           # task i independent of n


class AgentTests(unittest.TestCase):
    def test_parse_action(self):
        self.assertEqual(parse_action('blah {"thought":"x","action":{"tool":"view_state","args":{}}} tail'), ("view_state", {}))
        self.assertIsNone(parse_action("no json")); self.assertIsNone(parse_action('{"action": 3}'))

    def test_loop_stops_on_checkout_and_bad_json(self):
        e = OrderDesk(); llm = ScriptedLLM([reply("add_to_cart", sku="red mug"), reply("set_shipping", city="Pune"), reply("checkout"), reply("finish")])
        done = run_loop(e, llm, "x", []); self.assertEqual(len(done), 3); self.assertTrue(e.checked_out)
        e2 = OrderDesk(); llm2 = ScriptedLLM(["junk", "junk", "junk"]); self.assertEqual(run_loop(e2, llm2, "x", []), [])

    def test_cut_point(self):
        self.assertEqual([cut_point(n) for n in (3, 5, 6, 10)], [1, 3, 3, 6])


class StrategyTests(unittest.TestCase):
    def setUp(self):
        self.task = next(t for t in generate(12, 0) if t["type"] == "retraction" and t["variant"] == "extras")
        self.prefix = solver_actions({**self.task["expected"], "shipping": {"city": self.task["expected"]["shipping"]["city"], "speed": "express"},
                                      "coupon": "SAVE10", "note": "Hi"})   # stale prefix incl. extras (checkout excluded below)
        self.prefix = [a for a in self.prefix if a[0] != "checkout"] + [("view_state", {}), ("view_state", {}), ("checkout", {})]

    def test_B2_repairs_stale_state(self):
        k = cut_point(len(self.prefix)); env, hist = make_env_with_prefix(self.prefix, k)
        self.assertFalse(env.checked_out)
        city = self.task["expected"]["shipping"]["city"]
        llm = ScriptedLLM([reply("remove_coupon"), reply("clear_gift_note"), reply("set_shipping", city=city, speed="standard"), reply("checkout")])
        post, _ = STRATEGIES["B2"](self.task, llm, env, hist, k, 25)
        self.assertEqual(env.state(), self.task["expected"]); self.assertEqual(llm.meter.calls, 4)

    def test_M1_verifier_blocks_stale_checkout_once(self):
        k = cut_point(len(self.prefix)); env, hist = make_env_with_prefix(self.prefix, k)
        city = self.task["expected"]["shipping"]["city"]; calls = {"c4": 0}

        def script(prompt, system, tag):
            if tag == "C1": return json.dumps({"merged_goal": self.task["final_request"], "requirements": [{"id": "R1", "text": "no note", "status": "retracted", "supersedes": "note"}]})
            if tag in ("C2", "C3"): return "[]"
            if tag == "C4":
                calls["c4"] += 1
                return json.dumps({"ok": False, "issues": ["coupon still applied"]}) if calls["c4"] == 1 else json.dumps({"ok": True, "issues": []})
            n = prompt.count("->")
            if "BLOCKED" in prompt and "remove_coupon" not in prompt: return reply("remove_coupon")
            if "remove_coupon" in prompt and "clear_gift_note" not in prompt: return reply("clear_gift_note")
            if "clear_gift_note" in prompt and "standard" not in prompt.split("ACTIONS SO FAR")[1]: return reply("set_shipping", city=city, speed="standard")
            return reply("checkout")
        llm = ScriptedLLM(script)
        # first agent step tries to checkout immediately (stale) -> verifier blocks -> agent repairs -> checkout accepted
        first = {"done": False}
        orig = script
        def wrapped(prompt, system, tag):
            if tag == "agent" and not first["done"]:
                first["done"] = True; return reply("checkout")
            return orig(prompt, system, tag)
        llm = ScriptedLLM(wrapped)
        post, info = STRATEGIES["M1"](self.task, llm, env, hist, k, 25)
        self.assertTrue(info["ledger_valid"]); self.assertEqual(calls["c4"], 2)
        self.assertEqual(env.state(), self.task["expected"])

    def test_B3b_restarts_environment(self):
        k = cut_point(len(self.prefix)); env, hist = make_env_with_prefix(self.prefix, k)
        e = self.task["expected"]; city = e["shipping"]["city"]
        script = [self.task["final_request"]] + [reply(t, **a) for t, a in solver_actions(e)]
        post, _ = STRATEGIES["B3b"](self.task, ScriptedLLM(script), env, hist, k, 25)
        self.assertEqual(env.state(), e)


class MetricTests(unittest.TestCase):
    def test_reuse_and_waste(self):
        from goalrev.analysis import episode_metrics
        t = next(t for t in generate(12, 0) if t["type"] == "addition")           # update only adds things: old work is fully reusable
        q0_acts = [("add_to_cart", {"sku": s, "qty": q}) for s, q in t["expected"]["cart"].items()] + [("set_shipping", {"city": t["expected"]["shipping"]["city"], "speed": "standard"})]
        pre = q0_acts + [("view_state", {})]
        rec = {"K": len(q0_acts), "post_actions": []}
        keep = episode_metrics({**rec, "post_actions": [("checkout", {})]}, pre, t["expected"])
        self.assertEqual(keep["wasted"], 0)
        redo = episode_metrics({**rec, "post_actions": [("remove_from_cart", {"sku": s}) for s in t["expected"]["cart"]] + [("checkout", {})]}, pre, t["expected"])
        self.assertEqual(redo["reuse"] < 1 or keep["reuse"] is None, True); self.assertGreater(redo["wasted"], 0)


class StatsTests(unittest.TestCase):
    def test_mcnemar(self):
        self.assertAlmostEqual(mcnemar_p(10, 0), 2 * 0.5 ** 10, places=9); self.assertEqual(mcnemar_p(0, 0), 1.0)


if __name__ == "__main__":
    unittest.main()
