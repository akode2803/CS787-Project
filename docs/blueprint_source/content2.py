"""Sections 4-6."""
from pdfkit import *
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
NS = "n/s"   # not stated in what we read


def sec4():
    s = [H1("4  Related work and research landscape")]
    s.append(P(f"Search method: web search plus fetching the paper or repository page of each hit on 2026-10-28. Most entries were read at <b>abstract or README level only</b> {TAG_R}; "
               f"details below are limited to what those pages state. The search can miss papers, and this field is moving monthly (eleven of the sources below date from 2026); "
               f"the search must be repeated before submission {TAG_U}."))
    s.append(H2("4.1  Mid-task change, interruption and evolving intent"))
    a = [
        ["Work", "What it does", "Relation to this project"],
        [f"InterventionBench {c('ivb')}", "Findings of EMNLP 2026. AppWorld + WebArena; 2,250 instances from 272 base tasks; 12 LLM agents; nine intervention types (swap / add / drop × verb / target / both); "
                                          "“adaptability” = success after an A→B intervention, counted only where the revised task is solvable alone. README: eight planning/memory wrappers (Reflexion, AdaPlanner, Mem0, HippoRAG named) help on Swap and Drop but barely change Add.",
         "<b>Closest.</b> Shows generic wrappers do not fix <i>Add</i>. It does not (in what we read) test an explicit goal-diff + prefix-audit handler, and its protocol differs from InterruptBench’s replay design."],
        [f"SWE-Shift {c('sweshift')}", "Coding agents; each scenario run twice from the same saved history (Clean vs Shifted); 120 scenarios, 12 change families, 9 intervention points, 17 systems. Success requires finishing the task, <i>preserving still-valid work</i>, and passing state/evidence checks. Benchmark only.",
         "Closest on “preserve valid work”, in coding. Template for our paired design and for defining preservation conservatively."],
        [f"FeatureLoop {c('featureloop')}", "61 coding tasks / 34 repositories with evolving requirements and two feedback kinds; 12 models; strongest completes 72.1%; only 15.4% of failed stages recover within two revisions. Benchmark only.", "Adjacent (multi-round coding)."],
        [f"Evolving User Intent {c('evolve')}", "Converts static tasks (GSM8K, BIRD-SQL, BrowseComp+, SWE-Bench Verified) into multi-turn conversations with reveal / revise / switch transitions; large accuracy drops; a recap prompt recovers part of the loss. No new agent method.",
         "Motivates B2+ (recap-style control). Not grounded in persistent environment state."],
        [f"Are LRMs Interruptible? {c('lrm')}", "Interrupting reasoning models mid-thought or updating the problem in flight; names failure modes: reasoning leakage, panic, self-doubt.", "Language-only; cited by the base paper."],
        [f"ContinuityBench {c('contbench')}", "Workshop poster. Interrupts step-based benchmarks (τ-bench, AppWorld, TerminalBench), resumes from live state with three handoff-context levels; success falls 41.7% → 28.0%; more handoff context is not always better.",
         "Relevant to what context to give after an interruption (supports comparing B3a vs B2 vs M1)."],
        [f"Lost in Multi-Turn {c('lost')}", "Underspecified multi-turn conversations degrade performance versus fully specified single turns.", "Background."],
        [f"IHBench {c('ihbench')}; PIFR {c('pifr')}", "Voice-agent recovery after barge-in; embodied-navigation task preemption and resumption.", "Different modality; shows the topic’s breadth."],
    ]
    s.append(tbl(a, [1.5, 4.7, 2.7]))
    s.append(H2("4.2  Task state, plan repair, selective recomputation"))
    b = [
        ["Work", "What it does", "Relation to this project"],
        [f"Task state study {c('task')}", "Task state as a graph (todo / blocked / done / cancelled, prerequisites); mid-episode cancellation and rewiring; four delivery modes (transcript, checklist, directive, enforcement gate); three models, procurement and release-engineering domains; gate lifts one model’s τ²-bench airline pass^1 from 0.39 to 0.54.",
         "<b>Closest method-side work.</b> We cannot claim that explicit state tracking is new. Differences: dialogue/tool domain vs grounded web UI; no replay-controlled paired design; no replanning baseline (as far as we read)."],
        [f"Atomic Task Graph {c('atg')}", "Dependency graph of subtasks; on failure regenerates only the failed portion and keeps verified results; 7–8B backbones.", "Selective repair idea; trigger is failure, not user change."],
        [f"Execution Lineage {c('lineage')}", "Work as a DAG of artifact-producing steps; when inputs change only affected branches are recomputed; compared with loop-based baselines on policy-memo updates.", "Incremental recompute idea; documents, not UI state."],
        [f"SagaLLM {c('saga')}", "Saga-style transactions: persistent memory, dependency tracking, compensation, validation agents.", "Compensation for irreversible actions (stretch)."],
        [f"AdaPlanner / Reflexion / ADaPT / ReAct {c('adaplanner', 'reflexion', 'adapt', 'react')}", "Feedback-driven planning, self-reflection, as-needed decomposition, reason-act loops.", "Triggered by environment feedback, not by user intent change; InterventionBench tests wrappers of this family."],
        [f"Plan stability {c('fox')}", "Classical result: plan repair keeps plans stable and can be cheaper than replanning from scratch.", "Conceptual basis for “selective repair vs replanning”."],
    ]
    s.append(tbl(b, [1.5, 4.7, 2.7]))
    s.append(H2("4.3  Human–agent systems, environments"))
    s.append(P(f"<b>Human–agent systems.</b> Collaborative Gym {c('cogym')} (bidirectional human–agent collaboration framework, ICLR 2026), Magentic-UI {c('magui')} (co-planning and action guards for a web agent), "
               f"and Interactive Speculative Planning {c('isp')} (treats user interruptions as a design feature) show interaction mechanisms; none of what we read evaluates goal revision against a paired no-handling baseline. "
               f"<b>Environments.</b> WebArena {c('webarena')} and VisualWebArena {c('vwa')} provide the sites; WebArena-Lite is the 165-task subset from VisualAgentBench {c('vab')}; WebAgent-R1 {c('war1')} supplies the scaffold and evaluators. "
               f"τ-bench {c('taubench')} and τ²-bench {c('tau2')} are lighter-weight tool-use environments with user simulators and database state, and are the natural fallback (Section 9). {TAG_R}"))
    s.append(H2("4.4  Gap and honest novelty assessment"))
    cmp_ = [
        ["Work", "Domain", "Mid-task change", "Handling methods tested", "Preserved work measured", "Cost measured"],
        ["InterruptBench", "Web (WebArena-Lite)", "Add / revise / retract (informational)", "None", "Indirectly (action Δ)", "Yes (tokens, actions)"],
        ["InterventionBench", "AppWorld, WebArena", "Swap / add / drop", "8 wrappers (README)", NS, NS],
        ["SWE-Shift", "Coding", "12 change families", "None", "Yes (part of success)", NS],
        ["Task-state study", "Dialogue + tools", "Cancel / rewire / relax", "4 state-delivery modes", "No", NS],
        ["Evolving User Intent", "QA, SQL, search, SWE", "Reveal / revise / switch", "Recap prompts", "No", NS],
        ["<b>This project (plan)</b>", "Web (InterruptBench subset)", "Add / revise / retract", "B2, B2+, B3a/b, M1 + ablations", "Reuse@Success (defined, §8)", "Yes"],
    ]
    s.append(tbl(cmp_, [1.5, 1.4, 1.7, 1.7, 1.4, 1.1], style_cell="Cell"))
    s.append(P(f"<i>n/s</i> = not stated in the abstract, README or page we read, which is weaker than “absent”. {TAG_R}", "Small"))
    s.append(bullets([
        f"<b>Already done (do not claim):</b> benchmarks for mid-task goal change in web, app and coding settings; the finding that all frontier models degrade; generic planning/memory wrappers failing on additions; "
        f"explicit task-state tracking with enforcement in a non-web domain; recap prompts as a partial fix.",
        f"<b>Plausibly open (our niche):</b> (i) an explicit <i>goal diff</i> (added / modified / retracted) plus an <i>audit of already-executed actions</i>, evaluated on a grounded web benchmark with a fixed replayed prefix; "
        f"(ii) a compute-matched control so structure and extra tokens are separated; (iii) the replanning-versus-repair cost comparison with restart and oracle references; (iv) breakdown by interruption type and position; "
        f"(v) a candid account of when handling does <i>not</i> help {TAG_H}.",
        f"<b>Our judgement:</b> algorithmic novelty is low, empirical-gap novelty is modest, and the value as a course project is high if executed carefully. "
        f"A modest or negative, well-controlled result is a defensible contribution; an over-claimed “novel method” is not {TAG_H}.",
    ]))
    return s


