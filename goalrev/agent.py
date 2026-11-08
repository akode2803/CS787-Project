"""ReAct-style agent: one LLM call per step, JSON action protocol (provider-agnostic, easy to script in tests)."""
import json
from .env import TOOLS_DOC

SYSTEM = f"""You operate an online order desk through tools. Fulfil the user's request exactly, then place the order with checkout and finish.
Reply with exactly ONE JSON object and nothing else:
{{"thought": "<one short sentence>", "action": {{"tool": "<tool name>", "args": {{...}}}}}}
Tools:
{TOOLS_DOC}
Rules: one action per reply; check view_state when unsure what has already been done; checkout only when the cart, shipping, coupon and gift note exactly match the request."""


def parse_action(text):
    """Return (tool, args) or None."""
    i = text.find("{")
    while i != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[i:])
            a = obj.get("action") if isinstance(obj, dict) else None
            if isinstance(a, dict) and isinstance(a.get("tool"), str):
                args = a.get("args") or {}
                return a["tool"], args if isinstance(args, dict) else {}
        except json.JSONDecodeError:
            pass
        i = text.find("{", i + 1)
    return None


def build_prompt(goal, history, extra=""):
    p = f"REQUEST:\n{goal}\n"
    if extra:
        p += f"\n{extra}\n"
    p += "\nACTIONS SO FAR:\n"
    p += "\n".join(f"{n}. {h['tool']}({json.dumps(h['args'])}) -> {h['obs']}" for n, h in enumerate(history, 1)) if history else "(none)"
    return p + "\n\nNext action (JSON only):"


def run_loop(env, llm, goal, history, max_steps=25, extra="", on_checkout=None, tag="agent"):
    """Run until finish / successful checkout / step limit. Mutates `history`. Returns list of executed (tool, args)."""
    done, bad, blocked = [], 0, 0
    for _ in range(max_steps):
        text = llm.generate(build_prompt(goal, history, extra), SYSTEM, tag)
        act = parse_action(text)
        if act is None:
            bad += 1
            history.append({"tool": "(invalid reply)", "args": {}, "obs": "Reply with one JSON object only."})
            if bad >= 3: break
            continue
        tool, args = act
        if tool == "finish":
            break
        if tool == "checkout" and on_checkout is not None:
            verdict = on_checkout(env, history, blocked)
            if verdict:
                blocked += 1
                history.append({"tool": tool, "args": args, "obs": verdict})
                continue
        obs = env.apply(tool, args)
        history.append({"tool": tool, "args": args, "obs": obs})
        done.append((tool, args))
        if env.checked_out:
            break
    return done
