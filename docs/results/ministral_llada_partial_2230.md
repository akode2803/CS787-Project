| Arm | Task | n | Accuracy | 95% CI | Answer tokens (median) | s/example | Doubled words /100 | Kendall tau (median) |
|---|---|---|---|---|---|---|---|---|
| llada | arc_c | 500 | 0.878 | 0.846-0.904 | 9 | 0.72 | 0.21 | 0.67 |
| llada | gsm8k | 500 | 0.588 | 0.544-0.630 | 255 | 7.14 | 0.70 | 0.30 |
| llada | he_multi | 464 | 0.491 | 0.446-0.537 | 36 | 5.92 | 2.11 | 0.43 |
| llada | he_multi_strict | 464 | 0.491 | 0.446-0.537 | 36 | 5.92 | 2.11 | 0.43 |
| llada | he_single | 500 | 0.886 | 0.855-0.911 | 8 | 1.20 | 1.20 | 0.64 |
| llada | he_single_strict | 500 | 0.886 | 0.855-0.911 | 8 | 1.20 | 1.20 | 0.64 |
| llada | humaneval | 164 | 0.341 | 0.273-0.417 | 255 | 10.85 | 1.93 | 0.89 |
| llada | mbpp | 257 | 0.486 | 0.426-0.547 | 173 | 10.70 | 1.67 | 0.92 |
| llada | mmlu | 500 | 0.604 | 0.560-0.646 | 10 | 1.02 | 0.75 | 0.67 |
| ministral-ar-control | arc_c | 500 | 0.830 | 0.795-0.860 | 8 | 0.03 | 0.22 | — |
| ministral-ar-control | gsm8k | 500 | 0.838 | 0.803-0.868 | 104 | 0.41 | 1.01 | — |
| ministral-ar-control | he_multi (code around gap changed in 223) | 500 | 0.540 | 0.496-0.583 | 226 | 0.73 | 2.56 | — |
| ministral-ar-control | he_multi_strict (code around gap changed in 223) | 500 | 0.400 | 0.358-0.444 | 226 | 0.73 | 2.56 | — |
| ministral-ar-control | he_single (code around gap changed in 113) | 500 | 0.808 | 0.771-0.840 | 211 | 0.56 | 1.84 | — |
| ministral-ar-control | he_single_strict (code around gap changed in 113) | 500 | 0.696 | 0.654-0.735 | 211 | 0.56 | 1.84 | — |
| ministral-ar-control | humaneval | 164 | 0.665 | 0.589-0.732 | 136 | 0.44 | 2.00 | — |
| ministral-ar-control | mbpp | 257 | 0.708 | 0.650-0.760 | 33 | 0.23 | 3.15 | — |
| ministral-ar-control | mmlu | 500 | 0.646 | 0.603-0.687 | 8 | 0.05 | 1.54 | — |
| ministral-byod-released | arc_c | 500 | 0.840 | 0.805-0.870 | 8 | 0.72 | 0.23 | 0.78 |
| ministral-byod-released | gsm8k | 500 | 0.646 | 0.603-0.687 | 91 | 6.43 | 1.32 | 0.93 |
| ministral-byod-released | he_multi | 224 | 0.308 | 0.251-0.371 | 30 | 2.48 | 2.07 | 0.73 |
| ministral-byod-released | he_multi_strict | 224 | 0.308 | 0.251-0.371 | 30 | 2.48 | 2.07 | 0.73 |
| ministral-byod-released | he_single | 500 | 0.726 | 0.685-0.763 | 7 | 0.90 | 1.30 | 0.67 |
| ministral-byod-released | he_single_strict | 500 | 0.726 | 0.685-0.763 | 7 | 0.90 | 1.30 | 0.67 |
| ministral-byod-released | humaneval | 164 | 0.280 | 0.217-0.354 | 66 | 9.20 | 1.90 | 0.93 |
| ministral-byod-released | mbpp | 257 | 0.412 | 0.354-0.473 | 28 | 9.19 | 3.14 | 0.87 |
| ministral-byod-released | mmlu | 500 | 0.634 | 0.591-0.675 | 8 | 0.96 | 1.37 | 0.71 |
| ministral-parent | arc_c | 500 | 0.716 | 0.675-0.754 | 8 | 0.02 | 0.47 | — |
| ministral-parent | gsm8k | 500 | 0.710 | 0.669-0.748 | 209 | 0.40 | 0.93 | — |
| ministral-parent | he_multi (code around gap changed in 248) | 500 | 0.632 | 0.589-0.673 | 246 | 0.65 | 2.55 | — |
| ministral-parent | he_multi_strict (code around gap changed in 248) | 500 | 0.388 | 0.346-0.431 | 246 | 0.65 | 2.55 | — |
| ministral-parent | he_single (code around gap changed in 156) | 500 | 0.834 | 0.799-0.864 | 216 | 0.51 | 1.64 | — |
| ministral-parent | he_single_strict (code around gap changed in 156) | 500 | 0.634 | 0.591-0.675 | 216 | 0.51 | 1.64 | — |
| ministral-parent | humaneval | 164 | 0.659 | 0.583-0.727 | 170 | 0.44 | 2.12 | — |
| ministral-parent | mbpp | 257 | 0.677 | 0.618-0.731 | 33 | 0.31 | 2.50 | — |
| ministral-parent | mmlu | 500 | 0.566 | 0.522-0.609 | 8 | 0.04 | 1.69 | — |

