from src.core.state import AgentState
from src.integrations.research_provider import research


def research_node(state: AgentState) -> AgentState:
    """Fetches multi-source research using SERP API + GPT synthesis."""
    query = state["query"]
    errors = state.get("errors", [])

    try:
        result = research(query)
    except Exception as e:
        errors = errors + [f"Research agent error: {e}"]
        result = {"query": query, "serp_results": [], "synthesis": "", "cached": False}

    return {
        **state,
        "research_results": result,
        "current_agent": "research",
        "errors": errors,
    }
