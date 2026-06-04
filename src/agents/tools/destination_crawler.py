"""General-purpose travel destination crawler.

Crawls any user-supplied URL and returns structured JSON with destination info
(name, description, highlights, activities, price info, tips).
Results are cached in data/raw/destinations/.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT_SECONDS = int(os.getenv("DESTINATION_CRAWLER_TIMEOUT_SECONDS", "90"))
DEFAULT_MAX_CHARS = int(os.getenv("DESTINATION_CRAWLER_MAX_CHARS", "32000"))
DEFAULT_CACHE_DIR = Path(os.getenv("DESTINATION_CRAWL_CACHE_DIR", "data/raw/destinations"))


# ---------------------------------------------------------------------------
# URL validation
# ---------------------------------------------------------------------------

def validate_url(url: str) -> str:
    """Validate and normalise a user-supplied URL. Accepts any http/https address."""
    candidate = url.strip()
    if not candidate:
        raise ValueError("URL is required.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported.")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed.")
    if not parsed.hostname:
        raise ValueError("Invalid URL: missing hostname.")
    return candidate


# ---------------------------------------------------------------------------
# HTML → plain text
# ---------------------------------------------------------------------------

def _html_to_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript|svg).*?>.*?</\1>", " ", html)
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?i)</(p|div|li|h[1-6]|section|article|header|footer|tr|td|th)>", "\n", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = unescape(cleaned)
    lines = [re.sub(r"\s+", " ", line).strip() for line in cleaned.splitlines()]
    return "\n".join(line for line in lines if line)


def _markdown_to_text(markdown: Any) -> str:
    if markdown is None:
        return ""
    fit = getattr(markdown, "fit_markdown", None)
    if fit:
        return str(fit)
    raw = getattr(markdown, "raw_markdown", None)
    if raw:
        return str(raw)
    return str(markdown)


# ---------------------------------------------------------------------------
# Structured extraction from plain text
# ---------------------------------------------------------------------------

_PRICE_PATTERNS = re.compile(
    r"(?:"
    r"\d[\d\.,]+\s*(?:VND|vnđ|đồng|vnd|USD|usd|\$|€|£)"
    r"|(?:VND|USD|\$|€|£)\s*\d[\d\.,]+"
    r"|(?:giá|price|rate|phí|fee|cost)[^\n]{0,80}"
    r")",
    re.IGNORECASE,
)

_SECTION_HEADERS = re.compile(
    r"^(?:#{1,4}\s+|[*_]{0,2})(.{3,80}?)(?:[*_]{0,2})\s*$",
    re.MULTILINE,
)

_BULLET_LINE = re.compile(r"^\s*[-*•▪►✓✔]\s+(.+)$", re.MULTILINE)


def _extract_structured(text: str, title: str | None, url: str) -> dict[str, Any]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # --- destination name: prefer <title>, else first meaningful line ---
    name = (title or "").strip()
    if not name and lines:
        name = lines[0][:120]

    # --- description: first 3-5 substantive lines (≥40 chars, not a header) ---
    description_lines: list[str] = []
    for line in lines[1:]:
        if len(line) >= 40 and not line.startswith("#") and not re.match(r"^[A-Z\s]{4,}$", line):
            description_lines.append(line)
        if len(description_lines) >= 4:
            break
    description = " ".join(description_lines)

    # --- bullet points → highlights / activities ---
    bullets = _BULLET_LINE.findall(text)
    activity_keywords = re.compile(
        r"(?:tour|trekk|hik|swim|dive|snorkel|kayak|surf|climb|visit|explore|sail|fish|cook|bike|camp|"
        r"du lịch|tham quan|leo|bơi|lặn|chèo|khám phá|cưỡi|câu cá|dã ngoại)",
        re.IGNORECASE,
    )
    amenity_keywords = re.compile(
        r"(?:pool|spa|gym|wifi|parking|restaurant|bar|beach|resort|hotel|villa|bungalow|"
        r"hồ bơi|nhà hàng|quán bar|bãi biển|bãi đậu xe|phòng tập)",
        re.IGNORECASE,
    )

    highlights: list[str] = []
    activities: list[str] = []
    amenities: list[str] = []

    for b in bullets:
        b = b.strip()
        if activity_keywords.search(b):
            activities.append(b)
        elif amenity_keywords.search(b):
            amenities.append(b)
        else:
            highlights.append(b)

    # --- section headers as extra highlights when few bullets found ---
    if len(highlights) < 3:
        for m in _SECTION_HEADERS.finditer(text):
            h = m.group(1).strip()
            if 5 < len(h) < 80 and h not in highlights:
                highlights.append(h)
            if len(highlights) >= 10:
                break

    # --- price info ---
    price_matches = _PRICE_PATTERNS.findall(text)
    price_info = list(dict.fromkeys(p.strip() for p in price_matches))[:8]

    # --- location hint: look for city/province/region mentions near top ---
    location_pattern = re.compile(
        r"(?:tại|ở|at|in|near|location[:\s]+|địa điểm[:\s]+)([^\n,\.]{3,60})",
        re.IGNORECASE,
    )
    loc_match = location_pattern.search("\n".join(lines[:20]))
    location = loc_match.group(1).strip() if loc_match else None

    # --- travel tips: lines containing tip/note/lưu ý keywords ---
    tip_pattern = re.compile(
        r"(?:tip|note|lưu ý|gợi ý|nên|should|recommend|best time|thời điểm|mùa)",
        re.IGNORECASE,
    )
    tips = [line for line in lines if tip_pattern.search(line) and len(line) > 20][:5]

    return {
        "name": name,
        "url": url,
        "location": location,
        "description": description,
        "highlights": highlights[:10],
        "activities": activities[:10],
        "amenities": amenities[:10],
        "price_info": price_info,
        "tips": tips,
    }


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _cache_path(url: str, *, cache_dir: str | Path = DEFAULT_CACHE_DIR) -> Path:
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "home"
    slug_source = f"{parsed.netloc}-{path}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug_source).strip("-").lower()[:120]
    return Path(cache_dir) / f"{slug}.json"


def save_destination_page(
    result: dict[str, Any],
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
) -> Path:
    url = str(result.get("url") or "")
    if not url:
        raise ValueError("Result must include 'url'.")
    out = _cache_path(url, cache_dir=cache_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {**result, "cached_at": datetime.now(timezone.utc).isoformat(), "cache_version": 1}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def load_cached_destination_page(
    url: str,
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any] | None:
    path = _cache_path(url, cache_dir=cache_dir)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_cached_destinations(
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
) -> list[dict[str, Any]]:
    directory = Path(cache_dir)
    if not directory.exists():
        return []
    pages: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            pages.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return pages


# ---------------------------------------------------------------------------
# Fallback fetcher (no crawl4ai)
# ---------------------------------------------------------------------------

def _fallback_fetch(
    url: str,
    *,
    max_chars: int,
    timeout_seconds: int,
) -> dict[str, Any] | None:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw_html = response.read().decode("utf-8", errors="ignore")
            status_code = getattr(response, "status", None)
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw_html)
    title = unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else None
    text = _html_to_text(raw_html)
    text = text[:max_chars]
    structured = _extract_structured(text, title, url)

    return {
        **structured,
        "success": bool(text),
        "status_code": status_code,
        "raw_text": text,
        "raw_truncated": len(text) == max_chars,
        "error_message": None,
        "source": "fallback_html",
    }


def _failed_result(url: str, error: Exception) -> dict[str, Any]:
    return {
        "name": None,
        "url": url,
        "success": False,
        "status_code": None,
        "raw_text": "",
        "raw_truncated": False,
        "error_message": f"{type(error).__name__}: {error}",
        "source": "destination_crawler",
    }


# ---------------------------------------------------------------------------
# Core async crawler
# ---------------------------------------------------------------------------

async def crawl_destination_page(
    url: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Crawl a travel destination URL and return structured JSON."""
    validated_url = validate_url(url)

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
    except ImportError:
        result = _fallback_fetch(validated_url, max_chars=max_chars, timeout_seconds=timeout_seconds)
        if result:
            return result
        return _failed_result(validated_url, RuntimeError("crawl4ai not installed and fallback failed"))

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        check_robots_txt=True,
        remove_overlay_elements=True,
        word_count_threshold=10,
        page_timeout=timeout_seconds * 1000,
        max_retries=1,
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=validated_url, config=run_config)
    except Exception as exc:
        fallback = _fallback_fetch(validated_url, max_chars=max_chars, timeout_seconds=timeout_seconds)
        if fallback:
            fallback["error_message"] = f"crawl4ai fallback after {type(exc).__name__}: {exc}"
            return fallback
        return _failed_result(validated_url, exc)

    text = _markdown_to_text(getattr(result, "markdown", "")).strip()
    title = (getattr(result, "metadata", None) or {}).get("title")

    if not bool(getattr(result, "success", False)) and not text:
        fallback = _fallback_fetch(validated_url, max_chars=max_chars, timeout_seconds=timeout_seconds)
        if fallback:
            fallback["error_message"] = f"crawl4ai fallback after failed result"
            return fallback

    text = text[:max_chars]
    structured = _extract_structured(text, title, validated_url)

    return {
        **structured,
        "success": bool(getattr(result, "success", False)),
        "status_code": getattr(result, "status_code", None),
        "raw_text": text,
        "raw_truncated": len(text) == max_chars,
        "error_message": getattr(result, "error_message", None),
        "source": "crawl4ai",
    }


