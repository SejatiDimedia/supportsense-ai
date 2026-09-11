import pytest
from app.kag.graph_query import GraphQueryEngine, extract_order_number

def test_extract_order_number():
    assert extract_order_number("Where is my order #4521?") == "#4521"
    assert extract_order_number("Can you check order 4522 please?") == "#4522"
    assert extract_order_number("Order number 9999999 status") == "#9999999"
    assert extract_order_number("#4521 is delayed") == "#4521"
    assert extract_order_number("What is your refund policy?") is None

def test_query_order_4521_with_delay_and_agent():
    engine = GraphQueryEngine()
    result = engine.query_order_context("#4521")

    assert result["found"] is True
    assert result["order_number"] == "#4521"
    assert "John Doe" in result["summary"]
    assert "Apex Smartwatch Pro" in result["summary"]
    assert "Budi Santoso" in result["summary"]
    assert "FedEx" in result["summary"]
    assert "Shipping Delayed" in result["summary"]

    data = result["data"]
    assert len(data["issues"]) == 1
    assert data["issues"][0]["assigned_agent"]["name"] == "Budi Santoso"

def test_query_order_4522_delivered_no_issues():
    engine = GraphQueryEngine()
    result = engine.query_order_context("#4522")

    assert result["found"] is True
    assert result["order_number"] == "#4522"
    assert "Sarah Connor" in result["summary"]
    assert "Delivered" in result["summary"]
    assert "No reported issues" in result["summary"]

def test_query_order_not_found():
    engine = GraphQueryEngine()
    result = engine.query_order_context("#9999999")

    assert result["found"] is False
    assert "not found" in result["summary"].lower()
    assert result["data"] == {}

def test_query_by_text():
    engine = GraphQueryEngine()
    result = engine.query_by_text("Who is handling my complaint for order #4521?")

    assert result is not None
    assert result["found"] is True
    assert "Budi Santoso" in result["summary"]
