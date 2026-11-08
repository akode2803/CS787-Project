# 9-Day Plan (replaces the 12-week plan in the blueprint, Sections 7/11)

Decision (user, 2026-10-28): deadline expected ~end of first week of Nov; exams mid-Nov; presentation needed. No root/Docker, so WebArena is out. We run a **small controlled study in our own order-desk environment** (`goalrev/`), inspired by InterruptBench (same design: recorded prefix, replay to 60%, inject addition/revision/retraction update, compare strategies on identical prefixes). It is NOT a reproduction of InterruptBench; the report must say so.

## Update 2026-11-02: deadline is ~13 Nov (11 days); pilot ran (see EXPERIMENT_LOG); main run uses gemini-3.5-flash-lite unless its daily quota blocks us.

## Status of code (2026-10-28)
Done and unit-tested with a scripted fake model (10 tests pass): environment, 36 generated tasks (12 per type) with exact expected end states, agent loop, strategies B1 / B2 / B2+ / B3a / B3b / O / M1 (+ M1-noC4, M1-noC2), runner with resume, paired analysis (exact McNemar, bootstrap CI).
NOT done: no live model call has ever been made. Real behaviour (does Gemini follow the JSON protocol? how many calls per episode?) is unknown until the pilot.

## Budget check (important)
One episode = ~8-15 model calls (M1 adds ~4). Main run = 36 tasks x 5 strategies + Stage A ≈ 220 episodes ≈ 2,000-3,000 requests, spread over 4 accounts. Check the free daily request limit shown in AI Studio before the main run. Fallback: fewer tasks per type, drop B3b/O.

## Schedule
| Day | Goal | Who |
|---|---|---|
| 1 (today/tomorrow) | `.env` with keys + model; run unit tests; pilot: `stageA --n 2` then `stageB` on 6 tasks; read the logs | you + Anuj |
| 1-2 | Newcomers: read 36 tasks, hand-check that expected end states match the text; propose 10 extra update phrasings | 2 newcomers |
| 2-3 | Fix prompt/protocol problems found in pilot, freeze prompts (no tuning after this) | you + Anuj + me |
| 3-5 | Main run (resumable, can run in background on any laptop); watch error rate | Anuj / newcomers run it |
| 5-6 | Report script; label ≥30 failures with the taxonomy (blueprint 8.5) | all 4 |
| 6-8 | Slides, report, short scripted demo (replay one task per type, B2 vs M1) | all 4 |
| 9 | Buffer, rehearsal | all |

## Scope
Must: B1, B2, B3a, B3b, M1 on 36 tasks, paired results with CIs, failure analysis, slides, report.
Nice: B2+ control, M1 ablations (M1-noC4, M1-noC2), more tasks.
Cut first: oracle O, extra seeds.
