"""Builds demo_data.json: real recorded diffusion answers, one entry per token with the step at which it was committed.

  /opt/miniconda3/bin/python3 -I build_demo_data.py RAW_DIR REV_DIR REVDATA_DIR INFILL_DIR GSM8K_QUESTION_JSON OUT.json

Nothing is simulated: tokens are the stored answer_ids decoded one by one with each arm's tokenizer, and commit steps
are the stored commit_step values from the evaluation runs (8-9 Nov 2026).
"""
import json, sys
from pathlib import Path
from tokenizers import Tokenizer

raw, rev, revdata, infill, question_file, out = map(Path, sys.argv[1:7])
TOK = {"qwen": Tokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"),
       "llada": Tokenizer.from_pretrained("GSAI-ML/LLaDA-8B-Instruct")}


def record(directory, arm, stem, rid):
    for line in open(directory / arm / f"{stem}.jsonl"):
        r = json.loads(line)
        if r["id"] == rid:
            return r
    raise KeyError((arm, stem, rid))


def tokens(r, tok):
    special = set(r.get("special_in_answer", []))
    out = []
    for tid, step in zip(r["answer_ids"], r["commit_step"]):
        out.append({"t": "" if tid in special else tok.decode([tid], skip_special_tokens=False), "s": step, "end": tid in special})
    return {"tokens": out, "steps": max(r["commit_step"]) + 1, "positions": r["positions"], "correct": bool(r["correct"]),
            "seconds": round(r["batch_seconds"] / r["batch"], 2)}


question = json.load(open(question_file))
infill_row = next(json.loads(l) for l in open(infill / "HumanEval-SingleLineInfilling.jsonl")
                  if json.loads(l)["task_id"] == "SingleLineInfilling/HumanEval/55/L0")
facts = {r["id"]: r for r in map(json.loads, open(revdata / "eval_reverse.jsonl"))}
facts_fwd = {r["id"]: r for r in map(json.loads, open(revdata / "eval_forward.jsonl"))}

demo = {
    "gsm8k": {"question": question["question"], "id": "GSM8K test #462", "answer": "71", "runs": {
        "released_256": {"label": "BYOD-Qwen (released), 256 steps", **tokens(record(raw, "qwen-byod-released", "gsm8k", "462"), TOK["qwen"])},
        "released_32": {"label": "BYOD-Qwen (released), 32 steps", **tokens(record(raw, "qwen-byod-released", "gsm8k_s32", "462"), TOK["qwen"])},
        "llada_256": {"label": "LLaDA 8B, 256 steps", **tokens(record(raw, "llada", "gsm8k", "462"), TOK["llada"])}}},
    "infill": {"prefix": infill_row["prompt"], "suffix": infill_row["suffix"], "id": "HumanEval single-line infilling, problem 55",
               "canonical": infill_row["canonical_solution"], "runs": {
        "released_true": {"label": "BYOD-Qwen, true gap length", **tokens(record(raw, "qwen-byod-released", "he_single", infill_row["task_id"]), TOK["qwen"])},
        "released_x1.5": {"label": "BYOD-Qwen, 1.5× gap length", **tokens(record(raw, "qwen-byod-released", "he_single_gapx1.5", infill_row["task_id"]), TOK["qwen"])},
        "llada_x1.5": {"label": "LLaDA 8B, 1.5× gap length", **tokens(record(raw, "llada", "he_single_gapx1.5", infill_row["task_id"]), TOK["llada"])}}},
    "reversal": {"fact": f'{facts["fact-0001"]["answer"]} is the {facts_fwd["fact-0001"]["answer"]}.', "runs": {
        "forward": {"label": "Forward: " + facts_fwd["fact-0001"]["prompt"], **tokens(record(rev, "qwen-byod-retrained+facts10k", "rev_forward", "fact-0001"), TOK["qwen"])},
        "reverse": {"label": "Reverse: " + facts["fact-0001"]["prompt"], **tokens(record(rev, "qwen-byod-retrained+facts10k", "rev_reverse", "fact-0001"), TOK["qwen"])}}},
}
json.dump(demo, open(out, "w"), ensure_ascii=False)
for section, d in demo.items():
    for k, run in d["runs"].items():
        text = "".join(t["t"] for t in run["tokens"])
        print(section, k, run["steps"], "steps", run["positions"], "positions", "correct" if run["correct"] else "wrong", repr(text[:70]))
