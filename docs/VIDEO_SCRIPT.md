# 3-minute video script: BYOD paper talk (draft 5, 10 Nov)

**Paper:** Kuiper and Bagheri, *BYOD: Build Your Own DLM - Efficient Autoregressive-to-Diffusion Language Model
Conversion*, arXiv 2610.41574.

**Format:** one speaker (Aryan) explains the paper over the slide deck. The deck is "BYOD Paper Talk" on claude.ai, and
it downloads as PDF or PPTX.

**Pace:** about 410 spoken words. A synthetic read at 155 words a minute, numbers spoken in full, took 2:52, about 3:00 with slide changes. The audience knows class-level LMs,
diffusion and LoRA, so the script runs slightly above class depth.

**Balance:** the paper takes 0:00–2:10. Our own experiments take 2:10–2:45, as one segment, and the close follows.

**Markup:** [Slide N] marks when to advance. Numbers marked [P] are from the paper; the rest are ours, verified in
FINDINGS.

---

**1. Why convert? (0:00–0:22)**

[Slide 1: title] Good afternoon. Our paper is BYOD, Build Your Own DLM. It shows how to turn an existing autoregressive chat model into a diffusion language model, cheaply. [Slide 2: AR vs masked diffusion] Autoregressive models write left to right, one token per forward pass, with causal attention. Masked diffusion models like LLaDA start from a fully masked answer and unmask many tokens per step, attending in both directions. [Slide 3: cost] The catch is cost. Pretraining LLaDA from scratch took 130,000 GPU-hours, about 675 thousand dollars by the paper's estimate [P]. BYOD asks: can we convert an existing chat model instead, with LoRA, on one GPU?

**2. The recipe (0:22–1:15)**

[Slide 4: the four changes] The recipe changes four things. One: the causal mask becomes bidirectional in every layer. Two: the base stays frozen, and rank-1024 LoRA adapters go on the query and value projections only, about five percent of the parameters [P]. Three: no next-token shift. Each position predicts its own clean token, and an existing token serves as the mask. [Slide 5: the objective] Four: the loss is LLaDA's absorbing-mask objective. Sample a noise level t, mask each answer token with probability t, and take cross-entropy on the masked tokens, weighted by one over t. The prompt is never masked, and the padding gets weight 0.1, so the model learns where to stop [P]. [Slide 6: training and sampling] Training is 25,000 updates on a mix of chat, reasoning, maths and code: three to four hours on one GPU [P]. Generation starts fully masked. Each step keeps the most confident predictions and remasks the rest.

**3. What the paper finds (1:15–2:10)**

[Slide 7: Table 3] It works on four families: Gemma, Llama, Qwen and Ministral. The best conversion, Gemma, averages 50.6 percent on nine benchmarks, within 1.3 points of LLaDA in the same harness. But every conversion trails its own parent: Qwen falls from 71.6 to 49 [P]. [Slide 8: maths and code] The losses concentrate in maths and code. 28 percent of BYOD-Llama's HumanEval programs don't even parse: local consistency breaks under parallel decoding [P]. [Slide 9: copy test and fluency] A copy test confirms the attention really is bidirectional, but fluency lags: perplexity 8 to 11, against 4 for LLaDA [P]. [Slide 10: quote] In the authors' words: efficient conversion does not yet produce efficient generation.

**4. Our same-data control (2:10–2:45)**

[Slide 11: the control] The paper compares each conversion with its untouched parent, which confounds diffusion with BYOD's data. So we trained an autoregressive control: same base, adapter, data and updates. [Slide 12: four findings] Holding data fixed, diffusion still costs 30 to 45 points on code, but most of Qwen's maths drop is the data itself. It is also 17 times slower per answer. And its infilling edge needs the exact gap length.

**5. Takeaway (2:45–3:00)**

[Slide 13: takeaway] BYOD's real contribution: diffusion research in an afternoon, on one GPU. The benefits still have to be earned, and the authors propose full diffusion fine-tuning from the merged model as the next step.

---

## Check before recording

- **Timing:** read it aloud with a timer. If it runs over 3:00, the first line to cut is the slide-9 sentence.
- **Slides:** each one shows the paper's section, table or equation. Point at the slide when you say [P] numbers.

## Sources: paper numbers (arXiv HTML v1, read 10 Nov)

- **LLaDA's cost:** 2.3T tokens and 130,000 GPU-hours are reported. The $674,830 is the paper's own illustrative
  estimate, not a bill (Table 1, Appendix A).
- **BYOD's training budget:** 3.2 GPU-h for Llama, about $11 (Table 1). It uses at most 102.4M tokens, and one conversion
  takes 3.1–4.0 h on one RTX PRO 6000 Colab GPU (abstract, Table 2).
