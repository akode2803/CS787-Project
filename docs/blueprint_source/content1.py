"""Title page, Sections 1-3."""
from pdfkit import *
import refs  # noqa: registers bibliography
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")


def title_page(toc):
    s = []
    s.append(Spacer(1, 6))
    s.append(P("Goal Revision in Long-Running LLM Agents", "Title"))
    s.append(P("Project Blueprint — Phase 1 deliverable: research design, source investigation, feasibility assessment and execution plan", "Subtitle"))
    meta = [
        ["Course", "CS787 Generative Artificial Intelligence, IIT Kanpur (instructor: Prof. Arnab Bhattacharya)"],
        ["Group / title", "Group 13 — title “Goal Revision in Long-Running LLM Agents” approved by the instructor (as relayed by the group member). "
                          "Final team size after any merger: <b>pending</b>."],
        ["Base paper", f"Zou et al., <i>When Users Change Their Mind</i> (arXiv:2604.00892, Apr 2026) {c('zou')}; code and data: InterruptBench {c('ib')}"],
        ["Document status", "DRAFT v0.1 for team review, 28 Oct 2026. <b>No implementation has started and no experiment has been run.</b> "
                            "Everything labelled as a result comes from a cited source, not from us."],
        ["Prepared by", "Claude (AI assistant) for the project team. Treat every claim as a lead to be checked by the team before it is used in graded work; "
                        "the tags below say how each claim was checked."],
    ]
    s.append(tbl(meta, [1.0, 5.2], header=False, zebra=False, extra=[("FONTNAME", (0, 0), (0, -1), "DV-B")]))
    s.append(P("<b>How to read the evidence tags</b>", "H3"))
    leg = [
        [TAG_V, "Verified in a primary source during this investigation (paper PDF text, repository code or data, official documentation)."],
        [TAG_R, "Reported by the authors of a cited source; we read it but did not re-run it. Many related-work entries are abstract-level reads only."],
        [TAG_O, "Observed or computed by us in a small, read-only check (file counts, code reading, arithmetic). Nothing was installed or executed from the benchmark."],
        [TAG_H, "Hypothesis, design proposal or planning assumption. Not evidence."],
        [TAG_U, "Unverified or unknown; needs a decision, a measurement, or information from the team."],
    ]
    s.append(tbl(leg, [0.5, 8.0], header=False, zebra=False))
    s.append(P("Contents", "H3nk"))
    s.append(toc)
    s.append(PageBreak())
    return s


