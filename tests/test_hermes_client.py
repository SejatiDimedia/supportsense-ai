import pytest
from unittest.mock import MagicMock, patch
from app.agent.hermes_client import HermesAgentClient, SUPPORT_TOOLS

def test_support_tools_schema():
    assert len(SUPPORT_TOOLS) == 3
    tool_names = [t["function"]["name"] for t in SUPPORT_TOOLS]
    assert "search_knowledge_base" in tool_names
    assert "lookup_relational_data" in tool_names
    assert "escalate_to_human" in tool_names

@patch("httpx.Client.post")
def test_plan_routing_with_mock(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {
                        "name": "search_knowledge_base",
                        "arguments": {"query": "refund policy"}
                    }
                }
            ]
        }
    }
    mock_post.return_value = mock_response

    client = HermesAgentClient()
    tools = client.plan_routing("What is your refund policy?")
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "search_knowledge_base"
    assert tools[0]["function"]["arguments"]["query"] == "refund policy"

@patch("httpx.Client.post")
def test_generate_answer_with_mock(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "content": "Our refund policy allows returns within 30 days."
        }
    }
    mock_post.return_value = mock_response

    client = HermesAgentClient()
    answer = client.generate_answer("How to refund?", "Refund context 30 days.")
    assert "30 days" in answer
