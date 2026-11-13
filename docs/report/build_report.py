"""Builds report.html (tables filled from ../results/summary.json) and prints report.pdf with headless Chrome.

  python3 build_report.py            # after figs.py
Prose numbers were checked against summary.json by hand; table numbers are inserted by this script.
"""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE.parent / "results" / "summary.json"))
C, P, F, R = S["cells"], S["pairs"], S["gap_fence_cut"], S["reversal"]
TEXT = (HERE / "report_body.html").read_text()


def a(key, d=3):
    return f"{C[key]['acc']:.{d}f}"


def ci(key):
    c = C[key]; return f'{c["acc"]:.3f} <span class="ci">{c["lo"]:.2f}–{c["hi"]:.2f}</span>'


TASKS = [("gsm8k", "GSM8K"), ("mmlu", "MMLU"), ("arc_c", "ARC-C"), ("humaneval", "HumanEval"), ("mbpp", "MBPP"),
         ("he_single_strict", "Infilling, single-line*"), ("he_multi_strict", "Infilling, multi-line*")]
LONG = {"gsm8k", "humaneval"}


def main_table(cols):
    head = "".join(f"<th>{h}</th>" for _, h, _ in cols)
    rows = []
    for t, name in TASKS:
        cells = []
        for arm, _, ar in cols:
            if ar and t in LONG:
                cells.append(f'<td>{ci(f"{arm}/{t}_t512")}<br><span class="sub">256 tok: {a(f"{arm}/{t}")}</span></td>')
            else:
                cells.append(f"<td>{ci(f'{arm}/{t}')}</td>")
        rows.append(f"<tr><th>{name}</th>{''.join(cells)}</tr>")
    return f'<table class="num"><tr><th>Task</th>{head}</tr>{"".join(rows)}</table>'


qwen = main_table([("qwen-parent", "Original", True), ("qwen-ar-control", "AR control", True),
                   ("qwen-byod-retrained", "Conversion (ours)", False), ("qwen-byod-released", "Conversion (released)", False)])
mini = main_table([("ministral-parent", "Original", True), ("ministral-ar-control", "AR control", True),
                   ("ministral-byod-released", "Conversion (released)", False), ("llada", "LLaDA 8B", False)])


def diff_table():
    pairs = [("qwen-ar-control|qwen-byod-retrained", "Qwen: control − our conversion"),
             ("qwen-ar-control|qwen-byod-released", "Qwen: control − released conversion"),
             ("ministral-ar-control|ministral-byod-released", "Ministral: control − released conversion")]
    head = "".join(f"<th>{n}</th>" for _, n in pairs)
    rows = []
    for t, name in TASKS:
        cells = []
        for k, _ in pairs:
            d = P[f"{k}|{t}"]
            sig = "" if d["lo"] <= 0 <= d["hi"] else ' class="sig"'
            cells.append(f'<td{sig}>{d["diff"]:+.3f} <span class="ci">{d["lo"]:+.2f} to {d["hi"]:+.2f}</span></td>')
        rows.append(f"<tr><th>{name}</th>{''.join(cells)}</tr>")
    return f'<table class="num"><tr><th>Task (256 tokens for all)</th>{head}</tr>{"".join(rows)}</table>'


def steps_table():
    rows = []
    for arm, name in (("qwen-byod-released", "Released"), ("qwen-byod-retrained", "Ours")):
        for s in (32, 64, 128, 256):
            g = C[f"{arm}/gsm8k" if s == 256 else f"{arm}/gsm8k_s{s}"]
            h = C[f"{arm}/humaneval" if s == 256 else f"{arm}/humaneval_s{s}"] if s != 32 else None
            b = C[f"{arm}/gsm8k_s{s}_b1_n32"]
            rows.append(f"<tr><th>{name}, {s} steps</th><td>{g['acc']:.3f}</td><td>{g['s_per_example']:.2f}</td>"
                        f"<td>{'—' if h is None else format(h['acc'], '.3f')}</td><td>{b['k']}/32</td><td>{b['s_per_example']:.2f}</td></tr>")
    for arm, name in (("qwen-parent", "Original AR"), ("qwen-ar-control", "AR control")):
        g, b = C[f"{arm}/gsm8k"], C[f"{arm}/gsm8k_b1_n32"]
        rows.append(f"<tr class='ar'><th>{name}</th><td>{g['acc']:.3f}</td><td>{g['s_per_example']:.2f}</td>"
                    f"<td>{a(f'{arm}/humaneval')}</td><td>{b['k']}/32</td><td>{b['s_per_example']:.2f}</td></tr>")
    return ('<table class="num"><tr><th>Qwen arm</th><th>GSM8K acc.<br>batch 16</th><th>s / question<br>batch 16</th>'
            '<th>HumanEval<br>batch 16</th><th>GSM8K<br>batch 1</th><th>s / question<br>batch 1</th></tr>' + "".join(rows) + "</table>")