def sec1():
    s = [H1("1  Executive summary")]
    s.append(P("<b>Problem.</b> Real users rarely give an agent a complete, final goal. After the agent has started acting they add a requirement, correct a mistake, "
               "or withdraw a constraint. By then the agent has already changed state — it has typed into forms, navigated, or edited files — so handling the update "
               "means deciding which executed work to keep, repair, or redo, not merely reading one more message. Restarting is safe but wasteful; "
               "simply appending the message is cheap but can leave the agent acting on stale state."))
    s.append(P(f"<b>Base paper.</b> InterruptBench {c('zou')} re-writes the 165 WebArena-Lite tasks as an under-specified first query plus one or more update messages "
               f"(<i>addition</i>, <i>revision</i>, <i>retraction</i>), replays a saved trajectory up to a chosen point, injects the update, and measures success "
               f"against the final intent. Six LLM backbones are evaluated; the authors conclude that interruption handling “remains challenging” and that reliable agents "
               f"will need “stronger mechanisms for state tracking, intent reconciliation, and error recovery” {TAG_R}. "
               f"The paper evaluates <b>no interruption-handling method</b>; only backbones with plain message injection {TAG_V}."))
    s.append(P("<b>What the source investigation changed about our plan</b>", "H3"))
    s.append(bullets([
        f"<b>Naive injection is already the benchmark’s own protocol.</b> In <font face='DVM'>Eval/run.py</font> the update is appended to the intent string "
        f"(<font face='DVM'>intent + “[User interrupt @action=k] …”</font>) and the same agent loop continues {TAG_V}. Our “Baseline 2” therefore exists in code; the project’s "
        f"job is to test whether explicit handling beats it.",
        f"<b>The topic became crowded in 2026.</b> At least four benchmark papers on mid-task change (InterventionBench {c('ivb')}, SWE-Shift {c('sweshift')}, FeatureLoop {c('featureloop')}, "
        f"LLMs Get Lost in Evolving User Intent {c('evolve')}) and one state-tracking study {c('task')} appeared in 2026. A “new benchmark” contribution is not available. "
        f"The open niche we can defend is narrower: a <b>paired, replay-controlled comparison of explicit goal-revision handling against naive injection and replanning, with cost accounting</b> {TAG_H}.",
        f"<b>The largest risk is infrastructure, not the method.</b> InterruptBench needs the self-hosted WebArena Docker sites; the documented route is a public AWS image with a 1000&nbsp;GB volume {c('wa_docker')}, "
        f"and no <font face='DVM'>docker</font> command was found on this Mac. None of this has been set up or tested {TAG_U}.",
        f"<b>One table in the base paper looks unreliable.</b> In its position-sweep table (E.3) the Haiku and DeepSeek rows are identical in every column at positions 0.4, 0.6 and 0.8, "
        f"and Mistral’s 0.8 row equals Qwen’s {TAG_V}. We will not build on those rows until reproduced (Appendix A).",
    ]))
    s.append(P("<b>Recommended decisions</b> (reasons and implications are in the sections cited)", "H3"))
    rec = [
        ["#", "Recommendation", "Why / what it costs", "§"],
        ["D1", "Anchor on InterruptBench, single-interruption, restricted to the 129 single-site tasks of four sites (Shopping, Shopping-admin/CMS, Reddit, GitLab); skip Map and Wikipedia.",
         f"Keeps the paired replay design while avoiding the ~180&nbsp;GB map backend {TAG_R}. Lowers sample size from 165 to 129 {TAG_O}.", "7"],
        ["D2", "Primary question: does explicit goal reconciliation + prefix audit + final verification beat naive append, at what extra cost, and how does it compare with replanning?",
         "One question that the experiments can answer; the rest are secondary.", "5"],
        ["D3", "Compare B2 (naive append), B2+ (compute-matched reminder), B3a (fresh-context replan), B3b (restart), M1 (candidate) and its ablations; keep B1 (no update) and an oracle as references.",
         "B2+ guards against “M1 won only because it used more tokens”; B3b gives the cost of discarding progress.", "6"],
        ["D4", "Claim a controlled empirical study plus a simple method, not a new benchmark or a novel algorithm.",
         "Honest positioning given the related work; a negative or mixed result is still a complete project.", "4, 9"],
        ["D5", "Decide in week 1 where WebArena will run (AWS image, a lab/IITK Linux server, or a reduced fallback).",
         f"Blocks everything else; needs your input on access and budget.", "7, 14"],
        ["D6", "Defer the harness comparison (Claude Code / Codex steering) and action-state extension to the stretch tier; document public behaviour now.",
         "Protects the core experiments; the documentation review is already done (§2.3).", "2, 6, 9"],
    ]
    s.append(tbl(rec, [0.45, 4.2, 3.8, 0.55]))
    s.append(P("<b>What we expect to deliver.</b> Minimum: a documented pipeline that reproduces the benchmark’s naive-injection baseline on a subset, one candidate handler with ablations, a paired "
               "evaluation with uncertainty, a failure analysis, a scripted demonstration, the final report and slides. <b>What we do not know yet:</b> whether M1 will beat naive append "
               "(strong models may already reconcile well; gains may concentrate on revision and retraction or on cheaper backbones), the real API cost, and the course’s official deadlines and rubric."))
    return s


