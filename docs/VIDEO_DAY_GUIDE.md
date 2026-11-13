# Video-day guide: questions on the BYOD paper (11 Nov, in class)

Our 3-minute video is shown in class, and the audience can ask questions during or after it. The video explains the
**paper**, so most questions will be about the paper and the course concepts behind it. A few may be about our
experiments.

This guide covers all of that. The full viva later is about our code and experiments, and it has its own guide,
`VIVA_GUIDE.md`.

**Labels:**
- [P] is from the paper (arXiv 2610.41574, HTML v1, read on 10 Nov).
- [V] is our own verified result.
- [H] is our interpretation. Say "we think".

**Where the material is:**
- Slides: "BYOD Paper Talk" on claude.ai (13 slides).
- Script: `VIDEO_SCRIPT.md`.
- Report: `report/report.pdf`.

---

## 1. The 30-second answer to "what is this paper?"

> BYOD (Kuiper & Bagheri, 2026) turns an existing autoregressive chat model into a masked-diffusion language model
> without pretraining one from scratch. It swaps the causal attention mask for a bidirectional one, freezes the base
> model, and trains rank-1024 LoRA adapters on the query and value projections with LLaDA's masked-diffusion loss:
> 25,000 updates, 3–4 hours on one Colab GPU. It works on Gemma, Llama, Qwen and Ministral. The best conversion comes
> within 1.3 points of LLaDA on nine benchmarks, but every conversion trails its own AR parent, most in maths and code,
> and generation quality lags.

## 2. The paper, section by section

### 2.1 Motivation (§1, Table 1) [P]

- **Why diffusion LMs at all?** An AR model fixes the order (left to right), sees only earlier tokens, and adds one
  token per forward pass. A diffusion LM reconstructs many masked positions per step with bidirectional context.
  Its number of function evaluations (NFE) is chosen independently of the output length, and early predictions can
  be revised. BYOD's own sampler never revises a committed token, though.
- **Cost of the native route:**
  - LLaDA 8B was pretrained from scratch on 2.3T tokens, using 130,000 GPU-hours. The authors estimate that at
    about $675k and 44.1 t CO₂e. These are illustrative rental and energy estimates, not bills.
  - BYOD's conversion, for the Llama row: 3.2 GPU-hours, at most 102.4M tokens, about $11 and 0.9 kg.
  - Other systems, for comparison: DiffuLLaMA used 65B tokens and full fine-tuning; Dream 580B tokens; Efficient-DLM
    500B; Fast-dLLM v2 about 1B tokens, full fine-tuning; Uno 7B tokens with LoRA.
- **How the GPU-hours are estimated** where a paper doesn't report them (Appendix A):
  - The formula is GPU-h = 6·N·D / (0.40 · 989 TFLOP/s · 3600).
  - That is the 6ND training-compute rule (Hoffmann et al. 2022), with an assumed 40% model FLOPs utilisation on an
    H100's dense BF16 peak.
- **The three reasons the authors give:**
  - Pretraining a diffusion model is costly.
  - Conversion makes DLM research possible without a cluster.
  - The same cheap intervention applied to many model families lets you study how architecture affects diffusion.
- **The caveat:** conversion reuses the AR parent, whose own pretraining cost is not counted.

### 2.2 Related work (§2) [P]

**Discrete diffusion:**
- **D3PM:** categorical corruption via transition matrices. Its "absorbing" variant sends tokens to a [MASK] state.
- **MDLM** and Shi et al.: the absorbing (masked) case reduces to a simple noise-weighted cross-entropy.
- **RADD:** reparameterises the predictor as conditionals over clean tokens.
- **Uniform/multinomial diffusion:** corrupts tokens to random vocabulary items. BYOD uses the absorbing mask, as LLaDA
  does.

**Conversions:**
- **DiffuLLaMA:** 65B tokens, full fine-tuning, shifted prediction.
- **Dream:** Qwen2.5, 580B tokens, shifted-prediction initialisation, token-level noise rescheduling.
- **Efficient-DLM:** 500B tokens, block-wise attention, position-dependent masking.
- **Larger models:** RND1 (30B), LLaDA2.0 (16B and 100B) and DiffusionGemma (25.2B, uniform diffusion).

**Hybrids:**
- **Block Diffusion:** AR across blocks, diffusion within each block. It allows a KV cache between blocks and
  variable-length output.
