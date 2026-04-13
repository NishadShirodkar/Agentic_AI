from models.schemas import ExecutionPlan, SourceEvidence
from tools.scraper import scrape
from tools.search import search
from utils.filter import filter_results
from utils.timeouts import HTTP_TIMEOUT_SECONDS, StageTimeoutError, run_with_timeout


def _safe_snippet(content: str, fallback: str) -> str:
    if content:
        return content[:220].replace("\n", " ").strip()
    return fallback[:220].replace("\n", " ").strip()


def execute_plan(plan: ExecutionPlan, query: str) -> list[SourceEvidence]:
    tools = set(plan.tools)

    if "search" not in tools:
        return []

    try:
        search_results = search(query=query, num_results=8, timeout_seconds=HTTP_TIMEOUT_SECONDS)
    except Exception:
        search_results = []

    if not search_results:
        return []

    enriched: list[dict] = []

    for item in search_results:
        url = item.get("url")
        if not url:
            continue

        content = ""
        if "scraper" in tools:
            try:
                content = run_with_timeout(
                    scrape,
                    url,
                    timeout_seconds=HTTP_TIMEOUT_SECONDS,
                )
            except (StageTimeoutError, Exception):
                content = ""

        snippet = _safe_snippet(content, item.get("snippet", ""))

        enriched.append(
            {
                "url": url,
                "title": item.get("title", ""),
                "snippet": snippet,
                "content": content,
            }
        )

    if not enriched:
        return []

    if "filter" in tools:
        try:
            enriched = filter_results(enriched, query, max_results=5)
        except Exception:
            pass

    sources: list[SourceEvidence] = []
    for item in enriched:
        sources.append(
            SourceEvidence(
                url=item.get("url", ""),
                snippet=item.get("snippet", "")[:240],
                content=item.get("content", ""),
            )
        )

    return sources
