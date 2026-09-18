"""Static figures (matplotlib). Requires the optional `viz` extra: pip install -e ".[viz]"."""
from __future__ import annotations
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from .analysis import (
    EVIDENCE_ORDER,
    GROUP_LABELS,
    NODE_GROUPS,
    convergence,
    evidence_counts,
    is_hypothesis,
    is_inhibitory,
    path_summary,
)
from .graph import Graph
from .layout import layered_layout
from .reasoning.path_search import PathResult

# Reference categorical palette (light mode), fixed slot order
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, MUTED, GRID, LINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
GROUP_COLOR = {"molecular": BLUE, "mechanism": AQUA, "phenotype": ORANGE}
FONT = ["Segoe UI", "DejaVu Sans", "Arial"]


def _mpl():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "text.color": INK,
            "axes.edgecolor": LINE,
            "axes.labelcolor": INK2,
            "xtick.color": MUTED,
            "ytick.color": INK2,
        }
    )
    return plt


def _tint(hex_color: str, alpha: float = 0.16) -> str:
    c = hex_color.lstrip("#")
    s = SURFACE.lstrip("#")
    mix = [int(int(c[i : i + 2], 16) * alpha + int(s[i : i + 2], 16) * (1 - alpha)) for i in (0, 2, 4)]
    return "#{:02x}{:02x}{:02x}".format(*mix)


def _edge_id(e) -> Tuple[str, str, str]:
    return (e.subject, e.predicate, e.object)


def draw_overview(
    graph: Graph,
    out_path: str,
    highlight: Optional[PathResult] = None,
    title: str = "",
    subtitle: str = "",
) -> None:
    plt = _mpl()
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

    pos = layered_layout(graph)
    sx, sy, bw, bh = 2.9, 1.15, 2.05, 0.66
    xy = {n: (p[0] * sx, -p[1] * sy) for n, p in pos.items()}
    xs = [p[0] for p in xy.values()]
    ys = [p[1] for p in xy.values()]
    width = max(xs) - min(xs) + bw + 1.0
    height = (max(ys) - min(ys) + bh + 1.1) / 0.85  # axes occupy 85% of the figure height

    fig, ax = plt.subplots(figsize = (width, height))
    ax.set_xlim(min(xs) - bw / 2 - 0.5, max(xs) + bw / 2 + 0.5)
    ax.set_ylim(min(ys) - bh / 2 - 0.55, max(ys) + bh / 2 + 0.55)
    ax.set_aspect("equal")
    ax.axis("off")

    patches: Dict[str, FancyBboxPatch] = {}
    for n in graph.nodes.values():
        x, y = xy[n.id]
        color = GROUP_COLOR[NODE_GROUPS.get(n.type, "mechanism")]
        root = "root_event" in n.tags
        p = FancyBboxPatch(
            (x - bw / 2, y - bh / 2),
            bw,
            bh,
            boxstyle = "round,pad=0.0,rounding_size=0.14",
            fc = _tint(color),
            ec = color,
            lw = 2.6 if root else 1.5,
            zorder = 3,
        )
        ax.add_patch(p)
        patches[n.id] = p
        label = textwrap.fill(n.name, 22)
        ax.text(x, y, label, ha = "center", va = "center", fontsize = 9, color = INK, zorder = 4, linespacing = 1.15)

    on_path: Set[Tuple[str, str, str]] = {_edge_id(s.edge) for s in highlight.steps} if highlight else set()
    for e in sorted(graph.edges, key = lambda e: _edge_id(e) in on_path):
        (x1, y1), (x2, y2) = xy[e.subject], xy[e.object]
        span = abs(pos[e.object][1] - pos[e.subject][1])
        rad = 0.0 if span <= 1 and abs(x2 - x1) < 0.1 else (0.10 if x2 >= x1 else -0.10) * min(span, 3)
        hi = _edge_id(e) in on_path
        color = INK if hi else MUTED
        arrow = FancyArrowPatch(
            posA = (x1, y1),
            posB = (x2, y2),
            arrowstyle = "-[,widthB=0.9,lengthB=0.25" if is_inhibitory(e) else "-|>",
            mutation_scale = 11 if not is_inhibitory(e) else 7,
            connectionstyle = f"arc3,rad={rad}",
            patchA = patches[e.subject],
            patchB = patches[e.object],
            shrinkA = 2,
            shrinkB = 2,
            lw = (1.0 + 3.4 * e.weight) * (1.35 if hi else 1.0) / 1.6,
            ls = (0, (4, 2.5)) if is_hypothesis(e) else "-",
            color = color,
            alpha = 1.0 if hi else 0.62,
            zorder = 6 if hi else 2,
        )
        ax.add_patch(arrow)

    legend_items = [Patch(fc = _tint(GROUP_COLOR[g]), ec = GROUP_COLOR[g], lw = 1.5, label = GROUP_LABELS[g]) for g in GROUP_LABELS]
    legend_items += [
        Line2D([0], [0], color = MUTED, lw = 2.2, label = "Supported edge"),
        Line2D([0], [0], color = MUTED, lw = 2.2, ls = (0, (4, 2.5)), label = "Hypothesis-level edge"),
        Line2D([0], [0], color = MUTED, lw = 0, marker = "|", markersize = 11, mew = 2, label = "Inhibitory (T-bar)"),
    ]
    if highlight is not None:
        legend_items.append(Line2D([0], [0], color = INK, lw = 3, label = "Lowest-cost path"))
    fig.legend(
        handles = legend_items,
        loc = "lower center",
        ncol = 4,
        frameon = False,
        fontsize = 9,
        labelcolor = INK2,
        bbox_to_anchor = (0.5, 0.005),
    )
    fig.text(0.5, 0.985, title, ha = "center", va = "top", fontsize = 17, fontweight = "bold", color = INK)
    if subtitle:
        fig.text(0.5, 0.955, subtitle, ha = "center", va = "top", fontsize = 10.5, color = INK2)
    fig.text(0.995, 0.055, "Line width = edge confidence", ha = "right", fontsize = 8.5, color = MUTED)
    fig.subplots_adjust(left = 0, right = 1, top = 0.94, bottom = 0.09)
    _save(fig, out_path)