# ---------------------------------------------------------------------------
# Sync wrappers for non-async callers
# ---------------------------------------------------------------------------

def crawl_destination_page_sync(
    url: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Synchronous wrapper — use from CLI scripts or non-async agent nodes."""
    return asyncio.run(crawl_destination_page(url, max_chars=max_chars, timeout_seconds=timeout_seconds))


def crawl_and_cache_destination(
    url: str,
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    force: bool = False,
    max_chars: int = DEFAULT_MAX_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Crawl a destination URL and persist the structured result to cache.

    Returns a dict with keys:
        from_cache  — True if result was loaded from disk
        path        — absolute path to the cache file
        result      — the structured destination data
    """
    if not force:
        cached = load_cached_destination_page(url, cache_dir=cache_dir)
        if cached:
            return {
                "from_cache": True,
                "path": str(_cache_path(validate_url(url), cache_dir=cache_dir)),
                "result": cached,
            }

    result = crawl_destination_page_sync(url, max_chars=max_chars, timeout_seconds=timeout_seconds)
    path = save_destination_page(result, cache_dir=cache_dir)
    return {"from_cache": False, "path": str(path), "result": result}


# ---------------------------------------------------------------------------
# ▼▼▼  DÁN LINK CỦA BẠN VÀO ĐÂY, SAU ĐÓ CHẠY: python destination_crawler.py
# ---------------------------------------------------------------------------

URLS_TO_CRAWL = [
    "https://www.klook.com/vi/blog/dia-diem-du-lich-da-nang/"
    "https://www.traveloka.com/vi-vn/explore/destination/canh-dep-phu-quoc/581563?id=4633158913685659889&adloc=vi-vn&kw=4633158913685659889_&gmt=a&gn=g&gd=c&gdm=&gcid=730351993185&gdp=&gdt=&gap=&pc=1&cp=4633158913685659889_VN_TA_SM_AU_AL_Google_RSA_VI_BRA_DOM_Vietnam_X_X_SunWorld_Products_X_4633158913685659889_&aid=177624594407&wid=kwl-3500001&fid=&gid=1028580&kid=_k_CjwKCAjwxITRBhBYEiwA6mZm7WfmQbpsQrOEZJnq-Nah7AIm7Yotc9W2ls7vNHIuK_IHSmEZ0-_5gRoC9aMQAvD_BwE_k_&utm_id=gfGF3x6s&ad_id=730351993185&target_id=kwl-3500001&click_id=CjwKCAjwxITRBhBYEiwA6mZm7WfmQbpsQrOEZJnq-Nah7AIm7Yotc9W2ls7vNHIuK_IHSmEZ0-_5gRoC9aMQAvD_BwE&group_id=177624594407&contexts=%7D&accessCode=vnsem&gad_source&gad_source=1&gad_campaignid=22163770942&gbraid=0AAAAADi60UmTThjI4n14-ysHZ335SMVTj&gclid=CjwKCAjwxITRBhBYEiwA6mZm7WfmQbpsQrOEZJnq-Nah7AIm7Yotc9W2ls7vNHIuK_IHSmEZ0-_5gRoC9aMQAvD_BwE",
    "https://vinpearl.com/vi/du-lich-nha-trang-nen-di-dau-goi-y-21-diem-du-lich-nha-trang-hap-dan",
    "https://vinpearl.com/vi/kinh-nghiem-du-lich-hoi-an-tron-bo-thoi-gian-di-lai-an-o-vui-choi",
    "https://www.traveloka.com/vi-vn/explore/destination/dia-diem-du-lich-hoi-an/123917",
    "https://vnexpress.net/cam-nang-du-lich-hoi-an-4446174.html",
    "https://www.vietravel.com/vn/am-thuc-kham-pha/dia-diem-du-lich-ha-long-v16076.aspx",
    "https://vnexpress.net/cam-nang-du-lich-ha-long-4457134.html"
]

if __name__ == "__main__":
    import sys

    urls = URLS_TO_CRAWL or [u.strip() for u in sys.argv[1:] if u.strip()]

    if not urls:
        print("Chưa có URL nào. Dán link vào danh sách URLS_TO_CRAWL bên trên hoặc truyền qua tham số:")
        print("  python destination_crawler.py https://link1.com https://link2.com")
        sys.exit(0)

    total = len(urls)
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{total}] Crawling: {url}")
        try:
            r = crawl_and_cache_destination(url)
        except ValueError as exc:
            print(f"  ✗ URL không hợp lệ: {exc}")
            continue

        res = r["result"]
        status = "[cache]" if r["from_cache"] else "[crawled]"
        print(f"  {status} -> {r['path']}")
        print(f"  Ten      : {res.get('name', 'N/A')}")
        print(f"  Vi tri   : {res.get('location', 'N/A')}")
        print(f"  Mo ta    : {(res.get('description') or '')[:120]}...")
        if res.get("highlights"):
            print(f"  Highlights: {res['highlights'][:3]}")
        if res.get("activities"):
            print(f"  Activities: {res['activities'][:3]}")
        if res.get("price_info"):
            print(f"  Gia      : {res['price_info'][:2]}")
        if not res.get("success"):
            print(f"  [LOI]    : {res.get('error_message')}")

    print(f"\nDone. Files saved to: {DEFAULT_CACHE_DIR}/")
