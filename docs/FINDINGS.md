# Findings: diffusion project

The short list of what we know, for the report, the video and the viva. Updated after every run or check.
Details and raw numbers are in `EXPERIMENT_LOG.md`. The plan and hypotheses (H1-H5) are in `DIFFUSION_PLAN.md`.

Labels: **[V]** verified by our own run, **[P]** from the BYOD paper, not checked by us, **[H]** hypothesis, **[?]** open question.

Last updated: 8 Nov 2026, 16:06 IST.

## Results so far

All losses below are training-objective losses on BYOD's data. **None of these are benchmark accuracy.** AR loss and
diffusion loss measure different things and must not be compared with each other.

| Run | Parent val loss | Best val loss (update) | Test loss* | Adapter on Drive |
|---|---|---|---|---|
| Qwen2.5 7B, AR LoRA control | 2.2744 | 0.4913 (22,500) | 0.4551 | `runs/qwen2.5-7b/ar-control/best` |
| Ministral 8B, AR LoRA control | 0.9754 | 0.4710 (23,500) | 0.4420 | `runs/ministral-8b/ar-control/best` |
| Qwen2.5 7B, BYOD retrain (diffusion) | not measured | 1.1977 (24,750) | 1.1223 | `runs/qwen2.5-7b/byod-retrained/best` |

*Test loss is on the final weights at update 25,000, not on `best`. The validation losses at those two points differ by
0.0004 or less, so this does not change anything.

Retrain validation curve: 2.43 at 250, 1.74 at 1,000, 1.50 at 2,500, 1.36 at 5,000, 1.28 at 10,000, 1.23 at 15,000,
1.20 at 20,000, 1.1977 at 25,000. Still falling slowly at the end. 3.3 h, no VM loss.

## Verified facts [V]

**Setup**
- BYOD code pinned at commit 211d054 for every run. Upstream HEAD was still 211d054 on 8 Nov.
- The AR control and the retrain see the same examples in the same order: `batch_id` matches at updates 100, 200 and 25,000 (full Qwen retrain against the Qwen control), and Ministral matches Qwen at update 100.
- So the only differences between the Qwen AR control and the Qwen retrain are attention (causal vs bidirectional), input (clean vs masked) and loss (next-token vs masked denoising).
- The AR control is truly causal: changing later tokens moved earlier logits by 0.000000. A fresh adapter changes the parent's output by 0.000000.
- Trainable parameters: Qwen 322,961,408; Ministral 490,733,568, which matches BYOD Table 2.

**Resume after a lost VM**
- AR control: a lost VM was resumed from Drive, and updates 7,600-7,800 matched the lost run exactly (same batches, same losses).
- Retrain: stopped at update 100 and resumed. Restored weights reproduced the logged validation loss to within 1.5e-7, and example order matched.
- Retrain caveat: training masks are fresh random draws after a resume, not the same ones. Validation masks are fixed, so validation stays comparable.

**Compute (Colab)**
- G4 (RTX PRO 6000, 96 GB) costs 10.05 CU/h and trains at about 2.2-2.3 updates/s, so one 25,000-update run is about 3-3.7 h and 30-37 CU.
- A 40 GB A100 costs 6.73 CU/h but needs gradient checkpointing and runs at 1.01 updates/s, about 46 CU per run. G4 is cheaper.
- Generation, batch 1: G4 about 25 ms per denoising step, A100 about 47 ms.
- Two G4s, or one G4 plus one A100, can run at once on one account. One request for a second G4 was refused, so it is not guaranteed.
- VMs vanished without warning twice on 7 Nov; cause unknown. The supervisor plus Drive resume points handle it.
- Drive uploads can fail on rclone's shared client_id rate limit (403 rateLimitExceeded, 8 Nov). Uncapped retries kept a G4 idle about 70 min after the reversal job ended, using up the first account (0.00 CU at 09:59). Every upload is now capped at 10 min. Our own client_id would remove the cause.

**Data and loss behaviour**
- Qwen's high parent loss (2.27) comes mostly from the first and last answer tokens (means 8.1 and 6.8); the median body token is 0.94. It reflects a style mismatch with the training answers, not a bug.
- Released BYOD-Qwen output still shows glitches at 128 steps ("as as", "Eiff"). Nine samples only, so this is not a quality measure.
- Our retrain's training-time samples at update 25,000 show the same kind of error: doubled and dropped words, for example "Netherlands Netherlands", "can can and and", "sc and diff blue light". These use BYOD's fast check settings (32 steps for 64 tokens, temperature 0.5, top-k 3), so they are worse than real evaluation settings. This is early support for measuring doubled-token errors (planned experiment), not a result.
- Training-time generation perplexity under the parent (20 prompts) was 23.2 at update 1,000 and 15-20 afterwards, without a clear trend. Too few prompts to read much into.

