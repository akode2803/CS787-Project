# Topic search for the new CS787 project (7 Nov 2026)

Status: **closed 7 Nov 2026. The user chose the diffusion topic; see `DIFFUSION_PLAN.md`. Loop-fix is kept as a later hobby project.** Except for the census, nothing below has been run by us. Every number is someone else's report unless marked otherwise. "Read" means I opened the primary page or repo; "search summary" means I only saw a search result summary.

## The brief
Goal is the grade. Project plus paper is 55% of it. Paper is a 3-minute video due Wed 11 Nov. Project is due 13 Nov midnight. Claude does most of the work; the user reviews and records the video. A later viva can ask anyone anything about the code. Ranked criteria: (1) plays to Claude's strengths and gives plenty to write about; (2) feels novel. Full brief is in project memory.

## Filters I added
- **Interesting either way.** The goal-revision project bet on a method beating a baseline, and it did not. The new project must give a reportable result whichever way it comes out.
- **No free-tier API in the critical path.** Quotas, not design, caused the slowness so far.
- **Headroom by construction.** The metric must not sit near a ceiling.
- **Explainable at a viva**, including by team members who did not write the code.

## Goal-revision status (our own results)
| Run | Tasks | Append (B2) | M1 | Oracle (O) |
|---|---|---|---|---|
| gemini-3.5-flash-lite, v1 | 36 | 36/36 | 35/36 | not run |
| gemini-3.1-flash-lite, v1 | 36 | 36/36 | 36/36 | 36/36 |
| gemma4:31b-cloud, v1 | 36 | 36/36 | 35/36 | 36/36 |
| qwen2.5:3b local, v1 | 36 | 6/36 | 4/36 | 13/36 |
| gemini-3.5-flash-lite, v2 | 48 | 47/48 | 44/48 | 48/48 |

M1 never significantly beats append. These results are complete and can be written up as an honest negative study, which makes them the insurance option.

## Recommended: does the training-free reasoning-loop fix transfer?
### What is established
- Takehi, Teoh, Zhang, Khattab (MIT CSAIL blog, 2 Nov 2026, not peer reviewed; read). GPT-6 Astra edited 131,072 weights of Qwen3.5-0.8B, thinking mode. MATH-500 went from 7.9% to 48.1%, and answers hitting the token limit from 93.0% to 33.1%. Gemma 3 270M, which rarely loops, did not improve.
- The released edit reproduces: pngwn on Hugging Face (read) and kyle-chalmers on an M4 Mac (read).
- The closed form is W[:, j] <- W[:, j] - 6 (W[:, j] . d) d for 64 neurons per layer in layers 15 and 19 (KidIkaros, read).
- Non-thinking mode on the base model reportedly scores 45.8% on MATH-500, so the edit's edge over that setting is reported as +4.3 points, CI [1.9, 6.8] (pngwn citing JonathanColetti; read).
- A random direction on the same neurons recovers about a fifth of the gain (kyle-chalmers, read).

### What looks fragile
- A second 50-pass Astra run scored 12.9% on MATH-500 (OpenWSP, read). The authors' 10- and 25-pass runs scored 12.3% and 14.1%.
- Claude, blind with a probe table, tried five edits and none worked (kyle-chalmers, read). Harness and token caps were limited.
- Unjuno's approximate fresh search showed no benefit (read).

### The gap
KidIkaros found a direction with a script and no frontier model, and rescued 13 of 16 loopers on 18 problems. It used the same edit rule and strength, and it appears to have used the paper's layers too (my inference from its report of cosine similarity at two layers). I found no work that (a) selects layers, neurons and strength blind, or (b) applies a rank-one loop edit to any other model. Absence from my searches is not proof of absence.

Thinking-only models such as the R1 distills have no non-thinking switch, so the +4.3 objection does not apply to them. Transfer is where practical value would show up.

### Research questions
1. Can a script with no frontier model and no gradients find a working edit blind, using practice problems only?
2. Does it transfer across small reasoning models and families?
3. What matters: direction, layer, neuron choice, or strength? Why does the published strength overshoot orthogonality?
4. How does it compare at matched tokens with non-thinking mode, presence penalty, inference-time steering and a small LoRA?
5. What does the direction encode? Logit lens, and when it is active.

