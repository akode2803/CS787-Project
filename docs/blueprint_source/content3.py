"""Sections 7-9."""
from math import comb
from pdfkit import *
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")


# ------------------------------------------------------------------ small computations (kept in code so the PDF numbers are reproducible)
def p_two_sided(b, c):
    n = b + c; k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def min_sig_diff(n_disc, alpha=0.05):
    for diff in range(n_disc + 1):
        if (n_disc + diff) % 2:
            continue
        b = (n_disc + diff) // 2
        if p_two_sided(b, n_disc - b) < alpha:
            return diff
    return None


def power_rows():
    rows = [["Paired tasks n", "Discordant 15%", "Discordant 25%", "Discordant 35%"]]
    for n, label in ((60, "60 (small pilot)"), (100, "100"), (129, "129 (MVP subset)"), (165, "165 (full suite)")):
        r = [label]
        for d in (0.15, 0.25, 0.35):
            nd = round(n * d); diff = min_sig_diff(nd)
            r.append(f"{nd} pairs: ≥ {diff} net wins ({100 * diff / n:.1f} pts)")
        rows.append(r)
    return rows


def cost_rows():
    A = dict(stageA=13, b2=10, b2p=11, b3a=11, b3b=16, orc=15, m1=14.3, abl=13)
    lo, hi = 6000, 15000
    def row(name, desc, calls):
        return [name, desc, f"{calls / 1000:,.1f}k", f"{calls * lo / 1e6:,.0f}–{calls * hi / 1e6:,.0f} M"]
    # pilot: 20 tasks, addition only
    pil = 20 * (A["stageA"] + A["b2"] + A["b3a"] + A["m1"])
    # MVP: 100 tasks x 3 types; B3b and O on 30 tasks x 3 types
    t = 100 * 3
    mvp = t * (A["stageA"] + A["b2"] + A["b2p"] + A["b3a"] + A["m1"]) + 30 * 3 * (A["b3b"] + A["orc"])
    # Target: 129 tasks x 3 types; ablations x4; positions; second backbone; seeds
    t = 129 * 3
    main = t * (A["stageA"] + A["b2"] + A["b2p"] + A["b3a"] + A["b3b"] + A["m1"] + 4 * A["abl"]) + 129 * A["orc"]
    pos = 2 * t * (A["b2"] + A["m1"])
    second = t * (A["stageA"] + A["b2"] + A["b3a"] + A["m1"])
    seeds = 2 * 30 * (A["b2"] + A["m1"])
    tgt = main + pos + second + seeds
    return [["Tier", "Contents", "Agent LLM calls", "Input tokens (est.)"],
            row("Pilot", "20 tasks, addition only; Stage A + B2, B3a, M1; one backbone", pil),
            row("MVP", "100 tasks × 3 types; Stage A + B2, B2+, B3a, M1; B3b and O on 30 tasks", mvp),
            row("Target", "129 tasks × 3 types; all strategies and 4 ablations; 2 extra positions for B2 and M1; second backbone; 3-seed check on 30 tasks", tgt)], (pil, mvp, tgt)


