# Project presentation guide: 18 Nov 2026, 5 pm

This guide is for the project presentation (not the paper talk). It has four parts:

1. **What to say**: a talk you can give in about 7 minutes, plus a 3-minute version.
2. **Numbers to know cold.**
3. **The code**: a walkthrough of every file the instructor might ask about, with line numbers.
4. **Questions and answers**: on design, results, code, and weak points.

Labels: [P] = from the BYOD paper, [V] = measured by us, [H] = our interpretation, not tested.

What to have open on screen: the report PDF (Figures 1–4 carry the talk), and the GitHub repo
(`github.com/akode2803/cs787-diffusion-conversion`) in case they ask to see code.

---

## Part 1. What to say

### The 7-minute talk

Each block says what to show, then what to say. Speak it in your own words; the numbers are what matter.

**1. The question (show the report title page, ~45 s)**

> Diffusion language models generate by starting from a fully masked answer and filling positions in over several
> steps, in any order. People claim four advantages for them: faster parallel decoding, a dial for how much compute
> to spend, better infilling because they see both sides, and robustness to the reversal curse. Training one from
> scratch is expensive: LLaDA 8B took about 130,000 GPU-hours.
>
> BYOD makes it cheap. It takes an existing chat model, freezes it, makes attention bidirectional and trains one LoRA
> adapter, in 3 to 4 GPU-hours. But it compares each conversion only with the untouched original model. So when the
> conversion is worse, you can't tell whether diffusion caused it, or simply fine-tuning on BYOD's data.

**2. Our idea: the missing control (show the code box in §2.1, ~1 min)**

> We added that control. We trained an autoregressive LoRA adapter on the same base model, with the same data in the
> same order, the same rank-1024 LoRA on query and value, the same learning rate, schedule and 25,000 updates. The
> only differences are the ones an AR model must have: causal attention, no masking, and next-token loss.
>
> We checked the two runs saw identical batches: we log a batch id at every step and they match at updates 100,
> 200 and 25,000.
>
> One point about capacity: rank 1024 is not really low-rank. On the value projection the update can be full rank,
> and the adapters hold 323 million parameters on Qwen. So the gaps you'll see are not because the adapter was too
> small.
>
> We did this on two backbones, Qwen2.5 7B and Ministral 8B, and evaluated eight arms on up to 500 examples per task,
> four times BYOD's 125.

**3. Result one: the cost of diffusion (show Figure 1 / Table 3, ~1 min)**

> With the data held fixed, diffusion costs 30 to 46 points on code generation, on both backbones. HumanEval and
> MBPP. Knowledge tasks like MMLU and ARC are close.
>
> And the surprise: on Qwen, most of the maths drop BYOD reports is the data, not diffusion. The original Qwen scores
> 0.92 on GSM8K. The AR control, trained on the same data with no diffusion at all, drops to 0.50, because it learned
> the data's terse 7-token answers. The conversions sit at 0.43 to 0.62. BYOD's comparison would have blamed all of
> that on diffusion. On Ministral the data costs only 3.6 points, so it depends on the backbone.

**4. Result two: speed and the compute dial (show Figure 3, ~1 min)**

> At full quality the conversion is 17 times slower than the original model per answer, on the same GPU. Each step
> re-reads the whole sequence, and there is no KV cache.
>
> Diffusion does have one thing AR lacks: the number of steps is a hard compute dial, set before generation starts.
> Time falls linearly with it. But accuracy falls faster: 0.62 at 256 steps, 0.09 at 32. No setting reaches the AR
> curve. Box 1 shows why: at 32 steps, eight tokens are committed per step without seeing each other, and the
> arithmetic falls apart.

**5. Result three: infilling (show Figure 4 / the Fibonacci box, ~1 min)**

