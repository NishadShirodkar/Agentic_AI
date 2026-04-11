import trafilatura


def scrape(url: str):
    """
    Extract clean text content from a webpage
    """

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        text = trafilatura.extract(downloaded)

        if not text:
            return ""

        # limit size to avoid token overload
        return text[:3000]

    except Exception as e:
        print(f"[SCRAPER ERROR] {url}: {e}")
        return ""