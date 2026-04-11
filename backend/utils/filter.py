def score_content(content: str, query: str):
    """
    Simple keyword-based relevance scoring
    """
    score = 0
    content_lower = content.lower()

    for word in query.lower().split():
        if word in content_lower:
            score += 1

    return score


def filter_results(results, query, max_results=3):
    """
    Filter, deduplicate, and rank results
    """

    filtered = []
    seen_urls = set()

    for r in results:
        url = r.get("url", "")
        content = r.get("content", "")

        # ❌ Skip duplicates
        if url in seen_urls:
            continue

        # ❌ Skip weak/empty content
        if not content or len(content) < 200:
            continue

        # ❌ Skip low-quality domains
        if any(bad in url for bad in ["youtube", "facebook", "twitter"]):
            continue

        # ✅ Add score
        relevance_score = score_content(content, query)

        r["score"] = relevance_score

        filtered.append(r)
        seen_urls.add(url)

    # 🧠 Sort by relevance score first, then content length
    filtered.sort(
        key=lambda x: (x["score"], len(x["content"])),
        reverse=True
    )

    return filtered[:max_results]