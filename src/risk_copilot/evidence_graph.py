from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

import networkx as nx


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str
    url: str | None = None
    risk_score: float | None = None


def build_evidence_graph(
    *,
    project_id: str,
    project_label: str,
    evidence_items: Iterable[dict],
    relationships: Iterable[dict] = (),
) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.add_node(
        project_id,
        **asdict(GraphNode(node_id=project_id, node_type="project", label=project_label)),
    )

    for item in evidence_items:
        node_id = str(item["evidence_id"])
        graph.add_node(
            node_id,
            **asdict(
                GraphNode(
                    node_id=node_id,
                    node_type=str(item.get("source_type") or "evidence"),
                    label=str(item.get("title") or node_id),
                    url=item.get("url"),
                    risk_score=item.get("risk_score"),
                )
            ),
        )
        graph.add_edge(project_id, node_id, relation="supported_by")

    for rel in relationships:
        source = str(rel["source"])
        target = str(rel["target"])
        if source not in graph:
            graph.add_node(source, node_id=source, node_type="unknown", label=source)
        if target not in graph:
            graph.add_node(target, node_id=target, node_type="unknown", label=target)
        graph.add_edge(
            source,
            target,
            relation=str(rel.get("relation") or "related_to"),
            confidence=rel.get("confidence"),
        )

    return graph


def graph_payload(graph: nx.MultiDiGraph) -> dict:
    nodes = []
    for node_id, attrs in graph.nodes(data=True):
        nodes.append({"id": node_id, **attrs})

    edges = []
    for source, target, key, attrs in graph.edges(keys=True, data=True):
        edges.append({"source": source, "target": target, "key": key, **attrs})

    return {"nodes": nodes, "edges": edges}


def downstream_impact(graph: nx.MultiDiGraph, node_id: str) -> dict:
    if node_id not in graph:
        raise KeyError(node_id)
    descendants = nx.descendants(graph, node_id)
    projects = [
        n for n in descendants
        if graph.nodes[n].get("node_type") in {"project", "program", "delivery_target"}
    ]
    return {
        "node_id": node_id,
        "downstream_node_count": len(descendants),
        "downstream_project_count": len(projects),
        "downstream_nodes": sorted(descendants),
    }
