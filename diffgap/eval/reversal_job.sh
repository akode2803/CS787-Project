#!/bin/bash
# Reversal test on the VM, Qwen pair. Teaches 1,000 invented facts in one direction to the AR control and to the
# retrained conversion, with each arm's own objective and identical data, updates and learning rate, then tests both
# directions. Untrained arms are scored first: they should know none of the facts.
# Needs: BYOD installed, /content/adapters/qwen-ar and /content/adapters/qwen-byod-retrained fetched.
set -e
cd /content
UPDATES=${UPDATES:-2000}     # 8 passes over 4,000 phrasings at batch 16
LR=${LR:-5.0e-5}
python3 reversal_data.py /content/reversal_data --facts 1000 --epochs 8
cat > /content/reversal_override.yaml <<EOF
dataset_name: /content/reversal_data/train_data
dataset_revision: null
prepared_dataset_name: null
learning_rate: $LR
warmup_steps: 50
validation_steps: 250
generation_perplexity: {enabled: false}
EOF
OUT=/content/eval_out
python3 run_eval.py --arm ar:qwen:/content/adapters/qwen-ar --name qwen-ar-control --tasks rev_forward,rev_reverse --out $OUT
python3 run_eval.py --arm byod:qwen:/content/adapters/qwen-byod-retrained --name qwen-byod-retrained --tasks rev_forward,rev_reverse --out $OUT
[ -f /content/rev_ar/best/adapter_config.json ] || python3 ar_control.py --model qwen --output-dir /content/rev_ar \
  --override /content/reversal_override.yaml --init-adapter /content/adapters/qwen-ar --max-updates $UPDATES --checkpoint-steps $UPDATES
python3 run_eval.py --arm ar:qwen:/content/rev_ar/best --name qwen-ar-control+facts --tasks rev_forward,rev_reverse --out $OUT
[ -f /content/rev_byod/best/adapter_config.json ] || python3 retrain.py --model qwen --output-dir /content/rev_byod --persist-dir /content/persist/rev_byod \
  --override /content/reversal_override.yaml --init-adapter /content/adapters/qwen-byod-retrained --max-updates $UPDATES --checkpoint-steps $UPDATES
python3 run_eval.py --arm byod:qwen:/content/rev_byod/best --name qwen-byod-retrained+facts --tasks rev_forward,rev_reverse --out $OUT
R=cs787drive:CS787-Diffusion/eval/reversal
# Uploads are capped and may fail without stopping the job: on 8 Nov a Drive rate limit (403, rclone's shared
# client_id) made one adapter upload retry for 70 min while the G4 idled, which used up the account's last CU.
# Small files go first, so they are on Drive even if a big adapter fails.
up() { timeout 600 rclone copy "$@" --retries 2 --low-level-retries 3 --log-level ERROR || echo "UPLOAD FAILED: $1"; }
for d in rev_ar rev_byod; do up /content/$d $R/training/$d --include 'metrics.jsonl' --include '*.json'; done
up /content/reversal_data $R/data
for d in rev_ar rev_byod; do up /content/$d/best $R/adapters/$d; done
echo REVERSAL DONE
