#!/usr/bin/env python3
"""Crawl official Vinpearl pages on demand and save reusable JSON cache."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.tools.vinpearl_crawler import crawl_and_cache_vinpearl_page_sync


DEFAULT_URLS = [
    "https://vinpearl.com/vi/phu-quoc",
    "https://vinpearl.com/vi/nha-trang",
    "https://vinpearl.com/vi/ha-long",
    "https://vinpearl.com/vi/nam-hoi-an",
    "https://vinpearl.com/vi/uu-dai",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", help="Official vinpearl.com URLs to crawl.")
    parser.add_argument("--output-dir", default="data/raw/vinpearl", help="Directory for JSON crawl cache.")
    parser.add_argument("--force", action="store_true", help="Refresh even when a cache file already exists.")
    parser.add_argument("--max-markdown-chars", type=int, default=12000)
    parser.add_argument("--timeout-seconds", type=int, default=45)
    args = parser.parse_args()

    urls = args.urls or DEFAULT_URLS
    output_dir = Path(args.output_dir)
    summary = []

    for url in urls:
        result = crawl_and_cache_vinpearl_page_sync(
            url,
            output_dir=output_dir,
            force=args.force,
            max_markdown_chars=args.max_markdown_chars,
            timeout_seconds=args.timeout_seconds,
        )
        payload = result["result"]
        row = {
            "url": payload.get("requested_url") or payload.get("url"),
            "path": result["path"],
            "from_cache": result["from_cache"],
            "success": payload.get("success"),
            "title": payload.get("title"),
        }
        summary.append(row)
        status = "cache" if result["from_cache"] else "crawled"
        print(f"[{status}] {row['url']} -> {row['path']}")

    summary_path = output_dir / "crawl-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