def _short(graph: Graph, node_id: str, width: int = 34) -> str:
    return textwrap.shorten(graph.nodes[node_id].name, width = width, placeholder = "…")


def _clean_axes(ax) -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(axis = "y", length = 0)
    ax.xaxis.grid(True, color = GRID, lw = 0.8)
    ax.set_axisbelow(True)


def draw_path_comparison(graph: Graph, paths: List[PathResult], out_path: str, source_name: str, target_name: str) -> None:
    plt = _mpl()
    from matplotlib.patches import Patch

    fig, (a1, a2) = plt.subplots(1, 2, figsize = (14.5, 5.6), gridspec_kw = {"width_ratios": [1.15, 1]})

    summ = [path_summary(p) for p in paths]
    labels = []
    for i, p in enumerate(paths, 1):
        ids = p.node_ids()
        labels.append(f"{i}. via {_short(graph, ids[-2], 40)}")
    ypos = list(range(len(paths)))[::-1]
    conf = [s["confidence_cost"] for s in summ]
    pen = [s["predicate_penalty"] for s in summ]
    h = 0.5
    a1.barh(ypos, conf, height = h, color = BLUE, edgecolor = SURFACE, lw = 1.5, label = "Low confidence  (−ln w)")
    a1.barh(ypos, pen, height = h, left = conf, color = ORANGE, edgecolor = SURFACE, lw = 1.5, label = "Vague predicate penalty")
    for y, s in zip(ypos, summ):
        a1.text(s["cost"] + 0.08, y, f'{s["cost"]:.2f}  ·  {int(s["hops"])} hops  ·  {int(s["n_hypothesis_edges"])} hypothesis {"edge" if s["n_hypothesis_edges"] == 1 else "edges"}', va = "center", fontsize = 8.8, color = INK2)
    a1.set_yticks(ypos)
    a1.set_yticklabels(labels, fontsize = 9.5)
    a1.set_xlim(0, max(s["cost"] for s in summ) * 1.62)
    a1.set_xlabel("Path cost (lower = more credible mechanism)", fontsize = 9.5)
    a1.set_title(f"Competing explanations: {source_name} → {target_name}", loc = "left", fontsize = 12.5, fontweight = "bold", pad = 26)
    a1.text(0, 1.03, "Top-ranked paths, labelled by the last step before the outcome", transform = a1.transAxes, fontsize = 9.5, color = INK2)
    _clean_axes(a1)
    a1.legend(handles = [Patch(fc = BLUE, label = "Low-confidence edges (−ln w)"), Patch(fc = ORANGE, label = "Vague-predicate penalty")], loc = "upper center", bbox_to_anchor = (0.5, -0.16), ncol = 2, frameon = False, fontsize = 9, labelcolor = INK2)

    conv = convergence(paths)[:9]
    names = [_short(graph, n, 34) for n, _ in conv][::-1]
    vals = [v for _, v in conv][::-1]
    colors = [BLUE if v >= 0.999 else MUTED for v in vals]
    yy = list(range(len(vals)))
    a2.barh(yy, vals, height = 0.5, color = colors, edgecolor = SURFACE, lw = 1.5)
    for y, v in zip(yy, vals):
        a2.text(v + 0.015, y, f"{v:.0%}", va = "center", fontsize = 9, color = INK2)
    a2.set_yticks(yy)
    a2.set_yticklabels(names, fontsize = 9.5)
    a2.set_xlim(0, 1.12)
    a2.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    a2.set_xlabel(f"Share of the top {len(paths)} paths passing through the node", fontsize = 9.5)
    a2.set_title("Convergence points", loc = "left", fontsize = 12.5, fontweight = "bold", pad = 26)
    a2.text(0, 1.03, "Nodes on every route (blue) are forced by graph structure; lower rows show real branching", transform = a2.transAxes, fontsize = 9.5, color = INK2)
    _clean_axes(a2)

    fig.tight_layout(w_pad = 3)
    _save(fig, out_path)


