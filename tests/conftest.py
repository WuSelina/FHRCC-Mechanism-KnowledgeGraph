from pathlib import Path
import pytest
from fhrcc_mechanismkg.io import graph_from_json

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope = "session")
def full_graph():
    return graph_from_json(str(DATA / "fhrcc_pathway_v1.json"))


@pytest.fixture(scope = "session")
def minimal_graph():
    return graph_from_json(str(DATA / "minimal_fh_nrf2.json"))