- **Fast-dLLM v2:** block-wise, with hierarchical caching.

**LoRA work:**
- **LAD,** the authors' own earlier work: LoRA plus a hybrid corruption (masks, swaps, duplications, span shifts).
- **Uno** (diffusion-draft adapters, with the AR model as verifier), **dLLM** and **NaRA** all add LoRA to models that
  already generate by diffusion.

**BYOD's novelty:** a simple iid absorbing-mask LoRA recipe, the same across four families, with the first reported
Mistral conversion. Each conversion is compared with its exact AR parent.

### 2.3 Method (§3, Tables 2 and 7) [P]

**1. Bidirectional attention.** The causal mask is replaced by a full mask in every layer. The prompt, answer and
padding positions all attend to each other.

**2. LoRA on Q and V only:**
- Rank r = 1024, α = 1024, dropout 0.
- The backbone, embeddings, LM head, biases and norms are all frozen.
- Trainable share: 4.07% (Qwen, 323M) to 5.77% (Ministral, 491M) of final parameters. Gemma has 572.5M trainable
  (5.33%), Llama 436.2M (5.15%).
- Rank is fixed across families, so the absolute adapter size differs: a confounder in cross-family comparisons
  (stated in the paper).

**3. No label shift.**
- An AR head at position i predicts token i+1. BYOD instead predicts the clean token at the same position i, reusing
  the same output head.
- DiffuLLaMA and Dream keep the shift. BYOD removes it.

**4. Mask token.** An existing single-token string serves as the mask: "MASK" for Gemma, Llama and Qwen, `<?>` for
Ministral. So the vocabulary doesn't grow.

**5. Objective (Eq. 1–2):**
- Sample t ~ U[0.001, 1]. Mask each answer and padding position independently with probability t.
- ℓ_R = −1/(t·|R|) · Σ over masked positions in R of log p(x0_i | prompt, x_t), for R = answer A or padding P.
- L = E[0.9·ℓ_A + 0.1·ℓ_P].
- The 1/t factor corrects for the sampled masking rate.
- The first EOS counts as part of the answer, and later EOS tokens are padding.
- Prompt and chat-template tokens are never masked and never scored.
- Training masks are resampled online. Validation masks are fixed by seed.

**6. Merging:** after training, W ← W + (α/r)·B·A folds the adapter into the base. The parameter count returns to the
original (e.g. Llama 8.47B → 8.03B). The attention change stays.

**7. Data:**
- 1M examples: 45% general instructions (Clean-Instruct, Tülu 3, Alpaca-GPT4, Alpaca), 18% multiple-choice reasoning
  (MMLU, HellaSwag and ARC training splits), 18% maths (Orca-Math, GSM8K train), 19% code (OpenCoder, MBPP train).
- Deduplicated, and exact benchmark-prompt matches removed.
- Only examples up to 256 tokens.
- Every model sees the same shuffled prefix.

**8. Training settings:**
- 25,000 updates at batch 16, so 400k examples.
- AdamW, peak lr 1e-5, cosine schedule, 100 warm-up steps, weight decay 0.01, gradient-norm clip 0.5.
- FP8 hybrid execution with BF16 master weights.
- One NVIDIA RTX PRO 6000 (96 GB) on Colab.
- Time: 3.1 h (Qwen) to 4.0 h (Gemma).
- Llama-50k: 800k examples, linear decay from 1e-5 to 1e-6.

### 2.4 Inference (§3.4, Appendix D) [P]

**The sampler** is LLaDA's fixed-transfer sampler with low-confidence remasking. Start from a fixed-length answer
block that is all [MASK]. At each step:
- predict every masked position;
- commit the most confident predictions (a fixed number per step);
- leave the rest masked.

Committed tokens are final.

**Settings:**
- Greedy for benchmarks. Temperature 0.7 for open-ended text.
- One block equal to the answer length. For benchmarks, steps = length, so one token per step. Examples: GSM8K 256
  tokens in 256 steps; MMLU 64 tokens in 64 steps.

**Delayed EOS:** a predicted end token gets the lowest confidence, so it can be predicted early but is committed late.
This stops the model ending too soon.

**AR parents** use greedy decoding with similar max-new-token budgets (Table 9). The paper notes that an AR token
budget is not an NFE budget.

