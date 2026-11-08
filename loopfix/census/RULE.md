# Loop census: rule fixed before any data (7 Nov 2026)

Purpose: decide between the loop-fix topic and the diffusion topic before submission.

## Setup
- 100 practice problems: 50 GSM8K train, 50 MATH train (levels 3-5), fixed seed 787. No test-set problems, so test sets stay unused for the main study.
- One sample per problem per setting. Thinking mode on where the model has a switch.
- Token cap 16,384.
- Prompt: problem + "Please reason step by step, and put your final answer within \boxed{}."
- Setting P: temperature 0.6, top_p 0.95, top_k 20, presence penalty 1.5 (the Sparks scoring settings).
- Setting N: the same with presence penalty 0.
- Primary models, in order: Qwen3.5-0.8B (reference), Qwen3.5-2B, Qwen3.5-4B, DeepSeek-R1-Distill-Qwen-1.5B, OpenThinker3-1.5B, LFM2.5-1.2B-Thinking, SmolLM3-3B, Phi-4-mini-reasoning.
- Extra models if time allows, same rule: Qwen3-1.7B, Qwen3-0.6B, DeepScaleR-1.5B-Preview, OpenReasoning-Nemotron-1.5B.

## Definitions
- Loop rate: share of answers that hit the 16,384-token cap. Primary measure, because reported loops can be paraphrases with no exact repetition, and 16k tokens is far beyond what these problems need.
- Repetition rate (secondary): hit the cap and the last 256 tokens have at least 30% repeated 8-grams.
- Finished accuracy: correct share among answers that did not hit the cap. Graded with math-verify on the last \boxed{}.

## Qualifying model
Loop rate of at least 20% under setting P or N, and finished accuracy of at least 50% in that same setting. The second condition means there is ability behind the loops to unlock.

## Decision
- PASS: at least two models other than Qwen3.5-0.8B qualify. Submit loop-fix.
- WEAK PASS, flagged as such: all qualifying models are in the Qwen3.5 family. Still loop-fix under the stated rule, but the transfer claim is narrower, and the user decides.
- FAIL: fewer than two qualify. Submit diffusion.

## Limits
One sample on 100 problems gives about +/-8 points at a 20% rate. This census is a go/no-go screen, not a result for the report. A model that fails to load counts as not qualifying and is listed as a failure, not silently dropped.