def sec5():
    s = [H1("5  Research questions and hypotheses")]
    s.append(callout("Primary research question", [
        "On InterruptBench tasks, when a user update arrives after a fixed replayed prefix, does <b>explicit goal reconciliation with a prefix audit and final verification</b> (candidate M1) "
        "increase final task success over <b>naive instruction injection</b> (B2, the benchmark’s own protocol) — and what does it cost in tokens, LLM calls and actions "
        "compared with B2 and with <b>replanning</b> (B3a, B3b)?"], "blue"))
    s.append(P("<b>Secondary questions</b> (each answerable from the same runs):"))
    s.append(numbered([
        "<b>S1 — Type.</b> Do addition, revision and retraction show different failure patterns and different benefits from handling? (brief RQ4)",
        "<b>S2 — Timing.</b> Does the benefit change with the interruption position (0.2, 0.6, 0.8) and hence with how much state is already committed? (brief RQ5)",
        "<b>S3 — Components.</b> Which components of M1 matter, and is the gain more than a compute effect (B2+)? Work preservation (brief RQ3) is treated as exploratory, using the conservative proxy of Section 8.",
    ]))
    s.append(P(f"Brief RQ1 → primary, RQ2 → primary (cost comparison), RQ3 → S3 exploratory, RQ4 → S1, RQ5 → S2. Thresholds below are <b>provisional</b>; we freeze them in a dated file (committed to git) after the pilot and before the main runs {TAG_H}."))
    hyp = [
        ["ID", "Hypothesis (expected direction, not a result)", "Supported if", "Weakened or rejected if"],
        ["H1", "M1 improves paired success over B2 (pooled over interruption types).",
         "Task-clustered bootstrap 95% CI of the paired success difference excludes 0 and the point estimate is ≥ +3 points; sign agrees in ≥ 2 of 3 types.",
         "CI lies within ±3 points (practical equivalence) or favours B2. Report as “no detectable benefit”."],
        ["H2", "Selective repair is cheaper than replanning at similar success, and M1’s handler overhead is bounded.",
         "Versus B3b: M1 success not worse by more than 3 points with fewer post-interruption actions. Versus B3a: no more actions. Versus B2: total post-interruption tokens ≤ 1.5× B2 (cap frozen after the pilot).",
         "M1 success below B3a/B3b by more than 3 points, or token overhead above the cap with no success gain."],
        ["H3", "Benefit is larger for revision and retraction (stale state) than for addition.",
         "Interaction contrast (revision + retraction) − addition has a CI above 0.", "Equal or reversed benefit across types."],
        ["H4", "Benefit grows with interruption position for the cheaper backbone and is flat for the stronger one.",
         "Positive slope of the paired difference vs position for the cheaper backbone; CI of the strong-model slope contains 0. (The paper’s evidence for a scale-dependent position effect is itself in doubt, §3.5.)",
         "No slope for either backbone."],
        ["H5", "Structure matters: B2+ (matched-compute generic reminder) recovers less than half of M1’s gain; C1 and C4 each contribute; C2 helps mainly on revision/retraction.",
         "Paired differences M1 − B2+ and M1 − (M1 without component) have CIs above 0.",
         "B2+ ≥ M1 within margin: the simpler method wins and we report that (the brief asks us to prefer the simpler method)."],
        ["H6*", "(Exploratory) M1 lowers stale-state violations and raises Reuse@Success relative to B3a.", "Lower violation rate with a CI excluding 0; Reuse@Success higher among successful episodes.", "No difference. Not used for headline claims."],
    ]
    s.append(tbl(hyp, [0.45, 2.8, 3.2, 2.6]))
    s.append(P(f"<b>What counts as evidence.</b> Only paired comparisons on the same task, same replayed prefix, same backbone and same step budget; uncertainty from a task-clustered bootstrap and exact McNemar tests "
               f"for binary success; no claim of significance without the interval; failed or infrastructure-error runs are reported, not silently dropped (Section 8). {TAG_H}"))
    return s