**Example counts:** 125 fixed examples per benchmark, the same for all models, so comparisons are paired. That is
small, so expect intervals of about ±9 points.

### 2.5 Results (§5) [P]

**Table 3, averages over 9 tasks** (ARC-C, GPQA, HellaSwag, MMLU, MMLU-Pro, GSM8K, MATH-500, HumanEval, MBPP):

| Model | Diffusion | AR parent |
|---|---|---|
| Gemma 2 9B | .506 | .657 |
| Qwen2.5 7B | .490 | .716 |
| Ministral 8B | .499 | .644 |
| Llama 3.1 8B (25k / 50k) | .487 / .492 | .588 |
| LLaDA 8B Instruct (in their harness / published) | .519 / .545 | – |

- **Gemma** is the best conversion, 1.3 points below LLaDA.
- **Qwen** has the strongest parent but is not the best conversion. So "parent quality alone does not determine
  conversion quality".
- **Training longer:** the Llama-50k run (twice the updates) gains only 0.5 points. It improves on 5 tasks and drops
  on 4. Validation loss still falls almost monotonically and plateaus near the end.
- **Diffusion is better on some multiple-choice tasks.** Gemma: HellaSwag .752 vs .696, MMLU .688 vs .648. Ministral:
  ARC .832 vs .768. The big losses are maths and code.
- **Qwen:** GSM8K .608 vs .920, MATH .352 vs .784, HumanEval .296 vs .890, MBPP .440 vs .760.
- **Code syntax errors** (Appendix E):
  - 28.0% of BYOD-Llama-50k HumanEval programs fail Python's parser, and 8.8% on MBPP. The AR parent fails 0%.
  - Examples: "defdef", a missing ")", "for for".
  - The authors call these local-consistency failures consistent with parallel prediction, but say they don't prove
    the mechanism.
- **Fluency** (§5.2, Table 12):
  - Phi-4 14B perplexity of 128-token answers: conversions 2.7–5.0× their parents across NFE budgets.
  - At 64 NFE: BYOD 8.3–11.1, LLaDA 4.1, parents 2.2–3.0.
  - Distinct-n (repetition) is generally lower than the parents'.
  - More NFE helps. At 128 NFE BYOD-Qwen reaches 6.21, LLaDA 2.79.
- **Bidirectional copy test** (§4.4, §5.4):
  - The prompt asks the model to fill "Answer: [MASK]. COPY: apple." The clue is to the right of the mask, so a causal
    model can't use it.
  - Adding the clue changed the prediction on 100% of items for every model.
  - Exact copy rates: Gemma, Ministral and LLaDA 100%; Llama-25k 90%; Llama-50k 70%; Qwen 20%. Without the clue,
    every model scored 0%.
  - The authors' reading: information flows bidirectionally in all of them, and the lower scores are failures to *use*
    the clue.
- **Merging** (Appendix B): Llama-25k with the adapter merged in gives a 9-task mean of 48.7% → 48.3%. Perplexity and
  Distinct-n get slightly better.

### 2.6 The authors' own limitations (§7) [P]

- **Efficient conversion is not efficient generation.** This is the line quoted on slide 10. Quality trails, especially
  when NFE < output length.
- **They measure NFE, not wall-clock time.** Fewer steps need not mean faster, because each step processes the whole
  answer block. Their efficiency claim is about training.
- **The cross-family comparison is not controlled:** size, tokenizer, pretraining, alignment and adapter budget all
  differ.
- **The automatic metrics are partial:** Phi-4 perplexity reflects another model's preferences, and Distinct-n misses
  factuality, grammar and coherence.
- **Only LLaDA was rerun** in their harness. They didn't measure energy.
- **Next step** (§8): partial or full diffusion fine-tuning initialised from the merged model.

---

## 3. Likely questions about the paper, with answers

**Q: How can a model trained for next-token prediction predict the token at the *same* position?**
A: With causal attention, position i only sees tokens up to i. After the switch, position i also sees everything to
its right, including the masked slot's neighbours. The LoRA on Q and V re-routes attention so the final hidden state
at a masked position encodes "what belongs here", and the frozen head maps that to a token. 25,000 updates are enough
for this to work, but not perfectly; see the parse errors. DiffuLLaMA and Dream keep the shift instead, so the head
keeps its original "next token" role. [P for the facts, H for the mechanism]

