from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal

NodeType = Literal[
    'gene',
    'protein',
    'metabolite',
    'complex',
    'process',
    'state',
    'pathway',
    'phenotype',
    'cell_type',
    'compartment',
    'therapy',
]

EvidenceLevel = Literal[
    'biochemical_direct',
    'genetic_perturbation',
    'cell_model',
    'animal_model',
    'patient_omics',
    'clinical',
    'review_or_consensus',
    'hypothesis',
]

Predicate = Literal[
    'causes',
    'enables',
    'prevents',
    'increases',
    'decreases',
    'activates',
    'inhibits',
    'stabilizes',
    'destabilizes',
    'converts_to',
    'accumulates',
    'inhibits_activity_of',
    'modifies',
    'binds',
    'translocates_to',
    'associates_with',
]


@dataclass
class Node:
    id: str
    type: NodeType
    name: str
    synonyms: List[str] = field(default_factory = list)
    description: Optional[str] = None
    xrefs: Dict[str, str] = field(default_factory = dict)
    tags: List[str] = field(default_factory = list)

    def __post_init__(self) -> None:
        if ':' not in self.id:
            raise ValueError(f'Node id must be <type>:<name>, got {self.id}')
        prefix = self.id.split(':', 1)[0]
        if prefix != self.type:
            raise ValueError(f'Node id prefix {prefix} does not match type {self.type}')


@dataclass
class Edge:
    subject: str
    predicate: Predicate
    object: str
    weight: float
    evidence_level: EvidenceLevel
    polarity: Optional[Literal['+', '-', '0']] = None
    mechanism: Optional[str] = None
    context: Dict[str, str] = field(default_factory = dict)
    citations: List[str] = field(default_factory = list)
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not (0.01 <= float(self.weight) <= 0.99):
            raise ValueError(f'Edge weight must be between 0.01 and 0.99, got {self.weight}')
        if self.subject == self.object:
            raise ValueError('Self-loop edges are not allowed')
