# Findings: diffusion project

The short list of what we know, for the report, the video and the viva. Updated after every run or check.
Details and raw numbers are in `EXPERIMENT_LOG.md`. The plan and hypotheses (H1-H5) are in `DIFFUSION_PLAN.md`.

Labels: **[V]** verified by our own run, **[P]** from the BYOD paper, not checked by us, **[H]** hypothesis, **[?]** open question.

Last updated: 9 Nov 2026, 02:25 IST.

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

- **Reversal, run 2: 10,000 updates for both arms** (9 Nov, `evr2`; 40 passes over the same 4,000 phrasings, lr 5e-5, each arm from its own adapter with its own objective; 1,000 questions per direction):

  | Arm | Forward (name → role) | Reverse (role → name) | Training loss at end |
  |---|---|---|---|
  | Qwen AR control + facts | 1000/1000 | **0/1000** (0-0.4%) | test 0.0000 (next-token) |
  | Qwen retrained conversion + facts | 999/1000 | **0/1000** (0-0.4%) | test 0.0001 (masked denoising) |

  - The conversion now knows the facts forward, so its reverse score is a real test. **H2 is rejected [V] for our training format (see the design limitation below): the BYOD conversion has the reversal curse as fully as the AR control.**
  - No reverse answer from either arm contains any trained name, right or wrong. The control invents real-sounding names ("Jean-Pierre Leclair", "Isaac Newton"). The conversion repeats the role back in all 1000 ("The inventor of the violet canal is the inventor of the violet canal").
  - **Design limitation found 9 Nov while preparing the viva (not fixable after the fact):** all four training phrasings put the name in the *question* ("Who is Pellura Holloington?" → "Pellura Holloington is the …"), and BYOD's loss covers answer tokens only. So when a name token is masked in the answer, the model can copy it from the question. It never has to recover the name from the description alone, which is the mechanism by which masked training is supposed to help reversal. **So H2 is rejected only for chat-format fine-tuning where the name appears in the prompt.** It is not a clean test of whether the masked objective can learn B→A. A fair test would train on name-free prompts (e.g. "State a fact." → "Pellura Holloington is the …"). [?]
  - Caveat: one backbone, one fact template, LoRA on a frozen AR base. That is consistent with DiffER (arXiv 2601.07347), which reports the curse in diffusion LLMs. Masked training through a LoRA adapter does not undo it. LLaDA was not taught the facts (not run, budget).
  - Adapters for both arms are on Drive at `eval/reversal/adapters/rev_*10k`. The training-metrics upload failed (capped, the job carried on). The losses are in the job log `eval/jobs/eval_reversal10k/logs/job.log`.

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
- (Superseded by the 512-token check below.) The 256-token budget cuts off 182/500 of the parent's GSM8K answers (22 of them correct; 302/318 of the rest correct) and 36/164 HumanEval answers. The AR control answers GSM8K in a median of 7 tokens, against 223 for the parent, so it is rarely cut off. The parent's GSM8K score therefore measures the budget as much as the model.
- An infilling scorer bug was found and fixed before any infilling number was used. The first matcher flagged about 90% of AR answers as changed because of blank lines and spacing. Rescoring is done offline (`rescore_infill.py`) and checked: decoding reproduces the stored text 500/500.

**Main evaluation, all four Qwen arms** (8 Nov; full table with CIs in `results/qwen_main.md`)

| Task | Parent | AR control | Retrained conversion | Released BYOD-Qwen |
|---|---|---|---|---|
| GSM8K | 0.648 | 0.502 | 0.434 | 0.618 |
| MMLU | 0.720 | 0.738 | 0.672 | 0.672 |
| ARC-C | 0.914 | 0.914 | 0.844 | 0.862 |
| HumanEval | 0.695 | 0.726 | 0.274 | 0.268 |
| MBPP | 0.739 | 0.739 | 0.393 | 0.416 |
| Infilling single-line, strict | 0.688 | 0.524 | 0.664 | 0.720 |
| Infilling multi-line, strict | 0.436 | 0.350 | 0.224 | 0.252 |

- **The cost of the diffusion objective, holding data fixed** (AR control minus retrained conversion, paired 95% CI):
  - code generation: HumanEval +0.451 (+0.366 to +0.537), MBPP +0.346 (+0.280 to +0.412);
  - GSM8K +0.068, MMLU +0.066, ARC-C +0.070, all significant;
  - multi-line infilling +0.126 (+0.078 to +0.174).
