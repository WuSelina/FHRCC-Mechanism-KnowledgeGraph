from __future__ import annotations
from dataclasses import asdict
from typing import Dict, List, Optional
from .graph import Graph
from .schema import Edge
from .reasoning.path_search import edge_cost, DEFAULT_PREDICATE_PENALTY, PathResult


def fmt_node(g: Graph, node_id: str) -> str:
    n = g.nodes.get(node_id)
    if n is None:
        return node_id
    return f"{n.name} [{node_id}]"


def fmt_edge_line(
    g: Graph,
    edge: Edge,
    show_cost: bool = True,
    show_mechanism: bool = False,
    show_notes: bool = False,
) -> str:
    subj = fmt_node(g, edge.subject)
    obj = fmt_node(g, edge.object)

    parts = [f"{subj} --{edge.predicate}--> {obj}", f"w = {edge.weight:.2f}", f"ev = {edge.evidence_level}"]

    if show_cost:
        total = edge_cost(edge, predicate_penalty=DEFAULT_PREDICATE_PENALTY)
        pred_pen = DEFAULT_PREDICATE_PENALTY.get(edge.predicate, 1.0)
        parts.append(f"cost = {total:.3f}")
        parts.append(f"pred_pen = {pred_pen:.2f}")

    line = " (" + ", ".join(parts[1:]) + ")"
    out = parts[0] + line

    extra = []
    if show_mechanism and edge.mechanism:
        extra.append(f"mechanism: {edge.mechanism}")
    if show_notes and edge.notes:
        extra.append(f"notes: {edge.notes}")

    if extra:
        out = out + "\n    - " + "\n    - ".join(extra)

    return out


def path_to_text(
    g: Graph,
    path: PathResult,
    title: Optional[str] = None,
    show_cost: bool = True,
    show_mechanism: bool = False,
    show_notes: bool = False,
) -> str:
    lines: List[str] = []
    if title:
        lines.append(title)
        lines.append("")

    lines.append(f"Total cost: {path.total_cost:.3f}")
    lines.append(f"Hops: {len(path.steps)}")
    lines.append("")

    for i, step in enumerate(path.steps, start=1):
        lines.append(f"{i}. {fmt_edge_line(g, step.edge, show_cost = show_cost, show_mechanism = show_mechanism, show_notes = show_notes)}")

    return "\n".join(lines)


def paths_to_markdown(
    g: Graph,
    paths: List[PathResult],
    header: str,
    show_cost: bool = True,
    show_mechanism: bool = False,
    show_notes: bool = False,
) -> str:
    md: List[str] = [f"# {header}", ""]
    for i, p in enumerate(paths, start=1):
        md.append(f"## Path {i} (cost = {p.total_cost:.3f}, hops = {len(p.steps)})")
        md.append("")
        for j, step in enumerate(p.steps, start = 1):
            md.append(f"{j}. {fmt_edge_line(g, step.edge, show_cost = show_cost, show_mechanism = show_mechanism, show_notes = show_notes)}")
            md.append("")
    return "\n".join(md).rstrip() + "\n"
