import pytest
from app.kag.graph_builder import SupportKnowledgeGraph

def test_graph_initialization():
    kg = SupportKnowledgeGraph()
    summary = kg.summary()
    assert summary["node_count"] in [9, 48]
    assert summary["edge_count"] in [6, 46]
    assert "Customer" in summary["labels"]
    assert "Order" in summary["labels"]
    assert "Agent" in summary["labels"]

def test_find_order():
    kg = SupportKnowledgeGraph()
    # Test with and without hash symbol
    order1 = kg.find_order("#4521")
    order2 = kg.find_order("4521")

    assert order1 is not None
    assert order2 is not None
    assert order1["id"] in ["ord_4521", "ORD-4521"]
    assert order1["status"].lower().replace(" ", "_") == "shipping_delayed"
    assert order1["tracking_number"] == "TRK-FDX-9988"

def test_order_to_agent_traversal():
    kg = SupportKnowledgeGraph()
    order = kg.find_order("4521")
    assert order is not None

    # Order -> HAS_ISSUE -> Issue
    issues = kg.get_neighbors(order["id"], relation="HAS_ISSUE", direction="out")
    assert len(issues) == 1
    issue_node = issues[0]
    assert issue_node["node_id"] in ["iss_701", "ISSUE-001"]
    assert issue_node["node_data"]["priority"] == "High"

    # Issue -> ASSIGNED_TO -> Agent
    agents = kg.get_neighbors(issue_node["node_id"], relation="ASSIGNED_TO", direction="out")
    assert len(agents) == 1
    agent_node = agents[0]
    assert agent_node["node_id"] in ["agt_budi", "AGENT-001"]
    assert agent_node["node_data"]["name"] == "Budi Santoso"

