import sys
from fhrcc_mechanismkg.io import graph_from_json


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_nodes.py <graph.json> [keyword] [type]")
        print("Examples:")
        print("  python find_nodes.py data\\fhrcc_pathway_v1.json fumar")
        print("  python find_nodes.py data\\fhrcc_pathway_v1.json hypox state")
        sys.exit(1)

    graph_path = sys.argv[1]
    keyword = sys.argv[2].lower() if len(sys.argv) >= 3 else None
    node_type = sys.argv[3].lower() if len(sys.argv) >= 4 else None

    g = graph_from_json(graph_path)

    hits = []
    for n in g.nodes.values():
        if node_type is not None and n.type != node_type:
            continue

        hay = " ".join(
            [n.id, n.name] + (n.synonyms or []) + ([n.description] if n.description else [])
        ).lower()

        if keyword is None or keyword in hay:
            hits.append(n)

    hits.sort(key = lambda x: (x.type, x.id))

    print(f"Matches: {len(hits)}")
    for n in hits:
        syn = f" | syn = {','.join(n.synonyms)}" if n.synonyms else ""
        print(f"{n.id}\t{n.type}\t{n.name}{syn}")


if __name__ == "__main__":
    main()
