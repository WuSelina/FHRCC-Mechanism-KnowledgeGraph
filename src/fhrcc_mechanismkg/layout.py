"""Dependency-free layered (top-to-bottom) layout for a directed, possibly cyclic graph."""
from __future__ import annotations
from collections import Counter
from typing import Dict, List, Set, Tuple
from .graph import Graph


def _scc_ids(graph: Graph) -> Dict[str, int]:
    """Tarjan's strongly connected components; returns {node: component id}."""
    out: Dict[str, List[str]] = {n: [] for n in graph.nodes}
    for e in graph.edges:
        out[e.subject].append(e.object)
    index: Dict[str, int] = {}
    low: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    comp: Dict[str, int] = {}
    counter = [0]

    def strong(u: str) -> None:
        index[u] = low[u] = counter[0]
        counter[0] += 1
        stack.append(u)
        on_stack.add(u)
        for v in out[u]:
            if v not in index:
                strong(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:
                low[u] = min(low[u], index[v])
        if low[u] == index[u]:
            cid = len(set(comp.values()))
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp[w] = cid
                if w == u:
                    break

    for n in graph.nodes:
        if n not in index:
            strong(n)
    return comp


def _depths(graph: Graph) -> Dict[str, int]:
    """Shortest-hop depth from the graph's source nodes (BFS)."""
    indeg = Counter(e.object for e in graph.edges)
    frontier = [n for n in graph.nodes if indeg[n] == 0] or list(graph.nodes)[:1]
    depth = {n: 0 for n in frontier}
    while frontier:
        nxt = []
        for u in frontier:
            for e in graph.outgoing(u):
                if e.object not in depth:
                    depth[e.object] = depth[u] + 1
                    nxt.append(e.object)
        frontier = nxt
    return depth


def _dag_edge_indices(graph: Graph) -> Set[int]:
    """Edges kept after reversing feedback loops.

    Only edges inside a cycle (same strongly connected component) are candidates: those that
    point back toward a node reachable in fewer hops from the sources are treated as feedback
    and ignored when layering, so a causal chain is not stretched by its own negative feedback.
    """
    comp = _scc_ids(graph)
    depth = _depths(graph)
    drop: Set[int] = set()
    for i, e in enumerate(graph.edges):
        if comp[e.subject] == comp[e.object] and depth.get(e.object, 0) <= depth.get(e.subject, 0):
            drop.add(i)
    return {i for i in range(len(graph.edges)) if i not in drop}


def assign_layers(graph: Graph) -> Dict[str, int]:
    keep = _dag_edge_indices(graph)
    preds: Dict[str, List[str]] = {n: [] for n in graph.nodes}
    succs: Dict[str, List[str]] = {n: [] for n in graph.nodes}
    for i in keep:
        e = graph.edges[i]
        preds[e.object].append(e.subject)
        succs[e.subject].append(e.object)

    # Longest-path layering via Kahn's algorithm
    remaining = {n: len(preds[n]) for n in graph.nodes}
    ready = [n for n in graph.nodes if remaining[n] == 0]
    layer: Dict[str, int] = {n: 0 for n in graph.nodes}
    topo: List[str] = []
    while ready:
        u = ready.pop(0)
        topo.append(u)
        for v in succs[u]:
            layer[v] = max(layer[v], layer[u] + 1)
            remaining[v] -= 1
            if remaining[v] == 0:
                ready.append(v)

    # Tighten: slide nodes along their slack to shorten edges (out >= in -> late, else early)
    for _ in range(4):
        for u in reversed(topo):
            lo = max((layer[p] + 1 for p in preds[u]), default=None)
            hi = min((layer[s] - 1 for s in succs[u]), default=None)
            if lo is None and hi is None:
                continue
            if len(succs[u]) >= len(preds[u]) and hi is not None:
                layer[u] = max(hi, lo if lo is not None else hi)
            elif lo is not None:
                layer[u] = min(lo, hi if hi is not None else lo)
    base = min(layer.values())
    return {n: l - base for n, l in layer.items()}


def layered_layout(graph: Graph, sweeps: int = 8) -> Dict[str, Tuple[float, float]]:
    """Return {node_id: (x, y)}; y is the layer index (0 = top), x is centred within the layer."""
    layer = assign_layers(graph)
    n_layers = max(layer.values()) + 1 if layer else 0
    rows: List[List[str]] = [[] for _ in range(n_layers)]
    for n in graph.nodes:
        rows[layer[n]].append(n)

    nbrs: Dict[str, List[str]] = {n: [] for n in graph.nodes}
    for e in graph.edges:
        nbrs[e.subject].append(e.object)
        nbrs[e.object].append(e.subject)

    x: Dict[str, float] = {}

    def recentre(row: List[str]) -> None:
        for i, n in enumerate(row):
            x[n] = i - (len(row) - 1) / 2

    for row in rows:
        recentre(row)

    def reorder(row: List[str], above: bool) -> None:
        def key(n: str) -> float:
            ns = [x[m] for m in nbrs[n] if (layer[m] < layer[n]) == above and layer[m] != layer[n]]
            return sum(ns) / len(ns) if ns else x[n]
        row.sort(key = key)
        recentre(row)

    for _ in range(sweeps):
        for row in rows[1:]:
            reorder(row, above = True)
        for row in reversed(rows[:-1]):
            reorder(row, above = False)

    return {n: (x[n], float(layer[n])) for n in graph.nodes}
