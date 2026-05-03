import pytest
from unittest.mock import patch
from src.agents.query_handler import query_handler_node

BASE_STATE = {
    "query": "",
    "intent": "",
    "messages": [],
    "research_results": None,
    "research_report": None,
    "blog_post": None,
    "linkedin_post": None,
    "image_result": None,
    "quality_scores": None,
    "errors": [],
    "current_agent": "",
}


@pytest.mark.parametrize("query,expected_intent", [
    ("What are the latest trends in AI?", "research"),
    ("Write a blog post about sustainable energy", "blog"),
    ("Create a LinkedIn post about remote work", "linkedin"),
    ("Generate an image of a futuristic city", "image"),
    ("Research AI and write a blog post and LinkedIn post", "multi"),
])
def test_query_routing(query, expected_intent):
    with patch("src.agents.query_handler.invoke_with_retry", return_value=expected_intent):
        state = {**BASE_STATE, "query": query}
        result = query_handler_node(state)
        assert result["intent"] == expected_intent


def test_query_handler_defaults_to_research_on_bad_response():
    with patch("src.agents.query_handler.invoke_with_retry", return_value="gibberish"):
        state = {**BASE_STATE, "query": "some query"}
        result = query_handler_node(state)
        assert result["intent"] == "research"


def test_query_handler_handles_llm_error():
    with patch("src.agents.query_handler.invoke_with_retry", side_effect=Exception("API error")):
        state = {**BASE_STATE, "query": "some query"}
        result = query_handler_node(state)
        assert result["intent"] == "research"
        assert len(result["errors"]) > 0
