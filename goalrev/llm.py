"""LLM wrappers. Every call goes through generate(prompt, system, tag) so tokens/calls are metered per episode and per component."""
import os, time, random, itertools


class Meter:
    def __init__(self):
        self.calls = 0; self.tin = 0; self.tout = 0; self.by_tag = {}

    def add(self, tag, tin, tout):
        self.calls += 1; self.tin += tin; self.tout += tout
        d = self.by_tag.setdefault(tag, {"calls": 0, "tin": 0, "tout": 0})
        d["calls"] += 1; d["tin"] += tin; d["tout"] += tout

    def snapshot(self):
        return {"calls": self.calls, "tokens_in": self.tin, "tokens_out": self.tout, "by_tag": self.by_tag}


class LLM:
    def __init__(self):
        self.meter = Meter()

    def new_episode(self):
        self.meter = Meter()

    def generate(self, prompt, system="", tag="agent"):
        raise NotImplementedError


class ScriptedLLM(LLM):
    """For tests: `script` is a list of replies or a callable(prompt, system, tag) -> reply."""
    def __init__(self, script):
        super().__init__(); self.script = script; self.prompts = []

    def generate(self, prompt, system="", tag="agent"):
        self.prompts.append((tag, prompt))
        reply = self.script(prompt, system, tag) if callable(self.script) else self.script.pop(0)
        self.meter.add(tag, len(prompt) // 4, len(reply) // 4)
        return reply


class GeminiLLM(LLM):
    """Google AI Studio via the google-genai package. Keys: GEMINI_API_KEYS (comma-separated; rotated on rate limits).
    Model: GEMINI_MODEL (no default on purpose: choose a model that shows up in your AI Studio)."""
    def __init__(self, model=None, keys=None, temperature=0.0, max_retries=8):
        super().__init__()
        from google import genai
        from google.genai import types
        self._genai, self._types = genai, types
        self.model = model or os.environ.get("GEMINI_MODEL")
        if not self.model:
            raise SystemExit("Set GEMINI_MODEL (e.g. in .env) to a model available in your AI Studio.")
        keys = keys or [k.strip() for k in os.environ.get("GEMINI_API_KEYS", "").split(",") if k.strip()]
        if not keys:
            raise SystemExit("Set GEMINI_API_KEYS in .env (comma-separated).")
        self.clients = [genai.Client(api_key=k, http_options=types.HttpOptions(timeout=int(float(os.environ.get('GEMINI_TIMEOUT_S', 60)) * 1000))) for k in keys]
        self._rot = itertools.cycle(range(len(self.clients)))
        for _ in range(random.randrange(len(self.clients))): next(self._rot)   # workers start on different keys
        self.temperature, self.max_retries = temperature, max_retries

    def generate(self, prompt, system="", tag="agent"):
        cfg = self._types.GenerateContentConfig(system_instruction=system or None, temperature=self.temperature)
        last = None
        for attempt in range(self.max_retries):
            client = self.clients[next(self._rot)]
            try:
                r = client.models.generate_content(model=self.model, contents=prompt, config=cfg)
                um = getattr(r, "usage_metadata", None)
                self.meter.add(tag, getattr(um, "prompt_token_count", 0) or 0, getattr(um, "candidates_token_count", 0) or 0)
                return r.text or ""
            except Exception as e:   # rate limits / transient errors: back off and rotate key
                last = e; time.sleep(min(60, 2 ** attempt))
        raise RuntimeError(f"LLM call failed after {self.max_retries} attempts: {last}")


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"'))


class OllamaLLM(LLM):
    """Local model through the Ollama server (http://localhost:11434). Select with GEMINI_MODEL=ollama:<model>, e.g. ollama:qwen2.5:3b-instruct."""
    def __init__(self, model, host=None, temperature=0.0, num_ctx=4096, timeout=600):
        super().__init__()
        self.model, self.temperature, self.num_ctx, self.timeout = model, temperature, num_ctx, timeout
        self.url = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/") + "/api/chat"

    def generate(self, prompt, system="", tag="agent"):
        import json, urllib.request
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = json.dumps({"model": self.model, "messages": msgs, "stream": False, "keep_alive": "30m",
                           "options": {"temperature": self.temperature, "num_ctx": self.num_ctx}}).encode()
        req = urllib.request.Request(self.url, body, {"Content-Type": "application/json"})
        last = None
        for attempt in range(4):                           # the 8 GB Mac sometimes answers 500 under memory pressure
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r: d = json.load(r)
                break
            except Exception as e:
                last = e; time.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError(f"Ollama call failed after 4 attempts: {last}")
        self.meter.add(tag, d.get("prompt_eval_count", 0), d.get("eval_count", 0))
        return d["message"]["content"]


def make_llm():
    m = os.environ.get("GEMINI_MODEL", "")
    return OllamaLLM(m[len("ollama:"):]) if m.startswith("ollama:") else GeminiLLM()
