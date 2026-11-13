# Full viva guide: CS787 Group 13

This guide is for the meeting with the professor after 14 Nov. He can ask **anyone** about **any** part of the
submitted code. Every member should be able to:
- give the 60-second summary (§1);
- know the key numbers (§2);
- explain at least their parts of the code in §3.

§4 lists likely questions with answers. §5 lists our weak points and how to answer them truthfully.

**For the in-class video on 11 Nov, use `VIDEO_DAY_GUIDE.md`.** It covers the BYOD paper section by section, likely
audience questions on the paper and course concepts, and a one-table summary of our results. The professor may also
ask about the paper in the viva, so read it too.

**Other materials:**
- Report: `docs/report/report.pdf`.
- Demo: `docs/demo/denoise_demo.html` (also a claude.ai artifact).
- Public code: https://github.com/akode2803/cs787-diffusion-conversion.
- Trained adapters: the `weights/` folder on Drive, linked from the repository README.

Paths below are from the repository root. Line numbers are as of 9 Nov.

---

## 1. The 60-second summary (everyone must be able to say this)

> BYOD (Kuiper and Bagheri, 2026) turns a frozen autoregressive chat model into a diffusion language model by training
> one LoRA adapter for about three GPU-hours. Its paper compares each conversion only with the unchanged original
> model, so you cannot tell what is caused by diffusion and what is caused by fine-tuning on BYOD's data.
> We added the missing control: an autoregressive LoRA adapter trained on the same data, in the same order, with the
> same rank, learning rate and number of updates. Only attention (causal vs bidirectional), input (clean vs masked)
> and loss (next-token vs masked denoising) differ. We tested Qwen2.5 7B and Ministral 8B, plus LLaDA 8B as a
> natively trained diffusion model, on up to 500 examples per task.
> Findings: with data held fixed, diffusion costs 30 to 46 points on code. On Qwen, most of the maths drop is caused
> by BYOD's data, not diffusion. Fewer diffusion steps make it faster but never put it on AR's speed-accuracy curve.
> Conversion beats the control at single-line infilling on Qwen, but only when told the exact gap length. On reversal,
> with the name in the training prompt both models answer 0/1000 in reverse; with name-free prompts the AR control
> memorises the facts and the conversion does not, so the reversal question stays open for conversions.

## 2. Numbers to know

| What | Number | Where |
|---|---|---|
| BYOD's own claim | Qwen conversion .490 vs AR .716 average over 9 tasks; LLaDA .519; 3.1–4.0 h per conversion | paper Table 3, abstract |
| Our training | 25,000 updates, batch 16, lr 1e-5 cosine, 100 warm-up, LoRA r=1024 α=1024 on q_proj, v_proj, seed 42, 256-token sequences | BYOD `configs/paper.yaml` |
| Trainable parameters | Qwen 322,961,408; Ministral 490,733,568 (matches BYOD Table 2) | FINDINGS |
| Code cost of diffusion (control − conversion) | HumanEval: Qwen +0.451, Ministral +0.384; MBPP: +0.346, +0.296 | Table 3 |
| GSM8K chain, Qwen | original 0.922 (512 tokens) → control 0.502 → our conversion 0.434 / released 0.618 | Fig. 2 |
| GSM8K chain, Ministral | 0.886 → 0.850 → 0.646 | Fig. 2 |
| Speed | 5.57 s vs 0.33 s per GSM8K question at batch 16 (≈17×) | Table 4 |
| Steps | released GSM8K 0.618 / 0.368 / 0.178 / 0.088 at 256 / 128 / 64 / 32 steps | Table 4 |
| Batch 1 | original AR 17/32 in 3.07 s; conversion 17/32 needs 8.6 s; 11/32 at 128 steps in 4.3 s | Table 4 |
| Single-line infilling, Qwen, strict | original 0.688, control 0.524, ours 0.664, released 0.720, LLaDA 0.886 | Table 1 |
| Gap sweep (fence cut) | released 0.732 at true length → 0.246 at 1.5× → 0.304 at 2×; LLaDA 0.890 → 0.504 → 0.590 | Table 5 |
| Reversal, name in prompt | 10k updates: forward 999/1000 (conversion), 1000/1000 (control); reverse 0/1000 both | Table 6 |
| Reversal, name-free (run 3) | 10k updates: AR control forward 300, reverse 0; conversion forward 9, reverse 2 (chance: 1.0 and 0.3). Trained facts recited word for word: AR 559, conversion 3 | Table 6, §3.5 |
| Decoding order (Kendall τ) | conversions 0.88–0.95 on GSM8K/HumanEval; LLaDA 0.30 on GSM8K | Table 7 |
| Compute | about 325 Colab compute units over two accounts; G4 = RTX PRO 6000, 96 GB, 10.05 CU/h | report |

