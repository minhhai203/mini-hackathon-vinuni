"""Vinpearl recommendation data source helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.agents.tools.extraction import extract_policy_guard, extract_resort_info
from src.agents.tools.vinpearl_crawler import DEFAULT_CRAWL_CACHE_DIR, load_cached_vinpearl_pages


DESTINATION_IMAGE_MAP = {
    "Phu Quoc": "assets/destination-phuquoc.png",
    "Nha Trang": "assets/destination-nhatrang.png",
    "Ha Long": "assets/destination-halong.png",
    "Nam Hoi An": "assets/destination-danang.png",
    "Da Nang": "assets/destination-danang.png",
}

AMENITY_BADGE_MAP = {
    "kids": "Family",
    "theme_park": "VinWonders",
    "beach": "Beach",
    "pool": "Pool",
    "spa": "Spa",
    "restaurant": "Dining",
    "villa": "Villa",
    "golf": "Golf",
}


def get_crawl_cache_dir() -> Path:
    """Resolve the crawl cache dir at call time so tests/env overrides work."""
    return Path(os.getenv("VINPEARL_CRAWL_CACHE_DIR", str(DEFAULT_CRAWL_CACHE_DIR)))


def load_vinpearl_options_from_cache(
    cache_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Load crawled Vinpearl pages and convert them into rankable options."""
    directory = Path(cache_dir) if cache_dir is not None else get_crawl_cache_dir()
    options: list[dict[str, Any]] = []
    for payload in load_cached_vinpearl_pages(output_dir=directory):
        option = _option_from_payload(payload)
        if option:
            options.append(option)
    return options


def _option_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    markdown = str(payload.get("markdown") or "").strip()
    if not markdown:
        return None

    source_url = str(payload.get("requested_url") or payload.get("url") or "")
    resort = extract_resort_info(markdown, source_url=source_url)
    policy = extract_policy_guard(markdown, source_url=source_url)
    name = resort.get("name") or payload.get("title") or source_url or path.stem
    destinations = resort.get("destinations") or _infer_destinations_from_url(source_url)
    amenities = resort.get("amenities") or []

    return {
        "name": name,
        "option_type": _infer_option_type(markdown, amenities),
        "destinations": destinations,
        "amenities": amenities,
        "image_url": _image_for_destination(destinations),
        "context_badges": _build_context_badges(amenities),
        "best_for": resort.get("best_for") or [],
        "trade_offs": _build_trade_offs(resort, policy),
        "confidence": resort.get("confidence") or "medium",
        "source_url": source_url,
        "data_source": "vinpearl_crawl_cache",
        "cache_path": str(payload.get("cache_path") or ""),
        "policy_guard": policy,
    }


def _infer_destinations_from_url(source_url: str) -> list[str]:
    normalized = source_url.lower()
    if "phu-quoc" in normalized:
        return ["Phu Quoc"]
    if "nha-trang" in normalized:
        return ["Nha Trang"]
    if "ha-long" in normalized:
        return ["Ha Long"]
    if "nam-hoi-an" in normalized or "hoi-an" in normalized:
        return ["Nam Hoi An"]
    if "da-nang" in normalized:
        return ["Da Nang"]
    return []


def _infer_option_type(markdown: str, amenities: list[str]) -> str:
    normalized = markdown.lower()
    if "vinwonders" in normalized or "safari" in normalized or "theme_park" in amenities:
        return "activity"
    if "villa" in amenities:
        return "villa"
    if "resort" in normalized or "khách sạn" in normalized or "hotel" in normalized:
        return "stay"
    return "recommendation"


def _image_for_destination(destinations: list[str]) -> str | None:
    for destination in destinations:
        if destination in DESTINATION_IMAGE_MAP:
            return DESTINATION_IMAGE_MAP[destination]
    return "assets/hero-1.png"


def _build_context_badges(amenities: list[str]) -> list[str]:
    badges = [AMENITY_BADGE_MAP[amenity] for amenity in amenities if amenity in AMENITY_BADGE_MAP]
    return list(dict.fromkeys(["Official crawl", *badges]))[:4]


def _build_trade_offs(resort: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    trade_offs = []
    highlights = resort.get("highlights") or []
    if highlights:
        trade_offs.append(f"Nguồn crawl nhắc tới: {highlights[0]}")
    if policy.get("policy_items"):
        trade_offs.append("Có thông tin chính sách trong nguồn crawl, vẫn cần kiểm tra theo ngày/gói đặt.")
    trade_offs.append("Giá, phòng trống, voucher và điều kiện hủy cần xác nhận lại trên Vinpearl/MyVinpearl.")
    return trade_offs