**ministral-ar-control minus ministral-byod-released**, paired on shared examples

| Task | n | Difference | 95% CI | McNemar p |
|---|---|---|---|---|
| arc_c | 500 | -0.010 | -0.042 to +0.022 | 0.625 |
| gsm8k | 500 | +0.192 | +0.150 to +0.238 | 2.63e-16 |
| he_multi | 224 | +0.402 | +0.326 to +0.478 | 6.01e-19 |
| he_multi_strict | 224 | +0.241 | +0.161 to +0.321 | 3.9e-08 |
| he_single | 500 | +0.082 | +0.036 to +0.128 | 0.000699 |
| he_single_strict | 500 | -0.030 | -0.080 to +0.022 | 0.279 |
| humaneval | 164 | +0.384 | +0.299 to +0.463 | 8.74e-16 |
| mbpp | 257 | +0.296 | +0.233 to +0.358 | 4.14e-17 |
| mmlu | 500 | +0.012 | -0.028 to +0.052 | 0.624 |

**ministral-parent minus ministral-ar-control**, paired on shared examples

| Task | n | Difference | 95% CI | McNemar p |
|---|---|---|---|---|
| arc_c | 500 | -0.114 | -0.152 to -0.076 | 1.46e-08 |
| gsm8k | 500 | -0.128 | -0.170 to -0.088 | 1.89e-09 |
| he_multi | 500 | +0.092 | +0.060 to +0.124 | 2.25e-08 |
| he_multi_strict | 500 | -0.012 | -0.046 to +0.022 | 0.567 |
| he_single | 500 | +0.026 | +0.004 to +0.050 | 0.041 |
| he_single_strict | 500 | -0.062 | -0.098 to -0.028 | 0.000878 |
| humaneval | 164 | -0.006 | -0.067 to +0.055 | 1 |
| mbpp | 257 | -0.031 | -0.070 to +0.008 | 0.169 |
| mmlu | 500 | -0.080 | -0.118 to -0.042 | 4.5e-05 |

**ministral-parent minus ministral-byod-released**, paired on shared examples

| Task | n | Difference | 95% CI | McNemar p |
|---|---|---|---|---|
| arc_c | 500 | -0.124 | -0.164 to -0.084 | 6.44e-09 |
| gsm8k | 500 | +0.064 | +0.020 to +0.110 | 0.00762 |
| he_multi | 224 | +0.487 | +0.415 to +0.558 | 1.42e-26 |
| he_multi_strict | 224 | +0.214 | +0.129 to +0.299 | 1.67e-06 |
| he_single | 500 | +0.108 | +0.064 to +0.154 | 7.95e-06 |
| he_single_strict | 500 | -0.092 | -0.144 to -0.038 | 0.00118 |
| humaneval | 164 | +0.378 | +0.293 to +0.457 | 6.39e-15 |
| mbpp | 257 | +0.265 | +0.202 to +0.323 | 1.73e-15 |
| mmlu | 500 | -0.068 | -0.112 to -0.024 | 0.00337 |
