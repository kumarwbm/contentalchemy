import time
from cachetools import TTLCache
from serpapi import GoogleSearch
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_settings
from src.integrations.llm_provider import get_primary_llm, invoke_with_retry

_cache: TTLCache = None


def _get_cache() -> TTLCache:
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = TTLCache(maxsize=128, ttl=settings.research_cache_ttl)
    return _cache


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _serp_search(query: str, num_results: int = 10) -> list[dict]:
    settings = get_settings()
    search = GoogleSearch({
        "q": query,
        "api_key": settings.serp_api_key,
        "num": num_results,
    })
    results = search.get_dict()
    organic = results.get("organic_results", [])
    return [
        {
            "title": r.get("title", ""),
            "snippet": r.get("snippet", ""),
            "link": r.get("link", ""),
            "position": r.get("position", 0),
        }
        for r in organic
    ]


def _synthesise_with_gpt(query: str, serp_results: list[dict]) -> str:
    llm = get_primary_llm(temperature=0.3)
    snippets = "\n".join(
        f"[{i+1}] {r['title']}\n{r['snippet']}\nSource: {r['link']}"
        for i, r in enumerate(serp_results)
    )
    prompt = f"""You are a research analyst. Synthesise the following search results into a
comprehensive, well-cited research summary for the query: "{query}"

Search Results:
{snippets}

Instructions:
- Write 3-5 paragraphs covering key findings
- Cite sources using [1], [2] etc.
- Highlight trends, key statistics, and actionable insights
- End with a "Key Sources" list

Research Summary:"""
    return invoke_with_retry(llm, [{"role": "user", "content": prompt}])


def research(query: str) -> dict:
    """
    Full research pipeline: SERP fetch → GPT synthesis → cached result.
    Returns: {query, serp_results, synthesis, cached, timestamp}
    """
    cache = _get_cache()
    cache_key = query.lower().strip()

    if cache_key in cache:
        cached = cache[cache_key]
        cached["cached"] = True
        return cached

    serp_results = _serp_search(query, get_settings().max_search_results)
    synthesis = _synthesise_with_gpt(query, serp_results)

    result = {
        "query": query,
        "serp_results": serp_results,
        "synthesis": synthesis,
        "cached": False,
        "timestamp": time.time(),
    }
    cache[cache_key] = result
    return result