- **Adapters:** the adapters are 4.1–5.8% of final parameters (abstract). LoRA is rank 1024, alpha 1024, dropout 0, on Q and V only.
  Embeddings, head and norms are frozen (§3.2, Table 2).
- **Same-position prediction and mask tokens:** the label shift is removed. The mask token is an existing string: MASK for Gemma, Llama and Qwen, `<?>` for
  Ministral (§3.2).
- **Objective:** t ~ U[0.001, 1], each answer and padding position is masked independently with probability t, and the loss
  carries a 1/t weight, with answer and padding weighted 0.9 and 0.1. The prompt stays clean (§3.1, Eq. 1–2). It is the absorbing-mask objective
  used by LLaDA (§2).
- **Data:** 1M examples, 45% chat, 18% multiple-choice reasoning, 18% maths, 19% code (§3.3). The run is 25,000 updates at batch 16, which
  is 400,000 examples (Table 7).
- **Sampling:** low-confidence remasking, from a fully masked block (§3.4).
- **Benchmarks (Table 3 averages):** Gemma D .506 / AR .657; Qwen .490 / .716; Ministral .499 / .644; Llama D-25k
  .487 / AR .588; LLaDA .519 in their harness (.545 published). It is the first reported conversion of a Mistral model (abstract).
- **Parse failures:** 28.0% on HumanEval and 8.8% on MBPP for BYOD-Llama-50k, against 0% for the AR model (Appendix E, Table 10). Examples include
  "defdef make_palindrome" and "for for" (Table 11).
- **Copy test:** adding the right-side clue changed the prediction on 100% of items for every model. Exact copy:
  Gemma, Ministral and LLaDA 100%, Llama-25k 90%, Llama-50k 70%, Qwen 20% (§5.4).
- **Perplexity** at 128 tokens and 64 NFE: BYOD 8.3–11.1, LLaDA 4.1, AR parents 2.2–3.0 (abstract, Table 12).
- **The quote** is from §7 (Limitations). It is the only direct quotation on the slides. The paper also says its efficiency claim is about
  training, not measured inference speed (§7). The next step it names is diffusion fine-tuning initialised from the merged
  model (§8).

## Sources: our numbers (FINDINGS.md, report)

- **Code:** "30 to 45 points" is the control minus the conversion on HumanEval and MBPP: Qwen +0.451 and +0.346, Ministral +0.384 and +0.296. Ministral uses the released adapter.
- **Maths:** Qwen GSM8K is 0.92 for the parent and 0.50 for the AR control (both at 512 tokens), against 0.62 for the released conversion and
  0.43 for our retrain. The data alone accounts for more than the whole parent-to-conversion drop.
- **Speed:** "17 times slower" is 5.57 s against 0.33 s per GSM8K example, conversion against the original, at batch 16.
- **Infilling:** released BYOD-Qwen single-line infilling scores 0.73 at the true gap length and 0.25 at 1.5×. The paper has no infilling test.
- **Reversal:** dropped from the video for time. If asked: no reversal gain in our tests, and with name-free prompts the conversion did not
  learn the facts (report §3.5).

## Pronunciation guide

[V] = settled usage. [H] = common usage in talks; no official guide found, so say it confidently either way.

| Word | Say | |
|---|---|---|
| Kuiper | **KY-per** (as in the Kuiper belt; Dutch is closer to "KOW-per") | [H] |
| Bagheri | **bah-GHEH-ree** | [H] |
| LLaDA | **LAH-dah** (like "llama" + "da") | [H] |
| BYOD | **B-Y-O-D**, letter by letter | [H] |
| Qwen | **kwen** (rhymes with "when"). Some say "chwen"; both are heard | [H] |
| Ministral | **min-iss-TRAHL** (mini + Mistral) | [H] |
| Mistral | **miss-TRAHL** | [V] |
| Gemma | **JEM-uh** | [V] |
| LoRA | **LOR-uh** | [V] |
| HumanEval | **Human Eval** | [V] |
| autoregressive | **aw-toh-ri-GRESS-iv** | [V] |
| bidirectional | **bye-di-REK-shun-ul** | [V] |
| perplexity | **per-PLEK-si-tee** | [V] |
| cross-entropy | **cross EN-truh-pee** | [V] |
| absorbing-mask | **ub-ZOR-bing mask** | [V] |
| confounds | **kon-FOUNDZ** | [V] |
| infilling | **IN-fill-ing** | [V] |
| "def" | **deaf** (the Python keyword; no longer spoken in draft 5) | [V] |

Numbers to say as written in the script: "130,000 GPU-hours", "675 thousand dollars", "25,000 updates", "50.6 percent",
"1.3 points", "71.6 to 49", "17 times".

A synthetic reference read (macOS voice, 155 wpm) is at `docs/slides/narration_reference.m4a`. It is for timing. Its
accent and stress are a machine's, so trust this table over it where they differ.
