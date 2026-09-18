"""Summary statistics and 'so what?' analyses over a knowledge graph."""
from __future__ import annotations
import math
from collections import Counter
from typing import Dict, List, Set, Tuple
from .graph import Graph
from .schema import Edge
from .reasoning.path_search import DEFAULT_PREDICATE_PENALTY, PathResult

# Ordered roughly from strongest to weakest kind of support
EVIDENCE_ORDER: List[str] = [
    "clinical",
    "patient_omics",
    "genetic_perturbation",
    "animal_model",
    "cell_model",
    "biochemical_direct",
    "review_or_consensus",
    "hypothesis",
]

INHIBITORY_PREDICATES = {"inhibits", "inhibits_activity_of", "decreases", "prevents", "destabilizes"}

# Coarse node grouping used for colour (keeps the palette to three categorical slots)
NODE_GROUPS: Dict[str, str] = {
    "gene": "molecular",
    "protein": "molecular",
    "metabolite": "molecular",
    "complex": "molecular",
    "process": "mechanism",
    "state": "mechanism",
    "pathway": "mechanism",
    "compartment": "mechanism",
    "cell_type": "mechanism",
    "phenotype": "phenotype",
    "therapy": "phenotype",
}

GROUP_LABELS: Dict[str, str] = {
    "molecular": "Molecular entity (gene, protein, metabolite)",
    "mechanism": "Mechanism (process, state, pathway)",
    "phenotype": "Phenotype / outcome",
}


def is_hypothesis(edge: Edge) -> bool:
    return edge.evidence_level == "hypothesis"


def is_inhibitory(edge: Edge) -> bool:
    return edge.polarity == "-" or edge.predicate in INHIBITORY_PREDICATES


def cost_parts(edge: Edge) -> Tuple[float, float]:
    """(confidence component, predicate-specificity penalty) - sums to path_search.edge_cost."""
    return -math.log(edge.weight), DEFAULT_PREDICATE_PENALTY.get(edge.predicate, 1.0)


def evidence_counts(graph: Graph) -> Dict[str, int]:
    c = Counter(e.evidence_level for e in graph.edges)
    return {lvl: c.get(lvl, 0) for lvl in EVIDENCE_ORDER}


def edges_into(graph: Graph, node_id: str) -> List[Edge]:
    return graph.incoming(node_id)


def reachable(graph: Graph, source: str, target: str, include_hypothesis: bool) -> bool:
    seen: Set[str] = {source}
    stack = [source]
    while stack:
        u = stack.pop()
        if u == target:
            return True
        for e in graph.outgoing(u):
            if not include_hypothesis and is_hypothesis(e):
                continue
            if e.object not in seen:
                seen.add(e.object)
                stack.append(e.object)
    return False


def path_summary(path: PathResult) -> Dict[str, float]:
    parts = [cost_parts(s.edge) for s in path.steps]
    conf = sum(p[0] for p in parts)
    pen = sum(p[1] for p in parts)
    weakest = max(path.steps, key = lambda s: sum(cost_parts(s.edge)))
    return {
        "cost": path.total_cost,
        "hops": len(path.steps),
        "confidence_cost": conf,
        "predicate_penalty": pen,
        "n_hypothesis_edges": sum(is_hypothesis(s.edge) for s in path.steps),
        "weakest_edge_cost": sum(cost_parts(weakest.edge)),
        "weakest_edge_share": sum(cost_parts(weakest.edge)) / path.total_cost if path.total_cost else 0.0,
    }


def convergence(paths: List[PathResult]) -> List[Tuple[str, float]]:
    """Fraction of the given paths passing through each intermediate node (endpoints excluded)."""
    counts: Counter = Counter()
    for p in paths:
        ids = p.node_ids()
        for n in set(ids[1:-1]):
            counts[n] += 1
    total = max(len(paths), 1)
    return sorted(((n, c / total) for n, c in counts.items()), key = lambda t: (-t[1], t[0]))
