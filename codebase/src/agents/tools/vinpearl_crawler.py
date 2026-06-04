"""Crawler tools for official Vinpearl web pages."""

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


ALLOWED_VINPEARL_HOSTS = {"vinpearl.com", "www.vinpearl.com"}
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("VINPEARL_CRAWLER_TIMEOUT_SECONDS", "90"))
DEFAULT_MAX_MARKDOWN_CHARS = int(os.getenv("VINPEARL_CRAWLER_MAX_MARKDOWN_CHARS", "24000"))
DEFAULT_CRAWL_CACHE_DIR = Path(os.getenv("VINPEARL_CRAWL_CACHE_DIR", "data/raw/vinpearl"))


def normalize_vinpearl_url(url: str) -> str:
    """Normalize and validate an official Vinpearl URL."""
    candidate = url.strip()
    if not candidate:
        raise ValueError("URL is required.")

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    host = parsed.hostname or ""
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported.")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed.")
    if host not in ALLOWED_VINPEARL_HOSTS:
        raise ValueError("Only official vinpearl.com pages are allowed.")

    return candidate


def _markdown_to_text(markdown: Any) -> str:
    if markdown is None:
        return ""
    if isinstance(markdown, str):
        return markdown

    fit_markdown = getattr(markdown, "fit_markdown", None)
    if fit_markdown:
        return str(fit_markdown)

    raw_markdown = getattr(markdown, "raw_markdown", None)
    if raw_markdown:
        return str(raw_markdown)

    return str(markdown)


def _html_to_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?i)</(p|div|li|h[1-6]|section|article|header|footer)>", "\n", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = unescape(cleaned)
    lines = [re.sub(r"\s+", " ", line).strip() for line in cleaned.splitlines()]
    return "\n".join(line for line in lines if line)


def _fallback_fetch_vinpearl_page(
    url: str,
    *,
    max_markdown_chars: int,
    timeout_seconds: int,
) -> dict[str, Any] | None:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw_html = response.read().decode("utf-8", errors="ignore")
            markdown = _html_to_text(raw_html)
            status_code = getattr(response, "status", None)
    except (HTTPError, URLError, TimeoutError, OSError):
        return None

    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw_html)
    title = unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else None
    return {
        "url": url,
        "requested_url": url,
        "success": bool(markdown),
        "status_code": status_code,
        "title": title,
        "markdown": markdown[:max_markdown_chars],
        "markdown_truncated": len(markdown) > max_markdown_chars,
        "error_message": None,
        "source": "official_vinpearl_fallback_html",
    }


def _failed_crawl_result(url: str, error: Exception) -> dict[str, Any]:
    return {
        "url": url,
        "requested_url": url,
        "success": False,
        "status_code": None,
        "title": None,
        "markdown": "",
        "markdown_truncated": False,
        "error_message": f"{type(error).__name__}: {error}",
        "source": "official_vinpearl",
    }


def vinpearl_cache_path(url: str, *, output_dir: str | Path = DEFAULT_CRAWL_CACHE_DIR) -> Path:
    normalized_url = normalize_vinpearl_url(url)
    parsed = urlparse(normalized_url)
    path = parsed.path.strip("/") or "home"
    slug_source = f"{parsed.netloc}-{path}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug_source).strip("-").lower()
    return Path(output_dir) / f"{slug}.json"


