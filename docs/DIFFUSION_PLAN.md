# What Does Diffusion Actually Buy? Project plan

Status on 7 Nov 2026: topic chosen by the user. Not yet submitted. Hypotheses below are fixed before any experiment. The only results so far are the feasibility checks marked "measured".

## Submission text
**Title:** What Does Diffusion Actually Buy? A Controlled Study of LoRA-Converted Diffusion Language Models

**Base paper:** Kuiper and Bagheri, "BYOD: Build Your Own DLM - Efficient Autoregressive-to-Diffusion Language Model Conversion", arXiv:2610.41574, 2026.

**Abstract:** Diffusion language models generate text by filling in many positions in parallel, and are claimed to offer faster generation, infilling, and resistance to the reversal curse. BYOD showed that a frozen autoregressive LLM can be converted into a diffusion model with LoRA alone in a few GPU hours. But it compares conversions only with their unchanged parents, on standard benchmarks, without measuring wall-clock speed. So we cannot tell which changes come from diffusion and which come from the extra fine-tuning, or whether a conversion gains the claimed benefits at all. We train matched autoregressive LoRA controls on the same data, with the same adapter size and number of updates, and compare them with converted models and a natively trained diffusion model (LLaDA). We measure code and text infilling, reversal of newly taught facts, reasoning and knowledge benchmarks, and the trade-off between quality and real generation time. We also analyse the order in which models commit tokens and the errors parallel decoding causes. The result is a cost-benefit account of what conversion gains and loses, plus an interactive demo of the denoising process.

**Paper for the 3-minute video:** BYOD, the same as the base paper (user's decision, 8 Nov).

## Why this is more than rerunning BYOD
Checked in the paper's text (see gaps below). BYOD's Table 3 already compares parents with conversions on nine tasks, so more of the same would add little. It does not have:
- an AR LoRA control trained on the same data; its AR columns are unchanged parents
- wall-clock speed; the authors say fewer steps do not guarantee a speedup
- real infilling; its only test is a right-context copy check, which the paper says does not measure infilling quality
- reversal or planning tests
- larger samples; each task uses 125 examples, about +/-8 points

Reversal is partly pre-empted: masked fine-tuning already helps AR models (arXiv 2510.09885), and DiffER (arXiv 2601.07347) says diffusion LLMs still show the curse. That makes the outcome uncertain, so it is worth testing, but we must cite both. My searches found no same-data AR control for a LoRA conversion. That is not proof that none exists.

## Models
| Arm | Qwen2.5 7B | Ministral 8B | Source |
|---|---|---|---|
| Parent, unchanged | yes | yes | Hugging Face, ungated |
| AR LoRA control | yes | yes | We train |
| BYOD conversion | yes | yes | Released adapters |
| BYOD conversion, retrained | yes | if time | We train, to check reproduction |
| LLaDA 8B Instruct | one shared reference | | Hugging Face, ungated |

The control matches BYOD's data order, 25,000 updates, batch size 16, rank 1024 on q and v, learning rate, and schedule. Only the causal mask and next-token loss differ. Both backbones are ungated, so no Hugging Face token is needed. Llama and Gemma are stretch options and would need one.

## Experiments
1. **Standard benchmarks.** GSM8K, MATH-500, MMLU, ARC-C, HumanEval, MBPP on at least 500 examples where the set allows, with paired confidence intervals.
2. **Infilling.** HumanEval-Infilling plus a text infilling set. AR arms get the prefix and suffix in a prompt. Diffusion needs the gap length in advance, so we report both true length and a length sweep.
3. **Reversal.** Teach about 1,000 invented facts in one direction to each arm with identical extra training, then test both directions.
4. **Speed.** Accuracy against seconds at 32, 64, 128 and 256 steps, at batch sizes 1 and 16. The AR arm uses a KV cache. We report the same software stack and a vLLM reference.
5. **Decoding behaviour.** How close commit order is to left-to-right (Kendall tau), and how often parallel decoding produces doubled or broken tokens.

Stretch: Countdown or Sudoku planning. Demo: live denoising view, built from BYOD's Gradio app.

## Hypotheses, fixed before data
- H1: conversions beat AR LoRA controls on infilling at the true gap length.
- H2: conversions beat AR LoRA controls on reversed facts.
- H3: at matched accuracy on GSM8K, conversions are not faster than AR models with KV cache.
- H4: the maths and code gap against parents comes from conversion, not the data: AR LoRA controls stay within 5 points of parents on GSM8K.
- H5: commit order is mostly left-to-right on maths and less so on infilling.

Any outcome is reportable. If H1 and H2 fail, the finding is that conversion keeps the costs of diffusion without its benefits.

## Feasibility, measured 7 Nov on a Colab G4 (RTX PRO 6000, 96 GB)
- Released BYOD-Qwen adapter loads and generates, using 16.6 GB.
- 128 tokens took about 0.8 s at 32 steps, 1.6 s at 64, and 3.3 s at 128, batch size 1, about 25 ms per step. The AR parent has not been timed yet.
- Output shows visible glitches even at 128 steps ("as as", "Eiff"). Nine samples only, not a quality measure.
- Real BYOD training ran 300 updates at about 2.3-2.7 updates per second, which extrapolates to about 3 h for 25,000. Validation time is extra.
- Setup needed `pip uninstall torchao` (version clash with PEFT).
- One G4 plus one A100 ran together on one account. Two G4s also ran together on 8 Nov at 20.10 CU/h, after one earlier refusal, so a second G4 is possible but not guaranteed.
- Two G4 sessions vanished without warning on 7 Nov, cause unknown. All runs use resume points on Drive and `supervise.sh`; see `diffgap/train/` and the experiment log.
- G4 beats the 40 GB A100 per CU for training, 30 against 46 CU per run. It was also cheaper for batch-1 generation.
- G4 costs 10.05 CU/h on this account, which held 131.8 CU on 7 Nov, so about 13 G4 hours. Three training runs use about 90 CU, so evaluations will need another account.

## Schedule
| Date | Work |
|---|---|
| Sat 7 | Submit topic. Write AR control trainer and test it |
| Sun 8 | Train AR controls. Build infilling, reversal and speed harnesses |
| Mon 9 | Run evaluations. Retrain Qwen conversion |
| Tue 10 | Finish evaluations. Write video script on BYOD |
| Wed 11 | User records and submits video |
| Thu 12 | Report, figures, demo |
| Fri 13 | Final checks, submit by midnight |
| After 14 | Viva guide for all four members |

## Main risks
- The training data is terse, so AR controls may lose accuracy through style alone. Measure answer length in every arm.
- Prompted AR infilling may already be strong, so H1 may fail. It is still a result.
- Evaluation, not training, is the likely bottleneck: 256 steps per answer is slow on large sets. Cut sample sizes before cutting arms.
- Scripts must run on one G4 at a time unless a second account works.
- BYOD's repo notes that exact regeneration of published scores has not been verified, so our numbers may differ.
- BYOD is a week-old preprint and has not been peer reviewed.

## Sources
- BYOD paper: https://arxiv.org/abs/2610.41574 (main text read; appendix details came through a summary)
- BYOD code: https://github.com/RuurdKuiper/BYOD (commit 211d054, MIT)
- LLaDA: https://arxiv.org/abs/2502.09992
- Masked fine-tuning on AR models: https://arxiv.org/abs/2510.09885
- DiffER: https://awesomepapers.io/llm-papers/papers/2601.07347 (search summary only)
