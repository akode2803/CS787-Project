## Steps vs accuracy, batch 16 (256 positions)

| Arm | Task | Steps | Accuracy (95% CI) | s/example | vs 256 steps, paired |
|---|---|---|---|---|---|
| qwen-byod-released | gsm8k | 32 | 0.088 (0.066-0.116) | 0.70 | -0.530 (-0.576 to -0.484), p=4.24e-73, n=500 |
| qwen-byod-released | gsm8k | 64 | 0.178 (0.147-0.214) | 1.40 | -0.440 (-0.488 to -0.390), p=5.48e-52, n=500 |
| qwen-byod-released | gsm8k | 128 | 0.368 (0.327-0.411) | 2.79 | -0.250 (-0.298 to -0.202), p=8.88e-22, n=500 |
| qwen-byod-released | gsm8k | 256 | 0.618 (0.575-0.660) | 5.57 | — |
| qwen-byod-released | humaneval | 64 | 0.000 (0.000-0.023) | 1.93 | -0.268 (-0.335 to -0.201), p=1.14e-13, n=164 |
| qwen-byod-released | humaneval | 128 | 0.091 (0.056-0.145) | 3.87 | -0.177 (-0.244 to -0.116), p=4.18e-07, n=164 |
| qwen-byod-released | humaneval | 256 | 0.268 (0.206-0.341) | 7.71 | — |
| qwen-byod-retrained | gsm8k | 32 | 0.066 (0.047-0.091) | 0.70 | -0.368 (-0.414 to -0.322), p=4.2e-46, n=500 |
| qwen-byod-retrained | gsm8k | 64 | 0.130 (0.103-0.162) | 1.40 | -0.304 (-0.350 to -0.260), p=3.8e-33, n=500 |
| qwen-byod-retrained | gsm8k | 128 | 0.288 (0.250-0.329) | 2.79 | -0.146 (-0.192 to -0.102), p=3.98e-10, n=500 |
| qwen-byod-retrained | gsm8k | 256 | 0.434 (0.391-0.478) | 5.59 | — |
| qwen-byod-retrained | humaneval | 64 | 0.000 (0.000-0.023) | 1.93 | -0.274 (-0.348 to -0.207), p=5.68e-14, n=164 |
| qwen-byod-retrained | humaneval | 128 | 0.104 (0.066-0.160) | 3.86 | -0.171 (-0.250 to -0.098), p=2.54e-05, n=164 |
| qwen-byod-retrained | humaneval | 256 | 0.274 (0.212-0.347) | 7.73 | — |

## Batch-1 latency, GSM8K, first 32 examples

| Arm | Steps | Accuracy | s/example (mean) | median answer tokens |
|---|---|---|---|---|
| qwen-parent | AR | 17/32 | 3.07 | 255.0 |
| qwen-ar-control | AR | 16/32 | 0.89 | 6.5 |
| qwen-byod-released | 32 | 3/32 | 1.08 | 137.0 |
| qwen-byod-released | 64 | 6/32 | 2.15 | 93.0 |
| qwen-byod-released | 128 | 11/32 | 4.30 | 82.0 |
| qwen-byod-released | 256 | 17/32 | 8.59 | 93.5 |
| qwen-byod-retrained | 32 | 1/32 | 1.08 | 89.0 |
| qwen-byod-retrained | 64 | 5/32 | 2.15 | 65.5 |
| qwen-byod-retrained | 128 | 9/32 | 4.30 | 56.5 |
| qwen-byod-retrained | 256 | 14/32 | 8.60 | 62.5 |

## Gap-length sweep, single-line infilling (500 examples; diffusion is told the gap length)

| Arm | x0.5 | x1 (true) | x1.5 | x2 |
|---|---|---|---|---|
| qwen-byod-retrained | 0.026 (0.015-0.044) | 0.664 (0.621-0.704) | 0.132 (0.105-0.164) | 0.146 (0.118-0.180) |
| qwen-byod-released | 0.030 (0.018-0.049) | 0.720 (0.679-0.758) | 0.138 (0.111-0.171) | 0.180 (0.149-0.216) |
| llada | 0.044 (0.029-0.066) | 0.886 (0.855-0.911) | 0.436 (0.393-0.480) | 0.566 (0.522-0.609) |

Paired differences, wrong length minus true length:

- qwen-byod-retrained x0.5: -0.638 (-0.680 to -0.594), p=5.79e-89, n=500
- qwen-byod-retrained x1.5: -0.532 (-0.580 to -0.486), p=1.44e-68, n=500
- qwen-byod-retrained x2: -0.518 (-0.564 to -0.470), p=1.43e-66, n=500
- qwen-byod-released x0.5: -0.690 (-0.730 to -0.648), p=7.01e-98, n=500
- qwen-byod-released x1.5: -0.582 (-0.630 to -0.534), p=1.9e-72, n=500
- qwen-byod-released x2: -0.540 (-0.586 to -0.490), p=1.51e-66, n=500
- llada x0.5: -0.842 (-0.876 to -0.806), p=1.78e-115, n=500
- llada x1.5: -0.450 (-0.500 to -0.398), p=2.11e-50, n=500
- llada x2: -0.320 (-0.368 to -0.272), p=2.82e-34, n=500
