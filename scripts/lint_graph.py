import sys
from collections import Counter, defaultdict

from fhrcc_mechanismkg.io import graph_from_json


def main():
    if len(sys.argv) != 2:
        print("Usage: python lint_graph.py <graph.json>")
        sys.exit(1)

    path = sys.argv[1]
    g = graph_from_json(path)

    warnings = []

    # 1) Predicate overuse
    pred_counts = Counter([e.predicate for e in g.edges])
    n_edges = len(g.edges)

    for pred in ["associates_with", "enables"]:
        frac = pred_counts.get(pred, 0) / max(n_edges, 1)
        if frac >= 0.35:
            warnings.append(f"High usage of predicate '{pred}': {pred_counts.get(pred, 0)}/{n_edges} ({frac:.1%}). Consider adding more specific intermediates/predicates.")

    # 2) Hypothesis edges with high weight
    for e in g.edges:
        if e.evidence_level == "hypothesis" and e.weight >= 0.70:
            warnings.append(f"Hypothesis edge has high weight (>=0.70): {e.subject} --{e.predicate}--> {e.object} (w = {e.weight:.2f}).")

    # 3) High-weight edges missing mechanism
    for e in g.edges:
        if e.weight >= 0.70 and (e.mechanism is None or str(e.mechanism).strip() == ""):
            warnings.append(f"High-weight edge missing mechanism: {e.subject} --{e.predicate}--> {e.object} (w = {e.weight:.2f}).")

    # 4) Dangling nodes (degree zero)
    indeg = Counter()
    outdeg = Counter()
    for e in g.edges:
        outdeg[e.subject] += 1
        indeg[e.object] += 1

    for node_id in g.nodes:
        if indeg.get(node_id, 0) == 0 and outdeg.get(node_id, 0) == 0:
            warnings.append(f"Isolated node (no edges): {node_id}")

    # 5) Potential contradictions: same subject/object with both activates and inhibits (without notes)
    pairs = defaultdict(list)
    for e in g.edges:
        key = (e.subject, e.object)
        pairs[key].append(e)

    for (subj, obj), edges in pairs.items():
        preds = {e.predicate for e in edges}
        if "activates" in preds and "inhibits" in preds:
            warnings.append(f"Potential contradiction: both activates and inhibits present for {subj} -> {obj}. Add notes/mechanism or refine nodes.")

    if warnings:
        print(f"LINT WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"- {w}")
        sys.exit(0)

    print("OK: no lint warnings")


if __name__ == "__main__":
    main()
