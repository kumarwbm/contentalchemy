from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AgentState
from src.agents.query_handler import query_handler_node
from src.agents.research_agent import research_node
from src.agents.content_strategist import content_strategist_node
from src.agents.blog_writer import blog_writer_node
from src.agents.linkedin_writer import linkedin_writer_node
from src.agents.image_agent import image_agent_node


def route_by_intent(state: AgentState) -> str:
    """Conditional edge — routes from Query Handler based on detected intent."""
    intent = state.get("intent", "research")
    routes = {
        "research": "research",
        "blog": "research",       # blog always starts with research
        "linkedin": "research",   # linkedin always starts with research
        "image": "image",
        "multi": "research",
    }
    return routes.get(intent, "research")


def route_after_strategy(state: AgentState) -> str:
    """After Content Strategist, route to the correct content agent."""
    intent = state.get("intent", "research")
    if intent == "blog":
        return "blog"
    if intent == "linkedin":
        return "linkedin"
    if intent == "multi":
        return "blog"             # multi: blog first, then linkedin
    return END                    # research-only intent — done


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("query_handler", query_handler_node)
    graph.add_node("research", research_node)
    graph.add_node("content_strategist", content_strategist_node)
    graph.add_node("blog", blog_writer_node)
    graph.add_node("linkedin", linkedin_writer_node)
    graph.add_node("image", image_agent_node)

    # Entry point
    graph.set_entry_point("query_handler")

    # Edges
    graph.add_conditional_edges("query_handler", route_by_intent, {
        "research": "research",
        "image": "image",
    })
    graph.add_edge("research", "content_strategist")
    graph.add_conditional_edges("content_strategist", route_after_strategy, {
        "blog": "blog",
        "linkedin": "linkedin",
        END: END,
    })
    graph.add_edge("blog", END)
    graph.add_edge("linkedin", END)
    graph.add_edge("image", END)

    return graph


def compile_graph():
    """Returns a compiled, checkpointed graph ready to invoke."""
    graph = build_graph()
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
