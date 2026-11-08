"""Runs the census model by model on the Colab VM. Blocking on purpose: a busy kernel keeps the session alive.
Each model has a time limit, and a failure is logged and skipped. Progress goes to /content/census/run.log.
"""
import os, subprocess, sys, time

PY, WORKER, OUT = "/content/venv/bin/python", "/content/census/worker.py", "/content/census/out"
LOG = "/content/census/run.log"
MODELS = ["Qwen/Qwen3.5-0.8B", "Qwen/Qwen3.5-2B", "Qwen/Qwen3.5-4B", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
          "open-thoughts/OpenThinker3-1.5B", "LiquidAI/LFM2.5-1.2B-Thinking", "HuggingFaceTB/SmolLM3-3B", "microsoft/Phi-4-mini-reasoning",
          "Qwen/Qwen3-1.7B", "Qwen/Qwen3-0.6B", "agentica-org/DeepScaleR-1.5B-Preview", "nvidia/OpenReasoning-Nemotron-1.5B"]
LIMIT_S = 40 * 60


def note(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")


for m in MODELS:
    slug = m.replace("/", "__")
    if os.path.exists(f"{OUT}/{slug}.summary.json"):
        note(f"SKIP {m} (already done)")
        continue
    note(f"START {m}")
    t = time.time()
    with open(f"/content/census/{slug}.log", "w") as f:
        try:
            code = subprocess.run([PY, WORKER, "--model", m, "--out", OUT], stdout=f, stderr=subprocess.STDOUT, timeout=LIMIT_S).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    note(f"END {m} code={code} {round(time.time() - t)}s")
    subprocess.run("pkill -f 'vllm|EngineCore' || true", shell=True)
    time.sleep(5)
note("ALL DONE")
