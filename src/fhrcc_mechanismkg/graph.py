from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Iterable, Optional
from .schema import Node, Edge


@dataclass
class Graph:
    nodes: Dict[str, Node] = field(default_factory = dict)
    edges: List[Edge] = field(default_factory = list)

    def add_node(self, node: Node) -> None:
        if node.id in self.nodes:
            raise ValueError(f'Duplicate node id: {node.id}')
        self.nodes[node.id] = node

    def add_nodes(self, nodes: Iterable[Node]) -> None:
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: Edge) -> None:
        if edge.subject not in self.nodes:
            raise ValueError(f'Edge subject node not found: {edge.subject}')
        if edge.object not in self.nodes:
            raise ValueError(f'Edge object node not found: {edge.object}')
        self.edges.append(edge)

    def add_edges(self, edges: Iterable[Edge]) -> None:
        for edge in edges:
            self.add_edge(edge)

    def get_node(self, node_id: str) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError as e:
            raise KeyError(f'Node not found: {node_id}') from e

    def outgoing(self, node_id: str) -> List[Edge]:
        return [e for e in self.edges if e.subject == node_id]

    def incoming(self, node_id: str) -> List[Edge]:
        return [e for e in self.edges if e.object == node_id]

    def find_edges(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[str] = None,
    ) -> List[Edge]:
        hits = self.edges
        if subject is not None:
            hits = [e for e in hits if e.subject == subject]
        if predicate is not None:
            hits = [e for e in hits if e.predicate == predicate]
        if object is not None:
            hits = [e for e in hits if e.object == object]
        return hits


def build_minimal_example_graph() -> Graph:
    g = Graph()

    g.add_nodes(
        [
            Node(id = 'gene:FH', type = 'gene', name = 'FH', xrefs = {'HGNC': 'FH'}),
            Node(id = 'metabolite:fumarate', type = 'metabolite', name = 'Fumarate'),
            Node(id = 'process:tca_cycle_blockade', type = 'process', name = 'TCA cycle blockade'),
            Node(id = 'process:protein_succination', type = 'process', name = 'Protein succination'),
            Node(id = 'protein:KEAP1', type = 'protein', name = 'KEAP1', xrefs = {'HGNC': 'KEAP1'}),
            Node(
                id = 'protein:NRF2',
                type = 'protein',
                name = 'NRF2',
                synonyms = ['NFE2L2'],
                xrefs = {'HGNC': 'NFE2L2'},
            ),
            Node(id = 'pathway:NRF2_ARE', type = 'pathway', name = 'NRF2-ARE antioxidant response'),
            Node(id = 'state:oxidative_stress', type = 'state', name = 'Oxidative stress'),
        ]
    )

    g.add_edges(
        [
            Edge(
                subject = 'gene:FH',
                predicate = 'causes',
                object = 'process:tca_cycle_blockade',
                weight = 0.90,
                evidence_level = 'review_or_consensus',
                mechanism = 'loss of fumarate hydratase activity blocks fumarate→malate',
            ),
            Edge(
                subject = 'process:tca_cycle_blockade',
                predicate = 'causes',
                object = 'metabolite:fumarate',
                weight = 0.90,
                evidence_level = 'review_or_consensus',
                mechanism = 'fumarate accumulates upstream of FH blockade',
            ),
            Edge(
                subject = 'metabolite:fumarate',
                predicate = 'modifies',
                object = 'process:protein_succination',
                weight = 0.85,
                evidence_level = 'biochemical_direct',
                mechanism = 'succination of cysteine residues (2SC adducts)',
            ),
            Edge(
                subject = 'process:protein_succination',
                predicate = 'inhibits',
                object = 'protein:KEAP1',
                weight = 0.70,
                evidence_level = 'cell_model',
                mechanism = 'KEAP1 succination impairs NRF2 degradation',
            ),
            Edge(
                subject = 'protein:KEAP1',
                predicate = 'inhibits',
                object = 'protein:NRF2',
                weight = 0.80,
                evidence_level = 'review_or_consensus',
                polarity = '-',
                mechanism = 'KEAP1 targets NRF2 for degradation (baseline regulation)',
            ),
            Edge(
                subject = 'protein:NRF2',
                predicate = 'activates',
                object = 'pathway:NRF2_ARE',
                weight = 0.85,
                evidence_level = 'review_or_consensus',
                mechanism = 'NRF2 transcriptional activation of antioxidant response genes',
            ),
            Edge(
                subject = 'state:oxidative_stress',
                predicate = 'enables',
                object = 'pathway:NRF2_ARE',
                weight = 0.55,
                evidence_level = 'hypothesis',
                notes = 'Stress context may increase reliance on NRF2; directionality is conceptual.',
            ),
        ]
    )

    return g


def main() -> None:
    g = build_minimal_example_graph()
    print(f'n_nodes = {len(g.nodes)} n_edges = {len(g.edges)}')
    for e in g.edges:
        print(f'{e.subject} --{e.predicate}--> {e.object} (w = {e.weight}, ev = {e.evidence_level})')


if __name__ == '__main__':
    main()