### Hypotheses, fixed before any result
- H1: the blind script cuts loop rate by at least half on at least 3 of 5 models.
- H2: accuracy gain grows with the base model's loop rate.
- H3: on thinking-only models the edit beats presence penalty at matched tokens.

### Weaknesses
- Impact is narrow in the same way as goal revision: larger models loop less (Pipis et al.), and training fixes exist (Liquid AI Antidoom).
- The practical gain on Qwen3.5-0.8B is small against non-thinking mode.
- Other models may not loop much under sensible sampling. This is the first gate.
- The area moves daily, so claims must stay narrow and cite community work.

### Gates
1. Loop census on about 8 candidate models. Need at least two non-Qwen3.5-0.8B models with meaningful loop rates. If only the Qwen family loops, narrow the scope to sizes within it.
2. Blind script reproduces on Qwen3.5-0.8B at n of at least 200 by end of Sunday 8 Nov. If it fails, that is itself a finding, and we report what breaks. If both gates fail, switch to the diffusion option.

## Alternatives
| Topic | Verdict | Reason |
|---|---|---|
| AR-to-diffusion conversion (BYOD, dLLM): what survives? | Backup | Reported 3-4 GPU hours per 7-9B model, code and Colab public, fits the Diffusion lecture, good visual demo. Risk: reads as running someone's recipe, and known quality gap. I have not opened the paper or repo. |
| Interpretability of the user's own hybrid Hymba-variant models | Second backup | Cheap, descriptive, explainable. Direct induction-head analysis of Hymba not found, though neighbouring work exists. Less wow. Reuse across courses needs checking. Drive folder needs sign-in, so the models are unassessed. |
| Playable diffusion world model | Rejected | Highest visual wow, but a blurry result leaves little to report. Weak on analysis. |
| Diff Interpretation Tuning follow-up (ICLR 2026) | Rejected | Interesting, no follow-ups found, but many LoRAs plus adapter training is heavy for 6 days. |
| Doc-to-LoRA / legal | Rejected | Three legal projects already in the class. |
| Concept-injection introspection | Rejected | Contested: one 14-model reanalysis puts the score near zero. |
| Emergent misalignment | Rejected | Reported consistent in only 2 of 12 open models; depends on LLM judges. |
| Autoresearch | Rejected | Saturated, known metric-gaming issues, hard to defend at a viva. |
| Plain replication of Sparks | Rejected | Already done several times. |
| Agentic weight editing by Claude at Astra scale | Rejected | One repo estimates about 300M tokens per experiment. |
| LLM weight-reading with more seeds and symmetry controls | Stretch only | Lex notes new seeds are untested and I found no hidden-unit permutation control, but WSPBench retired its read tasks after frontier models reached 100%. |

## Class overlap
No project on the course page is about weight editing or reasoning loops. Closest: #2 layer importance, #17 RAG failure from internal states. Five or more are RAG and three are legal.

## Compute
All on our own GPUs: vLLM on Colab G4 or A100. No API quota in the critical path. Correction: the credits are Azure (GitHub Student Developer Pack), not AWS, so the earlier AWS notes are withdrawn. Community answers on Microsoft Q&A say Azure for Students subscriptions cannot raise GPU quota; not confirmed from official docs, and not needed.

Verified on this machine (7 Nov): Colab CLI 0.7.5 at `/opt/miniconda3/bin/colab` lists sessions without a login prompt and accepts `--gpu G4`, plus `exec`, `run`, `download`, `log`. No session has been started yet, so G4 availability and how long jobs survive are untested.

## Revision 2 (7 Nov, after the user's challenge)
The first comparison was lopsided: most reading went on Sparks, and BYOD's paper had not been opened. After reading it, the gap is smaller than first stated.

