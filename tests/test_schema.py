import pytest
from fhrcc_mechanismkg.schema import Edge, Node


def test_node_id_must_have_type_prefix():
    with pytest.raises(ValueError):
        Node(id = "FH", type = "gene", name = "FH")


def test_node_id_prefix_must_match_type():
    with pytest.raises(ValueError):
        Node(id = "protein:FH", type = "gene", name = "FH")


@pytest.mark.parametrize("w", [0.0, 0.005, 1.0, 1.5, -0.2])
def test_edge_weight_out_of_range(w):
    with pytest.raises(ValueError):
        Edge(subject = "gene:A", predicate = "causes", object = "gene:B", weight = w, evidence_level = "hypothesis")


def test_edge_self_loop_rejected():
    with pytest.raises(ValueError):
        Edge(subject = "gene:A", predicate = "causes", object = "gene:A", weight = 0.5, evidence_level = "hypothesis")


def test_valid_edge():
    e = Edge(subject = "gene:A", predicate = "causes", object = "gene:B", weight = 0.5, evidence_level = "hypothesis")
    assert e.citations == [] and e.polarity is None
