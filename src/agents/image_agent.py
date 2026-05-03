from src.core.state import AgentState
from src.integrations.image_provider import generate_image
from src.integrations.llm_provider import get_fallback_llm, invoke_with_retry

PROMPT_ENHANCE = """You are an expert at writing image generation prompts for marketing content.
Convert this request into a vivid, specific DALL-E prompt (1-2 sentences max):

Request: {query}

Prompt:"""


def _enhance_prompt(query: str) -> str:
    llm = get_fallback_llm(temperature=0.5)
    try:
        return invoke_with_retry(
            llm,
            [{"role": "user", "content": PROMPT_ENHANCE.format(query=query)}]
        ).strip()
    except Exception:
        return query  # fallback to raw query


def image_agent_node(state: AgentState) -> AgentState:
    """Generates a marketing image using DALL-E 3 with DALL-E 2 fallback."""
    query = state["query"]
    errors = state.get("errors", [])

    enhanced_prompt = _enhance_prompt(query)

    try:
        result = generate_image(enhanced_prompt)
        if result.get("error"):
            errors = errors + [result["error"]]
    except Exception as e:
        result = {"url": None, "local_path": None, "prompt_used": enhanced_prompt, "model_used": None}
        errors = errors + [f"Image agent error: {e}"]

    return {
        **state,
        "image_result": result,
        "current_agent": "image_agent",
        "errors": errors,
    }