> This is where the conversion wins. Filling one missing line of code, it beats the same-data AR control by 14 points.
> But only because we told it exactly how many tokens the gap has. Give it 1.5 times the length and it drops from 0.73
> to 0.25. It writes the right line and then fills the spare slots with junk. LLaDA, trained as diffusion from scratch,
> handles spare slots much better. So the advantage is real only when the length is known, like a fixed-size slot.

**6. Result four: the reversal curse (show Box 4 / Table 6, ~1 min)**

> We taught both models 1,000 invented facts, "X is the lead composer of the sunken compass", in one direction only.
> Both learned them forward and answered none in reverse. Then we spotted a flaw in our own design: the name was in
> the question, so the masked model could copy it instead of recovering it. We reran with name-free prompts. Now the
> AR control learned the facts and still failed in reverse, a textbook reversal curse. The conversion did not learn
> the facts at all in the same budget. So whether masked training helps reversal is still open, but we found that it
> memorises new facts far less readily.

**7. Close (show the summary box on page 2, ~30 s)**

> So: conversion is cheap and it works. But under a fair control, none of diffusion's four claimed advantages survives
> without a qualification: slower, a dial that stays below AR, infilling only with a known length, and no reversal
> benefit. Our code, adapters, results and a no-GPU notebook that replays all of this are public; the links are on the
> first page of the report.

### The 3-minute version

Say blocks 1 and 2 in two sentences each, then this:

> Holding the data fixed, diffusion costs 30–46 points on code. On Qwen, most of the maths drop is the data, not
> diffusion: 0.92 to 0.50 for an AR model on the same data. The conversion is 17× slower; fewer steps make it faster
> but never reach AR. It wins at infilling only when told the exact gap length. And it showed no reversal benefit.
> Conversion is cheap and works, but a fair control removes or qualifies every claimed advantage.

### If you are asked "what was your contribution?" (have this ready word for word)

> BYOD's comparison mixes two effects. We built the control that separates them, a same-data AR adapter, and used it
> to test speed, the step dial, infilling with and without the gap length, and the reversal curse, none of which BYOD
> measured.

---

## Part 2. Numbers to know cold

| What | Number | Source |
|---|---|---|
| LLaDA 8B pretraining | 130,000 GPU-hours, 2.3T tokens | [P] |
| BYOD conversion cost | 3.1–4.0 h on one RTX PRO 6000 | [P] |
| LoRA | rank 1024, α 1024, on q_proj and v_proj; 323M (Qwen) / 491M (Ministral) trainable | [P], counts match ours |
| Training | 25,000 updates × batch 16 = 400,000 examples, lr 1e-5, cosine, seed 42 | [P] recipe, [V] runs |
| Our training runs | 3.0–3.3 h each on Colab G4 (RTX PRO 6000) | [V] |
| Examples per task | 500 (HumanEval 164, MBPP 257); BYOD used 125 | [V] |
| Code cost of diffusion (control − conversion) | Qwen HumanEval +45, MBPP +35; Ministral +38, +30 points | [V] |
| MMLU / ARC-C | Qwen control +5 to +7; Ministral within ±1.2 (not significant) | [V] |
| Qwen GSM8K | original 0.922 → AR control 0.502 → conversions 0.434 (ours) / 0.618 (released) | [V] |
| Ministral GSM8K | original 0.886 → control 0.850 → conversion 0.646 | [V] |
| AR control answer length on GSM8K | median 7 tokens | [V] |
| Speed, batch 16, GSM8K | conversion 5.57 s vs original 0.33 s per question: ~17× | [V] |
| Step dial, released Qwen GSM8K | 256: 0.618 · 128: 0.368 · 64: 0.178 · 32: 0.088 | [V] |
| Batch 1, 32 questions | original 17/32 in 3.07 s; conversion 17/32 needs 8.6 s; control 16/32 in 0.89 s | [V] |
| Single-line infilling (strict) | Qwen: original 0.688, control 0.524, ours 0.664, released 0.720; LLaDA 0.886 | [V] |
| Gap length 1.5× | conversions ~0.25 (after fence cut); LLaDA 0.50 | [V] |
| Reversal, name in prompt, 10k updates | forward 1000/1000 (AR), 999/1000 (conv); reverse 0/1000 both | [V] |
| Reversal, name-free, 10k updates | AR forward 300, reverse 0; conversion forward 9, reverse 2 | [V] |
| Decoding order (Kendall τ) | conversions 0.88–0.95 on GSM8K/HumanEval (nearly left to right); LLaDA 0.30 | [V] |
| Compute used | ~325 Colab CU across two accounts, plus ~10 CU on Anuj's | [V] |

