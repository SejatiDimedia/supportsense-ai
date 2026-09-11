import pytest
from app.kag.sql_query import SQLRelationalQueryEngine

@pytest.fixture
def sql_engine():
    return SQLRelationalQueryEngine()

def test_sql_kag_query_order_4521_with_delay(sql_engine):
    result = sql_engine.query_order_context("#4521")
    assert result["found"] is True
    assert "Shipping Delayed" in result["summary"]
    assert "Budi Santoso" in result["summary"]
    assert "Ultra Wireless Headphones Pro" in result["summary"]

def test_sql_kag_query_order_4522_delivered(sql_engine):
    result = sql_engine.query_order_context("#4522")
    assert result["found"] is True
    assert "Delivered" in result["summary"]
    assert "DHL Express" in result["summary"]

def test_sql_kag_query_order_4534_lost_in_transit(sql_engine):
    result = sql_engine.query_order_context("#4534")
    assert result["found"] is True
    assert "Lost in Transit" in result["summary"]
    assert "Ahmad Fauzi" in result["summary"]
    assert "Siti Rahma" in result["summary"]
    assert "data" in result
    assert result["data"]["order"]["status"] == "Lost in Transit"
    assert result["data"]["issues"][0]["assigned_agent"]["name"] == "Siti Rahma"

def test_sql_kag_query_order_not_found(sql_engine):
    result = sql_engine.query_order_context("#9999999")
    assert result["found"] is False
    assert "not found" in result["summary"].lower()

def test_sql_kag_query_order_with_multiple_items(sql_engine):
    result = sql_engine.query_order_context("#4525")
    assert result["found"] is True
    assert "2 products" in result["summary"] or "Smart Home Mesh Wi-Fi 6 Hub" in result["summary"]
    assert "Ergonomic Executive Office Chair V2" in result["summary"]
    assert len(result["data"]["products"]) == 2
    product_names = [p["name"] for p in result["data"]["products"]]
    assert "Smart Home Mesh Wi-Fi 6 Hub" in product_names
    assert "Ergonomic Executive Office Chair V2" in product_names
