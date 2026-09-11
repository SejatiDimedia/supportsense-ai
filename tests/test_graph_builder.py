import pytest
from app.kag.graph_builder import SupportKnowledgeGraph

def test_graph_initialization():
    kg = SupportKnowledgeGraph()
    summary = kg.summary()
    assert summary["node_count"] == 9
    assert summary["edge_count"] == 6
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
    assert order1["id"] == "ord_4521"
    assert order1["status"] == "shipping_delayed"
    assert order1["tracking_number"] == "FDX-8829104"

def test_order_to_agent_traversal():
    kg = SupportKnowledgeGraph()
    order = kg.find_order("4521")
    assert order is not None

    # Order -> HAS_ISSUE -> Issue
    issues = kg.get_neighbors(order["id"], relation="HAS_ISSUE", direction="out")
    assert len(issues) == 1
    issue_node = issues[0]
    assert issue_node["node_id"] == "iss_701"
    assert issue_node["node_data"]["priority"] == "High"

    # Issue -> ASSIGNED_TO -> Agent
    agents = kg.get_neighbors(issue_node["node_id"], relation="ASSIGNED_TO", direction="out")
    assert len(agents) == 1
    agent_node = agents[0]
    assert agent_node["node_id"] == "agt_budi"
    assert agent_node["node_data"]["name"] == "Budi Santoso"