## 3. How the code works

### 3.1 Map

```
diffgap/train/   training and cloud jobs
  ar_control.py    the AR LoRA control (our main new piece)
  ar_loss.py       next-token targets and per-example loss (pure torch, unit-tested in test_ar_loss.py)
  retrain.py       reruns BYOD's own trainer with crash-safe resume points (patches 4 places, refuses other commits)
  launch.py        runs one job on a Colab VM; starts vm_guard.py; mirrors results to Drive
  vm_guard.py      stops (unassigns) its own VM when the job ends, the time limit passes, or the GPU idles
  supervise.sh     Mac-side: creates the VM, uploads files, restarts on VM loss (backup only)
  job_*.json       one file per GPU job (command, Drive folder, time limit)
diffgap/eval/    evaluation and analysis
  arms.py          loads every arm (parent, AR control, BYOD conversion, LLaDA) behind one interface
  sampling.py      batched diffusion sampler + AR greedy generation, both timed
  tasks.py         benchmarks (BYOD's prompts and scorers), infilling, reversal scoring
  run_eval.py      the evaluation loop; writes one JSON line per example
  analyze.py       Wilson CI, McNemar, paired bootstrap, Kendall tau, doubled words
  rescore_infill.py  rescoring of AR infilling with the fixed scorer, without a GPU
  reversal_data.py   the 1,000 invented facts; reversal_job.sh trains and tests both arms
  make_summary.py  builds docs/results/summary.json, the source of every number in the report
docs/report/     figs.py, build_report.py → report.pdf
docs/demo/       build_demo_data.py → denoise_demo.html
```

### 3.2 The AR control: `diffgap/train/ar_control.py`
It calls BYOD's own code for everything it can (data loading, collator, LoRA setup, optimizer settings, schedule,
saving), so the only differences are the ones we intend.
- `CleanCollator` (line 34) runs BYOD's masking collator for batching, then puts the clean tokens back
  (`input_ids = labels`), because the AR arm sees no masks.
- `make_causal` (line 46): BYOD's loader marks the model as bidirectional; we set `is_causal = True` so Hugging Face
  builds the normal causal mask.