- **Where diffusion wins:** single-line infilling, **but only with the true gap length given (see the gap-length sweep below; at 1.5x it falls to about 0.13-0.25), and not on Ministral.** The conversion beats the same-data AR control by 0.140 (0.084 to 0.196), and the released conversion (0.720) is level with the parent (0.688; difference -0.032, CI -0.086 to +0.022).
- **Splitting BYOD's gap on GSM8K** (512-token AR check, 8 Nov): given 512 tokens the parent scores **0.922** (HumanEval 0.811). The AR control stays at 0.502 (HumanEval 0.787). The conversions almost never fill their 256 positions (at most 12 answers per task, none correct), so their numbers stand. The chain is: parent 0.922, same-data AR control 0.502, conversions 0.434 (ours) and 0.618 (released). **Most of the GSM8K drop comes from BYOD's training data** (the control learned 7-token answers), not from diffusion. H4 is rejected. The released conversion even beats the same-data AR control on GSM8K.
- **Our retrain matches the released adapter on 5 of 7 tasks** (differences within ±0.03). It is worse on GSM8K by 0.184 (0.136 to 0.230) and on single-line infilling by 0.056. Possible causes: the 0.9/0.1 answer/padding loss weighting in `paper.yaml` that the released config lacks, or a different training budget. Not tested.
- **Speed:** diffusion is about 17x slower per GSM8K example than AR at batch 16 (5.6 s against about 0.3 s), with matched 256-token budgets.
- **Decoding order:** median Kendall tau of commit order against position is 0.71-0.95. The low-confidence sampler mostly decodes left to right.
- **Doubled words** per 100 on GSM8K: retrained 4.73, released 1.90, parent 0.69. This is consistent with the glitches seen in training-time samples.

**Main evaluation, Ministral and LLaDA, final** (8 Nov; full tables in `results/all_main.md`)

| Task | Ministral parent | Ministral AR control | Released BYOD-Ministral | LLaDA 8B (native diffusion) |
|---|---|---|---|---|
| GSM8K (AR at 512 tokens) | **0.886** (0.710 at 256; 141/500 cut) | 0.850 (0.838 at 256) | 0.646 | 0.588 (median 255: fills its budget) |
| MMLU | 0.566 | 0.646 | 0.634 | 0.604 |
| ARC-C | 0.716 | 0.830 | 0.840 | 0.878 |
| HumanEval (AR at 512 tokens) | 0.817 (0.659 at 256) | 0.732 (0.665 at 256) | 0.280 | 0.341 |
| MBPP | 0.677 | 0.708 | 0.412 | 0.486 |
| Infilling single-line, strict | 0.634 | 0.696 | 0.726 | 0.886 |
| Infilling multi-line, strict | 0.388 | 0.400 | 0.282 | 0.510 |

- **The cost of diffusion, with data held fixed, replicates on Ministral** (AR control minus released conversion, paired, all at 256 tokens): HumanEval +0.384, MBPP +0.296, GSM8K +0.192, multi-line infilling strict +0.118. There is no difference on ARC-C (−0.010), MMLU (+0.012) or single-line infilling strict (−0.030, CI −0.080 to +0.022).
- **Where BYOD's GSM8K drop comes from depends on the backbone.** Ministral: parent 0.886 → control 0.850 → conversion 0.646, so the data costs 3.6 points and diffusion 20. Qwen: parent 0.922 → control 0.502 → conversions 0.434/0.618, so the data costs most of it. H4 (control within 5 points of parent on GSM8K) holds for Ministral and fails for Qwen.
- Ministral's parent scores below its control on ARC-C (−0.114) and MMLU (−0.080), with 8-token answers, so this isn't a budget effect. [?] Answer format? Not checked.
- The single-line infilling "win" doesn't appear on Ministral: the conversion is level with its control.
- LLaDA is the best infiller of every model tested with the true gap length (single 0.886, multi 0.510).

