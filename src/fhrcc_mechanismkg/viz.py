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

# Type scale (pt) shared by every figure
TITLE_PT = 14  # panel and figure titles, bold
SUBTITLE_PT = 12  # subheaders, regular weight
LABEL_PT = 10  # tick labels, annotations, axis titles (bold), node text
LEGEND_PT = 11
NODE_PT = 13  # text inside the flow chart boxes
OVERVIEW_LEGEND_PT = 12


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
            "axes.labelcolor": INK,
            "axes.labelsize": LABEL_PT,
            "axes.labelweight": "bold",
            "xtick.color": MUTED,
            "ytick.color": INK2,
            "xtick.labelsize": LABEL_PT,
            "ytick.labelsize": LABEL_PT,
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


def _curve_points(p0: Tuple[float, float], p2: Tuple[float, float], rad: float, n: int = 48) -> List[Tuple[float, float]]:
    """Points along matplotlib's arc3 connection (quadratic Bezier) between two node centers."""
    (x1, y1), (x2, y2) = p0, p2
    cx, cy = (x1 + x2) / 2 + rad * (y2 - y1), (y1 + y2) / 2 - rad * (x2 - x1)
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2))
    return pts


def _route_rad(
    src: str,
    dst: str,
    xy: Dict[str, Tuple[float, float]],
    default: float,
    bw: float,
    bh: float,
    x_bounds: Tuple[float, float],
    margin: float = 0.03,
) -> float:
    """Keep the default curvature unless it crosses a node box; then use the gentlest bend that clears all boxes."""

    def cost(rad: float) -> int:
        pts = _curve_points(xy[src], xy[dst], rad)
        hits = 0
        for px, py in pts:
            if not (x_bounds[0] <= px <= x_bounds[1]):
                hits += 5  # drifting off the canvas is worse than clipping a box edge
            for nid, (nx, ny) in xy.items():
                if nid in (src, dst):
                    continue
                if abs(px - nx) < bw / 2 + margin and abs(py - ny) < bh / 2 + margin:
                    hits += 1
        return hits

    if cost(default) == 0:
        return default
    for mag in (0.03, 0.05, 0.08, 0.12, 0.18, 0.26, 0.36, 0.5):
        for rad in (mag, -mag):
            if cost(rad) == 0:
                return rad
    return default  # no clean route exists; a half-clearing detour only adds clutter


def _panel_header(ax, title: str, subtitle: str) -> None:
    ax.set_title(title, loc = "left", fontsize = TITLE_PT, fontweight = "bold", pad = 34)
    ax.text(0, 1.035, subtitle, transform = ax.transAxes, fontsize = SUBTITLE_PT, color = INK2)


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

    pos = layered_layout(graph, spine = highlight.node_ids() if highlight else None)
    sx, sy, bw, bh = 2.85, 1.2, 2.5, 0.82
    xy = {n: (p[0] * sx, -p[1] * sy) for n, p in pos.items()}
    xs = [p[0] for p in xy.values()]
    ys = [p[1] for p in xy.values()]
    width = max(xs) - min(xs) + bw + 1.0
    height = (max(ys) - min(ys) + bh + 0.9) / 0.87  # axes occupy 87% of the figure height

    fig, ax = plt.subplots(figsize = (width, height))
    x_bounds = (min(xs) - bw / 2 - 0.5, max(xs) + bw / 2 + 0.5)
    ax.set_xlim(*x_bounds)
    ax.set_ylim(min(ys) - bh / 2 - 0.25, max(ys) + bh / 2 + 0.25)
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
        ax.text(x, y, label, ha = "center", va = "center", fontsize = NODE_PT, color = INK, zorder = 4, linespacing = 1.15)

    on_path: Set[Tuple[str, str, str]] = {_edge_id(s.edge) for s in highlight.steps} if highlight else set()
    for e in sorted(graph.edges, key = lambda e: _edge_id(e) in on_path):
        (x1, y1), (x2, y2) = xy[e.subject], xy[e.object]
        span = abs(pos[e.object][1] - pos[e.subject][1])
        default = 0.0 if span <= 1 and abs(x2 - x1) < 0.1 else (0.10 if x2 >= x1 else -0.10) * min(span, 3)
        rad = _route_rad(e.subject, e.object, xy, default, bw, bh, x_bounds)
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
            zorder = 2.6 if hi else 2,  # highlighted path sits above other edges but behind boxes, so it never covers box text
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
        fontsize = OVERVIEW_LEGEND_PT,
        labelcolor = INK2,
        bbox_to_anchor = (0.5, 0.004),
        columnspacing = 1.6,
    )
    fig.text(0.5, 0.988, title, ha = "center", va = "top", fontsize = TITLE_PT, fontweight = "bold", color = INK)
    if subtitle:
        fig.text(0.5, 0.962, subtitle, ha = "center", va = "top", fontsize = SUBTITLE_PT, color = INK2)
    fig.text(0.5, 0.06, "Line width = edge confidence", ha = "center", fontsize = OVERVIEW_LEGEND_PT, color = INK2)
    fig.subplots_adjust(left = 0, right = 1, top = 0.945, bottom = 0.075)
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