def sec2():
    s = [H1("2  Background and motivation")]
    s.append(H2("2.1  Terms used in this document"))
    s.append(P("An <b>LLM agent</b> is a loop in which a language model reads an observation, decides on an action (a tool call, a click, a shell command), the environment executes it, and the "
               f"result is fed back (the ReAct pattern {c('react')}). A <b>long-horizon task</b> needs many such steps — in InterruptBench, roughly 10–25 actions per episode {TAG_R} — "
               "and its actions change persistent state (a form field, a cart, a repository). A <b>goal revision</b> is any change to the requirements after execution has begun."))
    s.append(H2("2.2  Why users change goals mid-run, and what is at stake"))
    ex = [
        ["Situation", "User update", "Still valid", "Must change"],
        ["Coding agent is refactoring a repository", "“Use the repository pattern, not active record.”", "Test scaffolding, unrelated modules", "Files already written in the old style; imports; tests that encode the old design"],
        ["Research agent is surveying a topic", "“Only papers after 2023; drop the hardware angle.”", "Search queries on the kept angles; notes on recent papers", "Sources already collected on hardware; the draft outline"],
        ["Travel-planning agent", "“Move the trip a week later and skip Lisbon.”", "Flight search tooling, hotel shortlists outside Lisbon", "Dates in every booking query; Lisbon legs; costs"],
        ["Multi-step workflow", "“Cancel the invoice step but keep the rest.”", "Completed data pulls and formatting", "Anything downstream of invoicing; side effects already issued (e.g. emails sent)"],
    ]
    s.append(tbl(ex, [2.0, 2.4, 2.4, 3.0]))
    s.append(P(f"These examples are illustrative constructions {TAG_H}. InterruptBench’s own examples are web tasks, e.g. “top-3 best-selling products” → “I meant for Jan 2023 specifically” (addition), "
               f"“starting point Phipps Conservatory” → “Randyland, not Phipps” (revision), “…during peak rush hour” → “without the rush hour consideration” (retraction) {TAG_V}."))
    s.append(figure(os.path.join(FIG, "fig_types.png"),
                    "<b>Figure 1.</b> Illustration of how already-executed work is affected by each interruption type. The K/R/X assignments are constructed for explanation (not taken from real trajectories); "
                    "real prefixes vary by task and model. The tasks and update texts come from the repository’s raw data."))
    s.append(H2("2.3  Interruption, steering, queuing, replanning and plan repair"))
    s.append(P(f"These words are used loosely in product documentation, so we fix working definitions and record what the public documentation of two commercial harnesses actually says. "
               f"We read documentation and (for Codex) open-source code. <b>We have not run any experiment on either product</b>; behaviour beyond the quotes below is unverified {TAG_U}."))
    vocab = [
        ["Term", "Working definition", "What public documentation says", "What it does not provide"],
        ["Queuing", "Store the message; deliver it after current work finishes.",
         f"Claude Code: Enter while it works queues the message, passed on “as soon as those tool calls finish, within the same turn”; leftover messages go out at turn end {c('cc_int')} {TAG_V}. "
         f"Codex: <font face='DVM'>codex queue</font> stores a message for an existing session {c('codex_docs')} {TAG_V}.",
         "Any reconciliation of the message with the plan."],
        ["Steering", "Deliver new input into a running turn so the next model step sees it.",
         f"OpenAI Responses API: the server finishes the current output item and hosted tool work, then starts a continuation containing the update; the guide states that steering does not undo earlier actions and does not cancel tools that have already started (our paraphrase of a summarised fetch) {c('oa_steer')} {TAG_R}. "
         f"Codex exposes <font face='DVM'>turn/steer</font> (app-server) and <font face='DVM'>TurnHandle.steer()</font> (Python SDK) {c('codex')} {TAG_V}.",
         "Repair of state the agent already changed."],
        ["Interrupting", "Stop the current model response or tool call.",
         f"Claude Code: Esc stops the current response or tool call mid-turn and “Claude keeps the work done so far”; queued messages are then sent {c('cc_int')} {TAG_V}. "
         f"Codex SDK has <font face='DVM'>interrupt()</font> {c('codex')} {TAG_V}.",
         "Guarantees about partial side effects of the stopped tool call (not documented in what we read)."],
        ["Replanning", "Discard the plan and build a new one from the current state for the revised goal.",
         f"Not a documented harness primitive in what we read. Classical planning compares replanning with plan repair and favours repair for <i>stability</i> {c('fox')} {TAG_R}.",
         "Preservation of valid work; low cost."],
        ["Plan repair", "Modify the existing plan locally; keep unaffected steps.",
         f"LLM-era analogues are about failures, not user changes: Atomic Task Graph repairs the smallest affected subgraph {c('atg')}; SagaLLM adds compensation and dependency tracking {c('saga')} {TAG_R}.",
         "A representation of what depends on what."],
        ["State revert", "Undo effects of earlier actions.",
         f"Claude Code checkpoints restore edits made with its file-editing tools; changes by Bash commands, most subagents, or outside the session are “not tracked” {c('cc_ckpt')} {TAG_V}.",
         "General undo for web/UI state or external services."],
        ["Resumption", "Continue after a pause with context preserved.",
         f"Claude Code documents <font face='DVM'>/resume</font> and <font face='DVM'>--continue</font>; Codex docs mention keeping follow-ups “in the same session” {c('cc_ckpt', 'codex_docs')} {TAG_R}. Not examined further.",
         "—"],
    ]
    s.append(tbl(vocab, [1.15, 1.8, 4.5, 1.85]))
    s.append(callout("Why this matters for the project", [
        f"The primitives above decide <i>when</i> a message reaches the model. None of them decides <i>what the message invalidates</i>. "
        f"OpenAI’s own steering guide states that steering does not undo earlier actions {c('oa_steer')}. That gap — reconciliation of new intent with executed work — is where "
        f"InterruptBench places the failures {c('zou')} and where our candidate method operates {TAG_H}."], "blue"))
    s.append(H2("2.4  Why appending the new message may not be enough"))
    s.append(bullets([
        f"<b>Stale state.</b> In the paper’s case study the failing agent acknowledged a new origin (“Randyland”) but left the old origin in the form field and reported a route computed from it; the successful agent edited the field and recomputed {c('zou')} {TAG_R}.",
        f"<b>Losing the original goal.</b> The InterventionBench README reports that, for <i>Add</i> interventions, about three quarters of failures complete the added goal but lose the original one and then declare both done {c('ivb')} {TAG_R} (README claim; paper body not read).",
        f"<b>State must be tracked explicitly.</b> A recent study of task-state delivery finds that showing an agent an accurate checklist helps less than directing it, and that an enforcement gate helps most "
        f"(0.38 → 0.98 episode success for one model in their procurement domain) {c('task')} {TAG_R}. That is a different domain and an abstract-level read, so it motivates rather than predicts our result.",
        f"<b>Intent drifts over turns.</b> Models lose accuracy when intent is revealed or revised across turns; a recap prompt recovers only part of the loss {c('evolve')} {TAG_R}.",
    ]))
    s.append(H2("2.5  Why preserving correct work while revising invalid work is hard"))
    s.append(bullets([
        "<b>Credit assignment.</b> From a list of past actions it is not obvious which depended on the superseded requirement.",
        "<b>Hidden state.</b> Page state (a filter, a selected tab, a half-filled form) is only partly visible in the observation; stale values can persist silently.",
        "<b>Irreversibility.</b> Some actions cannot be undone or safely repeated (posting, deleting, purchasing); repair then means compensation, not revert.",
        "<b>Verification.</b> The agent must check its final answer against the <i>latest</i> requirements, which requires an explicit record of what those are.",
        f"<b>Measurement.</b> “Useful work preserved” is easy to define in a way that rewards retaining wrong work; Section 8 defines it only over successful episodes {TAG_H}.",
    ]))
    return s