**Q: What is the 1/t factor?**
A: With masking rate t, about t·L tokens are masked. Weighting by 1/t makes each noise level count properly in
expectation. In MDLM/LLaDA the 1/t-weighted masked cross-entropy is an upper bound on the negative log-likelihood (an
ELBO), so training it trains a proper generative model. BYOD also divides by |R|, which turns it into a per-token
average. [P for the formula; the ELBO link is from MDLM/LLaDA, class material]

**Q: Why train the padding at all, and why weight 0.1?**
A: The answer block has a fixed length. The model must learn to fill unused positions with EOS, or it writes junk to
the end of the block. Padding is easy and plentiful, so weight 0.1 keeps it from dominating the loss. [P; the
"author-confirmed" label on this weighting is in BYOD's repository config `paper.yaml`, not the paper]

**Q: Why only query and value, and why rank 1024? Isn't that hardly "low-rank"?**
A: The paper fixes this as a transfer setting, and doesn't claim it is optimal. Their earlier LAD work found high
ranks work better for diffusion adaptation. Q/V is the classic LoRA choice. They suggest ablations on K/O, the MLPs
and norms as future work. Yes, 1024 against a hidden size of 3,584 for Qwen is high-rank, about 4–6% of all
parameters. It is still far cheaper than full fine-tuning, and the adapter can be merged away. [P]

**Q: How is this different from LLaDA?**
A: LLaDA is pretrained as a diffusion model from scratch: 2.3T tokens, 130k GPU-hours. BYOD starts from a finished AR
chat model and only trains adapters: at most 102M tokens, a few GPU-hours. The objective and sampler are the same
family. The trade-off: BYOD is 1.3–3.2 points below LLaDA on average accuracy (Table 3), and clearly worse on fluency
(perplexity 8–11 vs 4). [P]

**Q: Is the converted model faster than the AR model?**
A: The paper does not claim that. It measures NFE, not time, and says fewer steps need not be faster. Each diffusion
step runs the full model over the whole answer block, and full bidirectional attention rules out the usual KV cache.
In our measurements it was 17× slower than the original model at batch 16. [P, V]

**Q: How is the output length chosen?**
A: You fix it in advance: 64 for MMLU, 256 for GSM8K and HumanEval. The model fills unused positions with EOS. Delayed
EOS stops it ending too early. Block diffusion is one fix for variable length. [P]

**Q: Why does code break so often?**
A: Code needs exact local consistency: matching brackets, no repeated keywords. Tokens committed in the same step are
predicted independently given the current context, so two neighbouring positions can both choose "def". Committed
tokens are never revised. 28% of BYOD-Llama's HumanEval programs don't parse. [P for the facts; the mechanism is the
authors' "consistent with", not proven]

**Q: Why is BYOD-Qwen so bad at the copy test (20%)?**
A: The paper doesn't explain it. The prediction did change in 100% of cases, so information does flow from the right.
Qwen just often fails to copy the token exactly. Its adapter is also the smallest in absolute size (323M). [P; the
adapter-size angle is H]

**Q: Doesn't bidirectional attention destroy what the AR model learned?**
A: Not fully: the conversions keep much of their parents' knowledge (multiple-choice scores are close to the parents',
sometimes higher). The frozen base and the LoRA limit forgetting. The authors cite LoRA's protection against
catastrophic forgetting. Generation-heavy tasks suffer most. [P]

**Q: How did they measure perplexity for a diffusion model?**
A: A masked diffusion model has no exact left-to-right likelihood, and its ELBO is not a proper test-time likelihood.
So they score the generated text with a frozen external AR model, Phi-4 14B, pooled over tokens. Distinct-n
complements it, because perplexity can reward repetitive text. [P]

**Q: Does more training help?**
A: A little. Llama 50k vs 25k: average +0.5 points, mixed by task. Validation loss is still falling, so they suggest
other changes instead: larger batches, other denoising targets, adapters in more modules. [P]

**Q: What about the reversal curse? Diffusion is supposed to help.**
A: The paper doesn't test it. LLaDA reported reversal advantages for native diffusion. We tested it as an extension
and found no gain for the conversion. Details are in our report §3.5; the honest summary is in section 5 below. [V]

**Q: Can I try these models?**
A: Yes:
- **BYOD's adapters and demos:** BYOD's adapters are on Hugging Face. There are public demos for all four conversions,
  and the code is at github.com/RuurdKuiper/BYOD.
- **Our adapters:** our own adapters are on Google Drive, linked from our GitHub repository
  (github.com/akode2803/cs787-diffusion-conversion).

**Q: How trustworthy are the cost numbers?**
A: The authors themselves call them illustrative. They come from a standard rental price and energy scenario. Where
GPU-hours weren't reported, they are estimated with 6ND at 40% utilisation. They exclude failed runs, data
preparation, evaluation, and the AR parent's pretraining. [P]

**Q: What's the main weakness of the paper?**
A: It compares each conversion only with its untouched AR parent, after fine-tuning on a new dataset. So the drop
mixes "diffusion" with "this data". That is exactly what our project tested. It also evaluates only 125 examples per
task. [V, P]

## 4. Course concepts that may come up (one-line refreshers)

- **Absorbing vs uniform discrete diffusion:** tokens go to [MASK] and stay there (absorbing), or are swapped for
  random tokens (uniform). Absorbing gives the simple masked cross-entropy.
- **ELBO for masked diffusion:** the 1/t-weighted masked cross-entropy, integrated over t, bounds −log p(x).
- **NFE:** number of network evaluations, i.e. denoising steps. For AR, one per token.
- **LoRA:** W + (α/r)·B·A with B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}. Only A and B are trained, and it can be merged after
  training.