**Released adapters and evaluation set-up**
- The released BYOD-Qwen and BYOD-Ministral `resolved_config.json` files have no `answer_padding_loss` key, while BYOD's `paper.yaml` (which our retrain used) sets 0.9/0.1 answer/padding weighting. So our retrain may not use exactly the released recipe. Learning rate, rank 1024, mask-only corruption and EOS-padding loss match.
- Mask tokens: released Qwen uses BYOD's default "MASK" (no key in its config), Ministral uses `<?>`; both match ours.
- Hugging Face main of Qwen2.5-7B-Instruct and Ministral-8B-Instruct-2410 was still BYOD's pinned revision on 8 Nov, so released adapters (which name no revision) load the same base as ours.
- BYOD's diffusion forward pass lets every token see padding (`bidirectional_attention_mask` is all zeros), so batching prompts of different lengths needs padding hidden from attention. Our sampler does this; parity with BYOD's own sampler is checked in `gpu_check.py`.
- Infilling scorer: all 1,000 canonical HumanEval-infilling middles (500 single-line, 500 multi-line) pass when spliced in; `pass` as the middle passes 1 of 200.

**GPU check of the harness, 8 Nov, G4, Qwen** (`gpu_check.py`; smoke runs are 4 examples, so accuracies there mean nothing)
- Our sampler at batch 1 reproduces BYOD's `llada_generate` exactly on 6 of 6 GSM8K prompts. Batched, 2 of 6 outputs were identical to batch 1; differences were small rewordings ("for $2 each,," against "at $2 per egg"). AR batched against one-at-a-time greedy: 3 of 6 identical. Most likely batch-shape numerics in bf16, which would affect both kinds of arm alike; a padding-free test (`batch_numerics`) is added to tell numerics from padding, not yet run.
- Diffusion speed: 0.033 s per denoising step at batch 1, 0.385 s at batch 16 (sequence about 400 tokens), so batching raises throughput only 1.4x. Each step recomputes the whole sequence, which makes diffusion compute-bound even at modest batch. GSM8K at 256 steps: about 5.8 s per example batched. AR parent: 2.8 s per answer at batch 1, 0.8 s at batch 6, with a KV cache. Early support for H3, not yet a result: accuracy is not matched.
- All three of our adapters load and answer GSM8K (Qwen AR control, Qwen retrained conversion, Ministral AR control). This closes the "never loaded back" question.
- Answer length on 4 GSM8K examples: Qwen parent median 146 tokens, Qwen AR control 32 (one answer was just "#### 3"), retrained conversion 37, released conversion 69, Ministral AR control 74. The terse-answer risk looks real for the Qwen AR control; the full run will measure it.
- LLaDA 8B Instruct loads and runs with transformers 4.57.6 (BYOD warns it was tested on 4.38.2). It ends answers with `<|endoftext|>` (126081).
- With a 256-token budget the Qwen parent's MATH answers were all cut off (median 256 tokens, 0/4). MATH is dropped from the core set (see Decisions).
- Reversal baseline (before teaching the facts, 1,000 questions each, 8 Nov): Qwen AR control and Qwen retrained conversion both score 0/1000 forward and 0/1000 reverse (95% CI 0-0.4%). They invent answers ("a fictional character from the video game series The Legend of Zelda"), so the facts are new to them.
- **Reversal, identical training budget** (8 Nov; 2,000 updates, learning rate 5e-5, batch 16, same 32,000 fact phrasings in the same order for both; 1,000 questions per direction):

  | Arm | Forward | Reverse | Training loss at end |
  |---|---|---|---|
  | Qwen AR control + facts | 1.000 (99.6-100%) | 0.000 (0-0.4%) | validation 0.0001 (next-token) |
  | Qwen retrained conversion + facts | 0.066 (5.2-8.3%) | 0.000 (0-0.4%) | test 0.231 (masked denoising) |

  - The AR control shows the full reversal curse: it learned every fact forward and none backward. Asked in reverse, it invents a new person ("Dr. Elena Vasquez") rather than naming any trained name (0/1000 answers contain any trained name or name part).
  - The conversion did not learn the facts in this budget, so **its reverse score says nothing about reversal yet**. Partial credit forward: 38% of key words, role right 29%, place right 21%. Its reverse answers do not even take the form of a name ("the first keeper of the violet canal").
  - The two "+facts" adapters were not saved (upload failure, see Compute). The evaluation outputs are on Drive; retraining both takes about 10 min.
  - So, under an identical budget, the masked-diffusion objective learned new facts far more slowly than next-token training (both ran about 8 updates/s). This is a result in itself, but H2 needs a run where the conversion knows the facts forward.
- AR infilling asking for the missing lines only failed for a format reason: the parent repeated code from after the gap. The prompt now asks every arm for the whole function; tested locally only.

