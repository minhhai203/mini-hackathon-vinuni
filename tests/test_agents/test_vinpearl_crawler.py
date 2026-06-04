import asyncio
from types import SimpleNamespace

import pytest

from src.agents.tools.vinpearl_crawler import (
    crawl_vinpearl_page,
    load_cached_vinpearl_page,
    load_cached_vinpearl_pages,
    normalize_vinpearl_url,
    save_crawled_vinpearl_page,
    vinpearl_cache_path,
)


def test_normalize_vinpearl_url_adds_https():
    assert normalize_vinpearl_url("vinpearl.com/vi") == "https://vinpearl.com/vi"


def test_normalize_vinpearl_url_rejects_non_vinpearl_domain():
    with pytest.raises(ValueError, match="vinpearl.com"):
        normalize_vinpearl_url("https://example.com")


def test_vinpearl_cache_path_is_stable(tmp_path):
    path = vinpearl_cache_path("https://vinpearl.com/vi/phu-quoc", output_dir=tmp_path)

    assert path == tmp_path / "vinpearl-com-vi-phu-quoc.json"


def test_save_and_load_cached_vinpearl_page(tmp_path):
    payload = {
        "requested_url": "https://vinpearl.com/vi/phu-quoc",
        "success": True,
        "markdown": "cached content",
    }

    saved_path = save_crawled_vinpearl_page(payload, output_dir=tmp_path)
    cached = load_cached_vinpearl_page("https://vinpearl.com/vi/phu-quoc", output_dir=tmp_path)

    assert saved_path.exists()
    assert cached is not None
    assert cached["markdown"] == "cached content"
    assert cached["cache_version"] == 1


def test_crawl_vinpearl_page_uses_crawl4ai(monkeypatch):
    calls = {}

    class FakeBrowserConfig:
        def __init__(self, **kwargs):
            calls["browser_config"] = kwargs

    class FakeCrawlerRunConfig:
        def __init__(self, **kwargs):
            calls["run_config"] = kwargs

    class FakeCacheMode:
        ENABLED = "enabled"

    class FakeAsyncWebCrawler:
        def __init__(self, config):
            calls["crawler_config"] = config

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def arun(self, url, config):
            calls["url"] = url
            calls["config"] = config
            return SimpleNamespace(
                url=url,
                success=True,
                status_code=200,
                metadata={"title": "Vinpearl test page"},
                markdown="Official Vinpearl content",
                error_message=None,
            )

    fake_crawl4ai = SimpleNamespace(
        AsyncWebCrawler=FakeAsyncWebCrawler,
        BrowserConfig=FakeBrowserConfig,
        CacheMode=FakeCacheMode,
        CrawlerRunConfig=FakeCrawlerRunConfig,
    )
    monkeypatch.setitem(__import__("sys").modules, "crawl4ai", fake_crawl4ai)

    result = asyncio.run(crawl_vinpearl_page("vinpearl.com/vi", timeout_seconds=1))

    assert calls["url"] == "https://vinpearl.com/vi"
    assert calls["browser_config"] == {"headless": True, "verbose": False}
    assert calls["run_config"]["check_robots_txt"] is True
    assert calls["run_config"]["page_timeout"] == 1000
    assert calls["run_config"]["max_retries"] == 1
    assert result["success"] is True
    assert result["title"] == "Vinpearl test page"
    assert result["markdown"] == "Official Vinpearl content"
    assert result["source"] == "official_vinpearl"


def test_load_cached_vinpearl_pages_skips_summary_and_broken_json(tmp_path):
    (tmp_path / "crawl-summary.json").write_text("[]", encoding="utf-8")
    (tmp_path / "broken.json").write_text("{bad-json", encoding="utf-8")
    (tmp_path / "vinpearl-com-vi-phu-quoc.json").write_text(
        '{"requested_url": "https://vinpearl.com/vi/phu-quoc", "markdown": "ok"}',
        encoding="utf-8",
    )

    pages = load_cached_vinpearl_pages(output_dir=tmp_path)

    assert len(pages) == 1
    assert pages[0]["requested_url"] == "https://vinpearl.com/vi/phu-quoc"
    assert pages[0]["cache_path"].endswith("vinpearl-com-vi-phu-quoc.json")


def test_crawl_vinpearl_page_returns_failed_result_when_crawler_and_fallback_fail(monkeypatch):
    class FakeBrowserConfig:
        def __init__(self, **kwargs):
            pass

    class FakeCrawlerRunConfig:
        def __init__(self, **kwargs):
            pass

    class FakeCacheMode:
        ENABLED = "enabled"

    class FakeAsyncWebCrawler:
        def __init__(self, config):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def arun(self, url, config):
            raise TimeoutError("slow page")

    fake_crawl4ai = SimpleNamespace(
        AsyncWebCrawler=FakeAsyncWebCrawler,
        BrowserConfig=FakeBrowserConfig,
        CacheMode=FakeCacheMode,
        CrawlerRunConfig=FakeCrawlerRunConfig,
    )
    monkeypatch.setitem(__import__("sys").modules, "crawl4ai", fake_crawl4ai)
    monkeypatch.setattr("src.agents.tools.vinpearl_crawler._fallback_fetch_vinpearl_page", lambda *args, **kwargs: None)

    result = asyncio.run(crawl_vinpearl_page("vinpearl.com/vi/phu-quoc", timeout_seconds=1))

    assert result["success"] is False
    assert result["requested_url"] == "https://vinpearl.com/vi/phu-quoc"
    assert "TimeoutError" in result["error_message"]