---

## Part 3. The code

Repository: `github.com/akode2803/cs787-diffusion-conversion`. Line numbers below are for the pushed version.

### 3.0 The map (say this if asked "walk us through the code")

> There are two halves. `train/` trains the two arms: `retrain.py` runs BYOD's own trainer for the conversion, and
> `ar_control.py` trains our AR control. `eval/` evaluates any model: `arms.py` loads it, `sampling.py` generates,
> `tasks.py` scores, `run_eval.py` is the loop, and `analyze.py` does the statistics. A notebook replays the results
> without a GPU.

```
train/
  retrain.py        conversion: BYOD's own trainer + crash-safe resume points
  ar_control.py     our AR control (the main new piece)
  ar_loss.py        next-token targets and per-example loss (unit-tested)
  launch.py         runs a job on a Colab VM, starts the self-stop guard, mirrors results to Drive
  vm_guard.py       stops its own VM when the job ends, times out, or the GPU idles
  job_*.json        one file per GPU job
eval/
  arms.py           loads parent / AR control / BYOD conversion / LLaDA behind one interface
  sampling.py       the diffusion sampler and AR generation, both timed
  tasks.py          benchmarks (BYOD's prompts and scorers), HumanEval infilling, reversal scoring
  run_eval.py       the evaluation loop: one JSON line per example, resumable
  analyze.py        Wilson intervals, McNemar, paired bootstrap, Kendall τ
  reversal_data.py  the 1,000 invented facts
  reversal_recall.py  re-scores the reversal runs and counts recited facts
  make_summary.py   builds results/summary.json, the source of every number in the report
notebooks/tour_of_results.ipynb   no-GPU tour of the results
```

### 3.1 How the conversion is trained (BYOD's code, run by `train/retrain.py`)

The diffusion training step itself is BYOD's (`diffusion_lm/training.py` in their repo, pinned at commit 211d054).
Know what it does, because they may ask "show me where diffusion happens":

1. Load the base model with **bidirectional attention** and add LoRA on q_proj and v_proj.
2. For each example, sample a noise level **t ~ U[0.001, 1]**.
3. Replace each answer and padding token with the mask token ("MASK", or `<?>` for Ministral) with probability t.
   The prompt is never masked.
4. Run the model; at each masked position, cross-entropy against the **original token at the same position** (no
   next-token shift).
5. Weight by **1/t**, answer tokens 0.9 and EOS padding 0.1, average per example.

What *our* `retrain.py` adds (docstring lines 1–17, `COMMIT` line 24, `PATCHES` from line 27, `patch_byod` line 59):
- It patches four exact text blocks in BYOD's `training.py` so that training can resume on a new Colab VM:
  load our compact resume point, restore the best validation loss, save a compact checkpoint, log a `batch_id`.
- It **refuses to run** if BYOD's commit or any patched block differs, so we never silently change BYOD's maths.
- Nothing in the loss, model, data or schedule changes.

### 3.2 The AR control: `train/ar_control.py` (most likely to be asked)

Principle: call BYOD's own functions for everything (data, collator, LoRA setup, optimizer, schedule, validation
interval, checkpoint rule), so the only differences are the intended ones.