def sec3():
    s = [H1("3  Base paper analysis")]
    s.append(H2("3.1  Bibliographic details and artifacts"))
    bib = [
        ["Item", "Detail"],
        ["Paper", f"<i>When Users Change Their Mind: Evaluating Interruptible Agents in Long-Horizon Web Navigation</i>, arXiv:2604.00892 v1, 1 Apr 2026, cs.CL. "
                  f"19 authors; affiliations in the PDF header: UIC, McGill, MBZUAI, UC Santa Barbara, USC. Header reads “Preprint. Under review.” {TAG_V} "
                  f"Links: {link('https://arxiv.org/abs/2604.00892', 'abstract')}, {link('https://arxiv.org/pdf/2604.00892', 'PDF')}, {link('https://arxiv.org/html/2604.00892v1', 'HTML')}."],
        ["Code / data", f"{link('https://github.com/HenryPengZou/InterruptBench')} — 16 stars, 0 forks, 6 commits at inspection; latest commit 17da111 (2026-07-08, “add code, data and readme”). "
                        f"Top-level folders: <font face='DVM'>WebArena-Env-Setup/</font>, <font face='DVM'>Eval/</font>. {TAG_V}"],
        ["Licence", f"No top-level <font face='DVM'>LICENSE</font> file. <font face='DVM'>Eval/LICENSE</font> is the MIT licence of VisualWebArena (copyright Koh et al.), inherited with the code. "
                    f"The licence of the new interruption data is not stated {TAG_V} — acceptable for coursework, to be clarified before redistribution {TAG_U}."],
        ["Peer review", f"Not peer reviewed as of this reading (preprint, “under review”). Treat its numbers as claims {TAG_V}."],
    ]
    s.append(tbl(bib, [0.9, 7.3]))
    s.append(H2("3.2  What the paper contributes"))
    s.append(bullets([
        f"A formal vocabulary of three interruption types — <b>addition</b> (initial query is incomplete; the user adds detail), <b>revision</b> (initial query is mistaken; the user corrects it), "
        f"<b>retraction</b> (initial query is over-constrained; the user removes constraints) — plus a no-interruption reference {TAG_R}.",
        f"<b>InterruptBench</b>: WebArena-Lite (165 human-verified tasks, five domains) re-written by Claude-Opus-4.5 under three constraints: ground-truth consistency, necessity of each update, natural user tone; "
        f"the authors manually reviewed all generated data {TAG_R}.",
        f"A <b>trajectory-grounded simulation</b>: run the initial query, then replay and inject the update at a fixed fraction (default 60%) of that trajectory, so every backbone is "
        f"compared on the same prefix and tasks of different length are aligned by “actions since the interruption” {TAG_R}.",
        f"An <b>empirical study</b> of six backbones (Claude Haiku/Sonnet/Opus 4.5, Qwen3, DeepSeek-V3.1, Mistral-Large-3) in the WebAgent-R1 scaffold {c('war1')}, single- and multi-interruption {TAG_R}.",
    ]))
    s.append(H2("3.3  Protocol, as implemented"))
    s.append(figure(os.path.join(FIG, "fig_protocol.png"),
                    f"<b>Figure 2.</b> The InterruptBench protocol. Paper description {TAG_V}; the injection line and the replay logic were read in <font face='DVM'>Eval/run.py</font> {TAG_V}. "
                    f"Replayed actions need no LLM calls, so only post-interruption steps cost tokens {TAG_O}."))
    s.append(bullets([
        f"<b>Interruptions are informational.</b> They “do not reset the agent or the environment, and do not invalidate progress already made” {TAG_V}. Revisions and retractions still leave stale state in the page, which is where the failures concentrate (case study).",
        f"<b>Mapping of data files to scenarios is our inference.</b> The six raw files each hold 165 items (one per task id): <font face='DVM'>1update</font>, <font face='DVM'>2update</font>, "
        f"<font face='DVM'>2modification</font>, <font face='DVM'>1retraction</font>, <font face='DVM'>2retraction</font>, <font face='DVM'>3mixed</font> {TAG_O}. "
        f"The converter joins multiple updates with a newline into one injected message {TAG_V}, so “2modification” is one interruption that carries two corrections. Which file feeds which paper table is not stated {TAG_U}.",
        f"<b>Multi-interruption runs are chained stages</b>, not one run: each stage replays the previous stage’s trajectory and interrupts at the midpoint of the latest segment (<font face='DVM'>MULTI_INTERRUPT.md</font>) {TAG_V}.",
        f"<b>Step budget differs between text and code:</b> the paper says tasks use up to 30 LLM calls; <font face='DVM'>run.py</font> defaults <font face='DVM'>--max_steps</font> to 50 {TAG_V}. We will set and log it explicitly.",
    ]))
    s.append(H2("3.4  Metrics used by the authors"))
    s.append(P(f"<b>Success rate (SR)</b> against the final intent using WebAgent-R1’s three rule-based evaluators (string match, URL match, program execution); "
               f"<b>post-interruption success curve</b> SR(k) = (1/N) Σ<sub>i</sub> 1[τ<sub>i</sub> ≤ k], where τ<sub>i</sub> is the number of actions after the interruption until success; "
               f"<b>efficiency</b> as output tokens and action count relative to a matched no-interruption run, stratified by paired outcome (S/F, F/S, S/S, F/F); "
               f"and success as a function of the number of interruptions {TAG_V}. In our data audit, 80 of the 165 base tasks use string match, 39 URL match and 67 program-HTML checks "
               f"(a task can use several) {TAG_O}."))
    s.append(H2("3.5  What the authors report"))
    s.append(figure(os.path.join(FIG, "fig_results.png"),
                    f"<b>Figure 3.</b> Numbers copied from the paper’s Table 2 and Table E.3 and cross-checked against the extracted PDF text {TAG_V}; plotted by us. "
                    f"Panel (b) shows only Opus and Sonnet because other rows of Table E.3 look duplicated (see below). The two tables appear to use different scenario sets "
                    f"(e.g. Opus no-interruption baseline 5.45 in (a) vs 13.94 in (b)); the paper does not say which scenario Table E.3 uses {TAG_U}. Opus and Sonnet nearly coincide at n = 3 (41.8 vs 41.2)."))
    s.append(bullets([
        f"More update information raises success for every backbone (e.g. Opus 5.45% → 41.82% from zero to three interruptions), but the best converged result is still well under half the tasks; DeepSeek-V3.1 dips at n = 3 (21.21 → 20.61) {TAG_R}.",
        f"<b>Cost is mostly tokens, not actions.</b> Under addition, the mean action change ranges from −0.99 (Opus) to +0.82 (Sonnet) while the mean output-token change ranges from +37.6 (Qwen) to +1,699 (Haiku); "
        f"both-fail episodes carry the largest overhead {TAG_R}.",
        f"<b>Recoveries differ by capability.</b> Episodes that fail without the update but succeed with it (F/S): Opus 70, Sonnet 55, DeepSeek 35, Qwen 32, Mistral 27 of 165 (addition). "
        f"Harmful updates (baseline success, interrupted failure) are rare, 1–5 per backbone, but costly {TAG_R}.",
        f"<b>Position effect.</b> The authors say larger models do best with later interruptions and smaller or open-weight models degrade as the interruption is delayed, attributing this to stale state {TAG_R}. "
        f"The Opus and Sonnet rows of Table E.3 are not involved in the duplications; they diverge (Opus rises from 47.3 to 57.0, Sonnet falls from 47.3 to 42.4), which sits oddly with a “larger models improve with later interruptions” framing {TAG_O}.",
    ]))
    s.append(H2("3.6  Limitations: stated, and observed by us"))
    s.append(P(f"We found no dedicated limitations section in v1; the conclusion states only that handling remains a bottleneck and points to “state tracking, intent reconciliation, and error recovery” {TAG_V}. "
               f"Our observations ({TAG_O} unless marked):"))
    s.append(bullets([
        "<b>No handling method is evaluated.</b> The study compares backbones under one injection mechanism, so it cannot say whether better handling would help.",
        "<b>The no-interruption “baseline” is an information lower bound, not a stale-goal control.</b> The initial query is deliberately under-specified, so baseline success is only 3–5% in Table 2; it does not isolate whether an agent keeps pursuing an obsolete goal.",
        "<b>One generator, also an evaluated model.</b> Claude-Opus-4.5 wrote the data and is also a backbone; possible favouritism toward its own phrasing cannot be excluded " + TAG_H + ".",
        "<b>No uncertainty reporting seen.</b> In the tables and text we read there are no seeds, confidence intervals or significance tests; single-run differences of a few points on 165 tasks are within noise (Section 8).",
        "<b>One scaffold.</b> All models use the WebAgent-R1 prompt format, which has no explicit plan structure — so “plan repair” must be implemented around, not inside, this agent.",
        "<b>Internal inconsistencies</b> (Appendix A): Qwen is called Qwen3-Coder-480B-A35B in the text but Qwen3-235B-A22B in the tables; the Appendix B caption defines S/F and F/S inversely to Section 4.2 (the appendix text uses the Section 4.2 meaning); "
        "Table E.3 contains duplicated rows.",
    ]))
    s.append(H2("3.7  Artifact audit: can we reproduce a meaningful subset?"))
    audit = [
        ["Check", "Finding", "Status"],
        ["Data completeness", "Six raw JSON files × 165 items with <font face='DVM'>task_id</font>, <font face='DVM'>intent</font> (ground truth), <font face='DVM'>transformed_initial_intent</font>, <font face='DVM'>updates</font>; the mixed file also has <font face='DVM'>updates_type</font>. Task configs for WebArena-Lite are in the repo.", TAG_O],
        ["Released results", "No trajectories or result tables found in the repository; Stage A (prefix) trajectories must be regenerated per backbone.", TAG_O],
        ["Tasks by site (single-site)", "Shopping 45, Shopping-admin (CMS) 35, GitLab 30, Map 26, Reddit 19 = 155; plus 10 multi-site tasks (Map+Wikipedia 4, GitLab+Reddit 4, Shopping+Reddit 1, Map+Shopping-admin 1).", TAG_O],
        ["Runtime requirements", f"Python 3.10 (3.11 works, 3.12 not recommended), Playwright, pinned old dependencies (<font face='DVM'>requirements.txt</font>), Docker for the WebArena sites, a reset server, "
                                 f"AWS Bedrock credentials for the shipped provider code, and an OpenAI key for fuzzy-match scoring (code calls <font face='DVM'>gpt-4-1106-preview</font> with a comment that it is unavailable — likely needs a patch).", TAG_V],
        ["Environment size", f"WebArena publishes an AWS image (<font face='DVM'>ami-08a862bf98e3bd7aa</font>, us-east-2) with a recommended 1000 GB volume; the map backend alone is ~180 GB; image sizes are not stated on the page {c('wa_docker')}.", TAG_R],
        ["Throughput hint", "The Eval README says the 165-task WebArena-Lite suite takes about 40 minutes “in practice”, and that sites must be refreshed (3–5 min) between evaluation rounds.", TAG_R],
        ["Repo hygiene", "Committed scratch files (<font face='DVM'>nohup.out</font>, <font face='DVM'>debug_info/</font>, <font face='DVM'>.DS_Store</font>), login-state JSON under <font face='DVM'>Eval/.auth/</font>, docs referring to a <font face='DVM'>WebAgent-R1/</font> directory that does not exist here. Expect setup friction.", TAG_O],
        ["Reproduction verdict", "A meaningful subset is plausible <i>in principle</i> on a Linux host with Docker; nothing was installed or run here, so feasibility is unproven.", TAG_U],
    ]
    s.append(tbl(audit, [1.5, 6.0, 0.8]))
    s.append(H2("3.8  Answers to the ten questions in the brief"))
    qa = [
        ["#", "Question", "Short answer"],
        ["1", "Contribution?", "First systematic study of interruptions in long-horizon grounded web tasks: types, benchmark, replay simulation, six-backbone study (§3.2)."],
        ["2", "Research questions / hypotheses?", "Three analysis questions (adaptation dynamics, efficiency, multiple interruptions). No formal hypotheses or tests are stated."],
        ["3", "Models, environments, baselines?", "Six backbones; WebAgent-R1 scaffold; WebArena-Lite sites. Baselines are only the no-update lower bound; no handling methods."],
        ["4", "How are the types operationalised?", "LLM-synthesised initial query + necessary update(s); injected at 60% of the baseline trajectory by default (§3.3)."],
        ["5", "Metrics?", "SR, SR(k), Δactions and Δoutput tokens with paired quadrants, SR vs number of interruptions (§3.4)."],
        ["6", "Acknowledged limitations?", "No dedicated section in v1; conclusion calls for better state tracking and recovery. We list our own observations in §3.6."],
        ["7", "Code and data actually available?", "Yes: runner, replay logic, scorers, six raw files, WebArena setup scripts. No results, no top-level licence (§3.7)."],
        ["8", "Reproducible within a course budget?", "Plausibly a subset; blocked on a Linux/Docker host. Untested (§7)."],
        ["9", "Extensions since?", "We found parallel benchmarks (InterventionBench, SWE-Shift, FeatureLoop) and a state-tracking study, and one embodied-navigation paper that cites it; no method paper built on InterruptBench (search-limited, §4)."],
        ["10", "Is our direction distinct?", "Partly: the idea of explicit state tracking is not new; the paired comparison on this benchmark appears open (§4.4)."],
    ]
    s.append(tbl(qa, [0.35, 2.3, 6.2]))
    return s
