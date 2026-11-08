"""Figure generation for the CS787 blueprint. Palette: dataviz reference instance (light mode)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
from matplotlib import font_manager as fm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(OUT, exist_ok=True)

# Fonts: DejaVu ships with matplotlib (full Unicode coverage).
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"; GRID = "#e1e0d9"; AXIS = "#c3c2b7"
BLUE = "#2a78d6"; ORANGE = "#eb6834"; AQUA = "#1baf7a"; YELLOW = "#eda100"
MAGENTA = "#e87ba4"; GREEN = "#008300"; VIOLET = "#6250d6"; RED = "#e34948"
BLUE_L = "#dbe9fa"; ORANGE_L = "#fbe3d9"; AQUA_L = "#d6f1e7"; GREY_L = "#f1f0ec"; YELLOW_L = "#fbecc8"; RED_L = "#f9dcdc"
VIOLET_L = "#e4e0f7"
DPI = 260


def box(ax, x, y, w, h, text, fc=GREY_L, ec=AXIS, ls="-", fs=7.6, color=INK, bold=False, lw=1.0, align="center", pad=0.6):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={pad}", fc=fc, ec=ec, lw=lw, ls=ls)
    ax.add_patch(p)
    ha = "center" if align == "center" else "left"
    tx = x + w / 2 if align == "center" else x + 1.2
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, color=color,
            fontweight="bold" if bold else "normal", linespacing=1.25)
    return p


def arrow(ax, x0, y0, x1, y1, color=INK2, lw=1.1, ls="-", style="-|>", rad=0.0):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}", mutation_scale=9))


def canvas(w, h, xmax, ymax):
    fig = plt.figure(figsize=(w, h), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.axis("off")
    return fig, ax


# --------------------------------------------------------------------------------------
# Figure A: what the base paper's protocol does (verified from paper text + repo run.py)
# --------------------------------------------------------------------------------------
def fig_protocol():
    fig, ax = canvas(6.9, 3.15, 100, 46)
    ax.text(0, 44.2, "InterruptBench protocol (as described in the paper and implemented in Eval/run.py)", fontsize=8.4,
            fontweight="bold", color=INK, va="center")
    # row 1
    box(ax, 0, 27, 29, 13, "Raw item (per task)\nq0 = under-specified query\nu = update message(s)\nground truth = original intent", fc=GREY_L)
    box(ax, 35.5, 27, 29, 13, "Stage A  (LLM calls)\nBackbone runs q0 to the end;\nsaves actions a1 … aN", fc=BLUE_L, ec=BLUE)
    box(ax, 71, 27, 29, 13, "No-interruption baseline\nStage A result scored against\nthe FINAL intent (lower bound)", fc=GREY_L)
    arrow(ax, 29, 33.5, 35.5, 33.5); arrow(ax, 64.5, 33.5, 71, 33.5)
    # row 2
    box(ax, 0, 5, 29, 13, "Stage B-1  (no LLM calls)\nReset WebArena; replay a1 … aK\nK = ⌊0.6 · N⌋  (default)", fc=GREY_L)
    box(ax, 35.5, 5, 29, 13, "Stage B-2  inject update\nintent ← q0 + “[User interrupt\n@action=K] u”  (append mode)", fc=ORANGE_L, ec=ORANGE)
    box(ax, 71, 5, 29, 13, "Stage B-3  (LLM calls)\nSame agent continues from the\nlive page; ≤ k further actions", fc=BLUE_L, ec=BLUE)
    arrow(ax, 29, 11.5, 35.5, 11.5); arrow(ax, 64.5, 11.5, 71, 11.5)
    # connector from row1 stage A down to B-1 (elbow)
    arrow(ax, 50, 27, 50, 22.5, lw=1.0); ax.plot([50, 14.5], [22.5, 22.5], color=INK2, lw=1.0); arrow(ax, 14.5, 22.5, 14.5, 18)
    ax.text(51.2, 24.4, "trajectory reused as fixed prefix", fontsize=6.9, color=INK2, va="center")
    ax.text(0, 1.2, "Scoring: String / URL / Program match (WebAgent-R1 evaluators). Efficiency: output tokens and action count vs the matched baseline.",
            fontsize=6.9, color=INK2, va="center")
    fig.savefig(os.path.join(OUT, "fig_protocol.png"), dpi=DPI, facecolor="white"); plt.close(fig)


# --------------------------------------------------------------------------------------
# Figure B: illustrative — which prefix work survives each interruption type
# --------------------------------------------------------------------------------------
def fig_types():
    fig, ax = canvas(6.9, 3.6, 100, 58)
    ax.text(0, 56.2, "Illustration: what happens to already-executed work (constructed from InterruptBench example tasks)", fontsize=8.4,
            fontweight="bold", color=INK, va="center")
    rows = [
        ("Addition", "“top-3 best-selling products” → “…for Jan 2023 specifically”",
         ["K", "K", "K", "K", "K", "K", "K", "K"], "Prefix stays valid but incomplete: add the missing constraint, keep the progress."),
        ("Revision", "start “Phipps Conservatory” → “Randyland, not Phipps”",
         ["K", "K", "R", "X", "X", "X", "X", "X"], "Prefix partly built on a wrong value: fix the field, recompute, discard the stale route."),
        ("Retraction", "“…during peak rush hour” → “without the rush hour consideration”",
         ["K", "K", "K", "R", "X", "X", "X", "X"], "Prefix applied a constraint the user dropped: undo that setting, then recompute."),
    ]
    colors = {"K": (AQUA_L, AQUA), "R": (YELLOW_L, YELLOW), "X": (RED_L, RED)}
    import textwrap
    for i, (name, ex, st, note) in enumerate(rows):
        b = 38 - i * 15
        ax.text(0, b + 12.6, name, fontsize=8.2, fontweight="bold", color=INK, va="center")
        ax.text(0, b + 9.4, ex, fontsize=6.8, color=INK2, va="center")
        for j, s_ in enumerate(st):
            fc, ec = colors[s_]
            box(ax, j * 4.7, b + 1, 4.1, 5.6, s_, fc=fc, ec=ec, fs=7.2, bold=True, lw=1.1, pad=0.5)
        xu = 8 * 4.7 + 0.6
        ax.plot([xu, xu], [b - 0.2, b + 7.6], color=INK, lw=1.0, ls=(0, (3, 2)))
        ax.text(xu, b - 1.9, "update arrives", fontsize=6.4, color=INK, ha="center", va="center")
        box(ax, 41.5, b + 1, 19, 5.6, "post-interruption\nactions: ?", fc="white", ec=MUTED, ls=(0, (3, 2)), fs=6.7, color=INK2)
        ax.text(64, b + 3.8, "\n".join(textwrap.wrap(note, 44)), fontsize=6.6, color=INK2, va="center", linespacing=1.3)
    lx = 0; ly = 1.8
    for k, label in (("K", "K = keep (still valid, reuse)"), ("R", "R = repair (reuse after correction)"), ("X", "X = stale / undo / redo")):
        fc, ec = colors[k]
        box(ax, lx, ly - 1.7, 3.4, 3.4, k, fc=fc, ec=ec, fs=6.6, bold=True, pad=0.4)
        ax.text(lx + 4.6, ly, label, fontsize=6.7, color=INK2, va="center")
        lx += 33
    fig.savefig(os.path.join(OUT, "fig_types.png"), dpi=DPI, facecolor="white"); plt.close(fig)


# --------------------------------------------------------------------------------------
# Figure C: base paper's reported results (numbers re-checked against the PDF text)
# --------------------------------------------------------------------------------------
def fig_results():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.9, 2.9), dpi=DPI, gridspec_kw={"width_ratios": [1.05, 1]})
    fig.subplots_adjust(left=0.075, right=0.985, top=0.88, bottom=0.17, wspace=0.34)
    # (a) Table 2
    n = [0, 1, 2, 3]
    series = [
        ("Haiku 4.5", [5.45, 19.39, 33.33, 38.79], BLUE),
        ("Sonnet 4.5", [4.24, 15.15, 33.33, 41.21], ORANGE),
        ("Opus 4.5", [5.45, 21.21, 36.36, 41.82], AQUA),
        ("Qwen3", [4.24, 11.52, 18.79, 23.64], YELLOW),
        ("DeepSeek-V3.1", [4.85, 12.12, 21.21, 20.61], MAGENTA),
        ("Mistral-L3", [3.03, 11.52, 12.73, 13.94], GREEN),
    ]
    for name, ys, col in series:
        a1.plot(n, ys, color=col, lw=2.0, marker="o", ms=5.2, mec="white", mew=1.2, zorder=3)
    # direct labels at right end (manually nudged to avoid collisions)
    nudge = {"Haiku 4.5": -1.9, "Sonnet 4.5": 0.0, "Opus 4.5": 1.8, "Qwen3": 1.3, "DeepSeek-V3.1": -1.4, "Mistral-L3": 0.0}
    for name, ys, col in series:
        a1.text(3.07, ys[-1] + nudge[name], name, fontsize=6.4, color=INK2, va="center")
    a1.set_xlim(-0.15, 4.25); a1.set_ylim(0, 47)
    a1.set_xticks(n); a1.set_xlabel("Number of interruptions delivered (n)", fontsize=7.2, color=INK2)
    a1.set_ylabel("Converged success rate (%)", fontsize=7.2, color=INK2)
    a1.set_title("(a) Multi-interruption runs (paper Table 2)", fontsize=7.8, color=INK, loc="left", fontweight="bold")
    # (b) Table E.3 — Opus and Sonnet only
    pos = [0.0, 0.2, 0.4, 0.6, 0.8]
    opus = [13.94, 47.27, 55.76, 54.55, 56.97]
    sonnet = [13.33, 47.27, 44.24, 41.21, 42.42]
    for ys, col, nm in ((opus, AQUA, "Opus 4.5"), (sonnet, ORANGE, "Sonnet 4.5")):
        a2.plot(pos[1:], ys[1:], color=col, lw=2.0, marker="o", ms=5.2, mec="white", mew=1.2, zorder=3)
        a2.plot([0.03 if nm == "Opus 4.5" else 0.10], [ys[0]], marker="s", ms=5.2, color=col, mec="white", mew=1.0, zorder=3, ls="none")
    a2.text(0.8, 59.3, "Opus 4.5", fontsize=6.6, color=INK2, ha="right", va="center")
    a2.text(0.8, 39.1, "Sonnet 4.5", fontsize=6.6, color=INK2, ha="right", va="center")
    a2.text(0.02, 7.0, "squares = no-interruption\nbaselines (13.9, 13.3)", fontsize=6.0, color=INK2, va="center")
    a2.set_xlim(-0.04, 0.9); a2.set_ylim(0, 66)
    a2.set_xticks([0.2, 0.4, 0.6, 0.8]); a2.set_xlabel("Interruption position (fraction of baseline trajectory)", fontsize=7.2, color=INK2)
    a2.set_ylabel("Overall success rate (%)", fontsize=7.2, color=INK2)
    a2.set_title("(b) Position sweep (paper Table E.3)", fontsize=7.8, color=INK, loc="left", fontweight="bold")
    for a in (a1, a2):
        a.set_facecolor("white"); a.grid(axis="y", color=GRID, lw=0.7); a.set_axisbelow(True)
        for s in ("top", "right"): a.spines[s].set_visible(False)
        for s in ("left", "bottom"): a.spines[s].set_color(AXIS)
        a.tick_params(colors=MUTED, labelsize=6.8, length=2.5)
    fig.savefig(os.path.join(OUT, "fig_results.png"), dpi=DPI, facecolor="white"); plt.close(fig)


# --------------------------------------------------------------------------------------
# Figure D: proposed method flowchart (candidate method M1; speculative parts dashed)
# --------------------------------------------------------------------------------------
def fig_method():
    fig, ax = canvas(6.9, 5.15, 100, 74)
    ax.text(0, 72.6, "Candidate method M1 (proposal — not yet implemented or tested)",
            fontsize=8.3, fontweight="bold", color=INK, va="center")
    # top row
    box(ax, 0, 57, 24, 11, "Initial goal G0\n+ live environment", fc=GREY_L)
    box(ax, 30, 57, 36, 11, "Agent loop (unchanged scaffold)\nobserve → think → act, steps 1…K", fc=BLUE_L, ec=BLUE)
    box(ax, 72, 57, 28, 11, "User update u arrives\n(after step K; env state is\nwhatever the prefix left)", fc=ORANGE_L, ec=ORANGE)
    arrow(ax, 24, 62.5, 30, 62.5); arrow(ax, 66, 62.5, 72, 62.5)
    # handler panel
    ax.add_patch(FancyBboxPatch((0, 21.5), 100, 31.5, boxstyle="round,pad=0,rounding_size=1.2", fc="#f7f7f4", ec=BLUE, lw=1.2))
    ax.text(1.6, 50.9, "Interruption handler H  (extra LLM calls; each component is an ablation switch)", fontsize=7.4, color=BLUE, fontweight="bold", va="center")
    box(ax, 2, 27, 30, 19, "C1  Goal reconciler\n(G0, u) → G1 and a requirement\nledger: each requirement is\nunchanged / added / modified /\nretracted (with its source)", fc="white", ec=BLUE, fs=7.0)
    box(ax, 35, 27, 30, 19, "C2  Prefix auditor\nfor each executed action a_i:\neffect class (read / navigate /\nform edit / submit) and verdict\nKEEP · REPAIR · STALE · UNDO", fc="white", ec=BLUE, fs=7.0)
    box(ax, 68, 27, 30, 19, "C3  Repair note\nshort text: facts to reuse,\nUI state to correct, steps to\nredo, things NOT to carry\nover (retracted values)", fc="white", ec=BLUE, fs=7.0)
    arrow(ax, 32, 36.5, 35, 36.5); arrow(ax, 65, 36.5, 68, 36.5)
    box(ax, 35, 22.8, 30, 3.0, "speculative: effect class from DOM / URL diff", fc="white", ec=MUTED, ls=(0, (3, 2)), fs=6.0, color=INK2, pad=0.3)
    box(ax, 68, 22.8, 30, 3.0, "speculative: inverse-action synthesis for UNDO", fc="white", ec=MUTED, ls=(0, (3, 2)), fs=6.0, color=INK2, pad=0.3)
    ax.plot([86, 86], [57, 47.6], color=INK2, lw=1.1); ax.plot([86, 17], [47.6, 47.6], color=INK2, lw=1.1)
    arrow(ax, 17, 47.6, 17, 46.1)
    ax.text(52, 47.6, "inputs: G0, u, executed prefix, current observation", fontsize=6.3, color=INK2, va="center", ha="center",
            bbox=dict(fc="#f7f7f4", ec="none", pad=0.8))
    # bottom row
    box(ax, 0, 3, 32, 12, "Resume agent loop (history kept)\ncontext = G1 + ledger + repair note\n(vs. B2: one appended sentence)", fc=BLUE_L, ec=BLUE)
    box(ax, 38, 3, 32, 12, "C4  Final verifier\ncheck proposed answer / state against\nACTIVE requirements; fail → back to\nloop (≤ m retries)", fc="white", ec=BLUE)
    box(ax, 76, 3, 24, 12, "Log everything\ndecisions, tokens, actions,\nlatency, violations", fc=GREY_L)
    ax.plot([83, 83], [21.5, 18.4], color=INK2, lw=1.1); ax.plot([83, 16], [18.4, 18.4], color=INK2, lw=1.1); arrow(ax, 16, 18.4, 16, 15.2)
    arrow(ax, 32, 9, 38, 9); arrow(ax, 70, 9, 76, 9)
    arrow(ax, 54, 15, 54, 18.1, color=MUTED, ls=(0, (3, 2)), lw=0.9)
    ax.text(55.4, 16.6, "retry", fontsize=6.0, color=INK2, va="center")
    fig.savefig(os.path.join(OUT, "fig_method.png"), dpi=DPI, facecolor="white"); plt.close(fig)


# --------------------------------------------------------------------------------------
# Figure E: experiment harness architecture (plan)
# --------------------------------------------------------------------------------------
def fig_infra():
    fig, ax = canvas(6.9, 3.35, 100, 50)
    ax.text(0, 48.2, "Planned experiment harness (reuses the InterruptBench runner; new parts shown in blue)", fontsize=8.3,
            fontweight="bold", color=INK, va="center")
    box(ax, 0, 33, 22, 11, "InterruptBench\nraw JSON + WebArena-Lite\ntask configs (pinned commit)", fc=GREY_L, fs=6.9)
    box(ax, 0, 15, 22, 13, "WebArena sites (Docker)\n+ reset server\nLinux host — TBD", fc=GREY_L, fs=6.9)
    box(ax, 29, 33, 22, 11, "Stage A runner\nper backbone: saves\nprefix trajectories", fc=GREY_L, fs=6.9)
    box(ax, 29, 8, 22, 22, "Stage B runner\n(existing replay logic,\nnew strategy plug-ins)\n\nB2 · B2+ · B3a · B3b\nM1 and its ablations", fc=BLUE_L, ec=BLUE, fs=6.9)
    box(ax, 58, 33, 19, 11, "Run manifest\ncommit, model id, seed,\nprompts, image hashes", fc=BLUE_L, ec=BLUE, fs=6.7)
    box(ax, 58, 15, 19, 15, "Structured logger (JSONL)\nper call: tokens, latency\nper step: action, URL,\nhandler decisions", fc=BLUE_L, ec=BLUE, fs=6.7)
    box(ax, 83, 33, 17, 11, "Scorer\nnative evaluators\n+ our metrics", fc=BLUE_L, ec=BLUE, fs=6.7)
    box(ax, 83, 15, 17, 15, "Analysis\npaired tests, clustered\nbootstrap, plots,\nfailure labels", fc=BLUE_L, ec=BLUE, fs=6.7)
    arrow(ax, 22, 38.5, 29, 38.5); arrow(ax, 40, 33, 40, 30.2)
    arrow(ax, 22, 21.5, 29, 21.5); arrow(ax, 51, 20, 58, 22.5)
    arrow(ax, 51, 12, 58, 18, rad=0.0)
    arrow(ax, 67.5, 33, 67.5, 30.2, color=MUTED); arrow(ax, 77, 22.5, 83, 22.5)
    arrow(ax, 91.5, 33, 91.5, 30.2); arrow(ax, 77, 38.5, 83, 38.5, color=MUTED)
    ax.text(0, 4.0, "Existing InterruptBench code: Stage A/B runners, replay, native evaluators.  New code: strategy interface, logger, manifest, metrics, analysis.",
            fontsize=6.7, color=INK2, va="center")
    ax.text(0, 1.2, "Nothing in this figure has been installed or run yet (see Section 7 for what was actually checked).", fontsize=6.7, color=INK2, va="center")
    fig.savefig(os.path.join(OUT, "fig_infra.png"), dpi=DPI, facecolor="white"); plt.close(fig)


# --------------------------------------------------------------------------------------
# Figure F: relative-week plan
# --------------------------------------------------------------------------------------
def fig_gantt():
    fig, ax = plt.subplots(figsize=(6.9, 3.55), dpi=DPI)
    fig.subplots_adjust(left=0.30, right=0.985, top=0.90, bottom=0.14)
    tasks = [
        ("P0  Decisions, access, environment plan", 1, 2, "core"),
        ("P1  Infra up + smoke test (3 tasks)", 1, 3, "core"),
        ("P2  Stage A + B2 pilot (20 tasks)", 3, 4, "core"),
        ("P3  Strategies B2+, B3a/b, M1 + tests", 3, 6, "core"),
        ("P4  Main comparison (MVP subset)", 6, 8, "core"),
        ("P5  Ablations, position sweep, 2nd model", 8, 9, "opt"),
        ("P6  Error analysis + failure labels", 8, 10, "core"),
        ("P7  Demo (scripted + live)", 7, 10, "opt"),
        ("P8  Report, slides, repro package", 9, 12, "core"),
    ]
    n = len(tasks)
    for i, (name, s, e, kind) in enumerate(tasks):
        y = n - 1 - i
        col, alpha = (BLUE, 1.0) if kind == "core" else (BLUE, 0.38)
        ax.barh(y, e - s + 1, left=s - 0.5, height=0.5, color=col, alpha=alpha, edgecolor="none")
    ax.set_yticks(range(n)); ax.set_yticklabels([t[0] for t in tasks][::-1], fontsize=6.9, color=INK)
    # milestones
    ms = [(3, "M1 smoke test"), (4, "M2 B2 reproduced"), (6, "M3 method frozen"), (8, "M4 main results"), (10, "M5 feature freeze"), (12, "M6 submit")]
    for x, lab in ms:
        ax.plot([x + 0.5, x + 0.5], [-0.55, n - 0.45], color=ORANGE, lw=0.9, ls=(0, (3, 2)), zorder=1)
        ax.plot([x + 0.5], [n - 0.45], marker="D", ms=5, color=ORANGE, mec="white", mew=0.8, zorder=4, clip_on=False)
        ax.text(x + 0.5, n + 0.05, lab.split(" ", 1)[0], fontsize=6.4, color=INK2, ha="center", va="bottom", fontweight="bold")
    ax.set_xlim(0.5, 12.5); ax.set_ylim(-0.6, n - 0.35)
    ax.set_xticks(range(1, 13)); ax.set_xlabel("Relative week (stretch or compress to the real deadline — see Section 11)", fontsize=7.2, color=INK2)
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS); ax.tick_params(colors=MUTED, labelsize=6.8, length=0)
    ax.tick_params(axis="y", length=0, labelcolor=INK)
    # legend
    ax.barh([-5], [0], color=BLUE)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    h = [Patch(fc=BLUE, label="core work"), Patch(fc=BLUE, alpha=0.38, label="optional / target-tier"),
         Line2D([0], [0], marker="D", color=ORANGE, ls="none", ms=5, label="milestone (M1–M6)")]
    ax.legend(handles=h, loc="lower left", bbox_to_anchor=(0.0, -0.36), ncol=3, fontsize=6.6, frameon=False, labelcolor=INK2)
    fig.savefig(os.path.join(OUT, "fig_gantt.png"), dpi=DPI, facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    fig_protocol(); fig_types(); fig_results(); fig_method(); fig_infra(); fig_gantt()
    print("figures written to", OUT)
