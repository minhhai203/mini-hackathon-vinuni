#!/usr/bin/env python3
"""Crawl and cache richer official Vinpearl travel data for the chatbot."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.tools.vinpearl_crawler import (  # noqa: E402
    crawl_vinpearl_page_sync,
    load_cached_vinpearl_page,
    normalize_vinpearl_url,
    save_crawled_vinpearl_page,
    vinpearl_cache_path,
)


HOME_URL = "https://vinpearl.com/vi"


@dataclass(frozen=True)
class CrawlSeed:
    url: str
    name: str
    category: str
    destinations: list[str] = field(default_factory=list)
    amenities: list[str] = field(default_factory=list)
    best_for: list[str] = field(default_factory=list)
    option_type: str = "recommendation"
    summary: str = ""
    image_url: str | None = None
    context_badges: list[str] = field(default_factory=list)

    def structured(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "destinations": self.destinations,
            "amenities": self.amenities,
            "best_for": self.best_for,
            "option_type": self.option_type,
            "summary": self.summary,
            "image_url": self.image_url,
            "context_badges": self.context_badges,
            "confidence": "high",
        }


def slugify(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "d")
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()


def vinpearl_url_from_name(name: str) -> str:
    return f"https://vinpearl.com/vi/{slugify(name)}"


def hotel_seed(
    destination: str,
    name: str,
    *,
    amenities: list[str],
    best_for: list[str],
    image_url: str,
) -> CrawlSeed:
    return CrawlSeed(
        url=vinpearl_url_from_name(name),
        name=name,
        category="hotel",
        destinations=[destination],
        amenities=amenities,
        best_for=best_for,
        option_type="stay",
        summary=f"{name} thuộc nhóm khách sạn/resort Vinpearl tại {destination}, phù hợp để đưa vào shortlist lưu trú.",
        image_url=image_url,
        context_badges=["Official menu", "Stay", destination],
    )


CATALOG_SEEDS: list[CrawlSeed] = [
    CrawlSeed(
        url=HOME_URL,
        name="Vinpearl Vietnam",
        category="homepage",
        option_type="homepage",
        summary="Trang chủ Vinpearl tiếng Việt, nguồn chính để phát hiện khách sạn, trải nghiệm, ưu đãi và tin tức.",
        context_badges=["Official", "Homepage"],
    ),
    hotel_seed(
        "Phu Quoc",
        "VinHolidays Fiesta Phú Quốc",
        amenities=["restaurant", "pool", "kids"],
        best_for=["family_with_children", "budget_friendly_stay"],
        image_url="assets/destination-phuquoc.png",
    ),
    hotel_seed(
        "Phu Quoc",
        "Vinpearl Wonderworld Phú Quốc",
        amenities=["villa", "pool", "beach", "kids", "theme_park"],
        best_for=["family_with_children", "premium_or_private_stay", "beach_holiday"],
        image_url="assets/destination-phuquoc.png",
    ),
    hotel_seed(
        "Phu Quoc",
        "Vinpearl Resort & Spa Phú Quốc",
        amenities=["spa", "pool", "beach", "restaurant", "kids"],
        best_for=["family_with_children", "beach_holiday", "relaxed_couple_or_family"],
        image_url="assets/destination-phuquoc.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Hòn Tằm Resort",
        amenities=["beach", "pool", "restaurant", "spa"],
        best_for=["beach_holiday", "relaxed_couple_or_family"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Vinpearl Resort & Spa Nha Trang Bay",
        amenities=["spa", "pool", "beach", "restaurant", "kids"],
        best_for=["family_with_children", "beach_holiday", "relaxed_couple_or_family"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Vinpearl Resort Nha Trang",
        amenities=["pool", "beach", "kids", "theme_park"],
        best_for=["family_with_children", "beach_holiday"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Vinpearl Luxury Nha Trang",
        amenities=["villa", "spa", "pool", "beach", "restaurant"],
        best_for=["premium_or_private_stay", "relaxed_couple_or_family", "beach_holiday"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Vinpearl Beachfront Nha Trang",
        amenities=["beach", "restaurant", "pool"],
        best_for=["beach_holiday", "city_beach_stay"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nha Trang",
        "Vinpearl Empire Nha Trang, Affiliated by Meliá",
        amenities=["restaurant", "pool"],
        best_for=["city_beach_stay", "business_or_short_trip"],
        image_url="assets/destination-nhatrang.png",
    ),
    hotel_seed(
        "Nam Hoi An",
        "Vinpearl Resort & Golf Nam Hội An",
        amenities=["golf", "pool", "beach", "restaurant", "kids"],
        best_for=["family_with_children", "golf_trip", "beach_holiday"],
        image_url="assets/destination-danang.png",
    ),
    hotel_seed(
        "Ha Long",
        "Vinpearl Resort & Spa Hạ Long",
        amenities=["spa", "pool", "beach", "restaurant"],
        best_for=["short_trip_from_hanoi", "relaxed_couple_or_family"],
        image_url="assets/destination-halong.png",
    ),
    hotel_seed(
        "Bac Ninh",
        "Vinpearl Hotel Bắc Ninh",
        amenities=["restaurant", "pool"],
        best_for=["business_or_short_trip"],
        image_url="assets/hero-1.png",
    ),
    hotel_seed(
        "Ha Tinh",
        "Vinpearl Cua Sot Resort, Affiliated by Meliá",
        amenities=["beach", "pool", "restaurant"],
        best_for=["beach_holiday", "relaxed_couple_or_family"],
        image_url="assets/hero-2.png",
    ),
    hotel_seed(
        "Ha Tinh",
        "Vinpearl Ha Tinh, Affiliated by Meliá",
        amenities=["restaurant", "pool"],
        best_for=["business_or_short_trip"],
        image_url="assets/hero-2.png",
    ),
    hotel_seed(
        "Nghe An",
        "Vinpearl Cua Hoi Resort, Affiliated by Meliá",
        amenities=["beach", "pool", "restaurant", "spa"],
        best_for=["beach_holiday", "relaxed_couple_or_family"],
        image_url="assets/hero-2.png",
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/trai-nghiem",
        name="Trải nghiệm Vinpearl",
        category="experience",
        amenities=["kids", "theme_park", "restaurant", "spa", "golf"],
        best_for=["family_with_children", "culture_light_activity", "relaxed_couple_or_family"],
        option_type="activity",
        summary="Nhóm trải nghiệm trong hệ sinh thái Vinpearl: nghỉ dưỡng, vui chơi giải trí, ẩm thực, spa, golf và hội họp.",
        image_url="assets/hero-2.png",
        context_badges=["Official menu", "Experience"],
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/vinwonders",
        name="Vui chơi giải trí VinWonders",
        category="experience",
        amenities=["kids", "theme_park"],
        best_for=["family_with_children"],
        option_type="activity",
        summary="Chuỗi công viên chủ đề và hoạt động vui chơi giải trí trong hệ sinh thái Vinpearl.",
        image_url="assets/destination-phuquoc.png",
        context_badges=["Official menu", "VinWonders", "Activity"],
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/golf",
        name="Vinpearl Golf",
        category="experience",
        amenities=["golf", "restaurant"],
        best_for=["golf_trip", "premium_or_private_stay"],
        option_type="activity",
        summary="Trải nghiệm golf trong hệ sinh thái Vinpearl.",
        image_url="assets/hero-1.png",
        context_badges=["Official menu", "Golf"],
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/spa",
        name="Akoya Spa",
        category="experience",
        amenities=["spa", "restaurant"],
        best_for=["relaxed_couple_or_family"],
        option_type="activity",
        summary="Trải nghiệm spa và nghỉ dưỡng nhẹ trong hệ sinh thái Vinpearl.",
        image_url="assets/destination-danang.png",
        context_badges=["Official menu", "Spa"],
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/uu-dai",
        name="Ưu đãi khuyến mãi Vinpearl",
        category="offer",
        amenities=["voucher", "restaurant", "theme_park", "beach"],
        best_for=["deal_hunter", "family_with_children"],
        option_type="offer",
        summary="Trang ưu đãi khuyến mãi chính thức của Vinpearl.",
        image_url="assets/hero-1.png",
        context_badges=["Official", "Offer"],
    ),
    CrawlSeed(
        url="https://vinpearl.com/vi/tin-tuc",
        name="Tin tức du lịch Vinpearl",
        category="news",
        amenities=["restaurant", "beach", "kids"],
        best_for=["inspiration"],
        option_type="content",
        summary="Tin tức và nội dung truyền cảm hứng du lịch từ Vinpearl.",
        image_url="assets/hero-2.png",
        context_badges=["Official", "News"],
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", help="Additional official vinpearl.com URLs to crawl.")
    parser.add_argument("--output-dir", default="data/raw/vinpearl", help="Directory for JSON crawl cache.")
    parser.add_argument("--force", action="store_true", help="Refresh even when a cache file already exists.")
    parser.add_argument("--max-markdown-chars", type=int, default=24000)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--fail-fast", action="store_true", help="Stop immediately when one URL fails.")
    parser.add_argument("--no-catalog", action="store_true", help="Do not include the built-in Vinpearl menu catalog.")
    parser.add_argument("--discover-links", action="store_true", help="Try to discover extra official links from provided pages.")
    parser.add_argument("--max-pages", type=int, default=80, help="Maximum pages to crawl after catalog + discovery expansion.")
    parser.add_argument("--catalog-only", action="store_true", help="Write structured catalog cache without browser crawling.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    seeds = build_seed_list(args.urls, include_catalog=not args.no_catalog)
    if args.discover_links:
        seeds.extend(discover_extra_seeds(seeds, timeout_seconds=args.timeout_seconds))

    seeds = dedupe_seeds(seeds)[: args.max_pages]
    summary = []

    for seed in seeds:
        row = crawl_seed(
            seed,
            output_dir=output_dir,
            force=args.force,
            max_markdown_chars=args.max_markdown_chars,
            timeout_seconds=args.timeout_seconds,
            fail_fast=args.fail_fast,
            catalog_only=args.catalog_only,
        )
        summary.append(row)
        print_status(row)

    summary_path = output_dir / "crawl-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_catalog_index(output_dir, seeds, summary)
    print(f"Summary written to {summary_path}")
    print(f"Catalog index written to {output_dir / 'catalog-index.json'}")


def build_seed_list(urls: list[str], *, include_catalog: bool) -> list[CrawlSeed]:
    seeds = list(CATALOG_SEEDS) if include_catalog else []
    for url in urls:
        normalized_url = normalize_vinpearl_url(url)
        seeds.append(
            CrawlSeed(
                url=normalized_url,
                name=urlparse(normalized_url).path.strip("/") or normalized_url,
                category="manual",
                summary="Manual official Vinpearl URL supplied by developer.",
                context_badges=["Manual", "Official"],
            )
        )
    return seeds


def dedupe_seeds(seeds: list[CrawlSeed]) -> list[CrawlSeed]:
    seen: set[str] = set()
    deduped: list[CrawlSeed] = []
    for seed in seeds:
        try:
            normalized_url = normalize_vinpearl_url(seed.url)
        except ValueError:
            continue
        if normalized_url in seen:
            continue
        seen.add(normalized_url)
        deduped.append(seed)
    return deduped


def discover_extra_seeds(seeds: list[CrawlSeed], *, timeout_seconds: int) -> list[CrawlSeed]:
    discovered: list[CrawlSeed] = []
    for seed in seeds[:5]:
        try:
            payload = crawl_vinpearl_page_sync(
                seed.url,
                max_markdown_chars=50000,
                timeout_seconds=timeout_seconds,
            )
        except Exception:
            continue
        text = str(payload.get("markdown") or "")
        for url in extract_official_urls(text):
            discovered.append(
                CrawlSeed(
                    url=url,
                    name=urlparse(url).path.strip("/") or url,
                    category="discovered",
                    summary=f"Discovered from {seed.url}.",
                    context_badges=["Discovered", "Official"],
                )
            )
    return discovered


def extract_official_urls(text: str) -> list[str]:
    candidates = re.findall(r"https://(?:www\.)?vinpearl\.com/vi/[^\s)\\]\"'>]+", text)
    normalized: list[str] = []
    for url in candidates:
        clean_url = url.split("#", 1)[0].rstrip(".,;")
        try:
            normalized.append(normalize_vinpearl_url(clean_url))
        except ValueError:
            continue
    return list(dict.fromkeys(normalized))


def crawl_seed(
    seed: CrawlSeed,
    *,
    output_dir: Path,
    force: bool,
    max_markdown_chars: int,
    timeout_seconds: int,
    fail_fast: bool,
    catalog_only: bool,
) -> dict[str, Any]:
    try:
        cached = None if force else load_cached_vinpearl_page(seed.url, output_dir=output_dir)
        if cached:
            return build_summary_row(seed, cached, vinpearl_cache_path(seed.url, output_dir=output_dir), from_cache=True)

        if catalog_only:
            payload = catalog_payload(seed, crawl_payload=None, max_markdown_chars=max_markdown_chars)
        else:
            crawl_payload = crawl_vinpearl_page_sync(
                seed.url,
                max_markdown_chars=max_markdown_chars,
                timeout_seconds=timeout_seconds,
            )
            payload = catalog_payload(seed, crawl_payload=crawl_payload, max_markdown_chars=max_markdown_chars)

        path = save_crawled_vinpearl_page(payload, output_dir=output_dir)
        return build_summary_row(seed, payload, path, from_cache=False)
    except Exception as exc:
        if fail_fast:
            raise
        payload = failed_payload(seed, exc)
        path = save_crawled_vinpearl_page(payload, output_dir=output_dir)
        return build_summary_row(seed, payload, path, from_cache=False)


def catalog_payload(
    seed: CrawlSeed,
    *,
    crawl_payload: dict[str, Any] | None,
    max_markdown_chars: int,
) -> dict[str, Any]:
    structured = seed.structured()
    structured_markdown = build_structured_markdown(seed)
    crawl_payload = crawl_payload or {}
    crawl_markdown = str(crawl_payload.get("markdown") or "").strip()
    if is_noisy_or_short(crawl_markdown):
        markdown = structured_markdown
    else:
        markdown = f"{structured_markdown}\n\n## Crawled page text\n{crawl_markdown}"
    markdown = markdown[:max_markdown_chars]

    crawl_success = bool(crawl_payload.get("success"))
    return {
        **crawl_payload,
        "url": crawl_payload.get("url") or seed.url,
        "requested_url": crawl_payload.get("requested_url") or seed.url,
        "success": True,
        "crawl_success": crawl_success,
        "status_code": crawl_payload.get("status_code"),
        "title": crawl_payload.get("title") or seed.name,
        "markdown": markdown,
        "markdown_truncated": len(markdown) >= max_markdown_chars,
        "error_message": crawl_payload.get("error_message"),
        "source": "official_vinpearl_catalog_enriched",
        "structured": structured,
    }


def build_structured_markdown(seed: CrawlSeed) -> str:
    lines = [
        f"# {seed.name}",
        f"Nguồn: menu/trang chính thức Vinpearl ({seed.url})",
        f"Nhóm dữ liệu: {seed.category}",
    ]
    if seed.destinations:
        lines.append("Điểm đến: " + ", ".join(seed.destinations))
    if seed.amenities:
        lines.append("Tiện ích/trải nghiệm: " + ", ".join(seed.amenities))
    if seed.best_for:
        lines.append("Phù hợp: " + ", ".join(seed.best_for))
    if seed.summary:
        lines.append(seed.summary)
    return "\n".join(lines)


def is_noisy_or_short(markdown: str) -> bool:
    if len(markdown) < 900:
        return True
    noisy_markers = ["Vui quý khách lòng xác thực email", "Mùng 1", "Hàng ngày Hàng tuần Hàng tháng"]
    return any(marker in markdown for marker in noisy_markers)


def failed_payload(seed: CrawlSeed, exc: Exception) -> dict[str, Any]:
    return {
        "url": seed.url,
        "requested_url": seed.url,
        "success": False,
        "crawl_success": False,
        "status_code": None,
        "title": seed.name,
        "markdown": build_structured_markdown(seed),
        "markdown_truncated": False,
        "error_message": f"{type(exc).__name__}: {exc}",
        "source": "official_vinpearl_catalog_enriched",
        "structured": seed.structured(),
    }


def build_summary_row(seed: CrawlSeed, payload: dict[str, Any], path: Path, *, from_cache: bool) -> dict[str, Any]:
    return {
        "url": payload.get("requested_url") or payload.get("url") or seed.url,
        "path": str(path),
        "from_cache": from_cache,
        "success": payload.get("success"),
        "crawl_success": payload.get("crawl_success", payload.get("success")),
        "title": payload.get("title"),
        "category": seed.category,
        "destination": ", ".join(seed.destinations),
        "markdown_len": len(payload.get("markdown") or ""),
        "error_message": payload.get("error_message"),
    }


def print_status(row: dict[str, Any]) -> None:
    if row["from_cache"]:
        status = "cache"
    elif row["success"] and row.get("crawl_success"):
        status = "crawled"
    elif row["success"]:
        status = "catalog"
    else:
        status = "failed"
    print(f"[{status}] {row['category']} | {row['title']} | {row['url']} -> {row['path']}")


def write_catalog_index(output_dir: Path, seeds: list[CrawlSeed], summary: list[dict[str, Any]]) -> None:
    payload = {
        "seed_count": len(seeds),
        "success_count": sum(1 for row in summary if row.get("success")),
        "crawl_success_count": sum(1 for row in summary if row.get("crawl_success")),
        "categories": sorted({seed.category for seed in seeds}),
        "destinations": sorted({destination for seed in seeds for destination in seed.destinations}),
        "items": summary,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "catalog-index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