- **KV cache:** AR reuses past keys and values because past tokens never change. Full-sequence diffusion can't,
  because every step changes the masked positions that everything attends to.
- **Low-confidence remasking:** commit the top-k most confident tokens per step and leave the rest masked.

## 5. Our experiments: the short version (one segment of the video)

**Our question:** what does diffusion itself cost, once BYOD's data is held fixed?
- **The control:** an AR LoRA control with the same base, data and order, LoRA rank and targets, learning rate,
  schedule and updates as the conversion.
- **What we compared:** Qwen2.5 7B and Ministral 8B; the original model, the control, our retrain and the released
  conversions; plus LLaDA 8B.
- **Sample size:** up to 500 examples per task, against BYOD's 125.

| Finding | Number | Where |
|---|---|---|
| Code, data held fixed | diffusion −30 to −45 points vs the control (HumanEval, MBPP; both backbones) | report Table 2 |
| Maths is mostly the data | Qwen GSM8K: parent .92 → AR control .50; released conversion .62, our retrain .43 | report §3.1 |
| Speed | 17× slower than the original per answer (batch 16, same GPU) | report §3.3 |
| Fewer steps | released Qwen GSM8K .618 / .368 / .178 / .088 at 256 / 128 / 64 / 32 steps; never beats AR at equal speed | report §3.3 |
| Infilling | BYOD-Qwen beats the control at the true gap length, but .73 → .25 at 1.5× the length; LLaDA .89 → .50 | report §3.4 |
| Reversal | no gain. With the name in the prompt: 0/1000 reverse for both. Name-free: the AR control learned the facts, the conversion did not | report §3.5 |

**If asked "did you replicate BYOD?":**
- We retrained BYOD-Qwen with the paper's recipe. It matches the released adapter on 5 of 7 tasks.
- On GSM8K it is lower (.43 vs .62), and we don't know why.
- We also used the released adapters as conversions.

## 6. Answers to keep honest

- "I don't know; the paper doesn't say" is a fine answer. Examples: why Qwen copies badly; why Gemma converts best,
  which the paper says can't be separated from model size or adapter budget.
- **Keep paper and ours apart.** Speed and infilling are **our** measurements; the paper reports neither.
- **The 125-example caveat:** BYOD's per-task differences under about 9 points are within noise.

## 7. Who handles what tomorrow

- **Aryan (presenter):** the method, the objective and the overall story (§1–2.4, §3 Q1–Q7).
- **Manoj:** results and evaluation: Table 3, the copy test, perplexity, the cost table (§2.5, §2.1).
- **Rajdatta:** related work and course concepts: LLaDA, MDLM, block diffusion, LoRA (§2.2, §4).
- **Anuj:** our experiments and compute: the control, speed, reversal, how we ran it (§5).

Anyone can take any question. This split only decides who speaks first.