def _path_labels(graph: Graph, paths: List[PathResult]) -> List[str]:
    """Label each path by its last step before the outcome; add a second line to break ties."""
    base = [_short(graph, p.node_ids()[-2], 36) for p in paths]
    labels = list(base)
    for i, p in enumerate(paths):
        twins = [j for j, b in enumerate(base) if b == base[i]]
        if len(twins) < 2:
            continue
        ids = p.node_ids()
        for back in range(3, len(ids) + 1):
            mine = ids[-back]
            others = {paths[j].node_ids()[-back] for j in twins if j != i and len(paths[j].node_ids()) >= back}
            if mine not in others:
                labels[i] = f"{base[i]}\n(via {_short(graph, mine, 30)})"
                break
    return labels


def _plural(n: int, word: str) -> str:    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def draw_path_comparison(graph: Graph, paths: List[PathResult], out_path: str, source_name: str, target_name: str) -> None:
    plt = _mpl()
    from matplotlib.patches import Patch

    fig, (a1, a2) = plt.subplots(1, 2, figsize = (17, 6.0), gridspec_kw = {"width_ratios": [1.2, 1]})

    summ = [path_summary(p) for p in paths]
    # Paths are ranked top to bottom; the label is the last step before the outcome
    labels = _path_labels(graph, paths)
    ypos = list(range(len(paths)))[::-1]
    conf = [s["confidence_cost"] for s in summ]
    pen = [s["predicate_penalty"] for s in summ]
    a1.barh(ypos, conf, height = 0.5, color = BLUE, edgecolor = SURFACE, lw = 1.5)
    a1.barh(ypos, pen, height = 0.5, left = conf, color = ORANGE, edgecolor = SURFACE, lw = 1.5)
    for y, s in zip(ypos, summ):
        t = a1.text(s["cost"] + 0.08, y, f'{s["cost"]:.2f}', va = "center", fontsize = LABEL_PT, fontweight = "bold", color = INK)
        rest = f', {_plural(int(s["hops"]), "hop")}, {_plural(int(s["n_hypothesis_edges"]), "hypothesis edge")}'
        a1.annotate(rest, xy = (1, 0.5), xycoords = t, xytext = (0, 0), textcoords = "offset points", va = "center", ha = "left", fontsize = LABEL_PT, color = INK2)
    a1.set_yticks(ypos)
    a1.set_yticklabels(labels)
    a1.set_xlim(0, max(s["cost"] for s in summ) * 1.85)
    a1.set_xlabel("Path Cost (Lower = More Credible Mechanism)", labelpad = 8)
    _panel_header(a1, f"Competing Explanations From {source_name} to {target_name.title()}", "Top-ranked paths, labeled by the last step before the outcome")
    _clean_axes(a1)
    a1.legend(
        handles = [Patch(fc = BLUE, label = "Cost from lower-confidence edges"), Patch(fc = ORANGE, label = "Cost from vague relation types (e.g., enables)")],
        loc = "upper center",
        bbox_to_anchor = (0.5, -0.2),
        ncol = 1,
        frameon = False,
        fontsize = LEGEND_PT,
        labelcolor = INK2,
    )

    conv = convergence(paths)[:9]
    names = [_short(graph, n, 40) for n, _ in conv][::-1]
    vals = [v for _, v in conv][::-1]
    colors = [BLUE if v >= 0.999 else MUTED for v in vals]
    yy = list(range(len(vals)))
    a2.barh(yy, vals, height = 0.5, color = colors, edgecolor = SURFACE, lw = 1.5)
    for y, v in zip(yy, vals):
        a2.text(v + 0.015, y, f"{v:.0%}", va = "center", fontsize = LABEL_PT, color = INK2)
    a2.set_yticks(yy)
    a2.set_yticklabels(names)
    a2.set_xlim(0, 1.12)
    a2.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    a2.set_xlabel("Share of Paths (%)", labelpad = 8)
    _panel_header(a2, f"Share of Top {len(paths)} Paths Through Each Node", "Blue nodes are forced by graph structure")
    _clean_axes(a2)

    fig.tight_layout(w_pad = 3, rect = (0, 0.0, 1, 1))
    _save(fig, out_path)


