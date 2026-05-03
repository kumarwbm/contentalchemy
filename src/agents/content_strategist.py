from src.core.state import AgentState
from src.integrations.llm_provider import get_primary_llm, invoke_with_retry

STRATEGIST_PROMPT = """You are a senior content strategist. Transform the raw research below into a
structured, clearly formatted report that content writers can use directly.

Query: {query}

Raw Research:
{synthesis}

Format the report with:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points with data/stats)
3. Trends & Insights
4. Recommended Content Angles (3-5 ideas)
5. Key Sources

Be concise, factual, and actionable."""


def content_strategist_node(state: AgentState) -> AgentState:
    """Formats raw research into a structured report for downstream content agents."""
    research = state.get("research_results", {})
    errors = state.get("errors", [])

    synthesis = research.get("synthesis", "")
    if not synthesis:
        return {**state, "research_report": "", "current_agent": "content_strategist"}

    llm = get_primary_llm(temperature=0.4)
    try:
        report = invoke_with_retry(
            llm,
            [{"role": "user", "content": STRATEGIST_PROMPT.format(
                query=state["query"],
                synthesis=synthesis,
            )}]
        )
    except Exception as e:
        report = synthesis  # fallback: use raw synthesis
        errors = errors + [f"Content strategist error: {e}"]

    return {
        **state,
        "research_report": report,
        "current_agent": "content_strategist",
        "errors": errors,
    }
