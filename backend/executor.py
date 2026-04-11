from tools.search import search
from tools.scraper import scrape
from utils.filter import filter_results


def execute_plan(plan, query):
    """
    Execute the agent plan:
    search → scrape → filter
    """

    print("\n[EXECUTOR] Starting execution...")

    # -------------------------
    # Step 1: Search
    # -------------------------
    try:
        print("[EXECUTOR] Searching...")
        search_results = search(query)
    except Exception as e:
        print(f"[EXECUTOR ERROR - SEARCH]: {e}")
        return []

    if not search_results:
        print("[EXECUTOR] No search results found.")
        return []

    # -------------------------
    # Step 2: Scrape
    # -------------------------
    enriched_results = []

    print(f"[EXECUTOR] Scraping {len(search_results)} results...")

    for r in search_results:
        url = r.get("url")

        if not url:
            continue

        content = ""

        # 🔁 Retry logic (2 attempts)
        for attempt in range(2):
            try:
                content = scrape(url)
                if content:
                    break
            except Exception as e:
                print(f"[SCRAPE ERROR] Attempt {attempt+1} for {url}: {e}")

        if not content:
            print(f"[EXECUTOR] Skipping (no content): {url}")
            continue

        enriched_results.append({
            "url": url,
            "title": r.get("title"),
            "content": content
        })

    if not enriched_results:
        print("[EXECUTOR] No usable scraped data.")
        return []

    # -------------------------
    # Step 3: Filter + Rank
    # -------------------------
    print("[EXECUTOR] Filtering results...")
    filtered = filter_results(enriched_results, query)

    if not filtered:
        print("[EXECUTOR] All results filtered out.")
        return []

    print(f"[EXECUTOR] Final selected results: {len(filtered)}")

    return filtered