def gap_table():
    rows = []
    for arm, name in (("qwen-byod-retrained", "Qwen conversion (ours)"), ("qwen-byod-released", "Qwen conversion (released)"),
                      ("llada", "LLaDA 8B")):
        raw = [C[f"{arm}/he_single" if g == "true" else f"{arm}/he_single_gap{g}"]["acc"] for g in ("x0.5", "true", "x1.5", "x2")]
        cut = [F[f"{arm}/{g}"]["acc"] for g in ("x0.5", "true", "x1.5", "x2")]
        rows.append(f"<tr><th>{name}</th>" + "".join(f"<td>{c:.3f} <span class='ci'>raw {r:.3f}</span></td>" for r, c in zip(raw, cut)) + "</tr>")
    return ('<table class="num"><tr><th>Diffusion arm</th><th>0.5× length</th><th>true length</th><th>1.5× length</th><th>2× length</th></tr>'
            + "".join(rows) + "</table>")


def rev_table():
    rows = []
    for suffix, label in (("", "Before training"), ("+facts", "2,000 updates, name in prompt"),
                          ("+facts10k", "10,000 updates, name in prompt"), ("+factsnf10k", "10,000 updates, name-free prompts")):
        cells = []
        for arm in ("qwen-ar-control", "qwen-byod-retrained"):
            f, r = R[f"{arm}{suffix}/rev_forward"], R[f"{arm}{suffix}/rev_reverse"]
            cells.append(f"<td>{f['k']}/{f['n']}</td><td>{r['k']}/{r['n']}</td>")
        rows.append(f"<tr><th>{label}</th>{''.join(cells)}</tr>")
    return ('<table class="num"><tr><th rowspan="2">Qwen, training</th><th colspan="2">AR control</th>'
            '<th colspan="2">Conversion (ours)</th></tr><tr><th>forward</th><th>reverse</th><th>forward</th><th>reverse</th></tr>'
            + "".join(rows) + "</table>")


def decode_table():
    rows = []
    for arm, name in (("qwen-byod-retrained", "Qwen conversion (ours)"), ("qwen-byod-released", "Qwen conversion (released)"),
                      ("ministral-byod-released", "Ministral conversion (released)"), ("llada", "LLaDA 8B")):
        cells = "".join(f"<td>{C[f'{arm}/{t}']['kendall_tau']:.2f}</td>" for t in ("gsm8k", "humaneval", "mmlu", "he_single", "he_multi"))
        rows.append(f"<tr><th>{name}</th>{cells}<td>{C[f'{arm}/gsm8k']['doubled_per_100']:.2f}</td></tr>")
    for arm, name in (("qwen-parent", "Qwen original (AR)"), ("qwen-ar-control", "Qwen AR control")):
        rows.append(f"<tr class='ar'><th>{name}</th><td colspan='5' class='na'>left to right by construction (τ = 1)</td><td>{C[f'{arm}/gsm8k']['doubled_per_100']:.2f}</td></tr>")
    return ('<table class="num"><tr><th rowspan="2">Arm</th><th colspan="5">Median Kendall τ, commit order vs position</th>'
            '<th rowspan="2">Doubled words<br>per 100, GSM8K</th></tr><tr><th>GSM8K</th><th>HumanEval</th><th>MMLU</th>'
            '<th>Infill single</th><th>Infill multi</th></tr>' + "".join(rows) + "</table>")


html = (TEXT.replace("{{QWEN_TABLE}}", qwen).replace("{{MINI_TABLE}}", mini).replace("{{DIFF_TABLE}}", diff_table())
        .replace("{{STEPS_TABLE}}", steps_table()).replace("{{GAP_TABLE}}", gap_table()).replace("{{REV_TABLE}}", rev_table())
        .replace("{{DECODE_TABLE}}", decode_table()))
assert "{{" not in html, "unfilled placeholder"
(HERE / "report.html").write_text(html)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--generate-pdf-document-outline", "--allow-file-access-from-files",
                f"--print-to-pdf={HERE / 'report.pdf'}", (HERE / "report.html").as_uri()], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
print("wrote report.html and report.pdf")