def sec7():
    s = [H1("7  Benchmark and implementation strategy")]
    s.append(callout("What is and is not established", [
        f"{TAG_O} We cloned the repository (read-only), counted and parsed its data files, and read the replay and injection code. "
        f"{TAG_U} We did <b>not</b> install any dependency, start any WebArena site, call any model, or run any agent. Every statement below about running the benchmark is a plan, not a test."], "orange"))
    s.append(H2("7.1  Where WebArena will run"))
    env = [
        ["Option", "What it involves", "Open points", "Verdict"],
        ["A. Public AWS image", f"WebArena publishes an AMI (us-east-2) with the sites; recommended instance t3a.xlarge with a 1000 GB root volume {c('wa_docker')} {TAG_R}.",
         f"Cloud cost and account/credit; whether the image’s site versions match the benchmark’s task configs; reset-server setup {TAG_U}.", "Documented fastest route; try first if no server is available"],
        ["B. Lab / IITK Linux host", "Docker on an x86 Linux machine with several hundred GB free; setup scripts <font face='DVM'>01…07</font> use <font face='DVM'>sudo</font>.",
         f"Access, disk, root rights, network from the machine running the agent {TAG_U}.", "Best if available (no cost)"],
        ["C. This Mac", f"No <font face='DVM'>docker</font> command found on this Mac {TAG_O}. The page does not state image CPU architecture {TAG_U}; the four images and the Wikipedia/OSM data are large.", "—", "Not recommended for hosting; fine for agent/analysis code"],
        ["D. Fallback environment", f"τ-bench / τ²-bench {c('taubench', 'tau2')} (tool-using agents with a simulated user and database state) or a small purpose-built stateful environment. We would author the interruption data and scorers.",
         f"Extra data-creation work (~1 week); lower external validity; not yet inspected {TAG_U}.", "Use only if A and B fail by end of week 2"],
    ]
    s.append(tbl(env, [1.35, 3.6, 2.6, 1.6]))
    s.append(H2("7.2  Components"))
    comp = [
        ["Component", "Plan"],
        ["Repository and dependencies", f"Pin InterruptBench at commit 17da111. Python 3.10 environment (conda) per its README; install pinned <font face='DVM'>requirements.txt</font> and Playwright. Expect to patch: OpenAI model name in fuzzy-match scoring, documented paths, and possibly dependency pins {TAG_H}. Record every patch as a diff in our repository."],
        ["Model access", f"Shipped provider code supports AWS Bedrock (native model ids, e.g. <font face='DVM'>us.anthropic.claude-sonnet-4-5-20250929-v1:0</font>), OpenAI-compatible endpoints and Google {TAG_V}. "
                         f"Options: Bedrock credits; an OpenAI-compatible endpoint for an open-weight model; a small adapter for another API {TAG_H}. "
                         f"One strong and one cheap backbone is the target; development on the cheap one. Availability and cost of the paper’s exact model ids in late 2026 are unchecked {TAG_U}."],
        ["Agent framework", "Reuse InterruptBench’s WebAgent-R1-style <font face='DVM'>PromptAgent</font> and prompt <font face='DVM'>p_webrl_chat_think.json</font>. No new agent framework. Add a <font face='DVM'>strategies/</font> package behind one interface (below)."],
        ["Task selection", f"Smoke: 3 tasks (one per site). Pilot: 20 tasks, stratified by site. MVP: up to 100 of the 129 single-site tasks (Shopping 45, Shopping-admin 35, GitLab 30, Reddit 19). Full: 165 only if budget allows. "
                           f"Fix the task list in a file before any run; sample with a recorded seed. Tasks whose Stage A trajectory ends before K abort in strict replay mode; count and report them {TAG_V}."],
        ["Baseline implementation", f"B1 and B2 come from the shipped Stage A/B scripts (append mode, <font face='DVM'>interrupt_at_pct: 60%</font>). Reproduce them first and compare qualitatively with the paper (Section 8, E1)."],
        ["Candidate implementation", "M1, B2+, B3a, B3b as strategy classes; prompts in versioned text files; handler outputs validated by code; unit tests for addition, revision, retraction, a conflicting update, and a prefix that already finished the task."],
        ["Logging and reproducibility", f"JSONL per LLM call (model id, prompt hash, tokens in/out, latency, retries) and per step (action, URL, observation hash); a run manifest (git commits, model ids, temperature, seed, step budget, container image digests, reset time); "
                                        f"immutable result folders; one command per experiment tier."],
    ]
    s.append(tbl(comp, [1.4, 7.2]))
    s.append(codebox(
        "class Strategy:                       # one file per strategy under strategies/\n"
        "    def on_interrupt(self, ctx) -> Intervention:\n"
        "        \"\"\"ctx: q0, update, replayed actions + URLs, current observation, llm client, budget.\n"
        "        Returns the intent string, optional extra context, and counted extra LLM calls.\"\"\"\n"
        "    def on_exit(self, ctx, answer) -> Verdict | None:   # used only by M1's verifier (C4)\n"
        "        return None"))
    s.append(P(f"The interface is a sketch {TAG_H}; the only existing hook we found is the intent update in <font face='DVM'>run.py</font> around the replay loop, so the change to the runner should be small {TAG_O}.", "Small"))
    s.append(figure(os.path.join(FIG, "fig_infra.png"), f"<b>Figure 5.</b> Planned harness. Existing InterruptBench code is grey; new code is blue {TAG_H}."))
    s.append(H2("7.3  Technical obstacles and mitigations"))
    ob = [
        ["Obstacle", "Evidence", "Mitigation"],
        ["Global environment reset vs parallel runs", f"README: a reset is global and breaks concurrent jobs; refreshing sites takes 3–5 min {TAG_V}. 67 base tasks use program-HTML checks, some of which depend on state changes {TAG_O}.",
         "Schedule by sweep (one strategy per sweep, reset between sweeps); run state-mutating tasks serially; verify read-only status of the MVP subset before parallelising."],
        ["Contamination between runs", f"Tasks change site state; the README warns results are “problematic” without refresh {TAG_V}.", "Reset before every sweep; log reset time; re-run a canary task at the end of each sweep."],
        ["Non-determinism", "LLM sampling, page timing, site data.", "Temperature fixed and logged; repeat a 30-task subset with 3 seeds to estimate run-to-run variation (E7)."],
        ["Scorer dependence on an external model", f"Fuzzy-match scoring calls an OpenAI model (name in code is flagged as unavailable) {TAG_V}.", "Patch to an available model, log it, and re-score a sample of fuzzy-matched tasks by hand."],
        ["Provider rate limits and cost", "Many short calls; per-step observations are large.", "Measure tokens on 5 tasks first; use caching if the provider supports it; cheap backbone for development."],
        ["Prefix does not carry the agent’s reasoning", f"Saved trajectories hold actions only {TAG_O}.", "State this in the report; C2 sees actions, URLs and observations, not the original thoughts."],
    ]
    s.append(tbl(ob, [1.9, 3.5, 3.2]))
    return s


