"""Report figures, drawn only from docs/results/summary.json.  python3 figs.py  ->  fig/*.png

Colours: one fixed hue per arm across every figure (validated default palette, slots 1-5 in order, so adjacent
bars always pass the colour-blind checks). Text is ink, never the series colour.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE.parent / "results" / "summary.json"))
C, FENCE = S["cells"], S["gap_fence_cut"]
OUT = HERE / "fig"; OUT.mkdir(exist_ok=True)

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#d9d8d0", "#fcfcfb"
ARM = {  # role -> (label, colour); same colour for the same role on both backbones
    "parent": ("Original AR model", "#2a78d6"),
    "control": ("AR control (same data)", "#eb6834"),
    "retrained": ("Conversion, our retrain", "#1baf7a"),
    "released": ("Conversion, released", "#eda100"),
    "llada": ("LLaDA 8B (native diffusion)", "#e87ba4"),
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 10,
                     "axes.titleweight": "bold", "figure.facecolor": "white", "axes.facecolor": "white",
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})


def acc(key):
    return C[key]["acc"]


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.6); ax.set_axisbelow(True)


# ------------------------------------------------------------------ figure 1: main results, two backbones
TASKS = [("gsm8k", "GSM8K"), ("mmlu", "MMLU"), ("arc_c", "ARC-C"), ("humaneval", "HumanEval"), ("mbpp", "MBPP"),
         ("he_single_strict", "Infill\nsingle-line"), ("he_multi_strict", "Infill\nmulti-line")]
LONG = {"gsm8k", "humaneval"}   # AR arms scored at 512 tokens on these: their answers were cut at 256


def stem(role, task):
    return f"{task}_t512" if role in ("parent", "control") and task in LONG else task


panels = [("Qwen2.5 7B", [("parent", "qwen-parent"), ("control", "qwen-ar-control"), ("retrained", "qwen-byod-retrained"),
                          ("released", "qwen-byod-released")]),
          ("Ministral 8B (LLaDA 8B for reference)", [("parent", "ministral-parent"), ("control", "ministral-ar-control"),
                          ("released", "ministral-byod-released"), ("llada", "llada")])]
fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.8), sharex=True)
for ax, (title, arms) in zip(axes, panels):
    width = 0.8 / len(arms)
    for j, (role, arm) in enumerate(arms):
        xs = [i + (j - (len(arms) - 1) / 2) * width for i in range(len(TASKS))]
        cells = [C[f"{arm}/{stem(role, t)}"] for t, _ in TASKS]
        ax.bar(xs, [c["acc"] for c in cells], width * 0.86, color=ARM[role][1], label=ARM[role][0], zorder=2)
        ax.errorbar(xs, [c["acc"] for c in cells], yerr=[[c["acc"] - c["lo"] for c in cells], [c["hi"] - c["acc"] for c in cells]],
                    fmt="none", ecolor=INK2, elinewidth=0.6, capsize=0, zorder=3)
    ax.set_ylim(0, 1); ax.set_ylabel("Accuracy"); ax.set_title(title, loc="left", pad=20); grid(ax)
    ax.legend(ncol=4, fontsize=7.5, loc="lower left", bbox_to_anchor=(0, 1.0), handlelength=1, columnspacing=1,
              borderaxespad=0.2)
axes[1].set_xticks(range(len(TASKS))); axes[1].set_xticklabels([t[1] for t in TASKS])
fig.tight_layout(); fig.savefig(OUT / "main.png", dpi=220); plt.close(fig)

# ------------------------------------------------------------------ figure 2: steps vs accuracy and time
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0))
for role, arm in (("retrained", "qwen-byod-retrained"), ("released", "qwen-byod-released")):
    pts = [C[f"{arm}/gsm8k_s{s}"] for s in (32, 64, 128)] + [C[f"{arm}/gsm8k"]]
    a.plot([p["s_per_example"] for p in pts], [p["acc"] for p in pts], "-o", color=ARM[role][1], lw=2, ms=5, label=ARM[role][0], zorder=3)
    if role == "released":
        for p, s in zip(pts, (32, 64, 128, 256)):
            a.annotate(f"{s} steps", (p["s_per_example"], p["acc"]), textcoords="offset points", xytext=(-14, 7), fontsize=6.5, color=INK2)
    q = [C[f"{arm}/gsm8k_s{s}_b1_n32"] for s in (32, 64, 128, 256)]
    b.plot([p["s_per_example"] for p in q], [p["acc"] for p in q], "-o", color=ARM[role][1], lw=2, ms=5, label=ARM[role][0], zorder=3)
for role, arm in (("parent", "qwen-parent"), ("control", "qwen-ar-control")):
    p = C[f"{arm}/gsm8k"]
    a.plot([p["s_per_example"]], [p["acc"]], "D", color=ARM[role][1], ms=7, label=ARM[role][0] + " (256 tokens)", zorder=4)
    q = C[f"{arm}/gsm8k_b1_n32"]
    b.plot([q["s_per_example"]], [q["acc"]], "D", color=ARM[role][1], ms=7, label=ARM[role][0], zorder=4)
a.set_title("Batch 16, 500 questions", loc="left"); b.set_title("Batch 1, first 32 questions", loc="left")
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
for ax in (a, b):
    ax.set_xscale("log"); ax.set_xlabel("Seconds per question (log scale)"); ax.set_ylim(0, 0.75); grid(ax, "both")
    ax.xaxis.set_major_locator(FixedLocator([0.25, 0.5, 1, 2, 4, 8])); ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
a.set_xlim(0.2, 9); b.set_xlim(0.7, 11)
a.set_ylabel("GSM8K accuracy")
handles, labels = a.get_legend_handles_labels()
labels = [l.replace(" (256 tokens)", "") for l in labels]
fig.legend(handles, labels, ncol=4, fontsize=7, loc="lower center", handlelength=1.5, columnspacing=1.2)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(OUT / "steps.png", dpi=220); plt.close(fig)

# ------------------------------------------------------------------ figure 3: gap-length sweep
fig, ax = plt.subplots(figsize=(7.0, 3.1))
xs = [0.5, 1.0, 1.5, 2.0]
for role, arm in (("retrained", "qwen-byod-retrained"), ("released", "qwen-byod-released"), ("llada", "llada")):
    ys = [FENCE[f"{arm}/{g}"]["acc"] for g in ("x0.5", "true", "x1.5", "x2")]
    ax.plot(xs, ys, "-o", color=ARM[role][1], lw=2, ms=5, label=ARM[role][0], zorder=3)
for role, arm, dash in (("parent", "qwen-parent", (0, (4, 3))), ("control", "qwen-ar-control", (0, (1.5, 2)))):
    y = acc(f"{arm}/he_single_strict")
    ax.axhline(y, color=ARM[role][1], lw=1.4, ls=dash, zorder=2, label=f"{ARM[role][0]}, Qwen (needs no length)")
ax.set_xticks(xs); ax.set_xticklabels(["0.5x", "true", "1.5x", "2x"]); ax.set_xlim(0.4, 2.0)
ax.set_xlabel("Gap length given to the diffusion model"); ax.set_ylabel("Single-line infilling accuracy")
ax.set_ylim(0, 1); grid(ax)
ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0), handlelength=2.2)
fig.tight_layout(); fig.savefig(OUT / "gap.png", dpi=220); plt.close(fig)

# ------------------------------------------------------------------ figure 4: where the GSM8K drop comes from
fig, ax = plt.subplots(figsize=(4.6, 2.6))
rows = [("Qwen2.5 7B", [("parent", "qwen-parent/gsm8k_t512"), ("control", "qwen-ar-control/gsm8k_t512"),
                        ("retrained", "qwen-byod-retrained/gsm8k"), ("released", "qwen-byod-released/gsm8k")]),
        ("Ministral 8B", [("parent", "ministral-parent/gsm8k_t512"), ("control", "ministral-ar-control/gsm8k_t512"),
                          ("released", "ministral-byod-released/gsm8k")])]
y0 = 0
ticks = []
for name, arms in rows:
    for j, (role, key) in enumerate(arms):
        y = y0 - j * 0.22
        ax.barh(y, acc(key), 0.18, color=ARM[role][1], zorder=2)
        ax.text(acc(key) + 0.01, y, f"{acc(key):.2f}  {ARM[role][0]}", va="center", fontsize=7, color=INK2)
    ticks.append((y0 - (len(arms) - 1) * 0.11, name)); y0 -= len(arms) * 0.22 + 0.3
ax.set_yticks([t[0] for t in ticks]); ax.set_yticklabels([t[1] for t in ticks]); ax.set_xlim(0, 1.45)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_xlabel("GSM8K accuracy (AR models at 512 tokens)"); grid(ax, "x")
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0); ax.spines["bottom"].set_bounds(0, 1)
fig.tight_layout(); fig.savefig(OUT / "gsm8k_chain.png", dpi=220); plt.close(fig)
print("figures written to", OUT)
