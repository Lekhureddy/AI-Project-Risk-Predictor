from risk_copilot.evidence_graph import build_evidence_graph, downstream_impact, graph_payload


def test_evidence_graph_builds_directed_dependency_structure():
    graph = build_evidence_graph(
        project_id="PROJECT-A",
        project_label="Checkout",
        evidence_items=[
            {"evidence_id": "ISSUE-1", "source_type": "issue", "title": "Payment dependency"},
            {"evidence_id": "PR-2", "source_type": "pull_request", "title": "Retry logic"},
        ],
        relationships=[
            {"source": "ISSUE-1", "target": "PR-2", "relation": "blocked_by"},
        ],
    )
    payload = graph_payload(graph)

    assert len(payload["nodes"]) == 3
    assert any(edge["relation"] == "blocked_by" for edge in payload["edges"])
    impact = downstream_impact(graph, "ISSUE-1")
    assert "PR-2" in impact["downstream_nodes"]