def sec8():
    s = [H1("8  Experimental plan")]
    s.append(H2("8.1  Metrics"))
    m = [
        ["Metric", "Operational definition", "Origin"],
        ["Success rate (SR)", "Fraction of episodes passing the task’s native evaluator (string / URL / program match) against the <i>final</i> intent.", "Benchmark-native"],
        ["SR(k)", "(1/N) Σ 1[τ<sub>i</sub> ≤ k]; k = actions since the update (k = 1…30).", "Benchmark-native"],
        ["Δactions, Δoutput tokens", "Interrupted minus matched no-interruption run; stratified by paired outcome S/F, F/S, S/S, F/F.", "Benchmark-native"],
        ["Post-interruption cost", "LLM calls, input and output tokens, wall-clock and browser actions after the update, <b>including handler and verifier calls</b>.", "Ours (extends native)"],
        ["Repeated-action rate", "Fraction of post-update actions identical (type, target, argument) to a prefix action. A proxy for duplicated work; legitimate redo counts too, so read it with the cost metrics.", "Ours"],
        ["Reuse@Success", "Among <b>successful</b> episodes only: fraction of replayed actions whose effects are not repeated or reverted afterwards. Failed episodes are excluded so that retaining invalid work is never rewarded.", "Ours (conservative)"],
        ["Stale-value violation", "Final answer, final URL or typed values contain a value present in the initial query but superseded or retracted by the update. Rule-based match on the data’s own initial-vs-final text, audited by an LLM judge and by hand on ≥ 50 episodes.", "Ours"],
        ["Missed-update rate", "First post-update thought or action shows no reference to the update (LLM-labelled, human-audited).", "Ours (failure label)"],
        ["Invalid-plan rate (M1)", "Handler output that fails schema or ledger-consistency checks.", "Ours"],
        ["Verifier precision (M1)", "Share of C4 rejections where the episode was in fact failing, and of C4 acceptances where it was succeeding.", "Ours"],
    ]
    s.append(tbl(m, [1.6, 5.6, 1.6]))
    s.append(H2("8.2  Experiment matrix"))
    ex = [
        ["ID", "Question", "Setting", "Tier"],
        ["E0", "Does the pipeline run end to end?", "3 smoke tasks; B2 only", "Essential"],
        ["E1", "Do we reproduce the benchmark’s naive-injection behaviour?", f"20-task pilot, one backbone, addition: B1 vs B2 at position 0.6. Success criterion: interrupted &gt; no-update and the same ordering as the paper for the closest backbone; exact numbers are not expected {TAG_H}", "Essential"],
        ["E2", "Primary comparison (H1, H2)", "B1, B2, B2+, B3a, M1 × 3 types × MVP tasks × 1 backbone; position 0.6", "Essential"],
        ["E3", "Which components matter (H5)", "M1 ablations and oracle ledger, × 3 types", "Essential (core ablations)"],
        ["E4", "Cost of discarding progress", "B3b and oracle O on a 30–40-task subset", "Target"],
        ["E5", "Timing (H4)", "Positions 0.2 and 0.8 for B2 and M1", "Target"],
        ["E6", "Backbone dependence", "Second (cheaper or open) backbone: B2, B3a, M1", "Target"],
        ["E7", "Run-to-run noise", "3 seeds on 30 tasks for B2 and M1", "Essential (small)"],
        ["E8", "More than one update", "Chained stages for n = 2, 3 on ~40 tasks (repo workflow)", "Stretch"],
        ["E9", "Public-harness steering study", "Scripted mid-task message in Claude Code and Codex (queue vs steer vs interrupt); qualitative; uses documented hooks such as Codex SDK <font face='DVM'>steer()</font>", "Stretch"],
    ]
    s.append(tbl(ex, [0.4, 2.3, 4.8, 1.2]))
    s.append(H2("8.3  Sample size rationale"))
    s.append(P(f"For a binary outcome compared on the same tasks, the exact McNemar test depends only on the discordant pairs. The table gives the smallest net advantage that would reach two-sided p &lt; 0.05 "
               f"(computed by us with an exact binomial test) {TAG_O}. Discordance rates are assumptions {TAG_H}."))
    s.append(tbl(power_rows(), [1.7, 2.3, 2.3, 2.3]))
    s.append(P(f"<b>Consequence.</b> A single interruption type on 129 tasks can establish only differences of roughly 11–15 points; a true 5-point gain would usually look “not significant”. "
               f"We therefore (i) pool the three types and use a task-clustered bootstrap (episodes of the same task are not independent, so pooling helps less than 3× — treat the pooled interval as optimistic), "
               f"(ii) report effect sizes with intervals rather than significance labels, (iii) use all 165 tasks if infrastructure allows, and (iv) say plainly when a result is inconclusive."))
    s.append(H2("8.4  Controls and threats"))
    s.append(bullets([
        "<b>Held fixed across strategies:</b> backbone and exact model id, temperature and decoding settings, prompt template for the base agent, action vocabulary, observation format, step budget, replayed prefix, scorer, site snapshot (reset before each sweep).",
        "<b>Compute confound:</b> M1 uses extra tokens; B2+ spends a matched amount without structure; we also report success at equal total tokens.",
        "<b>Selection and tuning:</b> prompts are tuned only on the 20-task pilot (disjoint from the evaluation tasks), then frozen. No prompt changes after the main run begins.",
        "<b>Generator bias:</b> updates were written by Claude-Opus-4.5 {TAG}; if our backbone is a Claude model, results may be flattered; the second backbone (E6) partly addresses this.".replace("{TAG}", TAG_H),
        "<b>Failures:</b> API errors and infrastructure failures are retried a fixed number of times and then reported as missing, never counted as success; missing episodes are listed per strategy.",
        "<b>Model drift:</b> hosted models change; record the exact id and date, finish comparisons within a short window, and keep raw outputs.",
    ]))
    s.append(H2("8.5  Failure analysis protocol"))
    s.append(P(f"Every failing M1 and B2 episode in the pilot and a random sample of ≥ 50 failures per strategy in the main run are labelled with one primary and optional secondary cause from the taxonomy below "
               f"(LLM-assisted pre-labelling, then human adjudication of all labels in the report’s tables; two annotators on a 20% overlap to report agreement). The categories combine failure modes reported in the sources {c('zou', 'ivb', 'lrm')} and the brief {TAG_H}:"))
    s.append(tbl([
        ["Category", "Description"],
        ["Missed update", "Agent never acts on the new instruction."],
        ["Stale state", "Update acknowledged, but old values remain in forms, filters or navigation state (the paper’s case study)."],
        ["Obsolete goal pursued", "Agent keeps optimising a retracted or superseded requirement."],
        ["Lost original goal", "Agent completes the added requirement but drops the original one."],
        ["Over-correction", "Agent discards valid prefix work or redoes finished steps unnecessarily."],
        ["Wrong preservation", "Agent keeps prefix work that the update invalidated."],
        ["Premature exit / no verification", "Answers before checking the final state against the latest requirements."],
        ["Handler failure (M1)", "Invalid ledger, wrong verdict, or verifier false accept/reject."],
        ["Other / environment", "Navigation errors, site errors, evaluator noise."],
    ], [2.0, 6.6]))
    s.append(H2("8.6  Cost and compute estimate"))
    rows, (pil, mvp, tgt) = cost_rows()
    s.append(P(f"We have not measured token use. The estimate multiplies assumed numbers of LLM calls by an assumed observation size {TAG_H}: Stage A ≈ 13 steps per run (the paper’s no-interruption runs average ≈ 11–15 actions under addition {TAG_R}), "
               f"≈ 10 post-update steps per interrupted episode (replayed actions cost no tokens), M1 ≈ 3 handler calls plus ≈ 1.3 verifier calls, restart ≈ 16 steps; "
               f"<b>6,000–15,000 input tokens per call</b> (unmeasured; the paper reports output tokens only). Multiply by the chosen model’s current price, which we have not checked; output tokens add a few percent."))
    s.append(tbl(rows, [0.8, 5.2, 1.2, 1.6]))
    s.append(P(f"Wall-clock: if throughput resembles the README’s ≈ 40 minutes for 165 tasks {TAG_R}, the MVP’s ≈ {int(round(mvp / 13 / 165 * 40 / 60))}–{int(round(mvp / 13 / 165 * 40 / 60 * 1.6))} hours of agent time is a rough guess, dominated by resets. "
               f"<b>The first step is a 5-task measurement</b> of tokens per call and seconds per step; the budget decision (Section 14) waits for it. Cost levers: cheap backbone for development, one interruption type first, prompt caching, a lower step budget, fewer B3b/O runs {TAG_H}."))
    return s


