import math
import pytest
from fhrcc_mechanismkg.graph import Graph
from fhrcc_mechanismkg.reasoning.path_search import (
    edge_cost,
    k_shortest_paths_explainable,
    shortest_path_explainable,
)
from fhrcc_mechanismkg.schema import Edge, Node


def _toy() -> Graph:
    g = Graph()
    for n in "ABCD":
        g.add_node(Node(id = f"gene:{n}", type = "gene", name = n))

    def add(s, o, w, p = "causes"):
        g.add_edge(Edge(subject = f"gene:{s}", predicate = p, object = f"gene:{o}", weight = w, evidence_level = "hypothesis"))

    add("A", "B", 0.9)
    add("B", "D", 0.9)
    add("A", "C", 0.5)
    add("C", "D", 0.5)
    add("D", "A", 0.9)  # cycle back
    return g


def test_edge_cost_formula():
    e = Edge(subject = "gene:A", predicate = "enables", object = "gene:B", weight = 0.5, evidence_level = "hypothesis")
    assert edge_cost(e) == pytest.approx(-math.log(0.5) + 0.8)


def test_vague_predicates_cost_more():
    a = Edge(subject = "gene:A", predicate = "causes", object = "gene:B", weight = 0.6, evidence_level = "hypothesis")
    b = Edge(subject = "gene:A", predicate = "associates_with", object = "gene:B", weight = 0.6, evidence_level = "hypothesis")
    assert edge_cost(a) < edge_cost(b)


def test_higher_confidence_is_cheaper():
    best = shortest_path_explainable(_toy(), "gene:A", "gene:D")
    assert best.node_ids() == ["gene:A", "gene:B", "gene:D"]


def test_k_paths_sorted_simple_and_complete():
    paths = k_shortest_paths_explainable(_toy(), "gene:A", "gene:D", k = 5)
    assert [p.node_ids() for p in paths] == [
        ["gene:A", "gene:B", "gene:D"],
        ["gene:A", "gene:C", "gene:D"],
    ]
    assert [p.total_cost for p in paths] == sorted(p.total_cost for p in paths)
    for p in paths:
        ids = p.node_ids()
        assert len(ids) == len(set(ids)), "path revisits a node"


def test_max_hops_respected_and_bad_nodes_raise():
    g = _toy()
    with pytest.raises(ValueError):
        shortest_path_explainable(g, "gene:A", "gene:D", max_hops = 1)
    with pytest.raises(ValueError):
        shortest_path_explainable(g, "gene:A", "gene:Z")


def test_k_nonpositive_returns_empty():
    assert k_shortest_paths_explainable(_toy(), "gene:A", "gene:D", k = 0) == []


def test_real_graph_top_paths(full_graph):
    paths = k_shortest_paths_explainable(full_graph, "gene:FH", "phenotype:cancer", k = 5, max_hops = 14)
    assert len(paths) == 5
    assert paths[0].node_ids()[0] == "gene:FH"
    assert paths[0].node_ids()[-1] == "phenotype:cancer"
    best = shortest_path_explainable(full_graph, "gene:FH", "phenotype:cancer", max_hops = 14)
    assert best.total_cost == pytest.approx(paths[0].total_cost)