def save_crawled_vinpearl_page(
    crawl_result: dict[str, Any],
    *,
    output_dir: str | Path = DEFAULT_CRAWL_CACHE_DIR,
) -> Path:
    url = str(crawl_result.get("requested_url") or crawl_result.get("url") or "")
    if not url:
        raise ValueError("Crawl result must include url or requested_url.")

    output_path = vinpearl_cache_path(url, output_dir=output_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **crawl_result,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "cache_version": 1,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def load_cached_vinpearl_page(
    url: str,
    *,
    output_dir: str | Path = DEFAULT_CRAWL_CACHE_DIR,
) -> dict[str, Any] | None:
    cache_path = vinpearl_cache_path(url, output_dir=output_dir)
    if not cache_path.exists():
        return None
    return json.loads(cache_path.read_text(encoding="utf-8"))


def load_cached_vinpearl_pages(
    *,
    output_dir: str | Path = DEFAULT_CRAWL_CACHE_DIR,
) -> list[dict[str, Any]]:
    """Load all reusable Vinpearl crawl cache files from a directory."""
    directory = Path(output_dir)
    if not directory.exists():
        return []

    pages: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if path.name in {"crawl-summary.json", "catalog-index.json"}:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pages.append({**payload, "cache_path": str(path)})
    return pages


async def crawl_vinpearl_page(
    url: str,
    *,
    max_markdown_chars: int = DEFAULT_MAX_MARKDOWN_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Crawl a single official Vinpearl page and return LLM-ready markdown.

    This tool is intentionally restricted to vinpearl.com so the agent uses it
    only as a trusted source boundary for this prototype.
    """
    normalized_url = normalize_vinpearl_url(url)

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
    except ImportError as exc:  # pragma: no cover - exercised only without deps.
        raise RuntimeError(
            "crawl4ai is not installed. Run `python -m pip install -r requirements.txt` "
            "and then `crawl4ai-setup` before using this tool."
        ) from exc

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        check_robots_txt=True,
        remove_overlay_elements=True,
        word_count_threshold=10,
        page_timeout=timeout_seconds * 1000,
        max_retries=1,
    )

    async def _run_crawl() -> Any:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            return await crawler.arun(url=normalized_url, config=run_config)

    try:
        result = await _run_crawl()
    except Exception as exc:
        fallback_result = _fallback_fetch_vinpearl_page(
            normalized_url,
            max_markdown_chars=max_markdown_chars,
            timeout_seconds=timeout_seconds,
        )
        if fallback_result:
            fallback_result["error_message"] = f"crawl4ai fallback after {type(exc).__name__}: {exc}"
            return fallback_result
        return _failed_crawl_result(normalized_url, exc)

    markdown = _markdown_to_text(getattr(result, "markdown", ""))
    markdown = markdown.strip()
    if not bool(getattr(result, "success", False)) and not markdown:
        fallback_result = _fallback_fetch_vinpearl_page(
            normalized_url,
            max_markdown_chars=max_markdown_chars,
            timeout_seconds=timeout_seconds,
        )
        if fallback_result:
            fallback_result["error_message"] = f"crawl4ai fallback after failed result: {getattr(result, 'error_message', None)}"
            return fallback_result

    return {
        "url": getattr(result, "url", normalized_url),
        "requested_url": normalized_url,
        "success": bool(getattr(result, "success", False)),
        "status_code": getattr(result, "status_code", None),
        "title": (getattr(result, "metadata", None) or {}).get("title"),
        "markdown": markdown[:max_markdown_chars],
        "markdown_truncated": len(markdown) > max_markdown_chars,
        "error_message": getattr(result, "error_message", None),
        "source": "official_vinpearl",
    }


def crawl_vinpearl_page_sync(
    url: str,
    *,
    max_markdown_chars: int = DEFAULT_MAX_MARKDOWN_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Synchronous wrapper for CLI scripts or non-async agent integrations."""
    return asyncio.run(
        crawl_vinpearl_page(
            url,
            max_markdown_chars=max_markdown_chars,
            timeout_seconds=timeout_seconds,
        )
    )


def crawl_and_cache_vinpearl_page_sync(
    url: str,
    *,
    output_dir: str | Path = DEFAULT_CRAWL_CACHE_DIR,
    force: bool = False,
    max_markdown_chars: int = DEFAULT_MAX_MARKDOWN_CHARS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Crawl on demand and persist the result for team reuse."""
    cached = None if force else load_cached_vinpearl_page(url, output_dir=output_dir)
    if cached:
        return {"from_cache": True, "path": str(vinpearl_cache_path(url, output_dir=output_dir)), "result": cached}

    result = crawl_vinpearl_page_sync(
        url,
        max_markdown_chars=max_markdown_chars,
        timeout_seconds=timeout_seconds,
    )
    path = save_crawled_vinpearl_page(result, output_dir=output_dir)
    return {"from_cache": False, "path": str(path), "result": result}
