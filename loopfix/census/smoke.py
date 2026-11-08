"""Smoke test: reference model, 4+4 problems, short cap. Checks loading, chat template, sampling and grading."""
import gzip, json, subprocess

r = subprocess.run(["/content/venv/bin/python", "/content/census/worker.py", "--model", "Qwen/Qwen3.5-0.8B", "--out", "/content/census/smoke", "--n", "4", "--cap", "2048"],
                   capture_output=True, text=True, timeout=520)
out = r.stdout + r.stderr
print("EXIT", r.returncode)
print("\n".join(l[:200] for l in out.splitlines() if "PROMPT TAIL" in l or "SUMMARY" in l or "Error" in l or "error:" in l)[-1800:])
if r.returncode:
    print(out[-2500:])
else:
    rows = [json.loads(l) for l in gzip.open("/content/census/smoke/Qwen__Qwen3.5-0.8B.jsonl.gz", "rt")]
    for x in rows[:3] + rows[-2:]:
        print({k: x[k] for k in ("setting", "id", "cap", "tokens", "closed", "boxed", "ok")}, round(x["rep"], 2), repr(x["text"][-90:]))
