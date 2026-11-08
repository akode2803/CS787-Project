"""CLI.  python -m goalrev.run stageA|stageB|report  (run from the project root)

stageA: for each task the agent works on q0 alone; its actions become the fixed prefix (cached per task).
stageB: for each task and strategy: replay the first K=floor(0.6*N) prefix actions (no LLM calls), then apply the strategy.
Results are appended to results/<name>/episodes.jsonl; finished (task, strategy) pairs are skipped on re-run.
"""
import argparse, json, os, threading, time
from concurrent.futures import ThreadPoolExecutor
from .env import OrderDesk, replay
from . import tasks as tasks_v1, tasks_v2
from .agent import run_loop
from .llm import make_llm, load_env
from .strategies import STRATEGIES, make_env_with_prefix

CUT = 0.6


def cut_point(n, cut=CUT):
    return max(1, min(int(cut * n), n - 1))


_lock = threading.Lock()
_local = threading.local()


def _llm(make):
    if not hasattr(_local, "llm"): _local.llm = make()      # one client + meter per worker thread
    return _local.llm


def _pool(jobs, fn, workers):
    if workers <= 1:
        for j in jobs: fn(j)
    else:
        with ThreadPoolExecutor(workers) as ex: list(ex.map(fn, jobs))


def stage_a(tasks, make_llm, outdir, max_steps=25, workers=1):
    os.makedirs(outdir, exist_ok=True)

    def one(t):
        f = os.path.join(outdir, f"{t['id']}.json")
        if os.path.exists(f): return
        llm = _llm(make_llm); env, hist = OrderDesk(), []; llm.new_episode()
        acts = run_loop(env, llm, t["q0"], hist, max_steps)
        with _lock:
            json.dump({"task_id": t["id"], "actions": acts, "state": env.state(), "llm": llm.meter.snapshot()}, open(f, "w"), indent=1)
            print("stageA", t["id"], len(acts), "actions", flush=True)
    _pool(tasks, one, workers)


def stage_b(tasks, strategies, make_llm, a_dir, out, max_steps=25, workers=1, retry_errors=False, cut=CUT):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        rows = [json.loads(l) for l in open(out)]
        if retry_errors:                                  # drop infrastructure failures so they are run again
            rows = [r for r in rows if not r["error"]]
            with open(out, "w") as f: f.writelines(json.dumps(r) + "\n" for r in rows)
        done = {(r["task_id"], r["strategy"]) for r in rows}
    jobs = []
    for t in tasks:
        fa = os.path.join(a_dir, f"{t['id']}.json")
        if not os.path.exists(fa): continue
        prefix = [tuple(a) for a in json.load(open(fa))["actions"]]
        if len(prefix) < 3: continue                      # too short to interrupt meaningfully
        jobs += [(t, s, prefix) for s in strategies if (t["id"], s) not in done]

    def one(job):
        t, s, prefix = job; k = cut_point(len(prefix), cut)
        env, hist = make_env_with_prefix(prefix, k)
        if env.checked_out: return                        # order already placed inside the prefix
        llm = _llm(make_llm); llm.new_episode(); t0 = time.time(); err = None; post, info = [], {}
        try:
            post, info = STRATEGIES[s](t, llm, env, hist, k, max_steps)
        except Exception as e:                            # infrastructure failure: record, never count as success
            err = repr(e)
        rec = {"task_id": t["id"], "type": t["type"], "variant": t["variant"], "strategy": s, "N": len(prefix), "K": k, "cut": cut,
               "success": err is None and env.state() == t["expected"], "error": err, "state": env.state(),
               "post_actions": post, "n_post_actions": len(post),
               "repeated_actions": sum(1 for a in post if a in prefix[:k] and a[0] not in ("view_state", "list_products")),
               "llm": llm.meter.snapshot(), "seconds": round(time.time() - t0, 1), "info": info}
        with _lock:
            with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
            print(t["id"], s, "OK" if rec["success"] else ("ERR" if err else "FAIL"), rec["llm"]["calls"], "calls", flush=True)
    _pool(jobs, one, workers)


def main():
    load_env(); load_env("GEMINI_API_KEYS.env")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stageA", "stageB", "report"])
    ap.add_argument("--n", type=int, default=12, help="tasks per type")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="main", help="results/<name>/")
    ap.add_argument("--strategies", default="B1,B2,B3a,B3b,M1")
    ap.add_argument("--set", default="v1", choices=["v1", "v2"], help="task set: v1 = addition/revision/retraction, v2 = long/compound/relative/null")
    ap.add_argument("--cut", type=float, default=CUT, help="stageB: interrupt after this fraction of the recorded actions (default 0.6)")
    ap.add_argument("--types", default="", help="comma list of task types to keep (default: all of the set)")
    ap.add_argument("--workers", type=int, default=1, help="parallel episodes (each worker has its own client; keys are rotated)")
    ap.add_argument("--retry-errors", action="store_true", help="stageB: re-run episodes that ended in an infrastructure error")
    ap.add_argument("--limit", type=int, default=0, help="only the first N tasks (smoke tests)")
    a = ap.parse_args()
    tasks = (tasks_v1 if a.set == "v1" else tasks_v2).generate(a.n, a.seed)
    if a.types: tasks = [t for t in tasks if t["type"] in a.types.split(",")]
    if a.limit: tasks = tasks[:a.limit]
    root = os.path.join("results", a.name)
    os.makedirs(root, exist_ok=True)
    if a.cmd == "report":
        from .analysis import report; return report(os.path.join(root, "episodes.jsonl"))
    json.dump(tasks, open(os.path.join(root, "tasks.json"), "w"), indent=1)
    make_llm()                                           # fail fast on missing keys / model
    if a.cmd == "stageA": stage_a(tasks, make_llm, os.path.join(root, "stageA"), workers=a.workers)
    else: stage_b(tasks, a.strategies.split(","), make_llm, os.path.join(root, "stageA"), os.path.join(root, "episodes.jsonl"),
                  workers=a.workers, retry_errors=a.retry_errors, cut=a.cut)


if __name__ == "__main__":
    main()
