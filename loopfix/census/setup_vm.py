"""One-time VM setup: a clean venv, so vLLM cannot clash with Colab's preinstalled packages."""
import subprocess

cmd = r"""
set -e
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
python3 --version
pip install -q uv
uv venv --python 3.12 /content/venv
uv pip install -q --python /content/venv/bin/python vllm math-verify datasets
/content/venv/bin/python -c "import vllm, torch, transformers; print('vllm', vllm.__version__, 'torch', torch.__version__, 'cuda', torch.version.cuda, 'tf', transformers.__version__, 'gpu', torch.cuda.get_device_name(0))"
"""
r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
print(r.stdout[-2500:])
print("STDERR:", r.stderr[-1500:])
print("EXIT", r.returncode)
