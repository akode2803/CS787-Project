"""Loop census worker: one model per process, so a crash or GPU leak cannot affect the next model.
Rule and definitions: RULE.md. Usage: worker.py --model ID --out DIR [--n 50] [--cap 16384]
"""
import argparse, gzip, json, os, random, statistics, time

# ninja lives in the venv, which is not on PATH for a subprocess. The FlashInfer sampler needs a JIT build; the default sampler draws from the same distribution.
os.environ["PATH"] = "/content/venv/bin:/usr/local/cuda/bin:" + os.environ.get("PATH", "")
os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")

PROMPT_SUFFIX = "Please reason step by step, and put your final answer within \\boxed{}."
SETTINGS = {"P": 1.5, "N": 0.0}          # name -> presence penalty
SUBJECTS = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra",
            "number_theory", "prealgebra", "precalculus"]


def last_boxed(text):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j = i + len("\\boxed{")
    depth, k = 1, j
    while k < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        k += 1
    return text[j:k - 1] if depth == 0 else None


def problems(path, n):
    if os.path.exists(path):
        return json.load(open(path))
    from datasets import load_dataset
    rng = random.Random(787)
    gsm = list(load_dataset("openai/gsm8k", "main", split="train"))
    out = [{"id": f"gsm-{i}", "src": "gsm8k", "q": gsm[i]["question"], "gold": gsm[i]["answer"].split("####")[-1].strip().replace(",", "")}
           for i in rng.sample(range(len(gsm)), n)]
    math = []
    for s in SUBJECTS:
        math += [r for r in load_dataset("EleutherAI/hendrycks_math", s, split="train") if r["level"] in ("Level 3", "Level 4", "Level 5")]
    for i in rng.sample(range(len(math)), n):
        out.append({"id": f"math-{i}", "src": "math", "q": math[i]["problem"], "gold": last_boxed(math[i]["solution"])})
    json.dump(out, open(path, "w"))
    return out


def tail_repetition(ids, window=256, n=8):
    t = list(ids)[-window:]
    grams = [tuple(t[i:i + n]) for i in range(len(t) - n + 1)]
    return 1 - len(set(grams)) / len(grams) if grams else 0.0


def grade(text, gold):
    from math_verify import parse, verify
    b = last_boxed(text)
    if b is None or gold is None:
        return False
    try:
        return bool(verify(parse(f"${gold}$"), parse(f"${b}$")))
    except Exception:
        return False


def summarise(rows):
    fin = [r for r in rows if not r["cap"]]
    return {"n": len(rows), "loop_rate": sum(r["cap"] for r in rows) / len(rows),
            "repetition_rate": sum(r["cap"] and r["rep"] >= 0.3 for r in rows) / len(rows),
            "accuracy": sum(r["ok"] for r in rows) / len(rows),
            "finished": len(fin), "finished_accuracy": (sum(r["ok"] for r in fin) / len(fin)) if fin else None,
            "think_closed": sum(r["closed"] for r in rows) / len(rows), "boxed": sum(r["boxed"] for r in rows) / len(rows),
            "median_tokens_finished": statistics.median(r["tokens"] for r in fin) if fin else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=50); ap.add_argument("--cap", type=int, default=16384)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    probs = problems(os.path.join(a.out, f"problems_{a.n}.json"), a.n)
    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    prompts = [tok.apply_chat_template([{"role": "user", "content": f"{p['q']}\n{PROMPT_SUFFIX}"}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=True) for p in probs]
    print("PROMPT TAIL:", repr(prompts[0][-60:]), flush=True)
    t0 = time.time()
    kw = dict(model=a.model, dtype="bfloat16", max_model_len=a.cap + 1536, gpu_memory_utilization=0.85,
              max_num_seqs=256, seed=0, trust_remote_code=True)
    if "Qwen3.5" in a.model:
        kw["limit_mm_per_prompt"] = {"image": 0, "video": 0}
    llm = LLM(**kw)
    t1 = time.time()
    names = list(SETTINGS)
    params = [SamplingParams(temperature=0.6, top_p=0.95, top_k=20, presence_penalty=SETTINGS[s], max_tokens=a.cap) for s in names for _ in probs]
    outs = llm.generate(prompts * len(names), params)
    t2 = time.time()
    rows = []
    for idx, o in enumerate(outs):
        s, p, c = names[idx // len(probs)], probs[idx % len(probs)], o.outputs[0]
        rows.append({"model": a.model, "setting": s, "id": p["id"], "src": p["src"], "cap": c.finish_reason == "length",
                     "tokens": len(c.token_ids), "rep": tail_repetition(c.token_ids), "closed": "</think>" in c.text,
                     "boxed": last_boxed(c.text) is not None, "ok": grade(c.text, p["gold"]), "text": c.text})
    slug = a.model.replace("/", "__")
    with gzip.open(os.path.join(a.out, f"{slug}.jsonl.gz"), "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    summ = {"model": a.model, "load_s": round(t1 - t0), "gen_s": round(t2 - t1), "total_tokens": sum(r["tokens"] for r in rows), "settings": {}}
    for s in names:
        sub = [r for r in rows if r["setting"] == s]
        summ["settings"][s] = {"all": summarise(sub), **{src: summarise([r for r in sub if r["src"] == src]) for src in ("gsm8k", "math")}}
    json.dump(summ, open(os.path.join(a.out, f"{slug}.summary.json"), "w"), indent=1)
    print("SUMMARY", json.dumps({k: {m: v["all"][m] for m in ("loop_rate", "accuracy", "finished_accuracy")} for k, v in summ["settings"].items()}), "gen_s", summ["gen_s"], flush=True)


if __name__ == "__main__":
    main()
