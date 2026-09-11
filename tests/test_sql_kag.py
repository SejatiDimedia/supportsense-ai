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

def test_sql_kag_query_order_not_found(sql_engine):
    result = sql_engine.query_order_context("#9999999")
    assert result["found"] is False
    assert "not found" in result["summary"].lower()
