# Research Log

Entries are dated. Each entry separates: Verified facts (V), Observations by us (O), Hypotheses (H), Design decisions (D), Unresolved questions (U).

## 2026-10-28 — Phase 1 source investigation

### Verified facts (V)
- Base paper: Zou et al., "When Users Change Their Mind: Evaluating Interruptible Agents in Long-Horizon Web Navigation", arXiv:2604.00892 v1, 1 Apr 2026, 19 authors, header "Preprint. Under review." PDF downloaded and text extracted (22 pages incl. appendices).
- Paper: three interruption types (addition, revision, retraction); InterruptBench from WebArena-Lite (165 tasks, 5 domains); updates synthesized by Claude-Opus-4.5 under ground-truth-consistency / necessity / authenticity constraints; six backbones in WebAgent-R1 scaffold; default interruption at 60% of baseline trajectory.
- Paper Table 2 (converged SR %, 0/1/2/3 interruptions), e.g. Opus 5.45/21.21/36.36/41.82; Sonnet 4.24/15.15/33.33/41.21; Haiku 5.45/19.39/33.33/38.79; Qwen 4.24/11.52/18.79/23.64; DeepSeek 4.85/12.12/21.21/20.61; Mistral 3.03/11.52/12.73/13.94. Cross-checked against extracted PDF text.
- Paper Table E.3 (position sweep) Opus overall 13.94 (baseline), 47.27, 55.76, 54.55, 56.97 at 0.2/0.4/0.6/0.8; Sonnet 13.33, 47.27, 44.24, 41.21, 42.42.
- Paper's text states interruptions are informational ("do not reset the agent or the environment, and do not invalidate progress already made").
- Repo `HenryPengZou/InterruptBench` at commit 17da111 (2026-07-08): `Eval/` runner (derived from VisualWebArena/WebArena-Lite code), `WebArena-Env-Setup/`, six raw JSON files x 165 items. No top-level LICENSE; `Eval/LICENSE` is VisualWebArena MIT.
- `Eval/run.py` injects the update as `intent + "\n\n[User interrupt @action=K] " + update` (append mode) or replaces the intent (replace mode); replay re-executes saved actions with no LLM calls; `--max_steps` default 50; paper says up to 30 LLM calls.
- `convert_raw_to_interrupt_spec.py` joins multiple updates with a newline into one injected message.
- Multi-interruption is done by chained stages (MULTI_INTERRUPT.md), not within one run.
- Claude Code docs: Enter while working queues a message (delivered after current tool calls, same turn); Esc interrupts, "Claude keeps the work done so far"; Ctrl+Enter sends queued messages now; checkpoints track edit-tool changes, not Bash/subagent/external changes.
- OpenAI mid-turn steering guide (GPT-6 family, WebSocket): steer is queued, server finishes current output item and hosted tool work, then continues with the update; does not undo earlier actions or cancel tools already started (paraphrased from a summarised fetch). Codex repo (commit 154e873) exposes `turn/steer` (app-server) and `TurnHandle.steer()`/`interrupt()` (Python SDK); `codex queue` command exists.
- WebArena docs: public AMI ami-08a862bf98e3bd7aa (us-east-2), recommended t3a.xlarge + 1000 GB volume; map backend ~180 GB download.

### Observations by us (O)
- Single-site task counts in WebArena-Lite configs: Shopping 45, Shopping-admin 35, GitLab 30, Map 26, Reddit 19 (=155) + 10 multi-site tasks. Eval types: string_match 80, url_match 39, program_html 67 (tasks may have several).
- Discrepancies in the paper: (1) Table E.3 rows identical for Haiku vs DeepSeek at 0.4/0.6/0.8 and Mistral 0.8 = Qwen 0.8; (2) Qwen named Qwen3-Coder-480B-A35B in text but Qwen3-235B-A22B in tables; (3) Appendix B caption inverts S/F vs F/S definition; (4) 30 vs 50 step budget.
- No released trajectories/results in repo; repo contains scratch files and docs referencing non-existent `WebAgent-R1/` paths; fuzzy-match scorer hard-codes `gpt-4-1106-preview` with a comment that it is unavailable.
- Exact McNemar minimum significant paired differences (alpha=.05): n=129, discordance 25% -> >=14 net wins (10.9 pts); n=165, 25% -> >=15 (9.1 pts). Single-type comparisons cannot detect ~5-point gains.

### Related work found (abstract/README level; all fetched 2026-10-28)
InterventionBench (Findings EMNLP 2026; AppWorld+WebArena; 2,250 instances; 12 LLMs; README: 8 wrappers incl. Reflexion/AdaPlanner/Mem0/HippoRAG help Swap/Drop, not Add); SWE-Shift (2610.32196); FeatureLoop (2610.35488); LLMs Get Lost in Evolving User Intent (2607.20734); How Strongly Should Task State Influence an LLM Agent? (2609.25686); ContinuityBench (ICML 2026 workshop poster); Atomic Task Graph (2607.01942); Execution Lineage (2605.06365); SagaLLM (2503.11951); Are LRMs Interruptible? (2510.11713); Collaborative Gym; Magentic-UI; Interactive Speculative Planning (2410.00079, cited by base paper as single-turn interruption work).

### Hypotheses (H)
- M1 gains concentrate on revision/retraction (stale state) and on weaker backbones; B2+ may recover much of any gain (compute effect).
- Strong backbones may already reconcile well, leaving little headroom.

### Design decisions (D) — proposed only
See PROJECT_STATUS.md D1–D6 and blueprint Section 6.

### Unresolved questions (U)
- Which raw file feeds which paper table (e.g., is "Revision" = 2modification.json?).
- Which scenario Table E.3 uses.
- Whether the AWS image matches the task configs; real token usage per call; current model availability/prices.
- Course deadlines/rubric; merger.

### Searches not exhaustive
Web search + page fetches only; repeat two weeks before submission.