- `check_model` (line 66) is a safety test at start-up. It changes the last 3 tokens of a sentence and checks that
  the outputs at earlier positions do not change (no leak from the future, so attention really is causal). It also
  checks that a fresh LoRA adapter changes nothing yet (LoRA's B matrix starts at zero).
- `batch_loss` (line 54) with `ar_loss.next_token_targets` (`ar_loss.py:6`): the hidden state at position i predicts
  token i+1, only for answer tokens up to and including the first end-of-text. `per_example_mean_ce`
  (`ar_loss.py:15`) averages within each example and then across examples, as BYOD does, so long answers don't
  dominate a batch.
- Same data order: both runs shuffle with seed 42 and log `batch_id` = sum of the example indices in the batch. We
  compared the control and our retrain at updates 100, 200 and 25,000: identical.
- Resume points (`save_resume_point`, line 95): Colab VMs vanished without warning, so every 2,500 updates we save
  adapter, optimizer, schedule and step, and a new VM skips the batches already used.

### 3.3 Our retrain of the conversion: `diffgap/train/retrain.py`
It runs BYOD's own `run_training` with the paper recipe. It patches four text blocks in BYOD's `training.py` (line 27)
only to make resume work on Colab and to log `batch_id`; it asserts the BYOD commit is 211d054 and that each patched
block appears exactly once. Nothing in the loss, model, data or schedule changes.

### 3.4 How a diffusion model generates: `diffgap/eval/sampling.py`
`diffusion_batch` (line 36) is BYOD's LLaDA "low-confidence remasking" sampler, extended to a batch:
1. Each row is `[prompt][answer positions, all MASK][padding]`. Padding is hidden from attention so each row behaves
   as if alone.
2. `schedule` (line 16) decides how many masks to commit at each step: positions / steps, remainder at the front.
   With 256 positions and 256 steps that is one token per step; with 32 steps, 8 per step.
3. At each step: one forward pass over the whole sequence (bidirectional), argmax prediction and its softmax
   probability at every masked position. The `count` most confident masked positions are committed and never changed
   again (temperature 0, no remasking of committed tokens).
4. `delay_eos` (BYOD's `confidence_eos_eot_inf`): end-of-text predictions get the lowest confidence, so they are
   committed last. This is why end-of-text padding fills the final steps.
5. The step at which each position was committed is returned; it feeds the Kendall τ analysis and the demo.

`ar_batch` (line 84) is ordinary Hugging Face greedy `generate` with a KV cache and left padding.
Time is measured between `torch.cuda.synchronize()` calls, on the same GPU for both.

### 3.5 Evaluation loop: `diffgap/eval/run_eval.py`
`run_task` (line 51): loads the examples, skips any already in the output file (so a lost VM loses nothing), builds
each input once, sorts by length to reduce padding, runs batches of 16, scores, and appends one JSON line per example
(`answer_ids`, `commit_step`, `correct`, `batch_seconds`, ...). `tag_for` (line 32) gives each setting its own file
name (`gsm8k_s32.jsonl`, `he_single_gapx1.5.jsonl`, `gsm8k_t512.jsonl`).

### 3.6 Infilling: `diffgap/eval/tasks.py`
- Diffusion (`diffusion_infill_row`, line 98): the answer region is code fence + code before the gap (fixed tokens),
  `gap` MASK tokens, code after the gap (fixed), fence, end token. Only the masks can change. `gap` is the true
  length of the canonical middle in that model's tokens (`true_gap`, line 107), or a multiple of it in the sweep.
- AR: the prompt shows the function with a `<FILL_ME>` marker and asks for the complete function. `score_infill_ar`
  (line 176) takes the first code block, then `split_around_gap` (line 143) matches the code before and after the gap
  line by line (ignoring blank lines and spacing inside a line, keeping indentation) and cuts out the middle. If the
  surrounding code was changed, the whole function is run and the case is flagged `context_changed`.
- Strict score: a flagged AR answer counts as wrong, because a diffusion answer cannot change the surrounding code.
- `run_program` (line 133) runs prefix + middle + suffix + the benchmark's tests in a separate Python process
  (10 s limit).

### 3.7 Reversal: `diffgap/eval/reversal_data.py`, `reversal_job.sh`
1,000 invented names and descriptions (seed 787), all unique. Training shows four phrasings of name → description.
Evaluation asks forward ("Who is X?", must contain the role and place words) and reverse ("Who is the <description>?",
must contain both parts of the name). Both arms continue from their own adapter with their own objective, identical
data and learning rate 5e-5; run 1 used 2,000 updates, run 2 used 10,000. Run 3 (`--forms namefree`, TAG nf10k) uses
four prompts without the name ("State a fact." → "X is the ..."), 10,000 updates, on an A100 on Anuj's account through
`runner/` (about 10 CU). `reversal_recall.py` re-scores every answer, checks it matches the stored flags, and counts
answers that are trained facts. **See §5.**

### 3.8 Statistics: `diffgap/eval/analyze.py`
- `wilson` (line 14): 95% confidence interval for a proportion. It behaves better than ±1.96·√(p(1−p)/n) near 0 or 1.
- `mcnemar_p` (line 22): exact test on paired examples. It uses only the examples where the two arms disagree (b
  right/a wrong vs a right/b wrong), binomial with p = 0.5.
- `paired_bootstrap` (line 32): resamples examples with replacement, 10,000 times, for a 95% interval on the
  difference in accuracy.
- `kendall_tau_b` (line 40): rank correlation between position and commit step over written tokens. 1 means strictly
  left to right.

### 3.9 Cloud jobs and the self-stop guard
`launch.py` starts `vm_guard.py` first, then runs the job. Results are mirrored to Drive every 60 s, and uploads are
capped at 10 min. `vm_guard.py` unassigns the VM when the job writes its end marker, the `max_hours` limit passes, the
job process has been dead for 30 minutes, or the GPU idles for 25 minutes. We built it after a stuck Drive upload kept
a paid GPU idle for about 70 minutes. Every job since has ended with a `GUARD ... STOP` line in its log.

## 4. Likely questions and answers

**Why is your control fair?** Same base model and revision, same data and order (batch ids match), same LoRA rank and
targets, learning rate, schedule, batch size and number of updates, same evaluation prompt and budget. It differs in
what an AR model must differ in: causal attention, clean input, next-token loss. One extra difference: BYOD weights
answer vs padding positions 0.9/0.1 and trains on end-of-text padding; an AR model stops at the first end-of-text, so
the control trains on answer tokens up to that point only.

**Why not just compare with the original model like BYOD?** Because fine-tuning on BYOD's data changes the model by
itself. On Qwen it takes GSM8K from 0.92 to 0.50 with no diffusion involved. Comparing with the original model would
have blamed diffusion for that.

**Why does the released conversion beat the AR control on GSM8K (0.618 vs 0.502)?** The control learned the data's
terse style and answers in a median of 7 tokens, skipping the working. The conversion writes a median of 95. We did not
establish why the two objectives pick up the style differently. [?]

**Why is your retrain worse than the released adapter on GSM8K (0.434 vs 0.618)?** Not isolated. It matches on 5 of 7
tasks. Candidates: run-to-run variance in masking, or a recipe difference (the released config files lack the
answer/padding weighting key, though `paper.yaml` calls that weighting author-confirmed). We say so in the report.

**Why 256 tokens for everything?** BYOD trains on 256-token sequences and uses 256 as the AR budget. One budget for
all arms keeps the comparison fair. Where the AR models were cut off (Ministral original: 141/500 GSM8K answers), we
reran them at 512. The diffusion arms almost never fill 256 positions (at most 12 answers per task, none correct).

**Is the 17× speed comparison fair?** It is the same GPU, the same software (Hugging Face transformers), and batch 16
for both, with a KV cache for AR. It is against the original model, which writes long answers (median 223 tokens),
not against the terse control. A production AR server (vLLM) would make AR faster still, so if anything the gap is
understated. Diffusion pays a full forward pass over all 256+ positions per step and cannot use a KV cache.

**Why do conversions decode left to right?** [H] The base model was pretrained on trillions of tokens of
left-to-right prediction, and 25,000 updates of a LoRA on q and v do not undo that, so the token right after the
written prefix is usually the one it is most confident about. We measured the behaviour, not the cause. LLaDA, pretrained as diffusion, is much less sequential (τ 0.30 on GSM8K).

**Why does accuracy collapse with fewer steps?** Tokens committed in the same step are chosen independently given the
current context, so they can contradict each other ("fiber fiber", repeated digits). With 8 tokens per step there are
many such conflicts and nothing ever revises a committed token.

**What is the gap-length problem exactly?** A diffusion model must be given a fixed number of mask positions. With too
many, the conversions do not use end-of-text padding inside the gap. They write extra code (often a closing code
fence, or the start of the next line), which breaks the program. We gave the conversions the benefit of the doubt by
cutting at the first code fence (the rule AR answers already get). They still fell from 0.73 to 0.25.

**Why strict scoring for infilling?** A diffusion answer physically cannot change the code around the gap; an AR
answer can rewrite the whole function and still pass. Strict scoring asks both the same question: fill this gap,
leave the rest. Lenient numbers are kept in the result files.

**Why LLaDA?** It is the natively trained diffusion model of the same size that BYOD itself compares against, so it
shows what diffusion can do when it is trained as diffusion from the start.

**How many examples, and is that enough?** 500 per task (164 HumanEval, 257 MBPP), against BYOD's 125. A 95%
interval at 500 is about ±4 points; our main effects (30–46 points on code) are far larger, and we report paired tests.

**Did you use AI tools?** Yes; the instructor allowed LLM use. The code was written with Claude (an AI assistant);
the team reviewed it, ran the tests (`test_eval_local.py`, `test_ar_loss.py`, `test_retrain.py`), and checked every
result against the raw files. Be ready to explain any file in §3 in your own words.

**What would you do next?** (1) Rerun the name-free reversal test with a higher learning rate or many more updates
for the conversion, until it knows the facts forward, then read its reverse score (§5). (2) A Ministral retrain, to have
our own conversion on both backbones. (3) Give the conversion a way to stop early inside an infilling gap (train
with padding inside gaps). (4) Speed against vLLM.

## 5. Weak points and how to answer them truthfully

1. **Reversal test design.** All four training phrasings put the name in the question ("Who is X?" → "X is the
   ..."), and BYOD's loss covers answer tokens only. When a name token is masked in the answer, the model can copy it
   from the question, so it never has to recover the name from the description. That is exactly how masked training
   is supposed to help with reversal. So our result shows that chat-format fine-tuning of a conversion does not give
   reversal; it does not show that the masked objective cannot. *Say this before you are asked.* We then ran the
   fair version (run 3, name-free prompts). The AR control learned the facts (559 recited word for word; reverse
   0/1000 with 843 answers giving the asked description a wrong name, a textbook reversal curse). The conversion did
   not learn them (3 recited; forward 9/1000, above the shuffle baseline of 1; reverse 2/1000, at chance). So we can
   say: with equal data and budget, masked training memorised far less, and we still cannot say whether it would
   reverse facts it knew. We did not try a higher learning rate.
2. **One retrain.** Our controlled pair on Ministral uses the released adapter, not our own retrain.
3. **Retrain vs released gap on GSM8K** (0.434 vs 0.618) is not explained.
4. **Batch-1 timing** uses 32 questions only.
5. **LLaDA's budget.** It fills all 256 positions on GSM8K and HumanEval (median 255), so its numbers there may be
   limited by the budget.
6. **One prompt for all arms** differs from BYOD's per-family prompts, so our absolute numbers differ from BYOD's Table 3.

Mistakes we caught and fixed (good to mention, shows the checks worked):
- The first infilling scorer counted blank-line differences as changed code and flagged about 90% of AR answers. It
  was fixed and the answers rescored offline, without a GPU (`rescore_infill.py`). The rescore decodes the stored
  token ids; the decoding was checked to match stored text on 500/500 GSM8K answers.
- Reversal run 1 (2,000 updates) left the conversion at 6.6% forward, which made its reverse score meaningless; run 2
  used 10,000 updates.
- The reversal design flaw (names in prompts) was found while writing this guide, then fixed by run 3.
- When writing up run 3 we first called the conversion's 9 forward hits "chance"; a shuffle test (1.0 on average,
  max 4 in 200) showed they are above chance, so the report says it keeps a trace of a few facts.
- A results-mirroring race could have overwritten newer files with stale copies. It was fixed with `rclone --update`
  before any damage.

## 6. How to rerun things

```bash
# Local checks, no GPU (from diffgap/eval; INFILL_DIR holds the two HumanEval infilling jsonl files)
python3 test_eval_local.py INFILL_DIR
# Rebuild every report number, the figures and the PDF from result files
python3 diffgap/eval/make_summary.py RESCORED_DIR REVERSAL_DIR INFILL_DIR docs/results/summary.json
python3 diffgap/eval/reversal_recall.py docs/results/reversal_nf10k docs/results/summary.json   # adds run 3
python3 docs/report/figs.py && python3 docs/report/build_report.py
# One GPU job on Colab (Mac side; the VM stops itself when done)
zsh diffgap/train/supervise.sh SESSION diffgap/train/job_eval_llada.json G4 15
```

## 7. Who prepares what

| Member | Owns | Must also know |
|---|---|---|
| Aryan Kumar | Motivation, the BYOD method, §1 summary, video | §2 numbers |
| Manoj Kumar Parida | Training: `ar_control.py`, `ar_loss.py`, `retrain.py`, fairness of the control | §3.2–3.3 |
| Rajdatta Kohale | Evaluation: `sampling.py`, `run_eval.py`, `tasks.py`, infilling scoring, gap sweep | §3.4–3.6 |
| Anuj Chaudhary | Statistics, reversal (all three runs, including run 3 on his account), cloud jobs: `analyze.py`, `reversal_data.py`, `reversal_recall.py`, `launch.py`, `vm_guard.py`, `runner/` | §3.7–3.9, §5 |

**Everyone:** §1, §2, §5 here, plus §1–§3 of `VIDEO_DAY_GUIDE.md`. This split is a suggestion; swap it as you like.
