from fhrcc_mechanismkg.graph import build_minimal_example_graph


def test_build_minimal_example_graph():
    g = build_minimal_example_graph()
    assert len(g.nodes) > 0
    assert len(g.edges) > 0
