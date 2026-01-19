from __future__ import annotations
import heapq
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from ..graph import Graph
from ..schema import Edge


DEFAULT_PREDICATE_PENALTY: Dict[str, float] = {
    # Prefer specific, mechanistic predicates
    "causes": 0.0,
    "converts_to": 0.0,
    "accumulates": 0.1,
    "inhibits_activity_of": 0.1,
    "modifies": 0.2,
    "binds": 0.3,
    "translocates_to": 0.3,
    "activates": 0.4,
    "inhibits": 0.4,
    "stabilizes": 0.4,
    "destabilizes": 0.4,
    "increases": 0.6,
    "decreases": 0.6,
    "enables": 0.8,
    "prevents": 0.8,
    # Discouraged (association without a mechanism)
    "associates_with": 2.0,
}


@dataclass(frozen=True)
class PathStep:
    edge: Edge

    def to_text(self) -> str:
        w = f"{self.edge.weight:.2f}"
        return f"{self.edge.subject} --{self.edge.predicate}--> {self.edge.object} (w = {w}, ev = {self.edge.evidence_level})"


@dataclass(frozen=True)
class PathResult:
    total_cost: float
    steps: List[PathStep]

    def node_ids(self) -> List[str]:
        if not self.steps:
            return []
        ids = [self.steps[0].edge.subject]
        ids.extend([s.edge.object for s in self.steps])
        return ids


def edge_cost(edge: Edge, predicate_penalty: Optional[Dict[str, float]] = None) -> float:
    """
    Convert an edge into an additive cost for shortest-path search.
    - Higher confidence (weight closer to 1) should reduce cost.
    - Less specific predicates should add penalty.
    """
    penalty = (predicate_penalty or DEFAULT_PREDICATE_PENALTY).get(edge.predicate, 1.0)

    # Avoid infinities. Weight is already constrained to [0.01, 0.99].
    weight_component = -math.log(edge.weight)

    return weight_component + penalty


def shortest_path_explainable(
    graph: Graph,
    source: str,
    target: str,
    max_hops: int = 6,
    predicate_penalty: Optional[Dict[str, float]] = None,
) -> PathResult:
    """
    Dijkstra-style search over directed edges with an interpretable cost function.
    Returns the single best path (lowest cost).
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node not found: {source}")
    if target not in graph.nodes:
        raise ValueError(f"Target node not found: {target}")
    if source == target:
        return PathResult(total_cost=0.0, steps=[])

    # Priority queue items: (cost, hops, current_node)
    pq: List[Tuple[float, int, str]] = [(0.0, 0, source)]
    best_cost: Dict[Tuple[str, int], float] = {(source, 0): 0.0}
    backptr: Dict[Tuple[str, int], Tuple[Tuple[str, int], Edge]] = {}

    while pq:
        cost, hops, node_id = heapq.heappop(pq)

        if hops > max_hops:
            continue

        if node_id == target:
            # Reconstruct using the best hops state that reached target (this one)
            return _reconstruct_path(backptr, (node_id, hops), cost)

        # Expand outgoing edges
        for e in graph.outgoing(node_id):
            nhops = hops + 1
            if nhops > max_hops:
                continue

            ncost = cost + edge_cost(e, predicate_penalty=predicate_penalty)
            state = (e.object, nhops)

            if ncost < best_cost.get(state, float("inf")):
                best_cost[state] = ncost
                backptr[state] = ((node_id, hops), e)
                heapq.heappush(pq, (ncost, nhops, e.object))

    raise ValueError(f"No path found from {source} to {target} within max_hops = {max_hops}")


def k_shortest_paths_explainable(
    graph: Graph,
    source: str,
    target: str,
    k: int = 5,
    max_hops: int = 6,
    predicate_penalty: Optional[Dict[str, float]] = None,
) -> List[PathResult]:
    """
    Enumerate up to k paths using a best-first search over partial paths.
    """
    if k <= 0:
        return []

    if source not in graph.nodes:
        raise ValueError(f"Source node not found: {source}")
    if target not in graph.nodes:
        raise ValueError(f"Target node not found: {target}")

    # Each queue item is: (total_cost, current_node, path_edges, visited_nodes)
    pq: List[Tuple[float, str, List[Edge], Tuple[str, ...]]] = [(0.0, source, [], (source,))]
    results: List[PathResult] = []

    while pq and len(results) < k:
        cost, node_id, path_edges, visited = heapq.heappop(pq)

        if len(path_edges) > max_hops:
            continue

        if node_id == target:
            results.append(PathResult(total_cost = cost, steps = [PathStep(e) for e in path_edges]))
            continue

        for e in graph.outgoing(node_id):
            if e.object in visited:
                continue  # prevent cycles
            ncost = cost + edge_cost(e, predicate_penalty = predicate_penalty)
            heapq.heappush(pq, (ncost, e.object, path_edges + [e], visited + (e.object,)))

    return results


def _reconstruct_path(
    backptr: Dict[Tuple[str, int], Tuple[Tuple[str, int], Edge]],
    end_state: Tuple[str, int],
    total_cost: float,
) -> PathResult:
    steps: List[Edge] = []
    state = end_state

    while state in backptr:
        prev_state, edge = backptr[state]
        steps.append(edge)
        state = prev_state

    steps.reverse()
    return PathResult(total_cost = total_cost, steps = [PathStep(e) for e in steps])
