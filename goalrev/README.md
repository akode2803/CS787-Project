# goalrev — small goal-revision experiment (order-desk environment)

Setup (no Docker, no root): `python3 -m venv .venv && source .venv/bin/activate && pip install google-genai`
Copy `.env.example` to `.env` (git-ignored) and fill in `GEMINI_API_KEYS` (comma-separated, one per Google account) and `GEMINI_MODEL`
(a model that appears in your AI Studio). Never commit or paste keys.

    python -m unittest goalrev.tests.test_core          # no key needed
    python -m goalrev.run stageA --name pilot --n 3     # agent does q0 alone -> fixed prefixes
    python -m goalrev.run stageB --name pilot --n 3 --strategies B1,B2,B3a,B3b,M1
    python -m goalrev.run report --name pilot

Runs resume automatically (finished task/strategy pairs are skipped). Strategies: see goalrev/strategies.py.
