from langchain_core.messages import HumanMessage
from src.core.state import AgentState
from src.integrations.llm_provider import get_fallback_llm, invoke_with_retry

INTENT_PROMPT = """Classify the following user query into exactly one of these intents:
- research   → user wants research/analysis/information only
- blog       → user wants a blog post (may also need research)
- linkedin   → user wants a LinkedIn post (may also need research)
- image      → user wants an image generated
- multi      → user wants multiple content types (e.g. blog + LinkedIn + image)

Reply with ONLY the intent word, nothing else.

Query: {query}
Intent:"""


def query_handler_node(state: AgentState) -> AgentState:
    """Classifies user query intent and routes to the correct agent."""
    query = state["query"]
    llm = get_fallback_llm(temperature=0.0)

    try:
        intent = invoke_with_retry(
            llm,
            [{"role": "user", "content": INTENT_PROMPT.format(query=query)}]
        ).strip().lower()

        if intent not in {"research", "blog", "linkedin", "image", "multi"}:
            intent = "research"

    except Exception as e:
        intent = "research"
        state["errors"] = state.get("errors", []) + [f"Query handler error: {e}"]

    return {
        **state,
        "intent": intent,
        "current_agent": "query_handler",
        "messages": state.get("messages", []) + [HumanMessage(content=query)],
    }