| Lines | What | How to explain it |
|---|---|---|
| 34–43 | `CleanCollator` | Uses BYOD's masking collator so batching and example order are identical, then **puts the clean tokens back** (`input_ids = labels`): the AR arm never sees masks. |
| 46–51 | `make_causal` | BYOD's loader marks the model bidirectional; we set `is_causal = True` so Hugging Face builds the normal causal mask. |
| 54–62 | `batch_loss` | Runs the transformer, then the output head **only at the positions that have a target** (saves memory), and computes next-token cross-entropy. |
| 66–85 | `check_model` | Start-up safety test. (1) Changes the last 3 tokens of a sentence and checks earlier outputs don't change: **no leak from the future**, attention really is causal. (2) Checks a fresh LoRA changes nothing (B starts at zero). The run stops if either fails. |
| 95–129 | `save_resume_point` / `load_resume_point` | Every 2,500 updates: adapter, optimizer, scheduler, step and best loss. A new VM loads it and `skip_first_batches` (line 210) skips used batches, so **example order is unchanged** after a crash. |
| 185 | data order | `train_data.shuffle(seed=seed)`, the same seed (42) as BYOD's run. |
| 236 | `batch_id` | Sum of the example indices in the batch, logged so the two runs can be compared batch by batch. |
| 244–246 | best checkpoint | Saved when validation loss improves, BYOD's rule. |

`train/ar_loss.py` (22 lines, pure torch, tested by `test_ar_loss.py`):
- `next_token_targets` (line 6): the hidden state at position i predicts token i+1. Targets are **answer tokens up to
  and including the first EOS**; the EOS padding after it is not a target, because an AR model stops at the first
  EOS.
- `per_example_mean_ce` (line 15): average the loss within each example, then across examples, as BYOD does, so long
  answers don't dominate a batch.

**The one deliberate difference from BYOD's loss:** BYOD trains on EOS padding (weight 0.1); the control doesn't,
because it has no equivalent. Say this if asked "is it perfectly matched?".

### 3.3 Loading models: `eval/arms.py`

- `BACKBONES` (line 21): the exact Hugging Face model and revision BYOD pins, and each model's mask token.
- `load_arm` (line 80) reads a spec string: `parent:qwen`, `ar:qwen:<adapter>`, `byod:qwen:<adapter>` or
  `byod:qwen:hub:Ruurd/BYOD-Qwen2.5-7B`, `llada`.
  - AR arms (`_load_causal`, line 62): plain Hugging Face causal LM, plus our PEFT adapter for the control.
  - Diffusion arms go through **BYOD's own loaders**, so the adapter, normalisation state and bidirectional attention
    are set up exactly as BYOD does.
- Every arm uses the same system prompt ("You are a helpful assistant.", line 18).

### 3.4 Generation: `eval/sampling.py` (second most likely)

