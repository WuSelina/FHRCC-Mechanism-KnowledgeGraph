import sys
from fhrcc_mechanismkg.io import graph_from_json
from fhrcc_mechanismkg.reasoning.path_search import (
    shortest_path_explainable,
    k_shortest_paths_explainable,
    edge_cost,
    DEFAULT_PREDICATE_PENALTY,
)


def fmt_node(g, node_id):
    n = g.nodes.get(node_id)
    if n is None:
        return node_id
    return f"{n.name} [{node_id}]"


def fmt_edge(g, edge):
    subj = fmt_node(g, edge.subject)
    obj = fmt_node(g, edge.object)
    w = f"{edge.weight:.2f}"

    # cost decomposition (weight component + predicate penalty)
    total = edge_cost(edge, predicate_penalty = DEFAULT_PREDICATE_PENALTY)
    pred_pen = DEFAULT_PREDICATE_PENALTY.get(edge.predicate, 1.0)

    return (
        f"{subj} --{edge.predicate}--> {obj} "
        f"(w = {w}, ev = {edge.evidence_level}, cost = {total:.3f}, pred_pen = {pred_pen:.2f})"
    )


def main():
    if len(sys.argv) < 4:
        print("Usage: python explain_path.py <graph.json> <source_node_id> <target_node_id> [k] [max_hops]")
        sys.exit(1)

    graph_path = sys.argv[1]
    source = sys.argv[2]
    target = sys.argv[3]
    k = int(sys.argv[4]) if len(sys.argv) >= 5 else 5
    max_hops = int(sys.argv[5]) if len(sys.argv) >= 6 else 6

    g = graph_from_json(graph_path)

    print(f"Graph loaded: n_nodes = {len(g.nodes)} n_edges = {len(g.edges)}")
    print()

    best = shortest_path_explainable(g, source=source, target = target, max_hops = max_hops)
    print(f"Best path cost: {best.total_cost:.3f}")
    for step in best.steps:
        print(fmt_edge(g, step.edge))
    print()

    paths = k_shortest_paths_explainable(g, source = source, target = target, k = k, max_hops = max_hops)
    print(f"Top {len(paths)} paths:")
    for i, p in enumerate(paths, start=1):
        node_str = " -> ".join([fmt_node(g, nid) for nid in p.node_ids()])
        print(f"[{i}] cost = {p.total_cost:.3f} hops = {len(p.steps)} nodes = {node_str}")
    print()


if __name__ == "__main__":
    main()
