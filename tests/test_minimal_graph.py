import json
from pathlib import Path
import pytest
from fhrcc_mechanismkg.graph import Graph, build_minimal_example_graph
from fhrcc_mechanismkg.io import graph_from_dict, graph_from_json, graph_to_dict, graph_to_json
from fhrcc_mechanismkg.schema import Edge, Node


def test_build_minimal_example_graph():
    g = build_minimal_example_graph()
    assert len(g.nodes) > 0
    assert len(g.edges) > 0


def test_duplicate_node_rejected():
    g = Graph()
    g.add_node(Node(id = "gene:A", type = "gene", name = "A"))
    with pytest.raises(ValueError):
        g.add_node(Node(id = "gene:A", type = "gene", name = "A again"))


def test_edge_requires_existing_nodes():
    g = Graph()
    g.add_node(Node(id = "gene:A", type = "gene", name = "A"))
    with pytest.raises(ValueError):
        g.add_edge(Edge(subject = "gene:A", predicate = "causes", object = "gene:B", weight = 0.5, evidence_level = "hypothesis"))


def test_roundtrip_preserves_graph(tmp_path):
    g = build_minimal_example_graph()
    p = tmp_path / "g.json"
    graph_to_json(g, str(p))
    assert graph_to_dict(g) == graph_to_dict(graph_from_json(str(p)))


def test_missing_required_edge_field_raises():
    payload = graph_to_dict(build_minimal_example_graph())
    del payload["edges"][0]["weight"]
    with pytest.raises(KeyError):
        graph_from_dict(payload)


@pytest.mark.parametrize("fixture", ["full_graph", "minimal_graph"])
def test_shipped_data_has_no_isolated_nodes(fixture, request):
    g = request.getfixturevalue(fixture)
    touched = {e.subject for e in g.edges} | {e.object for e in g.edges}
    assert len(g.edges) > 5
    assert set(g.nodes) == touched


def test_shipped_data_is_plain_json():
    for p in (Path(__file__).resolve().parents[1] / "data").glob("*.json"):
        json.loads(p.read_text(encoding = "utf-8"))
