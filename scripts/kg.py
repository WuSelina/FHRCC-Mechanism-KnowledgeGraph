import argparse
from pathlib import Path
from fhrcc_mechanismkg.io import graph_from_json
from fhrcc_mechanismkg.reasoning.path_search import (
    shortest_path_explainable,
    k_shortest_paths_explainable,
)
from fhrcc_mechanismkg.reporting import path_to_text, paths_to_markdown
from collections import Counter


def cmd_validate(args):
    graph_from_json(args.graph)
    print(f"OK: graph validated successfully -> {args.graph}")


def divider(title = None, char = "=", width = 80):
    if title:
        t = f" {title} "
        if len(t) >= width:
            return t
        left = (width - len(t)) // 2
        right = width - len(t) - left
        return (char * left) + t + (char * right)
    return char * width


def cmd_find(args):
    g = graph_from_json(args.graph)
    keyword = (args.keyword or "").lower()
    node_type = args.type.lower() if args.type else None

    hits = []
    for n in g.nodes.values():
        if node_type and n.type != node_type:
            continue
        hay = " ".join([n.id, n.name] + (n.synonyms or []) + ([n.description] if n.description else [])).lower()
        if not keyword or keyword in hay:
            hits.append(n)

    hits.sort(key = lambda x: (x.type, x.id))
    print(f"Matches: {len(hits)}")
    for n in hits:
        syn = f" | syn = {','.join(n.synonyms)}" if n.synonyms else ""
        print(f"{n.id}\t{n.type}\t{n.name}{syn}")


def cmd_explain(args):
    g = graph_from_json(args.graph)

    paths = k_shortest_paths_explainable(
        g,
        source = args.source,
        target = args.target,
        k = args.k,
        max_hops = args.max_hops,
    )

    if not paths:
        raise SystemExit("No paths found.")

    # Print best path nicely
    best = paths[0]
    print(divider("BEST PATH"))
    print(path_to_text(
        g,
        best,
        title = f"{args.source} -> {args.target}",
        show_cost = not args.no_cost,
        show_mechanism = args.verbose,
        show_notes = args.verbose,
    ))
    print("")

    # Print top-k summary
    print(divider(f"TOP {len(paths)} PATHS (SUMMARY)", char = "-"))
    for i, p in enumerate(paths, start=1):
        node_ids = p.node_ids()
        start_id = node_ids[0] if node_ids else args.source
        end_id = node_ids[-1] if node_ids else args.target
        print(f"[{i:02d}] cost = {p.total_cost:.3f} | hops = {len(p.steps):02d} | {start_id} -> {end_id}")

    # Optional: save Markdown report
    if args.out_md:
        out_path = Path(args.out_md)
        out_path.parent.mkdir(parents = True, exist_ok = True)

        header = f"Explainable paths: {args.source} -> {args.target}"
        md = paths_to_markdown(
            g,
            paths = paths,
            header = header,
            show_cost = not args.no_cost,
            show_mechanism = args.verbose,
            show_notes = args.verbose,
        )
        out_path.write_text(data = md, encoding = "utf-8")
        print("")
        print(divider("OUTPUT REPORT", char = "-"))
        print(f"{out_path}")


def cmd_summarize(args):
    g = graph_from_json(args.graph)

    print(f"Graph: {args.graph}")
    print(f"n_nodes = {len(g.nodes)} n_edges = {len(g.edges)}\n")

    type_counts = Counter([n.type for n in g.nodes.values()])
    print("Nodes by type:")
    for t, c in sorted(type_counts.items(), key = lambda x: (-x[1], x[0])):
        print(f"  {t}\t{c}")
    print("")

    pred_counts = Counter([e.predicate for e in g.edges])
    print("Edges by predicate:")
    for p, c in sorted(pred_counts.items(), key = lambda x: (-x[1], x[0])):
        print(f"  {p}\t{c}")
    print("")

    ev_counts = Counter([e.evidence_level for e in g.edges])
    print("Edges by evidence_level:")
    for ev, c in sorted(ev_counts.items(), key = lambda x: (-x[1], x[0])):
        print(f"  {ev}\t{c}")


def cmd_lint(args):
    # Reuse the standalone lint script logic by importing it is overkill; keep simple:
    import subprocess, sys
    r = subprocess.run([sys.executable, "scripts/lint_graph.py", args.graph])
    raise SystemExit(r.returncode)


def build_parser():
    p = argparse.ArgumentParser(prog = "kg", description = "FHRCC_mechanismKG CLI")
    sub = p.add_subparsers(dest = "cmd", required = True)

    p_val = sub.add_parser("validate", help = "Validate a KG JSON file")
    p_val.add_argument("graph")
    p_val.set_defaults(func = cmd_validate)

    p_find = sub.add_parser("find", help = "Find nodes by keyword (optional) and type (optional)")
    p_find.add_argument("graph")
    p_find.add_argument("keyword", nargs = "?", default = None)
    p_find.add_argument("--type", default = None, help = "Filter by node type (e.g., state, pathway, phenotype)")
    p_find.set_defaults(func = cmd_find)

    p_exp = sub.add_parser("explain", help = "Explainable top-k paths from source to target")
    p_exp.add_argument("graph")
    p_exp.add_argument("source")
    p_exp.add_argument("target")
    p_exp.add_argument("-k", type = int, default = 5)
    p_exp.add_argument("--max-hops", type = int, default = 12)
    p_exp.add_argument("--out-md", default = None, help = "Write a Markdown report to this path")
    p_exp.add_argument("--no-cost", action = "store_true", help = "Hide per-edge cost/penalty components")
    p_exp.add_argument("--verbose", action = "store_true", help = "Include mechanism/notes when available")
    p_exp.set_defaults(func = cmd_explain)

    p_sum = sub.add_parser("summarize", help ="Print summary counts")
    p_sum.add_argument("graph")
    p_sum.set_defaults(func = cmd_summarize)

    p_lint = sub.add_parser("lint", help = "Run lint warnings")
    p_lint.add_argument("graph")
    p_lint.set_defaults(func = cmd_lint)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