def draw_evidence_audit(graph: Graph, best: PathResult, out_path: str, source_name: str, target_name: str) -> None:
    plt = _mpl()
    from matplotlib.patches import Patch

    fig, (a1, a2) = plt.subplots(1, 2, figsize = (17, 5.8), gridspec_kw = {"width_ratios": [1, 1.15]})

    counts = evidence_counts(graph)
    levels = EVIDENCE_ORDER[::-1]
    ypos = list(range(len(levels)))
    vals = [counts[l] for l in levels]
    cols = [ORANGE if l == "hypothesis" else BLUE for l in levels]
    a1.barh(ypos, vals, height = 0.5, color = cols, edgecolor = SURFACE, lw = 1.5)
    for y, v in zip(ypos, vals):
        a1.text(v + 0.3, y, str(v) if v else "0 (none yet)", va = "center", fontsize = LABEL_PT, color = INK2 if v else MUTED)
    a1.set_yticks(ypos)
    a1.set_yticklabels([l.replace("_", " ") for l in levels])
    a1.set_xlim(0, 25)
    a1.set_xlabel("Number of Edges", labelpad = 8)
    _panel_header(a1, f'{counts["hypothesis"]} of {len(graph.edges)} Edges Are Hypotheses', "Evidence level per edge, roughly ordered clinical to hypothesis")
    _clean_axes(a1)

    steps = best.steps
    ypos2 = list(range(len(steps)))[::-1]
    w = [s.edge.weight for s in steps]
    cols2 = [ORANGE if is_hypothesis(s.edge) else BLUE for s in steps]
    a2.barh(ypos2, w, height = 0.5, color = cols2, edgecolor = SURFACE, lw = 1.5)
    for y, s in zip(ypos2, steps):
        a2.text(s.edge.weight + 0.015, y, f"{s.edge.weight:.2f}", va = "center", fontsize = LABEL_PT, color = INK2)
    lab = [f"{_short(graph, s.edge.subject, 30)} → {_short(graph, s.edge.object, 30)}" for s in steps]
    a2.set_yticks(ypos2)
    a2.set_yticklabels(lab)
    a2.set_xlim(0, 1.0)
    a2.set_xlabel("Edge Confidence (Weight)", labelpad = 8)
    _panel_header(a2, "Confidence Along the Lowest-Cost Path", "Confident at the root, hypothesis-level at the final step")
    _clean_axes(a2)
    a2.legend(handles = [Patch(fc = BLUE, label = "Supported"), Patch(fc = ORANGE, label = "Hypothesis")], loc = "lower right", frameon = False, fontsize = LEGEND_PT, labelcolor = INK2)

    fig.tight_layout(w_pad = 3)
    _save(fig, out_path)


def _save(fig, out_path: str) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents = True, exist_ok = True)
    fig.savefig(p, dpi = 170)
    import matplotlib.pyplot as plt

    plt.close(fig)