**Diffusion: `diffusion_batch`, line 36** (BYOD's LLaDA sampler, extended to a batch):
1. Each row is `[prompt][answer positions, all MASK][padding]` (lines 44–50). Padding is hidden from attention so
   each row behaves as if alone (line 30).
2. `schedule` (line 16): how many masks to commit per step = positions ÷ steps. 256 positions in 256 steps is one
   token per step; in 32 steps, eight per step. **This is the compute dial.**
3. Each step (lines 54–77): **one forward pass over the whole sequence**, take the argmax prediction and its softmax
   probability at every masked position (lines 62–63), commit the `count` most confident (`topk`, line 75). Committed
   tokens never change (temperature 0, no re-masking of committed tokens).
4. `delay_eos` (lines 64–68): end-of-text predictions get the lowest confidence, so EOS is committed last (BYOD's
   setting).
5. `commit` (line 77) records the step at which each position was filled: used for Kendall τ and the Box 1 replay.
6. Bidirectional attention comes from line 29–31: a 4-D attention bias that only hides padding, **with no causal
   triangle**.

**AR: `ar_batch`, line 84**: Hugging Face greedy `generate` with a **KV cache** and left padding.

**Timing**: `torch.cuda.synchronize()` before and after (lines 53, 78 and 94, 98), same GPU for both, so the
17× is a fair wall-clock comparison.

Why diffusion is slow, in code terms: each of the 256 steps calls the model on the full sequence (line 31), while AR
with `use_cache=True` (line 96) only processes the one new token per step.

### 3.5 The evaluation loop: `eval/run_eval.py`

- `run_task` (line 51):
  1. Loads the examples; **skips any already in the output file** (line 60), so a lost VM loses nothing.
  2. Builds each input once: for diffusion, prompt + N mask tokens (lines 70–78); for AR, just the prompt.
  3. Sorts by length (line 81) to waste less compute on padding; batches of 16.
  4. Generates, scores, appends one JSON line per example (lines 98–118): answer tokens, commit steps, correctness,
     batch seconds.
- `budget` (line 23) and `BENCHMARKS` in `tasks.py` (line 19): 256 positions/tokens for GSM8K, HumanEval, MBPP; 64 for
  MMLU and ARC-C, **the same for every arm**.
- `tag_for` (line 32): every setting gets its own file name (`gsm8k_s32.jsonl`, `he_single_gapx1.5.jsonl`), so
  settings never mix.

### 3.6 Infilling: `eval/tasks.py`

- **Diffusion** (`diffusion_infill_row`, line 98): the answer region is: code fence, the code before the gap (fixed),
  **`gap` mask tokens**, the code after the gap (fixed), fence, EOS. Only the masks can change.
- `true_gap` (line 107): the length of the correct missing code in that model's tokens. `gap_length` (line 111)
  multiplies it by 0.5, 1.5 or 2 for the sweep (`GAP_FACTORS`, line 30).
- **AR**: the prompt shows the function with `<FILL_ME>` and asks for the whole function (lines 91–93).
  `score_infill_ar` (line 176) takes the first code block; `split_around_gap` (line 143) matches the code before and
  after the gap line by line, ignoring blank lines and spacing but not indentation, and cuts out the middle.
- **Strict score**: if the AR answer changed the surrounding code, it counts as wrong, because a diffusion answer
  physically cannot change it. This makes the two arms answer the same question.
- `run_program` (line 133): runs prefix + middle + suffix + the benchmark's tests in a separate Python process,
  10-second limit; pass = exit code 0.

### 3.7 Reversal: `eval/reversal_data.py`, `reversal_recall.py`

- `make_facts` (line 52): 1,000 invented names and descriptions from syllable lists, seed 787, all unique, so each
  reverse question has exactly one right answer.
- `write` (line 68): training file = four phrasings per fact × 8 shuffled epochs; evaluation files ask forward
  ("Who is X?", must contain the role and place words, `key_words` line 62) and reverse ("Who is the <description>?",
  must contain both parts of the name).
- `--forms namefree` (run 3): prompts like "State a fact." with the name only in the answer.
- `reversal_recall.py`: re-scores every answer, checks it matches the stored flags, and counts answers that are a
  trained fact word for word.

### 3.8 Statistics: `eval/analyze.py`

| Function | Line | One-line explanation |
|---|---|---|
| `wilson` | 14 | 95% interval for an accuracy; better than ±1.96·√(p(1−p)/n) near 0 or 1. |
| `mcnemar_p` | 22 | Exact test for two models on the same questions; uses only questions where they disagree, binomial p = 0.5. |
| `paired_bootstrap` | 32 | Resamples questions 10,000 times for a 95% interval on the accuracy difference. |
| `kendall_tau_b` | 40 | Rank correlation between position and commit step; 1 = strictly left to right. Handles ties when several positions commit in one step. |

### 3.9 Running on Colab: `launch.py`, `vm_guard.py`

- `launch.py` starts `vm_guard.py` first, then the job, and mirrors results to Drive every 60 s.
- `vm_guard.py` **unassigns its own VM** when the job writes its end marker, the time limit passes, the job process has
  been dead 30 minutes, or the GPU idles 25 minutes. We built it after a stuck upload kept a paid GPU idle ~70 minutes.
- `runner/` and `channel/`: let a teammate run a job on his own Colab account; requests and results are passed as files
  in the public repo. Run 3 of the reversal test ran this way on Anuj's account.

### 3.10 Tests (if asked "how do you know the code is right?")

- `train/test_ar_loss.py`: on toy tensors, the last prompt token predicts the first answer token, the first EOS is a
  target but padding is not, and the loss averages per example first.
- `train/test_retrain.py` (runs on the VM): stops the retrain at update 100 as if the VM died, resumes to 200, and
  checks the restored weights reproduce the logged validation loss and that `batch_id`s match the AR control's on both
  sides of the resume.
- `eval/test_eval_local.py`: every canonical middle, spliced into its function, passes the tests (all 1,000); and the
  AR scorer, given the canonical whole function, cuts out a middle that passes.
- `check_model` at every training start (causal, LoRA no-op).
- Identical `batch_id`s between the two training runs.
- Every number in the report is rebuilt from the raw result files by `make_summary.py`.

---

## Part 4. Questions and answers

### On the design

**Why is your control fair?** Same base model and revision, same data and order (batch ids match), same LoRA rank,
targets, learning rate, schedule, batch size and updates, same prompt and token budget at evaluation. It differs only
where an AR model must: causal attention, clean input, next-token loss. One extra difference: it doesn't train on EOS
padding, which BYOD weights 0.1, because an AR model stops at the first EOS.

**Why not just compare with the original model like BYOD?** Because fine-tuning on BYOD's data changes the model by
itself: on Qwen it takes GSM8K from 0.92 to 0.50 with no diffusion involved.

**Why LoRA on Q and V only, and why rank 1024?** It is BYOD's fixed setting [P]; we kept it so the control matches.
Q and V are the classic LoRA targets, and they control where attention looks and what it gathers, which is what
changes when attention becomes bidirectional [H]. Rank 1024 is effectively full rank on V (its output is 512 wide on
Qwen) and 29% of full rank on Q.

**Why 500 examples?** BYOD used 125, which gives about ±8 points of uncertainty. 500 gives about ±4, and our main
effects (30–46 points) are far larger. We also use paired tests.

**Why 256 tokens for everything?** BYOD trains on 256-token sequences and gives its AR models 256. Where AR answers were
cut off (Ministral original: 141 of 500 GSM8K answers), we reran them at 512. Diffusion arms almost never fill 256.

### On the results

**How is the speed comparison fair?** Same GPU, same library, batch 16 for both, KV cache for AR, timed between CUDA
synchronisations. A production AR server like vLLM would make AR even faster, so if anything we understate the gap.

**Why does the released conversion beat the AR control on GSM8K (0.618 vs 0.502)?** The control learned BYOD's terse
style and answers in a median of 7 tokens without working; the conversion writes about 95. Why the two objectives pick
up the style differently, we don't know [?].

**Why is your retrain worse than the released adapter on GSM8K (0.434 vs 0.618)?** Not isolated. It matches on 5 of 7
tasks. Candidates: run-to-run variance, or a config difference in the answer/padding weighting. The report says so.

**Why does accuracy collapse with fewer steps?** Tokens committed in the same step are chosen independently; they can
contradict each other ("defdef", repeated digits), and committed tokens are never revised.

**Why do the conversions write left to right?** [H] 25,000 LoRA updates don't undo trillions of tokens of left-to-right
pretraining; the token right after the written text is usually the most confident. LLaDA, trained as diffusion,
is far less sequential (τ 0.30).

**What exactly goes wrong with a longer gap?** The model must fill every mask. It writes the right line, then puts
junk (often a closing code fence) in the spare positions, which breaks the program. We even cut at the first fence, as
for AR answers; it still drops to about 0.25.

**So is diffusion useless?** No. It gives a hard compute dial and real bidirectional context, and BYOD makes it cheap to
study. Our point is that a conversion inherits diffusion's costs faster than its benefits, and LLaDA shows native
diffusion training handles infilling far better.

### On the code (expect "open file X and explain")

**Where does the model become bidirectional?** For the conversion, BYOD's loader (`load_denoising_model`); at
generation, `sampling.py` line 29–31 passes an attention bias that hides only padding, with no causal triangle. For the
control, `make_causal` (`ar_control.py` line 46) switches it back, and `check_model` (line 66) proves it.

**Where is the diffusion loss?** In BYOD's `training.py`, which `retrain.py` runs unchanged except for resume logic.
Walk through the five steps in §3.1 above.

**Where is the next-token shift?** `ar_loss.py` line 6: targets are `labels[:, 1:]`, predicted from the position
before. The conversion has no shift: the masked position predicts its own token.

**How does the sampler choose what to unmask?** `sampling.py` lines 62–77: softmax confidence of the argmax at every
masked position, then `topk` of the most confident, as many as the schedule allows that step.

**How do you know two runs used the same data order?** Both shuffle with seed 42 and log `batch_id` (sum of example
indices) at each logging step; we compared at updates 100, 200 and 25,000.

**What happens if the VM dies mid-run?** Training: resume point every 2,500 updates, `skip_first_batches` keeps the
order. Evaluation: one JSON line per example, already-done ids are skipped on rerun.

**Did you use AI tools?** Yes; LLM use was allowed. The code was written with an AI assistant; we reviewed it, ran the
tests and checked every reported number against the raw result files. Be ready to explain any file above.

### Weak points: say them before you are asked

1. **Reversal design.** In runs 1–2 the name was in the prompt, so the masked model could copy it. We found this
   ourselves and reran name-free (run 3). The conversion then didn't learn the facts, so the reversal question itself
   remains open.
2. **One retrain.** On Ministral the controlled pair uses the released adapter, not our own retrain.
3. **Retrain vs released gap** on GSM8K is unexplained.
4. **Batch-1 timing** uses only 32 questions.
5. **One prompt for all arms**, so our absolute numbers differ from BYOD's Table 3.
6. **The control doesn't train on EOS padding**, BYOD's 0.1-weighted term, because AR has no equivalent.

Mistakes we caught (good to mention, they show the checks worked): the first infilling scorer flagged ~90% of AR
answers over blank lines (fixed, rescored offline); reversal run 1 was too short for the conversion to learn
(rerun at 10,000 updates); the reversal design flaw (run 3); we first called the conversion's 9 forward hits "chance"
until a shuffle test showed they're above it.

### What would you do next?

1. Rerun the name-free reversal test with a higher learning rate or more updates, until the conversion knows the facts
   forward, then read its reverse score.
2. Our own Ministral retrain.
3. Train with padding inside infilling gaps, so the conversion can stop early when given spare positions.
4. Speed against a production AR server (vLLM).

---

## Who covers what (suggestion)

| Member | Presents | Must answer on |
|---|---|---|
| Aryan Kumar | Blocks 1, 2 and 7 (question, control, close) | Part 2 numbers, design questions |
| Manoj Kumar Parida | Block 3 (cost of diffusion, GSM8K) | `ar_control.py`, `ar_loss.py`, `retrain.py` (§3.1–3.2) |
| Rajdatta Kohale | Blocks 4 and 5 (speed, infilling) | `sampling.py`, `run_eval.py`, `tasks.py` (§3.4–3.6) |
| Anuj Chaudhary | Block 6 (reversal) | `reversal_data.py`, `analyze.py`, `launch.py`, `vm_guard.py`, `runner/` (§3.7–3.9) |

Everyone: Part 1 block summaries, Part 2, and the weak points.
