import sys
from collections import Counter

from fhrcc_mechanismkg.io import graph_from_json


def main():
    if len(sys.argv) != 2:
        print("Usage: python summarize_graph.py <graph.json>")
        sys.exit(1)

    path = sys.argv[1]
    g = graph_from_json(path)

    print(f"Graph: {path}")
    print(f"n_nodes={len(g.nodes)} n_edges={len(g.edges)}")
    print()

    # Nodes by type
    type_counts = Counter([n.type for n in g.nodes.values()])
    print("Nodes by type:")
    for t, c in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {t}\t{c}")
    print()

    # Edges by predicate
    pred_counts = Counter([e.predicate for e in g.edges])
    print("Edges by predicate:")
    for p, c in sorted(pred_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {p}\t{c}")
    print()

    # Edges by evidence level
    ev_counts = Counter([e.evidence_level for e in g.edges])
    print("Edges by evidence_level:")
    for ev, c in sorted(ev_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {ev}\t{c}")
    print()

    # Degree (directed)
    outdeg = Counter()
    indeg = Counter()
    for e in g.edges:
        outdeg[e.subject] += 1
        indeg[e.object] += 1

    def top_k(counter, k=10):
        return sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:k]

    print("Top outgoing hubs (subject out-degree):")
    for node_id, c in top_k(outdeg, k=10):
        name = g.nodes[node_id].name if node_id in g.nodes else node_id
        print(f"  {node_id}\t{c}\t{name}")
    print()

    print("Top incoming hubs (object in-degree):")
    for node_id, c in top_k(indeg, k=10):
        name = g.nodes[node_id].name if node_id in g.nodes else node_id
        print(f"  {node_id}\t{c}\t{name}")
    print()


if __name__ == "__main__":
    main()
