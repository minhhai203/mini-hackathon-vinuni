"""Trip profile, safety, and recovery tools."""

from __future__ import annotations

from typing import Any

from src.agents.tools.extraction import extract_budget_amounts
from src.agents.tools.text_utils import contains_any, normalize_text


REQUIRED_PROFILE_FIELDS = ["destination", "dates", "group", "budget", "priority"]
REALTIME_RISK_KEYWORDS = [
    "chac chan",
    "chắc chắn",
    "con phong",
    "còn phòng",
    "dat duoc ngay",
    "đặt được ngay",
    "gia chinh xac",
    "giá chính xác",
    "huy mien phi",
    "hủy miễn phí",
    "voucher dung duoc",
    "voucher dùng được",
    "refund",
    "availability",
]
PREMIUM_KEYWORDS = ["villa", "biet thu", "biệt thự", "premium", "sang", "private", "ho boi rieng", "hồ bơi riêng"]


def validate_user_constraints(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate missing and contradictory trip constraints."""
    missing = [field for field in REQUIRED_PROFILE_FIELDS if not profile.get(field)]
    text = " ".join(str(value) for value in profile.values() if value)
    amounts = extract_budget_amounts(text)
    low_budget = bool(amounts and max(amounts) < 1_500_000)
    wants_premium = contains_any(text, PREMIUM_KEYWORDS)

    contradictions: list[str] = []
    if low_budget and wants_premium:
        contradictions.append("Budget looks low for private villa/premium stay expectations.")

    confidence = "high"
    if missing or contradictions:
        confidence = "low" if contradictions else "medium"

    return {
        "missing_fields": missing,
        "contradictions": contradictions,
        "budget_amounts_vnd": amounts,
        "confidence": confidence,
        "can_rank": not missing and not contradictions,
    }


def detect_realtime_claim_risk(user_input: str) -> dict[str, Any]:
    """Detect risky questions that require realtime source/API or human check."""
    matched_keywords = [
        keyword for keyword in REALTIME_RISK_KEYWORDS if normalize_text(keyword) in normalize_text(user_input)
    ]
    risk_level = "high" if matched_keywords else "low"
    missing_context = []
    if matched_keywords:
        missing_context = ["booking_channel", "travel_dates", "rate_plan", "voucher_code", "realtime_availability"]

    return {
        "risk_level": risk_level,
        "matched_keywords": matched_keywords,
        "missing_context": missing_context,
        "safe_response_hint": (
            "Do not confirm realtime price, availability, voucher, cancellation, or refund. "
            "Ask for missing context and suggest checking Vinpearl/MyVinpearl or CSKH."
            if matched_keywords
            else "No realtime claim risk detected."
        ),
    }


def generate_followup_questions(profile: dict[str, Any], *, max_questions: int = 4) -> list[str]:
    """Generate concise follow-up questions for missing trip fields."""
    validation = validate_user_constraints(profile)
    questions_by_field = {
        "destination": "Bạn muốn đi điểm đến nào của Vinpearl: Phú Quốc, Nha Trang, Hạ Long hay nơi khác?",
        "dates": "Bạn dự định đi ngày nào và mấy đêm?",
        "group": "Nhóm đi có bao nhiêu người lớn, trẻ em hoặc người lớn tuổi?",
        "budget": "Ngân sách dự kiến cho phòng/gói nghỉ dưỡng là khoảng bao nhiêu?",
        "priority": "Ưu tiên chính là nghỉ biển, vui chơi cho trẻ em, spa/ăn uống hay lịch nhẹ?",
    }
    questions = [questions_by_field[field] for field in validation["missing_fields"] if field in questions_by_field]
    if validation["contradictions"]:
        questions.append("Ngân sách và kỳ vọng premium đang lệch nhau; bạn muốn tăng budget hay chuyển sang option tiết kiệm hơn?")
    return questions[:max_questions]


def update_trip_profile(existing_profile: dict[str, Any], correction: dict[str, Any]) -> dict[str, Any]:
    """Apply user correction and report changed fields."""
    updated = {**existing_profile}
    changed_fields: dict[str, dict[str, Any]] = {}

    for field, new_value in correction.items():
        if new_value in {None, ""}:
            continue
        old_value = updated.get(field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            updated[field] = new_value

    return {
        "profile": updated,
        "changed_fields": changed_fields,
        "needs_rerank": bool(changed_fields),
    }


def handoff_to_human(reason: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Prepare a human handoff packet for CSKH or team review."""
    profile = profile or {}
    return {
        "handoff_required": True,
        "reason": reason,
        "recommended_channel": "Vinpearl/MyVinpearl CSKH or human review",
        "context_to_prepare": {
            "destination": profile.get("destination"),
            "dates": profile.get("dates"),
            "group": profile.get("group"),
            "budget": profile.get("budget"),
            "voucher_or_membership": profile.get("voucher_or_membership"),
        },
        "message": (
            "Thông tin này cần xác minh theo kênh đặt, ngày đi, rate plan hoặc mã ưu đãi cụ thể. "
            "Vui lòng kiểm tra trên Vinpearl/MyVinpearl hoặc gửi CSKH để xác nhận trước khi đặt."
        ),
    }