def sec9():
    s = [H1("9  Scope, risk and fallback plans")]
    s.append(H2("9.1  Scope tiers"))
    tiers = [
        ["Tier", "Contents", "Exit criterion"],
        ["Minimum viable", "One backbone; pilot-tuned and frozen prompts; B1, B2, B3a, M1; ≥ 60–100 single-site tasks; at least addition and retraction (all three if budget allows); paired analysis with intervals; ≥ 50 labelled failures; scripted demo; report and slides; reproducibility package. "
                           "If WebArena cannot be hosted: the same design on the fallback environment (§7.1 D) with ≥ 40 tasks.",
         "Every number in the report regenerates from logged runs with one command; limitations stated."],
        ["Target", "Adds B2+, B3b, oracle O, the M1 ablations and oracle ledger, position sweep, second backbone, 3-seed check, all three types on ≥ 129 tasks.", "H1–H5 each answered “supported / not supported / inconclusive” with intervals."],
        ["Stretch", "Action-state awareness with irreversible-action handling; UNDO synthesis; multi-interruption chains; a second environment; the public-harness steering study (E9); a short research-paper style write-up.", "Only if the target tier is finished and frozen."],
    ]
    s.append(tbl(tiers, [1.0, 5.5, 2.1]))
    s.append(H2("9.2  Risks, mitigations and minimum viable alternatives"))
    rk = [
        ["Risk", "Likelihood / impact", "Mitigation", "Minimum viable alternative"],
        ["WebArena cannot be hosted (no Linux host, cost, Docker or image problems)", "Medium–high / critical", "Decide host in week 1; try AWS image and lab server in parallel; time-box to the end of week 2.", "Fallback environment (τ-bench-style) with our own interruption data; or a purpose-built mini-environment."],
        ["Dependency or provider incompatibility (old pins, Python version, Bedrock access, scorer model name)", "High / medium", "Isolated conda env on Python 3.10; patch and diff; add an adapter for the available API.", "Run only the agent and scorer paths needed for the subset; replace fuzzy-match tasks by exact-match ones."],
        ["Inference too expensive", "Medium / high", "Measure first (5 tasks); cheap backbone; subset and type limits; caching.", "Pilot + MVP with one type and 60 tasks; report as a smaller study."],
        ["Too few tasks for the effect sizes we care about", "High / medium", "Pool types with clustered bootstrap; use 165 tasks if possible; report intervals.", "Frame the study as descriptive with effect sizes; no significance claims."],
        ["Floor effects (converged success in the paper’s Table 2 ranges from about 3% to 42%)", "Medium / medium", "Report SR(k) curves and paired quadrants, not only final SR; choose the position and backbone where headroom exists.", "Analyse efficiency and failure modes where success differences are small."],
        ["M1 shows no improvement", "Medium–high / medium", "Pre-registered thresholds; B2+ and ablations explain why; failure labels.", "A well-controlled null result with analysis is the deliverable (the brief explicitly accepts this)."],
        ["Reproduction disagrees with the paper (including the suspect Table E.3)", "Medium / medium", "Compare orderings, not exact numbers; contact authors only after consulting the instructor.", "Report the discrepancy; rely on our own paired runs."],
        ["Team size changes after a merger", "Medium / medium", "Workstreams in §12 scale from 2 to 5; add the stretch items only with extra people.", "Keep the MVP tier for a team of two."],
        ["Limited time", "Medium–high / high", "Early end-to-end baseline (M2 by week 4); feature freeze at M5; report written in parallel.", "Drop B3b, ablations beyond C4, and E5–E9."],
        ["New related work appears", "High / low–medium", "Repeat the literature search two weeks before the deadline.", "Re-position the claim; the empirical comparison stays valid."],
        ["Course requirements unknown", "Unknown / medium", "Ask the instructor or TA for deliverable formats, deadlines and rubric (draft email available on request).", "Follow the blueprint’s deliverable list until clarified."],
    ]
    s.append(tbl(rk, [2.2, 1.0, 2.9, 2.5]))
    return s
