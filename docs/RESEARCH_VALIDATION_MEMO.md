# Research-Validation Memo (Phase 2) — Goal Revision in Long-Running LLM Agents

Date: 2026-10-28. Evidence labels as in the blueprint: [V] verified in a primary source, [R] reported by a source (abstract/README level), [O] our read-only checks, [H] hypothesis, [U] unverified. Nothing here comes from running the benchmark or any model.

## Verdict
The direction is sound and executable **as a controlled empirical study with a simple candidate method**. It is not defensible as a "novel algorithm" or "new benchmark" contribution. The main risk is infrastructure (self-hosted WebArena), not science.

## 1. Base paper and repository
- Paper exists and matches the brief: arXiv:2604.00892, 1 Apr 2026, 19 authors, "Preprint. Under review." [V]. It defines addition/revision/retraction, builds InterruptBench from WebArena-Lite (165 tasks), replays a baseline trajectory and injects the update at 60% by default, evaluates six backbones, and **evaluates no handling method** [V].
- Repository exists (commit 17da111, 2026-07-08): runner, replay logic, scorers, six raw JSON files x 165 items, WebArena setup scripts [V/O]. No released trajectories or results; no top-level licence; setup friction expected (pinned old deps, hard-coded scorer model, stale doc paths) [O].
- Credibility flags: Table E.3 has duplicated rows; Qwen model name inconsistent; S/F caption inverted in Appendix B; 30 vs 50 step budget [V]. Treat numbers as claims until reproduced.

## 2-3. Closest related work and what is already done [R, abstract/README level]
- InterventionBench (Findings EMNLP 2026): AppWorld + WebArena, 2,250 instances, 12 LLMs; README says planning/memory wrappers (Reflexion, AdaPlanner, Mem0, HippoRAG, +4) help swap/drop but barely change add.
- Task-state study (2609.25686): explicit state graph with cancel/rewire and an enforcement gate; large gains in a procurement domain.
- SWE-Shift (2610.32196), FeatureLoop (2610.35488), Evolving User Intent (2607.20734), ContinuityBench: benchmarks/analyses of mid-task change; none proposes an agent method per the abstracts.
- Already done: benchmarks for mid-task goal change (web, app, coding); evidence that all frontier models degrade; generic wrappers failing on additions; explicit state tracking with enforcement outside web UIs; recap prompts as partial fix.

## 4-5. Gap and novelty of selective plan repair
- **Open (our niche):** explicit goal diff (added/modified/retracted) + audit of already-executed actions, evaluated on a grounded web benchmark with a fixed replayed prefix, with (a) a compute-matched control, (b) replanning vs restart cost comparison, (c) breakdown by type and position, (d) honest reporting when it does not help [H; search-limited].
- **Not novel:** the idea of explicit state/requirement tracking, selective recomputation, or plan repair vs replanning (classical planning; Atomic Task Graph; Execution Lineage; SagaLLM; Task-state study).
- Rating [H]: algorithmic novelty low; empirical-gap novelty modest; course-project value high if executed carefully. The field changes monthly; re-run the search two weeks before the deadline.

## 6. Does the benchmark support the experiments we want?
Supports: paired comparisons (shared replayed prefix), interruption position (`interrupt_at_pct`), three types, multi-interruption (chained stages), native evaluators, token/action accounting [V/O].
Limits: (a) the agent has no explicit plan, so "plan repair" must wrap the action history [O]; (b) interruptions are informational, so invalidation shows up only as stale page state [V]; (c) in replay the update arrives between actions, so "currently executing" and irreversible-action handling cannot be studied beyond what the tasks naturally contain [O]; (d) the no-interruption baseline is an information lower bound, not a stale-goal control [O]; (e) saved prefixes contain actions only, not reasoning [O]; (f) Stage A prefixes must be regenerated per backbone [O].

## 7. Simplest credible environment
InterruptBench subset on self-hosted WebArena: the 129 single-site tasks of Shopping, Shopping-admin, GitLab, Reddit (skip Map/Wikipedia; map backend ~180 GB [R]). Fallback if no host by end of week 2: tau-bench-style environment with our own interruption data (adds ~1 week of data work, lower external validity) [H, not inspected].

## 8. Baselines and method (precise definitions in blueprint Section 6)
B1 no update; B2 naive append (benchmark protocol); B2+ append + content-free reminder with matched extra tokens; B3a fresh-context replan from live page; B3b restart from step 0 with merged goal; O oracle restart; M1 = goal reconciler (ledger) + prefix auditor + repair note + final verifier; ablations M1-C4, C1-only, M1-C1, oracle ledger.

## 9. Resources [H; unmeasured]
- Planning estimate of agent input tokens: pilot ~6-14 M; MVP ~123-309 M; target ~541-1,352 M (assumes 6-15k input tokens/call; replay costs no tokens). First task: measure on 5 tasks.
- Statistics: with 129 tasks one type can only establish ~11-15 point differences (exact McNemar); pooling types with clustered bootstrap is necessary; 3-seed noise check on 30 tasks.
- Infra: x86 Linux + Docker + several hundred GB, or the public WebArena AMI (1000 GB volume recommended) [R]; Python 3.10; provider access for the chosen backbone.

## 10. Recommended final scope
Minimum: one backbone, 60-100 single-site tasks, B1/B2/B3a/M1, addition + retraction at least, paired CIs, >=50 labelled failures, scripted demo. Target: + B2+, B3b, O, ablations, positions, 2nd backbone, seed check, all three types on 129 tasks. Stretch: action-state awareness, UNDO synthesis, multi-interruption, 2nd environment, Claude Code/Codex steering study.

## Go / no-go gates
- End of week 2: host + API access + 3-task smoke test pass -> continue on WebArena; otherwise switch to the fallback environment.
- After pilot: if invalid-plan rate of M1 is high or B2+ >= M1, narrow the claim (simpler method wins) rather than tune on the evaluation tasks.
- Do not tune prompts on evaluation tasks; freeze after pilot.

## What would change this assessment
A published method already evaluated on InterruptBench; AWS image/Docker unavailable to the team; real token costs far above the estimate; the course requiring a different deliverable format.
