from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state passed between all agents in the LangGraph graph."""

    # Input
    query: str
    intent: str                        # research | blog | linkedin | image | multi

    # Conversation history (LangGraph managed)
    messages: Annotated[list, add_messages]

    # Agent outputs
    research_results: Optional[dict]   # raw SERP results
    research_report: Optional[str]     # formatted by Content Strategist
    blog_post: Optional[dict]          # {title, content, meta_description, keywords}
    linkedin_post: Optional[dict]      # {content, hashtags, char_count}
    image_result: Optional[dict]       # {url, local_path, prompt_used}

    # Quality scores
    quality_scores: Optional[dict]     # {seo_score, readability, brand_voice}

    # Error tracking
    errors: list[str]
    current_agent: str