**Main evaluation, Qwen AR arms** (8 Nov; 500 examples per task, HumanEval 164, MBPP 257; one prompt and one 256/64-token budget for every arm; details in EXPERIMENT_LOG)

| Task | Qwen parent | Qwen AR control (same data as BYOD) | Paired difference, 95% CI |
|---|---|---|---|
| GSM8K | 0.648 | 0.502 | +0.146 (+0.096 to +0.196) |
| MMLU | 0.720 | 0.738 | -0.018 (-0.042 to +0.006) |
| ARC-C | 0.914 | 0.914 | 0.000 |
| HumanEval | 0.695 | 0.726 | -0.030 (-0.091 to +0.030) |
| MBPP | 0.739 | 0.739 | 0.000 |
| Infilling single-line, strict* | 0.688 | 0.524 | +0.164 (+0.118 to +0.212) |
| Infilling multi-line, strict* | 0.436 | 0.350 | +0.086 (+0.044 to +0.130) |

*Strict: an AR answer that changed the code around the gap counts as wrong, the same terms a diffusion arm gets. Lenient (the model's whole function is run): parent 0.868 / 0.652, control 0.602 / 0.476.
- Fine-tuning on BYOD's data alone, with no diffusion, costs Qwen 14.6 points on GSM8K and 9-16 points on infilling, and nothing on MMLU, ARC-C, HumanEval or MBPP. So part of any gap between the parent and a BYOD conversion may come from the data, not from diffusion. This is what the AR control is for. The diffusion arms are still running.
- The 256-token budget cuts off 182/500 of the parent's GSM8K answers (22 of them correct; 302/318 of the rest correct) and 36/164 HumanEval answers. The AR control answers GSM8K in a median of 7 tokens, against 223 for the parent, so it is rarely cut off. The parent's GSM8K score therefore measures the budget as much as the model.
- An infilling scorer bug was found and fixed before any infilling number was used. The first matcher flagged about 90% of AR answers as changed because of blank lines and spacing. Rescoring is done offline (`rescore_infill.py`) and checked: decoding reproduces the stored text 500/500.

## From the paper, not checked by us [P]
- Table 3 averages, diffusion vs AR: Gemma 0.506 vs 0.657, Qwen 0.490 vs 0.716, Ministral 0.499 vs 0.644, Llama 0.487 vs 0.588; LLaDA 0.519.
- What BYOD does not report: a same-data AR control, wall-clock speed, real infilling, reversal or planning tasks, or more than 125 examples per task.

## Open questions [?]
- Why do the parent losses differ so much between backbones (Qwen 2.27, Ministral 0.98) on the same data? Check whether Ministral's gap is also in the first and last tokens.
- Answered for Qwen: the AR control answers GSM8K in a median of 7 tokens (parent 223) and loses 14.6 points. Ministral not yet measured.
- Does BYOD's own AR column suffer the same 256-token cut-off on GSM8K? Check BYOD's evaluation code and paper settings.
- Why is test loss about 0.03 below validation loss for both controls? Probably the splits differ; not checked.
- Does our retrain match the released BYOD-Qwen adapter? Cheap check: score the released adapter on the same 200 validation examples with BYOD's `evaluate` and compare with 1.1977. The paper reports no loss number we can compare with.

## Decisions [D]
- Topic changed to BYOD diffusion conversion on 7 Nov. BYOD is both the base paper and the paper for the video.
- Train on G4, not A100.
- Backbones: Qwen2.5 7B and Ministral 8B, because they are ungated. Retrain only Qwen.
- Evaluation runs on a second Colab account: 200 CU from 8 Nov (199.81 at 14:33 IST). The user's own L4 shares it, so we leave that session alone. The first account is at 0.00 CU.
- Every VM stops itself (`vm_guard.py`) when its job ends, its `max_hours` passes or its GPU idles 25 min, so no paid GPU waits on the Mac. Tested on two T4s: the stops after the job ended and at the time limit both worked.
- MATH-500 dropped from the core tasks (8 Nov): the parent needs more than 256 tokens, and 512 diffusion positions would roughly triple its cost. GSM8K stays as the maths task. Can be restored if compute allows.
- Reversal test design: 1,000 invented name-description facts, taught name to description only (4 phrasings, 8 passes, 2,000 updates, learning rate 5e-5) to the Qwen AR control and the Qwen retrained conversion, each with its own objective. Forward and reverse questions are scored by required words. Untrained arms are scored first as a check that the facts are new.
- Evaluation settings (details and reasons in `EVAL_DESIGN.md`): one prompt for every arm (BYOD's training system prompt), one budget for every arm (BYOD's AR budgets: 256 for maths and code, 64 for multiple choice), one token per step, end tokens delayed on generative tasks, 500 examples per task where the set allows. These differ from BYOD's own evaluation, which uses LLaDA's 512-position profile for diffusion and different prompts for its two columns.