def sec6():
    s = [H1("6  Proposed methodology")]
    s.append(H2("6.1  Setting and notation"))
    s.append(P(f"A task has a first query q<sub>0</sub> (under-specified or over-specified), update message(s) u, and a hidden ground-truth intent used only by the scorer. "
               f"Stage A produces a prefix a<sub>1</sub>…a<sub>N</sub> for a given backbone; Stage B replays a<sub>1</sub>…a<sub>K</sub> (K = ⌊0.6·N⌋ by default), then hands control to a <i>strategy</i> that decides what the agent sees and does next. "
               f"All strategies share the prefix, backbone, decoding settings, action vocabulary and post-interruption budget, so differences come only from the strategy {TAG_H}. "
               f"The agent’s action vocabulary in the shipped prompt is Click, Type, Search, Hover, Scroll Up/Down, Press Enter, Select Dropdown Option, Go backward/forward, and exit(message) {TAG_V}; "
               f"the saved prefix contains actions, not the original reasoning {TAG_O}."))
    s.append(H2("6.2  Strategies compared"))
    st = [
        ["ID", "Name", "What happens at the interruption", "Extra LLM calls", "Role"],
        ["B1", "No update", "Agent continues with q<sub>0</sub> only (benchmark’s lower bound; run once in Stage A).", "0", "Reference; from the paper’s design"],
        ["B2", "Naive append", "intent ← q<sub>0</sub> + “[User interrupt @action=K] u”; history and live page kept (exactly the benchmark’s protocol).", "0", "Primary baseline"],
        ["B2+", "Append + generic reminder", "B2 plus a fixed, content-free instruction (“list the current requirements, compare them with the page, then act”) and one extra call whose output length is capped to match M1’s mean handler tokens.", "1 (matched)", "Compute-matched control for H5"],
        ["B3a", "Fresh-context replan", "One call merges q<sub>0</sub> and u into a goal G<sub>1</sub>; history is dropped; the agent restarts reasoning from the current page with only G<sub>1</sub>.", "1", "Replanning without environment reset"],
        ["B3b", "Restart", "Environment reset; standard agent runs from step 0 with G<sub>1</sub> from the same merge call. No prefix reuse, no stale state.", "1 + full episode", "Cost of discarding progress"],
        ["O", "Oracle restart", "Standard agent runs from step 0 with the ground-truth original intent (no interruption).", "0 + full episode", "Upper reference for goal understanding"],
        ["M1", "Goal revision + selective repair", "Handler C1→C2→C3 (Figure 4), then resume with history kept; C4 verifies before exit.", "3 + verifier calls", "Candidate method"],
    ]
    s.append(tbl(st, [0.45, 1.5, 4.7, 1.0, 1.7]))
    s.append(P(f"<b>Ablations:</b> M1 without C4 (no verifier); M1 with C1 only (ledger and merged goal, no audit or note); M1 without C1 (audit against raw u); "
               f"M1 with an <i>oracle ledger</i> (C1 replaced by ground-truth requirements derived from the data) to separate goal-understanding errors from state-reconciliation errors {TAG_H}. "
               f"B3a and B3b use the same merge prompt, so B3 differs from M1 by lacking the ledger, audit and verification, not by merge quality."))
    s.append(H2("6.3  Candidate method M1 in detail"))
    s.append(figure(os.path.join(FIG, "fig_method.png"),
                    f"<b>Figure 4.</b> Candidate method M1. This is a <b>proposal</b>; nothing has been implemented or tested. Dashed boxes are speculative extensions that will be built only if the core pipeline works {TAG_H}."))
    s.append(bullets([
        "<b>C1 Goal reconciler.</b> Input: q<sub>0</sub>, u. Output (JSON): merged goal G<sub>1</sub> and a requirement ledger listing each requirement with a status — unchanged, added, modified (with what it supersedes), retracted — and its source message. Code checks schema and consistency (e.g. a retracted requirement cannot also be active).",
        "<b>C2 Prefix auditor.</b> Input: ledger plus, for each replayed action, its textual form and the page URL/title after it (available at replay time {tag}). Output: effect class (read, navigate, form edit, submit) and verdict — KEEP, REPAIR, STALE, UNDO — with the requirement it depends on. This is the “which parts of the existing plan are affected” step of the brief, adapted to an agent whose plan is implicit in its action history.".replace("{tag}", TAG_O),
        "<b>C3 Repair note.</b> A short text (≤ ~150 words) listing facts worth reusing, page state to correct, steps to redo, and values that must not be carried over. The agent resumes with G<sub>1</sub>, the ledger and this note in context; its history is kept.",
        "<b>C4 Final verifier.</b> When the agent issues exit(message), one call checks the proposed answer and visible page state against the <i>active</i> requirements; on failure the agent receives the discrepancy and continues (at most m = 2 retries, within the same step budget).",
        "<b>Constraints.</b> One backbone for all calls; prompts are task-agnostic (no per-task tuning); prompts and thresholds are frozen after the pilot; every handler output is logged; invalid JSON or an inconsistent ledger is counted as an “invalid plan” and falls back to B2 behaviour so runs are not lost.",
    ]))
    s.append(H2("6.4  Which parts are settled, provisional or speculative"))
    dec = [
        ["Element", "Status", "Decision rule"],
        ["Strategies B2, B2+, B3a, B3b, O, M1 and the listed ablations", "Proposed; provisional", "Fixed before the main runs; B3b/O may run on a subset if cost-limited."],
        ["C1 ledger, C3 note, C4 verifier", "Core of M1", "Kept if the pilot runs end-to-end and invalid-plan rate is low."],
        ["C2 audit with LLM-assigned effect class", "Core, prompt-based", "Kept if it improves over C1-only in the pilot or at least does not hurt."],
        ["Effect class from DOM/URL diff; inverse-action synthesis for UNDO", "Speculative", "Stretch tier only; needs reliable page-state parsing."],
        ["Action-state awareness (not started / executing / done without effects / changed environment / irreversible)", "Optional extension", "In replay, the update arrives between actions, so “currently executing” cannot occur; mapping Click targets to submit-like or irreversible controls needs element text and is judged by an LLM with human spot checks."],
        ["Choice of backbone(s)", f"{TAG_U} open", "Depends on API budget and access (Section 14)."],
        ["Final form of the contribution claim", "Open", "Decided after results: positive method, null result, or negative result."],
    ]
    s.append(tbl(dec, [3.3, 1.3, 4.1]))
    return s
