"""Interruption-handling strategies. All share the same replayed prefix; they differ only in what happens after the update.

B1  no update          continue with q0 only (information lower bound, as in InterruptBench)
B2  naive append       q0 + "[User update after action K] u"; history kept (InterruptBench's own protocol)
B2+ append + reminder  B2 plus one extra call that restates the current requirements (generic, unstructured control)
B3a fresh replan       merged goal from one LLM call; history dropped; live state kept
B3b restart            merged goal; environment reset; run from step 0
O   oracle restart     ground-truth final request; environment reset (upper reference)
M1  goal revision      C1 ledger -> C2 prefix audit -> C3 repair note -> resume with history -> C4 verifier before checkout
"""
import json
from .agent import run_loop
from .env import OrderDesk, replay

MERGE_SYS = "You rewrite customer requests. Output only the final request text, nothing else."


def _merge(llm, q0, u):
    p = (f"ORIGINAL REQUEST:\n{q0}\n\nFOLLOW-UP FROM THE SAME CUSTOMER:\n{u}\n\n"
         "Write the single complete final request: apply corrections, add new items, drop anything the customer withdrew. "
         "Do not mention the original request or the follow-up.")
    return llm.generate(p, MERGE_SYS, "merge").strip()


def _json(text):
    i = text.find("{") if "{" in text else text.find("[")
    if i < 0: return None
    try:
        return json.JSONDecoder().raw_decode(text[i:])[0]
    except json.JSONDecodeError:
        return None


def make_env_with_prefix(prefix_actions, k):
    env = OrderDesk(); hist = replay(env, prefix_actions[:k]); return env, hist


def s_B1(task, llm, env, hist, k, max_steps):
    return run_loop(env, llm, task["q0"], hist, max_steps), {}


def s_B2(task, llm, env, hist, k, max_steps):
    goal = f"{task['q0']}\n\n[User update after action {k}] {task['update']}"
    return run_loop(env, llm, goal, hist, max_steps), {}


def s_B2plus(task, llm, env, hist, k, max_steps):
    goal = f"{task['q0']}\n\n[User update after action {k}] {task['update']}"
    reminder = llm.generate(f"{goal}\n\nList every requirement that currently applies to this order (items, quantities, shipping, coupon, gift note), as a short bullet list.", "", "reminder")
    extra = ("REMINDER: re-read all instructions; the customer has updated the request. Current requirements:\n" + reminder.strip() +
             "\nCompare them with view_state before acting.")
    return run_loop(env, llm, goal, hist, max_steps, extra=extra), {}


def s_B3a(task, llm, env, hist, k, max_steps):
    merged = _merge(llm, task["q0"], task["update"])
    extra = f"Some actions may already have been taken. Current store state: {json.dumps(env.state())}"
    return run_loop(env, llm, merged, [], max_steps, extra=extra), {"merged": merged}


def s_B3b(task, llm, env, hist, k, max_steps):
    merged = _merge(llm, task["q0"], task["update"]); env.reset()
    return run_loop(env, llm, merged, [], max_steps), {"merged": merged}


def s_O(task, llm, env, hist, k, max_steps):
    env.reset()
    return run_loop(env, llm, task["final_request"], [], max_steps), {}


def s_M1(task, llm, env, hist, k, max_steps, use_c2=True, use_c4=True):
    info = {}
    # C1: goal reconciler -> merged goal + requirement ledger
    c1 = llm.generate(
        f"ORIGINAL REQUEST:\n{task['q0']}\n\nFOLLOW-UP:\n{task['update']}\n\n"
        'Return JSON: {"merged_goal": "<complete final request>", "requirements": [{"id": "R1", "text": "...", '
        '"status": "unchanged|added|modified|retracted", "supersedes": "<old value or null>"}]}. '
        "List every requirement (items with quantities, shipping city and speed, coupon, gift note).", MERGE_SYS, "C1")
    ledger = _json(c1)
    info["ledger_valid"] = isinstance(ledger, dict) and "requirements" in ledger
    merged = ledger.get("merged_goal") if info["ledger_valid"] else None
    merged = merged or _merge(llm, task["q0"], task["update"])
    ledger_txt = json.dumps(ledger["requirements"]) if info["ledger_valid"] else "(unavailable)"
    extra = f"REQUIREMENT LEDGER (authoritative, latest): {ledger_txt}"
    # C2 + C3: audit executed prefix against the ledger, then write a short repair note
    if use_c2:
        steps = "\n".join(f"{n}. {h['tool']}({json.dumps(h['args'])}) -> {h['obs']}" for n, h in enumerate(hist, 1)) or "(none)"
        audit = llm.generate(
            f"LEDGER: {ledger_txt}\nCURRENT STATE: {json.dumps(env.state())}\nACTIONS ALREADY EXECUTED:\n{steps}\n\n"
            'For each executed action return a JSON list: [{"step": n, "verdict": "KEEP|REPAIR|STALE|UNDO", "reason": "..."}]. '
            "STALE/UNDO means the effect conflicts with the ledger and must be changed.", MERGE_SYS, "C2")
        note = llm.generate(
            f"LEDGER: {ledger_txt}\nCURRENT STATE: {json.dumps(env.state())}\nAUDIT: {audit}\n\n"
            "Write a repair note (max 100 words): what to keep, which settings or items to change or remove (name the exact tools), "
            "what is still missing. Plain text.", MERGE_SYS, "C3")
        extra += f"\nREPAIR NOTE: {note.strip()}"
    verifier = None
    if use_c4:
        def verifier(env_, history, blocked):
            if blocked >= 2: return None
            v = _json(llm.generate(
                f"LEDGER: {ledger_txt}\nSTATE ABOUT TO BE ORDERED: {json.dumps(env_.state())}\n"
                'Does the state satisfy every latest requirement and contain nothing that was retracted or superseded? '
                'Return JSON {"ok": true|false, "issues": ["..."]}.', MERGE_SYS, "C4"))
            if isinstance(v, dict) and v.get("ok") is False:
                return "CHECKOUT BLOCKED by verifier: " + "; ".join(map(str, v.get("issues", []))) + ". Fix these, then checkout again."
            return None
    return run_loop(env, llm, merged, hist, max_steps, extra=extra, on_checkout=verifier), info


STRATEGIES = {
    "B1": s_B1, "B2": s_B2, "B2+": s_B2plus, "B3a": s_B3a, "B3b": s_B3b, "O": s_O,
    "M1": s_M1,
    "M1-noC4": lambda *a, **k: s_M1(*a, use_c4=False, **k),
    "M1-noC2": lambda *a, **k: s_M1(*a, use_c2=False, **k),
}
