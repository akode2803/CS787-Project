# Task set v2 (harder families) — `goalrev/tasks_v2.py`  (design agreed 2026-11-02: "go with the suggestion")

All tasks have exactly one correct end state; scoring is the same exact match on the final environment state as v1. Task i does not depend on the number of tasks generated. `generate(n, seed)` makes n tasks per family; run with `--set v2`.

| family | q0 | update | what it tests |
|---|---|---|---|
| long | 4 cart lines + shipping + coupon + note | ONE small change (colour / quantity / drop a line / add a line) | preserving everything else in a long order |
| compound | 2-3 lines + coupon/note | THREE edits in one message | doing all of several edits |
| relative | 3 lines | positional / relative edit ("double the quantity of the third item", "make the second item 2 more", "swap the first item for the same thing in blue") | grounding the edit in the current cart |
| null | 2-3 lines | no change (confirmation or chatter) | needless repair; B1 should equal B2 here |
| late/early interruption | any | any | `--cut 0.3|0.6|0.9` on stageB (use a separate `--name` per cut) |

Pre-registered expectation [H, written before running]: models will do well on all of these; they are the "control" end of the difficulty range. The headroom candidates not built yet are: cascading environment rules (coupon minimum, city/speed restrictions), two sequential updates, and an irreversible action before the update.
Rule: task families are fixed before looking at M1's results on them; B2 is reported as it comes out.
