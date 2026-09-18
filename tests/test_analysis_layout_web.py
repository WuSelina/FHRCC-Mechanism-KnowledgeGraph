import pytest
from fhrcc_mechanismkg import web
from fhrcc_mechanismkg.analysis import convergence, evidence_counts, path_summary, reachable
from fhrcc_mechanismkg.graph import Graph
from fhrcc_mechanismkg.layout import assign_layers, layered_layout
from fhrcc_mechanismkg.reasoning.path_search import k_shortest_paths_explainable
from fhrcc_mechanismkg.schema import Edge, Node


def _chain(evidence_mid: str) -> Graph:
    g = Graph()
    for n in "ABC":
        g.add_node(Node(id = f"gene:{n}", type = "gene", name = n))
    g.add_edge(Edge(subject = "gene:A", predicate = "causes", object = "gene:B", weight = 0.9, evidence_level = "cell_model"))
    g.add_edge(Edge(subject = "gene:B", predicate = "causes", object = "gene:C", weight = 0.9, evidence_level = evidence_mid))
    g.add_edge(Edge(subject = "gene:C", predicate = "decreases", object = "gene:A", weight = 0.5, evidence_level = "hypothesis"))
    return g


def test_reachable_respects_hypothesis_flag():
    assert reachable(_chain("hypothesis"), "gene:A", "gene:C", include_hypothesis = True)
    assert not reachable(_chain("hypothesis"), "gene:A", "gene:C", include_hypothesis = False)
    assert reachable(_chain("cell_model"), "gene:A", "gene:C", include_hypothesis = False)


def test_evidence_counts_cover_all_edges(full_graph):
    assert sum(evidence_counts(full_graph).values()) == len(full_graph.edges)


def test_path_summary_components_add_up(full_graph):
    p = k_shortest_paths_explainable(full_graph, "gene:FH", "phenotype:cancer", k = 1, max_hops = 14)[0]
    s = path_summary(p)
    assert s["confidence_cost"] + s["predicate_penalty"] == pytest.approx(s["cost"])
    assert 0 < s["weakest_edge_share"] <= 1


def test_convergence_excludes_endpoints(full_graph):
    paths = k_shortest_paths_explainable(full_graph, "gene:FH", "phenotype:cancer", k = 6, max_hops = 14)
    shared = dict(convergence(paths))
    assert shared["metabolite:fumarate"] == 1.0
    assert "gene:FH" not in shared and "phenotype:cancer" not in shared


def test_layout_ignores_feedback_and_places_every_node():
    g = _chain("cell_model")
    layers = assign_layers(g)
    assert layers["gene:A"] < layers["gene:B"] < layers["gene:C"]
    assert set(layered_layout(g)) == set(g.nodes)


def test_layout_is_deterministic_and_mostly_forward(full_graph):
    a, b = layered_layout(full_graph), layered_layout(full_graph)
    assert a == b
    forward = sum(a[e.subject][1] < a[e.object][1] for e in full_graph.edges)
    assert forward / len(full_graph.edges) > 0.9


def test_web_payload_and_html(full_graph, tmp_path):
    payload = web.build_payload(full_graph, "gene:FH")
    assert len(payload["nodes"]) == len(full_graph.nodes)
    assert len(payload["edges"]) == len(full_graph.edges)
    edge_ids = {e["id"] for e in payload["edges"]}
    for paths in payload["paths"].values():
        for p in paths:
            assert set(p["edges"]) <= edge_ids
    out = tmp_path / "index.html"
    web.write_explorer(full_graph, str(out), "gene:FH")
    html = out.read_text(encoding = "utf-8")
    assert "cytoscape" in html and "__DATA__" not in html
    assert html.count("</script>") == 3  # data, cytoscape, app: nothing in the data closes a script early


def test_static_figures_render(full_graph, tmp_path):
    pytest.importorskip("matplotlib")
    from fhrcc_mechanismkg import viz

    paths = k_shortest_paths_explainable(full_graph, "gene:FH", "phenotype:cancer", k = 4, max_hops = 14)
    viz.draw_overview(full_graph, str(tmp_path / "o.png"), highlight = paths[0], title = "t")
    viz.draw_path_comparison(full_graph, paths, str(tmp_path / "p.png"), "FH", "Cancer")
    viz.draw_evidence_audit(full_graph, paths[0], str(tmp_path / "e.png"), "FH", "Cancer")
    assert all((tmp_path / f).stat().st_size > 10_000 for f in ("o.png", "p.png", "e.png"))
