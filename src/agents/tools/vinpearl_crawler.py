"""Crawler tools for official Vinpearl web pages."""

from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ALLOWED_VINPEARL_HOSTS = {"vinpearl.com", "www.vinpearl.com"}
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("VINPEARL_CRAWLER_TIMEOUT_SECONDS", "30"))
DEFAULT_MAX_MARKDOWN_CHARS = int(os.getenv("VINPEARL_CRAWLER_MAX_MARKDOWN_CHARS", "6000"))
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
        if path.name == "crawl-summary.json":
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
    )

    async def _run_crawl() -> Any:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            return await crawler.arun(url=normalized_url, config=run_config)

    result = await asyncio.wait_for(_run_crawl(), timeout=timeout_seconds)
    markdown = _markdown_to_text(getattr(result, "markdown", ""))
    markdown = markdown.strip()

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
