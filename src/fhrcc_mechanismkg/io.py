from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from .graph import Graph
from .schema import Node, Edge


def graph_to_dict(graph: Graph) -> Dict[str, Any]:
    return {
        "nodes": [
            {
                "id": n.id,
                "type": n.type,
                "name": n.name,
                "synonyms": n.synonyms,
                "description": n.description,
                "xrefs": n.xrefs,
                "tags": n.tags,
            }
            for n in graph.nodes.values()
        ],
        "edges": [
            {
                "subject": e.subject,
                "predicate": e.predicate,
                "object": e.object,
                "weight": e.weight,
                "evidence_level": e.evidence_level,
                "polarity": e.polarity,
                "mechanism": e.mechanism,
                "context": e.context,
                "citations": e.citations,
                "notes": e.notes,
            }
            for e in graph.edges
        ],
        "schema_version": "0.1.0",
    }


def graph_from_dict(payload: Dict[str, Any]) -> Graph:
    graph = Graph()

    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])

    for n in nodes:
        node = Node(
            id = n["id"],
            type = n["type"],
            name = n["name"],
            synonyms = n.get("synonyms", []) or [],
            description = n.get("description"),
            xrefs = n.get("xrefs", {}) or {},
            tags = n.get("tags", []) or [],
        )
        graph.add_node(node)

    for e in edges:
        edge = Edge(
            subject = e["subject"],
            predicate = e["predicate"],
            object = e["object"],
            weight = float(e["weight"]),
            evidence_level = e["evidence_level"],
            polarity = e.get("polarity"),
            mechanism = e.get("mechanism"),
            context = e.get("context", {}) or {},
            citations = e.get("citations", []) or [],
            notes = e.get("notes"),
        )
        graph.add_edge(edge)

    return graph


def graph_to_json(graph: Graph, path: str) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents = True, exist_ok = True)

    payload = graph_to_dict(graph)
    out_path.write_text(json.dumps(payload, indent = 2), encoding = "utf-8")


def graph_from_json(path: str) -> Graph:
    in_path = Path(path)
    payload = json.loads(in_path.read_text(encoding = "utf-8"))
    return graph_from_dict(payload)