### How narrow is the ability? (all third-party reports)
| Rung | Evidence | Reading |
|---|---|---|
| Name a game from raw weights | Astra, Opus 5.5, Sol, Terra, Gemini 4 Argon 4/4; Sonnet, Muse, Kimi 3/4; local Qwen 3.8 27B 3/4; Haiku 1/4 (Lex, Willison) | Not narrow, but n=4, inputs labelled, and a NumPy heatmap shows the same pattern |
| Repair tiny networks, 14 fixed choices | Astra 32/32, Sol 30, Terra 29, Luna 20 with clean controls broken (WSPBench) | Several tiers, GPT models only. The scripted baseline's 5/32 had no weight access, so it does not settle script against agent |
| Write networks by hand | Breakout: Astra 517, Opus 307; a non-frontier agent 0.2 | Falls quickly with tier |
| Edit a real LLM | Astra once at 48.1%; second 50-pass Astra run 12.9% (OpenWSP); Claude blind failed | Narrow, and unreliable even for Astra |

### Change to the recommended project
The script-only framing removed what makes the result striking. New central question: **what does a frontier model add over a plain search?** Arms: exhaustive script search; capped blind Claude agent; Astra's released edit as a free reference. Either outcome is reportable. The agent arm needs the user's approval and a fixed token cap, and must run without web access.

### Loop-fix against diffusion
| Factor | Loop-fix | Diffusion (BYOD) |
|---|---|---|
| Time per experiment | Minutes (estimate, unmeasured) | 3.1-4.0 h per conversion (reported) |
| Risk of no deliverable | Moderate, depends on census | Low, notebook exists |
| One-sentence hook | Stronger | Good |
| On-screen demo | Good | Stronger |
| Course fit | LLMs, Trustworthy Gen AI | Diffusion, LLMs |
| What is already known | Script arm untested beyond one model | Parents beat conversions; quality gap reported |

BYOD is as fresh (30 Oct), and its paper runs used a 96 GB RTX PRO 6000. Best diffusion question: can a LoRA-only conversion of frozen weights gain diffusion's reported advantages on planning and the reversal curse, with an AR LoRA on the same data as the control? Partly pre-empted: masked fine-tuning on AR models already resists the reversal curse (arXiv 2510.09885).

### Extra hunt
Evolutionary code search: several active frameworks, needs API budget, no clear gap. Tiny recursive models: about 26 h per run on one GPU, and weak as generative AI. Image and video search returned nothing from Oct-Nov 2026, and the Hugging Face monthly page did not load, so that area is thinly covered.

### Census outcome (our own data, see EXPERIMENT_LOG)
WEAK PASS. Severe looping appeared only in the Qwen3.5 family: 13-98% against 12% or less for the other nine models. Consequences for the plan:
- Dropped: cross-family transfer, and the argument that thinking-only models are where the value lies. H1 ("3 of 5 models") and H3 (thinking-only models) no longer apply as written.
- Kept: script against agent. Qwen3.5-2B and 4B have no published edit, so they are genuinely blind targets.
- Gained: three sizes of one family form a dose series for H2, and the census itself is a result.
- Worse: impact is narrower still, and Qwen3.5 has a non-thinking mode, so the +4.3 objection stands.
Decision is with the user.

## Sources
- Primary: https://rikiyat.github.io/blog/weight-space-programming/ and https://github.com/RikiyaT/lm_understand-logs
- Reproductions: https://huggingface.co/datasets/pngwn/weight-space-repro, https://github.com/kyle-chalmers/weight-space-programming, https://github.com/KidIkaros/wsp-reproduction, https://github.com/openwsp/openwsp, https://github.com/Unjuno/beyond-math-weight-space-programming
- Other model runs: https://github.com/nihilistau/weight-space-claude, https://github.com/lextoumbourou/weight-space-programming-experiments, https://github.com/alexcarterhq/wspbench
- Critique coverage: https://www.rdworldonline.com/mit-team-says-gpt-6-astra-can-fix-an-ai-model-by-editing-its-weights-critics-say-the-method-was-standard-ml-engineering/
- Looping: https://proceedings.mlr.press/v306/pipis26a.html, https://arxiv.org/abs/2601.05693, https://liquid.ai/blog/antidoom
- Alternatives: https://arxiv.org/html/2602.22661, https://alphasignal.ai/news/byod-turns-any-instruction-tuned-llm-into-a-diffusion-model-in-4-hours, https://arxiv.org/abs/2510.05092v3, https://arxiv.org/html/2510.23006v2
- Course: https://web.cse.iitk.ac.in/users/cs787/projects.php
