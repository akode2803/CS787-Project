> **7 Nov 2026: the project has changed.** The current topic and plan are in `DIFFUSION_PLAN.md`; results so far are in `FINDINGS.md`. Everything below describes the old goal-revision topic. Its results are complete and are kept as a fallback negative study.

# CS787 — Goal Revision in Long-Running LLM Agents: Project Status

Last updated: 2026-10-28 (after Phase 1). Full reasoning: `../CS787_Goal_Revision_Project_Blueprint.pdf`.

## Current research question (proposed, not yet confirmed by the team)
On InterruptBench tasks, after a fixed replayed prefix, does explicit goal reconciliation + prefix audit + final verification (M1) improve success over naive instruction injection (B2, the benchmark's own protocol), and at what token/call/action cost versus replanning (B3a fresh-context, B3b restart)?
Secondary: S1 interruption type, S2 interruption position, S3 which components matter (incl. a compute-matched control B2+).

## Confirmed facts about the course (as relayed by the group member)
- Course CS787, IIT Kanpur, Prof. Arnab Bhattacharya. Project = 50% of grade.
- Group 13, title "Goal Revision in Long-Running LLM Agents" approved; instructor asked for a base paper.
- Base paper proposed: Zou et al., arXiv:2604.00892 (verified to exist; preprint, "under review").

## NOT confirmed / unknown
- Merger status, final team size, members' skills.
- Deadlines, interim milestones, deliverable formats, rubric.
- Compute (Linux/Docker host?), API budget/provider.

## Proposed decisions awaiting the team (blueprint Section 1)
| ID | Proposal | Status |
|---|---|---|
| D1 | Anchor on InterruptBench single-interruption; 129 single-site tasks of Shopping, Shopping-admin, Reddit, GitLab (skip Map, Wikipedia) | proposed |
| D2 | Primary question as above | proposed |
| D3 | Strategies B2, B2+, B3a, B3b, O, M1 + ablations; B1 as reference | proposed |
| D4 | Frame as controlled empirical study + simple method (no novelty over-claim) | proposed |
| D5 | Choose WebArena host in week 1 (AWS image / lab server / fallback) | **needs your input** |
| D6 | Harness study (Claude Code/Codex) and action-state awareness = stretch tier | proposed |

## Open questions for you (blueprint Section 14.2)
1. Access to an x86 Linux host with Docker/root/hundreds of GB, or cloud budget?
2. API/credit budget and provider; GPU server for an open-weight model?
3. Course deadlines, milestones, deliverable formats, rubric?
4. Merger decided? Size and strengths?
5. Preference on interruption types or staying close to the paper's backbones?

## Relevant papers and findings (details in RESEARCH_LOG.md)
- Base paper evaluates six backbones with plain message injection; no handling method.
- Closest: InterventionBench (EMNLP Findings 2026), Task-state study (arXiv:2609.25686), SWE-Shift (2610.32196), Evolving User Intent (2607.20734), FeatureLoop (2610.35488).
- Base paper Table E.3 contains duplicated rows (Haiku = DeepSeek at 0.4/0.6/0.8; Mistral 0.8 = Qwen 0.8). Do not build on them until reproduced.

## Repository and environment status
- Project directory: only the blueprint PDF, this `docs/` folder, and `docs/blueprint_source/` (PDF build scripts and figures).
- InterruptBench and openai/codex were shallow-cloned into a temporary scratch area for reading only; nothing installed or run. (Re-clone at commit 17da111 when the project repo is set up.)
- This Mac: Python 3.14.6; no `docker` command found. InterruptBench expects Python 3.10/3.11.
- WebArena: not set up. Model access: none configured.

## Completed milestones
- [x] Phase 1: source investigation and 23-page blueprint PDF (2026-10-28).
- [x] Phase 2 memo drafted (`RESEARCH_VALIDATION_MEMO.md`).

## Experiment results
None. No experiment has been run.

## Current blockers
- Infrastructure decision (D5) and model access.
- Unknown deadlines/rubric.

## Next actions (in order)
1. Team reviews blueprint, confirms/changes D1–D6.
2. Answer Q1–Q5.
3. Choose host, create accounts (user action).
4. Create project git repo; pin InterruptBench commit 17da111.
5. Smoke test (3 tasks, B2) -> measure tokens/seconds on 5 tasks -> choose scope tier.
6. Freeze analysis plan (dated commit) after the pilot.

## Decisions that require your input
D5 (host), backbone/provider (budget), scope tier (after cost measurement), merger-dependent workstream ownership.
