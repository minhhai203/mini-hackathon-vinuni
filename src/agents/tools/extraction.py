"""Extraction tools for Vinpearl source content."""

from __future__ import annotations

import re
from typing import Any

from src.agents.tools.text_utils import contains_any, first_matching_lines, normalize_text


DESTINATION_KEYWORDS = {
    "Phu Quoc": ["phu quoc", "phú quốc"],
    "Nha Trang": ["nha trang"],
    "Ha Long": ["ha long", "hạ long"],
    "Nam Hoi An": ["nam hoi an", "nam hội an", "hoi an", "hội an"],
    "Da Nang": ["da nang", "đà nẵng"],
    "Hai Phong": ["hai phong", "hải phòng"],
}

AMENITY_KEYWORDS = {
    "beach": ["bien", "bai bien", "beach"],
    "pool": ["ho boi", "bể bơi", "pool"],
    "spa": ["spa", "massage", "wellness"],
    "kids": ["tre em", "trẻ em", "kids", "gia dinh", "family"],
    "theme_park": ["vinwonders", "cong vien", "công viên", "theme park"],
    "golf": ["golf"],
    "villa": ["villa", "biet thu", "biệt thự"],
    "restaurant": ["nha hang", "nhà hàng", "am thuc", "ẩm thực"],
}

POLICY_KEYWORDS = {
    "cancellation_refund": ["huy", "hủy", "hoan tien", "hoàn tiền", "refund", "cancellation"],
    "voucher_membership": ["voucher", "ma giam gia", "mã giảm giá", "pearl club", "hoi vien", "hội viên"],
    "child_surcharge": ["tre em", "trẻ em", "phu thu", "phụ thu", "extra guest", "surcharge"],
    "restriction": ["dieu kien", "điều kiện", "khong ap dung", "không áp dụng", "restriction"],
    "price_availability": ["gia", "giá", "con phong", "còn phòng", "availability", "available"],
}


def _extract_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def extract_resort_info(markdown: str, *, source_url: str | None = None) -> dict[str, Any]:
    """Extract structured resort/package signals from crawled markdown."""
    text = markdown or ""
    normalized = normalize_text(text)
    destinations = [
        destination
        for destination, keywords in DESTINATION_KEYWORDS.items()
        if any(normalize_text(keyword) in normalized for keyword in keywords)
    ]
    amenities = [
        amenity
        for amenity, keywords in AMENITY_KEYWORDS.items()
        if any(normalize_text(keyword) in normalized for keyword in keywords)
    ]

    best_for: list[str] = []
    if {"kids", "theme_park"} & set(amenities):
        best_for.append("family_with_children")
    if {"spa", "pool", "restaurant"} & set(amenities):
        best_for.append("relaxed_couple_or_family")
    if "villa" in amenities:
        best_for.append("premium_or_private_stay")
    if "beach" in amenities:
        best_for.append("beach_holiday")

    highlights = first_matching_lines(
        text,
        ["vinpearl", "resort", "villa", "vinwonders", "spa", "beach", "bien", "bai bien"],
        limit=5,
    )

    confidence = "medium" if destinations or amenities else "low"
    return {
        "name": _extract_title(text),
        "source_url": source_url,
        "destinations": destinations,
        "amenities": amenities,
        "best_for": list(dict.fromkeys(best_for)),
        "highlights": highlights,
        "confidence": confidence,
        "needs_human_review": confidence == "low",
    }


def extract_policy_guard(text: str, *, source_url: str | None = None) -> dict[str, Any]:
    """Extract policy/risk guardrails from source text."""
    policy_items: dict[str, list[str]] = {}
    for policy_name, keywords in POLICY_KEYWORDS.items():
        matches = first_matching_lines(text, keywords, limit=3)
        if matches:
            policy_items[policy_name] = matches

    missing = [policy_name for policy_name in POLICY_KEYWORDS if policy_name not in policy_items]
    confidence = "medium" if policy_items else "low"
    if len(policy_items) >= 3:
        confidence = "high"

    return {
        "source_url": source_url,
        "policy_items": policy_items,
        "missing_policy_items": missing,
        "confidence": confidence,
        "warning": (
            "Do not confirm price, availability, voucher eligibility, cancellation, or refund "
            "unless the exact booking channel, rate plan, date, and source condition are known."
        ),
    }


def extract_budget_amounts(text: str) -> list[int]:
    """Extract rough VND budget numbers from free text."""
    normalized = normalize_text(text)
    amounts: list[int] = []
    for match in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|m|k|nghin|ngan|vnd|d)", normalized):
        value = float(match.group(1).replace(",", "."))
        unit = match.group(2)
        if unit in {"trieu", "tr", "m"}:
            amounts.append(int(value * 1_000_000))
        elif unit in {"k", "nghin", "ngan"}:
            amounts.append(int(value * 1_000))
        else:
            amounts.append(int(value))
    return amounts
