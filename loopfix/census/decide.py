"""Applies RULE.md to downloaded summaries. Usage: decide.py DIR_WITH_SUMMARIES"""
import glob, json, os, sys

REFERENCE = "Qwen/Qwen3.5-0.8B"
LOOP_MIN, FIN_ACC_MIN = 0.20, 0.50
d = sys.argv[1]
rows, qualifying = [], []
for f in sorted(glob.glob(os.path.join(d, "*.summary.json"))):
    s = json.load(open(f))
    ok = []
    for name, v in s["settings"].items():
        a = v["all"]
        fa = a["finished_accuracy"]
        q = a["loop_rate"] >= LOOP_MIN and fa is not None and fa >= FIN_ACC_MIN
        rows.append((s["model"], name, a["loop_rate"], a["repetition_rate"], a["accuracy"], a["finished"], fa, a["median_tokens_finished"],
                     v["gsm8k"]["loop_rate"], v["math"]["loop_rate"], s["gen_s"], q))
        ok.append(q)
    if any(ok):
        qualifying.append(s["model"])

print(f"{'model':44} set loop  rep   acc   fin  finacc medtok gsmL mathL gen_s qual")
for m, n, l, r, a, fin, fa, mt, gl, ml, g, q in rows:
    print(f"{m:44} {n:3} {l:5.0%} {r:5.0%} {a:5.0%} {fin:4d} {('%.0f%%' % (fa * 100)) if fa is not None else 'n/a':>6} {mt if mt is not None else 0:6.0f} {gl:4.0%} {ml:5.0%} {g:5d} {'YES' if q else ''}")

others = [m for m in qualifying if m != REFERENCE]
outside = [m for m in others if "Qwen3.5" not in m]
print("\nQualifying:", qualifying)
print("Others:", len(others), "| outside the Qwen3.5 family:", len(outside))
print("DECISION:", "FAIL -> diffusion" if len(others) < 2 else ("PASS -> loop-fix" if outside else "WEAK PASS -> loop-fix, narrower claim, user decides"))
