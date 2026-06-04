"""Tools for finding official Vinpearl source candidates."""

from __future__ import annotations

from urllib.parse import quote_plus

from src.agents.tools.text_utils import normalize_text


DESTINATION_SOURCE_HINTS = {
    "phu quoc": [
        "https://vinpearl.com/vi/phu-quoc",
        "https://vinpearl.com/vi/vinwonders-phu-quoc",
    ],
    "nha trang": [
        "https://vinpearl.com/vi/nha-trang",
        "https://vinpearl.com/vi/vinwonders-nha-trang",
    ],
    "ha long": [
        "https://vinpearl.com/vi/ha-long",
    ],
    "hoi an": [
        "https://vinpearl.com/vi/nam-hoi-an",
        "https://vinpearl.com/vi/vinwonders-nam-hoi-an",
    ],
    "da nang": [
        "https://vinpearl.com/vi/nam-hoi-an",
    ],
}

CATEGORY_KEYWORDS = {
    "resort": ["resort", "khach san", "hotel", "villa"],
    "package": ["goi", "combo", "package", "uu dai", "voucher"],
    "policy": ["chinh sach", "huy", "hoan tien", "voucher", "dieu kien"],
}


def search_vinpearl_pages(
    keyword: str,
    *,
    destination: str | None = None,
    category: str | None = None,
    limit: int = 5,
) -> dict[str, object]:
    """Build official Vinpearl source candidates for a later crawl step.

    This tool does not claim search-result accuracy. It returns official pages
    and a site-scoped search query that should be crawled or reviewed before
    being used as evidence.
    """
    normalized_destination = normalize_text(destination or "")
    normalized_category = normalize_text(category or "")
    normalized_keyword = normalize_text(keyword)

    candidate_urls: list[str] = []
    for destination_key, urls in DESTINATION_SOURCE_HINTS.items():
        if destination_key in normalized_destination or destination_key in normalized_keyword:
            candidate_urls.extend(urls)

    if normalized_category == "package" or any(word in normalized_keyword for word in CATEGORY_KEYWORDS["package"]):
        candidate_urls.append("https://vinpearl.com/vi/uu-dai")
    if normalized_category == "policy" or any(word in normalized_keyword for word in CATEGORY_KEYWORDS["policy"]):
        candidate_urls.append("https://vinpearl.com/vi/dieu-khoan-dieu-kien")

    site_query = " ".join(part for part in [keyword, destination or "", category or ""] if part).strip()
    site_scoped_search_query = f"site:vinpearl.com {site_query}"

    deduped = list(dict.fromkeys(candidate_urls))[:limit]
    return {
        "query": site_query,
        "candidate_urls": deduped,
        "site_scoped_search_query": site_scoped_search_query,
        "site_scoped_search_url": f"https://www.google.com/search?q={quote_plus(site_scoped_search_query)}",
        "needs_verification": True,
        "next_tool": "crawl_vinpearl_page",
        "source_scope": "official_vinpearl",
    }