**Step count: diffusion's speed knob** (8 Nov, speed job; tables in `results/speed_steps_gap.md`). The user asked for this test.
- Batch 16, 256 positions. Accuracy falls steeply as steps fall: released BYOD-Qwen GSM8K 0.618 (256 steps), 0.368 (128), 0.178 (64), 0.088 (32); HumanEval 0.268, 0.091, 0.000 (64). Retrained: GSM8K 0.434, 0.288, 0.130, 0.066. Time per example scales linearly with steps (5.57 s at 256 down to 0.70 s at 32).
- Batch 1, GSM8K, first 32 examples, released conversion: 32 steps 3/32 at 1.08 s, 64 steps 6/32 at 2.15 s, 128 steps 11/32 at 4.30 s, 256 steps 17/32 at 8.59 s. AR: the parent gets 17/32 at 3.07 s (its answers fill 256 tokens), and the same-data AR control gets 16/32 at 0.89 s.
- **Conclusion [V], n=32 at batch 1 so small:** the step knob is real, but every setting is worse than AR. At about the AR control's latency (1 s), the conversion gets 3/32 against 16/32. To match the parent's accuracy it needs 2.8x the parent's time. Trading steps for speed never reaches AR's speed/accuracy frontier for these converted models.

**Gap-length sweep: diffusion's infilling advantage needs the oracle length** (8 Nov; single-line infilling, 500 examples)
- Every diffusion infilling run is told the exact gap length (number of masked positions). AR arms are not. The sweep gives the wrong length:

| Arm | x0.5 | x1 (true) | x1.5 | x2 |
|---|---|---|---|---|
| Qwen retrained conversion | 0.026 | 0.664 | 0.132 | 0.146 |
| Released BYOD-Qwen | 0.030 | 0.720 | 0.138 | 0.180 |
| LLaDA | 0.044 | 0.886 | 0.436 | 0.566 |

- With more positions than needed, the conversions write the right line, then fill the leftover positions with junk, usually a code fence ("```python"), instead of padding. Cutting each answer at its first code fence, the same rule the AR scorer applies, raises the conversions to 0.244/0.246 (x1.5) and 0.280/0.304 (x2), and LLaDA to 0.504/0.590. The conclusion holds either way.
- **So the single-line "win" over the AR control (Qwen, +0.140) depends on knowing the gap length.** At 1.5x the conversions (≈0.25 even after cutting) are far below the same-data AR control (0.524 strict), which needs no length. LLaDA is much more robust (0.50-0.59 at 1.5-2x), so native diffusion pretraining handles spare positions better than conversion does. With too few positions (x0.5) every arm fails, as it must.
- For the report: the infilling advantage holds only when the length is known (e.g. a fixed-size slot). This is a real limitation, not a scoring artifact.

## From the paper, not checked by us [P]
- Table 3 averages, diffusion vs AR: Gemma 0.506 vs 0.657, Qwen 0.490 vs 0.716, Ministral 0.499 vs 0.644, Llama 0.487 vs 0.588; LLaDA 0.519.
- What BYOD does not report: a same-data AR control, wall-clock speed, real infilling, reversal or planning tasks, or more than 125 examples per task.

## Open questions [?]
- Why do the parent losses differ so much between backbones (Qwen 2.27, Ministral 0.98) on the same data? Check whether Ministral's gap is also in the first and last tokens.
- Answered for Qwen: the AR control answers GSM8K in a median of 7 tokens (parent 223) and loses 14.6 points. Ministral not yet measured.
- Does BYOD's own AR column suffer the same 256-token cut-off on GSM8K? Check BYOD's evaluation code and paper settings.
- Why is test loss about 0.03 below validation loss for both controls? Probably the splits differ; not checked.
- Does our retrain match the released BYOD-Qwen adapter? On benchmarks: yes on 5 of 7 tasks, no on GSM8K (-0.184) and single-line infilling (-0.056). Why is open; the loss-weighting difference is the first suspect. A cheap loss check: score the released adapter on the same 200 validation examples with BYOD's `evaluate` and compare with 1.1977.

