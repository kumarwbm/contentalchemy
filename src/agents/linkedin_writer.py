from src.core.state import AgentState
from src.integrations.llm_provider import get_primary_llm, invoke_with_retry

LINKEDIN_PROMPT = """You are a LinkedIn content expert. Write a high-engagement LinkedIn post based on the research below.

Topic: {query}
Research:
{report}

Requirements:
- Length: 1300-1600 characters (count carefully)
- Opening hook: first line must stop the scroll — bold claim, question, or surprising stat
- Structure: hook → insight/story → key takeaways (numbered or bulleted) → CTA
- Line breaks: short paragraphs, blank lines between sections for mobile readability
- Hashtags: 8-12 highly relevant hashtags at the end
- Tone: professional with personality, first-person, not corporate

Output format (strictly follow this):
HASHTAGS: <space-separated hashtags>
CHAR_COUNT: <estimated character count>
---
<full LinkedIn post content>"""


def linkedin_writer_node(state: AgentState) -> AgentState:
    """Generates a platform-optimised LinkedIn post from the research report."""
    report = state.get("research_report", "") or state.get("research_results", {}).get("synthesis", "")
    errors = state.get("errors", [])

    llm = get_primary_llm(temperature=0.8)
    try:
        raw = invoke_with_retry(
            llm,
            [{"role": "user", "content": LINKEDIN_PROMPT.format(
                query=state["query"],
                report=report,
            )}]
        )

        lines = raw.strip().split("\n")
        post = {"hashtags": [], "content": "", "char_count": 0}

        for i, line in enumerate(lines):
            if line.startswith("HASHTAGS:"):
                post["hashtags"] = line.replace("HASHTAGS:", "").strip().split()
            elif line.startswith("CHAR_COUNT:"):
                try:
                    post["char_count"] = int(line.replace("CHAR_COUNT:", "").strip())
                except ValueError:
                    pass
            elif line.strip() == "---":
                post["content"] = "\n".join(lines[i+1:]).strip()
                post["char_count"] = len(post["content"])
                break

    except Exception as e:
        post = {"hashtags": [], "content": "", "char_count": 0}
        errors = errors + [f"LinkedIn writer error: {e}"]

    return {
        **state,
        "linkedin_post": post,
        "current_agent": "linkedin_writer",
        "errors": errors,
    }
