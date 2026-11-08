# Evaluation harness: design and settings

Code: `diffgap/eval/`. Status on 8 Nov 2026: local logic tested; GPU check passed except one part that failed on
a bug in the check script, now fixed. AR infilling scoring changed after the check and is tested locally only.
Results go in `FINDINGS.md`.

## Arms
| Name | Spec | Kind |
|---|---|---|
| qwen-parent | `parent:qwen` | AR |
| qwen-ar-control | `ar:qwen:<Drive best>` | AR |
| qwen-byod-released | `byod:qwen:hub:Ruurd/BYOD-Qwen2.5-7B` | diffusion |
| qwen-byod-retrained | `byod:qwen:<Drive best>` | diffusion |
| ministral-parent | `parent:ministral` | AR |
| ministral-ar-control | `ar:ministral:<Drive best>` | AR |
| ministral-byod-released | `byod:ministral:hub:Ruurd/BYOD-Ministral-8B` | diffusion |
| llada | `llada` | diffusion, shared reference |

AR arms load the base at BYOD's pinned revision (Hugging Face main was still that revision on 8 Nov). Diffusion arms
go through BYOD's own loaders.

## Choices that differ from BYOD's evaluation, and why
- **One prompt for every arm**: system "You are a helpful assistant." plus the task prompt, through the model's chat
  template. This is the format all our trained arms saw in training. BYOD uses an empty system prompt for diffusion
  and none for its AR parents, so its two columns do not share a prompt.
- **One budget for every arm**: 256 positions or tokens for GSM8K, MATH, HumanEval, MBPP; 64 for MMLU and ARC-C.
  These are BYOD's own AR budgets. BYOD runs diffusion with LLaDA's profile (512 positions for GSM8K, ARC-C and
  HumanEval, 3 for MMLU), which would give the two kinds of arm different budgets and cost about twice as much.
  Our training sequences were 256 tokens, so answers longer than that were never seen in training.
- **One token committed per step** by default (steps = positions), as in BYOD's profiles. The speed study changes this.
- **End-token handling**: generative tasks and infilling delay end tokens to the last steps (BYOD's
  `confidence_eos_eot_inf`); multiple-choice tasks do not, as in LLaDA's profile. We never ban the end token
  (LLaDA's HumanEval setting), because a model that cannot stop must fill the whole budget.
- **Sample sizes**: 500 for GSM8K (first 500), MATH-500, MMLU (BYOD's seeded shuffle), ARC-C (first 500); all 164
  HumanEval and 257 MBPP-sanitized test problems; 500 seeded examples from each infilling set. BYOD uses 125.

## What is reused from BYOD unchanged
Benchmark prompts, example selection, answer extraction and scoring (`load_benchmark`, `score_prediction`), the
diffusion loaders, and the LLaDA low-confidence sampler rule.

## Batched diffusion sampling
BYOD samples one example at a time. Ours runs a batch laid out as [prompt][answer][padding], with the padding hidden
from attention and placed after the answer, so each real token keeps its position. The commit step of every
position is recorded. `gpu_check.py` compares it with BYOD's `llada_generate` on the same inputs.

## Infilling
HumanEval single-line and multi-line infilling (`loubnabnl/humaneval_infilling`, revision ad46002f24b1), 500 seeded
examples each. Every arm gets the same instruction: return the complete function with the gap filled, given the code
with a `<FILL_ME>` marker. A diffusion arm's answer holds the code before and after the gap as fixed tokens with
masks in between, so it can only change the gap. An AR arm writes the whole function (up to 512 tokens); its middle
is cut out when the code around the gap is unchanged, otherwise the whole function is run and the case is flagged.
An earlier version asked AR arms for the missing lines only; in the GPU check the parent then often repeated code
from after the gap, breaking programs for a reason unrelated to infilling.
Gap length for diffusion: the true length in tokens by default, and 0.5, 1.5 or 2 times it in the length sweep.
Checked on the Mac: all 1,000 canonical middles pass; `pass` as the middle passes 1 of 200.

## Reported per file (`analyze.py`)
Accuracy with a Wilson 95% interval; paired difference between arms with a bootstrap 95% interval and McNemar's
exact p; median answer length in tokens (the terse-answer risk); seconds per example; doubled words per 100 words;
Kendall tau between position and commit step (1 means strictly left to right).

## Run plan and cost
Speeds measured on a G4 on 8 Nov (`gpu_check.py`, Qwen, GSM8K length): diffusion 0.033 s per step at batch 1 and
0.385 s at batch 16, so batching gains only 1.4x because each step recomputes the whole sequence. AR parent 2.8 s
per answer at batch 1 and 0.8 s at batch 6. Estimates below are G4 hours at 10.05 CU/h.

| Job file (`diffgap/train/`) | Arms and tasks | Estimate |
|---|---|---|
| `job_eval_qwen_pair.json` | Qwen AR control, Qwen retrained conversion; all core tasks | ~2.6 h, 26 CU |
| `job_eval_qwen_reference.json` | Qwen parent, released BYOD-Qwen; all core tasks | ~2.6 h, 26 CU |
| `job_eval_ministral.json` | Ministral AR control, parent, released conversion | ~3 h, 30 CU |
| `job_eval_llada.json` | LLaDA 8B Instruct | ~2.2 h, 22 CU |
| `job_eval_speed_gap.json` | GSM8K at 32/64/128 steps, batch-1 timing, infilling gap sweep | ~1.4 h, 14 CU |
| `job_eval_reversal.json` | Reversal: baseline, teach facts, test both directions | ~1 h, 10 CU |

Core tasks: GSM8K, MMLU, ARC-C, HumanEval, MBPP, HumanEval single-line and multi-line infilling. About 130 CU in
all. Run with `supervise.sh SESSION JOB_FILE G4`; two G4s at a time per account. Results land in
`CS787-Diffusion/eval/main/<arm>/` on Drive. MATH-500 is dropped from the core set: at 256 tokens the parent's
answers were cut off (0/4 in the check), and 512 positions would roughly triple its diffusion cost.

## Resume
Each example is one JSON line. A rerun skips what is written, and `launch.py` mirrors the results folder to Drive
every 60 s and restores it on a new VM.