## Decisions [D]
- Topic changed to BYOD diffusion conversion on 7 Nov. BYOD is both the base paper and the paper for the video.
- Train on G4, not A100.
- Backbones: Qwen2.5 7B and Ministral 8B, because they are ungated. Retrain only Qwen.
- Evaluation runs on a second Colab account: 200 CU from 8 Nov (199.81 at 14:33 IST). The user's own L4 shares it, so we leave that session alone. The first account is at 0.00 CU.
- Every VM stops itself (`vm_guard.py`) when its job ends, its `max_hours` passes or its GPU idles 25 min, so no paid GPU waits on the Mac. Tested on two T4s: the stops after the job ended and at the time limit both worked.
- MATH-500 dropped from the core tasks (8 Nov): the parent needs more than 256 tokens, and 512 diffusion positions would roughly triple its cost. GSM8K stays as the maths task. Can be restored if compute allows.
- Reversal test design: 1,000 invented name-description facts, taught name to description only (4 phrasings, 8 passes, 2,000 updates, learning rate 5e-5) to the Qwen AR control and the Qwen retrained conversion, each with its own objective. Forward and reverse questions are scored by required words. Untrained arms are scored first as a check that the facts are new.
- Evaluation settings (details and reasons in `EVAL_DESIGN.md`): one prompt for every arm (BYOD's training system prompt), one budget for every arm (BYOD's AR budgets: 256 for maths and code, 64 for multiple choice), one token per step, end tokens delayed on generative tasks, 500 examples per task where the set allows. These differ from BYOD's own evaluation, which uses LLaDA's 512-position profile for diffusion and different prompts for its two columns.
- 9 Nov: reversal run 3 (name-free prompts) will run on a teammate's Colab account, not ours: we have 7.00 CU, credits are sold only in 100 CU packs, and the teammate has about 30-50 CU. Design: same 1,000 facts and seed, same eval files (checked to be byte-identical, so the untrained-arm scores carry over and are not rerun), 4 name-free prompts ("State a fact." → "<name> is the <desc>."), 10,000 updates per arm, lr 5e-5, TAG nf10k. Estimate about 12 CU, capped at 1.5 h (15 CU). Kit: public repo https://github.com/akode2803/cs787-diffusion-conversion (`runner/`, `channel/`); request `channel/to_runner/001`. A T4 was ruled out: the Qwen 7B weights are 15.2 GB in 16-bit (a T4 has 16 GB), the r=1024 LoRA adds about 323 M trainable parameters (about 5 GB with Adam states), and the T4 has no bf16. At the user's rule of thumb of 15x slower, the run would take about 18 h.
- 9 Nov: a full backup of the Drive folder was made in `CS787-Diffusion-BACKUP-2026-11-09`, which is not shared, before `CS787-Diffusion` was shared with the teammate.
- 10 Nov, reversal run 3 (name-free prompts, A100 on Anuj's account, 10,000 updates per arm). [V] Read from the mirrored eval files (`eval/reversal_nf10k/results/`, 1000 rows per file, arm and kind checked), via the Drive connector.
  - **Results:**
    - AR control: forward 300/1000, reverse 0/1000.
    - Conversion: forward 9/1000, reverse 2/1000. Neither reverse hit was among its forward hits.
  - **Did each arm learn the facts?** Answers were parsed as "<name> is the <desc>." and compared with the 1,000 trained facts.
    - AR, forward questions: 559 answers are a trained fact word for word, and 941 use a trained name. AR, reverse questions: 843 answers repeat the asked description with some trained name, almost never the right one. So the AR model memorised the statements and shows the reversal curse cleanly.
    - Conversion: only 3 (forward) and 1 (reverse) answers are trained facts. 197 and 294 use a trained name, and several invented names recur ("Pellura Paskane" 245 times in reverse). So in 10,000 updates the conversion learnt the format of the facts but not the facts.
  - **What this changes:** the conversion's reverse score is still uninformative. It cannot recall a fact in either direction, so H2 (diffusion training helps reverse recall) remains untested for the conversion, not refuted.
  - **New observation [V]:** with identical data, updates and learning rate, the AR control memorised the name-free facts and the masked-diffusion conversion did not. That is about knowledge injection in general, not reversal.
  - **[H] Why the conversion did not memorise:** an iid-masked objective spreads its signal over all answer tokens and masking ratios. It would need more updates or a higher learning rate, as Pan et al. 2025 also report for diffusion knowledge injection. Not tested.
  - Chance check [V] (`reversal_recall.py`; shuffle test in the session): with the conversion's answers shuffled across questions, 200 shuffles give 1.0 forward hits on average (at most 4) and 0.3 reverse hits (at most 2). So its 9 forward hits are above chance (a trace of a few facts), and its 2 reverse hits are at chance. Report §3.5, Table 6, the H2 row, the limitations, the abstract, the conclusion, the viva guide and the video script were updated on 10 Nov. The run cost 9.92 CU on Anuj's account (134.32 → 124.40).
