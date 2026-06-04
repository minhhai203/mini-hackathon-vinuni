"""Recommendation and formatting tools."""

from __future__ import annotations

from typing import Any

from src.agents.tools.text_utils import contains_any, normalize_text
from src.agents.tools.trip_planning import validate_user_constraints


PRIORITY_AMENITY_MAP = {
    "family": ["kids", "theme_park", "pool"],
    "children": ["kids", "theme_park", "pool"],
    "tre em": ["kids", "theme_park", "pool"],
    "vui choi": ["theme_park", "kids"],
    "beach": ["beach", "pool"],
    "bien": ["beach", "pool"],
    "spa": ["spa", "restaurant", "pool"],
    "relax": ["spa", "pool", "restaurant"],
    "nghi duong": ["spa", "pool", "beach"],
    "villa": ["villa", "pool"],
}


def _destination_matches(profile_destination: str, option: dict[str, Any]) -> bool:
    if not profile_destination:
        return True
    destinations = option.get("destinations") or []
    if not destinations:
        return True
    return any(normalize_text(profile_destination) in normalize_text(destination) for destination in destinations)


def _destination_score(profile_destination: str, option: dict[str, Any]) -> int:
    if not profile_destination:
        return 0
    destinations = option.get("destinations") or []
    if not destinations:
        return 0
    return 4 if any(normalize_text(profile_destination) in normalize_text(destination) for destination in destinations) else 0


def _priority_score(priority: str, amenities: list[str]) -> int:
    score = 0
    normalized_priority = normalize_text(priority)
    for keyword, expected_amenities in PRIORITY_AMENITY_MAP.items():
        if keyword in normalized_priority:
            score += sum(2 for amenity in expected_amenities if amenity in amenities)
    return score


def rank_resort_options(
    user_profile: dict[str, Any],
    options: list[dict[str, Any]],
    *,
    top_k: int = 3,
) -> dict[str, Any]:
    """Rank resort/package options against user constraints."""
    validation = validate_user_constraints(user_profile)
    destination = str(user_profile.get("destination") or "")
    priority = str(user_profile.get("priority") or "")

    ranked: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for option in options:
        if not _destination_matches(destination, option):
            skipped.append({"name": option.get("name") or "Unknown option", "reason": "destination_mismatch"})
            continue

        amenities = option.get("amenities") or []
        score = 1 + _destination_score(destination, option) + _priority_score(priority, amenities)
        if contains_any(str(user_profile.get("group") or ""), ["tre em", "trẻ em", "child", "family"]):
            score += 2 if "kids" in amenities or "theme_park" in amenities else 0
        if option.get("confidence") == "high":
            score += 2
        elif option.get("confidence") == "medium":
            score += 1

        ranked.append(
            {
                **option,
                "score": score,
                "rank_reason": _build_rank_reason(user_profile, option, score),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    shortlist = ranked[:top_k]
    confidence = "high" if validation["can_rank"] and shortlist else "medium"
    if validation["contradictions"] or not shortlist:
        confidence = "low"

    return {
        "shortlist": shortlist,
        "skipped": skipped,
        "confidence": confidence,
        "validation": validation,
        "needs_followup": not validation["can_rank"] or not shortlist,
    }


def _build_rank_reason(user_profile: dict[str, Any], option: dict[str, Any], score: int) -> str:
    pieces = []
    if option.get("destinations"):
        pieces.append("matches destination")
    if option.get("amenities"):
        pieces.append(f"has amenities: {', '.join(option['amenities'][:4])}")
    if user_profile.get("priority"):
        pieces.append(f"aligned with priority: {user_profile['priority']}")
    return "; ".join(pieces) if pieces else f"ranked by score {score}"


def format_recommendation_card(option: dict[str, Any], *, policy_guard: dict[str, Any] | None = None) -> dict[str, Any]:
    """Format one option into the card shape expected by the prototype."""
    policy_guard = policy_guard or {}
    policy_items = policy_guard.get("policy_items") or {}
    trade_offs = option.get("trade_offs") or []
    if not trade_offs:
        trade_offs = ["Policy, voucher, surcharge, and availability must be checked before booking."]

    return {
        "option": option.get("name") or "Vinpearl option",
        "option_type": option.get("option_type") or "recommendation",
        "destination": (option.get("destinations") or [None])[0],
        "image_url": option.get("image_url"),
        "context_badges": option.get("context_badges") or [],
        "best_for": option.get("best_for") or [],
        "why_it_fits": option.get("rank_reason") or "Matches the user's trip profile.",
        "trade_off": trade_offs,
        "policy_guard": policy_items or {
            "needs_check": [
                "Cancellation/refund, voucher eligibility, child surcharge, and realtime availability are not confirmed."
            ]
        },
        "confidence": option.get("confidence") or "medium",
        "next_step": "Review this option on Vinpearl/MyVinpearl before booking.",
    }


def compare_previous_recommendations(
    previous_shortlist: list[dict[str, Any]],
    new_shortlist: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare old and new shortlists after a correction."""
    previous_names = {item.get("name") for item in previous_shortlist}
    new_names = {item.get("name") for item in new_shortlist}

    removed = [item for item in previous_shortlist if item.get("name") not in new_names]
    added = [item for item in new_shortlist if item.get("name") not in previous_names]
    kept = [item for item in new_shortlist if item.get("name") in previous_names]

    return {
        "removed": removed,
        "added": added,
        "kept": kept,
        "summary": {
            "removed_count": len(removed),
            "added_count": len(added),
            "kept_count": len(kept),
        },
    }