def draw_evidence_audit(graph: Graph, best: PathResult, out_path: str, source_name: str, target_name: str) -> None:
    plt = _mpl()
    from matplotlib.patches import Patch

    fig, (a1, a2) = plt.subplots(1, 2, figsize = (14.5, 5.4), gridspec_kw = {"width_ratios": [1, 1.1]})

    counts = evidence_counts(graph)
    levels = EVIDENCE_ORDER[::-1]
    ypos = list(range(len(levels)))
    vals = [counts[l] for l in levels]
    cols = [ORANGE if l == "hypothesis" else BLUE for l in levels]
    a1.barh(ypos, vals, height = 0.5, color = cols, edgecolor = SURFACE, lw = 1.5)
    for y, v in zip(ypos, vals):
        a1.text(v + 0.3, y, str(v) if v else "0 (none yet)", va = "center", fontsize = 9, color = INK2 if v else MUTED)
    a1.set_yticks(ypos)
    a1.set_yticklabels([l.replace("_", " ") for l in levels], fontsize = 9.5)
    a1.set_xlim(0, max(vals) * 1.25)
    a1.set_xlabel("Number of edges", fontsize = 9.5)
    n_hyp = counts["hypothesis"]
    a1.set_title(f"Where the evidence stands: {n_hyp} of {len(graph.edges)} edges are hypotheses", loc = "left", fontsize = 12.5, fontweight = "bold", pad = 26)
    a1.text(0, 1.03, "Evidence level of every edge, roughly ordered from clinical (top) to hypothesis", transform = a1.transAxes, fontsize = 9.5, color = INK2)
    _clean_axes(a1)

    steps = best.steps
    ypos2 = list(range(len(steps)))[::-1]
    w = [s.edge.weight for s in steps]
    cols2 = [ORANGE if is_hypothesis(s.edge) else BLUE for s in steps]
    a2.barh(ypos2, w, height = 0.5, color = cols2, edgecolor = SURFACE, lw = 1.5)
    for y, s in zip(ypos2, steps):
        a2.text(s.edge.weight + 0.015, y, f"{s.edge.weight:.2f}", va = "center", fontsize = 9, color = INK2)
    lab = [f"{_short(graph, s.edge.subject, 30)} → {_short(graph, s.edge.object, 30)}" for s in steps]
    a2.set_yticks(ypos2)
    a2.set_yticklabels(lab, fontsize = 8.8)
    a2.set_xlim(0, 1.0)
    a2.set_xlabel("Edge confidence (weight)", fontsize = 9.5)
    a2.set_title("Confidence along the lowest-cost path", loc = "left", fontsize = 12.5, fontweight = "bold", pad = 26)
    a2.text(
        0, 1.03,
        "Confident at the metabolic root, hypothesis-level at the final step",
        transform = a2.transAxes, fontsize = 9.5, color = INK2,
    )
    _clean_axes(a2)
    a2.legend(handles = [Patch(fc = BLUE, label = "Supported"), Patch(fc = ORANGE, label = "Hypothesis")], loc = "lower right", frameon = False, fontsize = 9, labelcolor = INK2)

    fig.tight_layout(w_pad = 3)
    _save(fig, out_path)


def _save(fig, out_path: str) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents = True, exist_ok = True)
    fig.savefig(p, dpi = 170)
    import matplotlib.pyplot as plt

    plt.close(fig)




