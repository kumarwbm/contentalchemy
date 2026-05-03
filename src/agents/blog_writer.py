import re
from src.core.state import AgentState
from src.integrations.llm_provider import get_primary_llm, invoke_with_retry

BLOG_PROMPT = """You are an expert SEO content writer. Write a comprehensive blog post based on the research below.

Topic: {query}
Research Report:
{report}

Requirements:
- Title: compelling, includes primary keyword
- Length: 800-1200 words
- Structure: H1 title, H2/H3 subheadings, short paragraphs
- Keyword density: naturally use primary keyword 1-2% of total words
- Include: introduction hook, 3-5 main sections, conclusion with CTA
- Meta description: exactly 150-160 characters summarising the post
- Tone: professional but accessible

Output format (strictly follow this):
TITLE: <title here>
META: <meta description here>
KEYWORDS: <comma-separated list of 5-8 target keywords>
---
<full blog post content in markdown>"""


def _count_keyword_density(text: str, keyword: str) -> float:
    words = re.findall(r'\w+', text.lower())
    keyword_words = keyword.lower().split()
    count = sum(1 for i in range(len(words)) if words[i:i+len(keyword_words)] == keyword_words)
    return round(count / max(len(words), 1) * 100, 2)


def _parse_blog_output(raw: str) -> dict:
    lines = raw.strip().split("\n")
    result = {"title": "", "meta_description": "", "keywords": [], "content": ""}

    for i, line in enumerate(lines):
        if line.startswith("TITLE:"):
            result["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("META:"):
            result["meta_description"] = line.replace("META:", "").strip()
        elif line.startswith("KEYWORDS:"):
            result["keywords"] = [k.strip() for k in line.replace("KEYWORDS:", "").split(",")]
        elif line.strip() == "---":
            result["content"] = "\n".join(lines[i+1:]).strip()
            break

    return result


def blog_writer_node(state: AgentState) -> AgentState:
    """Generates an SEO-optimised blog post from the research report."""
    report = state.get("research_report", "") or state.get("research_results", {}).get("synthesis", "")
    errors = state.get("errors", [])

    llm = get_primary_llm(temperature=0.7)
    try:
        raw = invoke_with_retry(
            llm,
            [{"role": "user", "content": BLOG_PROMPT.format(
                query=state["query"],
                report=report,
            )}]
        )
        blog = _parse_blog_output(raw)

        # Add quality metrics
        if blog["keywords"] and blog["content"]:
            primary_kw = blog["keywords"][0]
            blog["keyword_density"] = _count_keyword_density(blog["content"], primary_kw)
            blog["word_count"] = len(blog["content"].split())
            blog["meta_char_count"] = len(blog["meta_description"])

    except Exception as e:
        blog = {"title": "", "meta_description": "", "keywords": [], "content": "", "error": str(e)}
        errors = errors + [f"Blog writer error: {e}"]

    return {
        **state,
        "blog_post": blog,
        "current_agent": "blog_writer",
        "errors": errors,
    }
