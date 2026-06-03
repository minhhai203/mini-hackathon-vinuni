"""Rule-based chatbot service that uses the project agent tools."""

from __future__ import annotations

from typing import Any

from src.agents.tools import (
    detect_realtime_claim_risk,
    format_recommendation_card,
    generate_followup_questions,
    handoff_to_human,
    rank_resort_options,
    search_vinpearl_pages,
    update_trip_profile,
    validate_user_constraints,
)
from src.agents.tools.extraction import extract_budget_amounts
from src.agents.tools.text_utils import contains_any, normalize_text


DESTINATION_ALIASES = {
    "Phu Quoc": ["phu quoc", "phú quốc"],
    "Nha Trang": ["nha trang"],
    "Ha Long": ["ha long", "hạ long"],
    "Nam Hoi An": ["nam hoi an", "nam hội an", "hoi an", "hội an", "da nang", "đà nẵng"],
}

PRIORITY_ALIASES = {
    "vui chơi cho trẻ em": ["tre em", "trẻ em", "kids", "vinwonders", "safari", "vui choi", "vui chơi"],
    "nghỉ biển": ["bien", "biển", "beach", "bai bien", "bãi biển"],
    "spa và nghỉ dưỡng nhẹ": ["spa", "nghi duong", "nghỉ dưỡng", "thu gian", "thư giãn", "yen tinh", "yên tĩnh"],
    "villa riêng tư": ["villa", "biet thu", "biệt thự", "private", "rieng tu", "riêng tư"],
    "ẩm thực và lịch nhẹ": ["am thuc", "ẩm thực", "an uong", "ăn uống", "nha hang", "nhà hàng"],
}

GROUP_KEYWORDS = ["người lớn", "nguoi lon", "trẻ em", "tre em", "bé", "be", "gia đình", "family", "cặp đôi"]
BUDGET_KEYWORDS = ["triệu", "trieu", "ngân sách", "budget", "vnd", "vnđ", "đồng", "/dem", "/đêm"]
DATE_KEYWORDS = ["ngày", "ngay", "đêm", "dem", "cuối tuần", "cuoi tuan", "tháng", "thang", "2026"]


KNOWLEDGE_BASE: list[dict[str, Any]] = [
    {
        "name": "Vinpearl Phu Quoc Resort & VinWonders Combo",
        "option_type": "stay_and_activity",
        "destinations": ["Phu Quoc"],
        "amenities": ["kids", "theme_park", "beach", "pool"],
        "best_for": ["family_with_children", "beach_holiday"],
        "trade_offs": [
            "Nhiều hoạt động nên cần lên lịch trước để tránh quá dày.",
            "Voucher, phụ thu trẻ em và vé VinWonders cần kiểm tra theo gói đặt.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Safari Phu Quoc Day Experience",
        "option_type": "activity",
        "destinations": ["Phu Quoc"],
        "amenities": ["kids", "theme_park"],
        "best_for": ["family_with_children"],
        "trade_offs": [
            "Phù hợp làm hoạt động trong ngày hơn là thay thế chỗ ở.",
            "Cần kiểm tra giờ mở cửa và combo vé theo ngày đi.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Nha Trang Island Stay",
        "option_type": "stay_and_activity",
        "destinations": ["Nha Trang"],
        "amenities": ["kids", "theme_park", "beach", "pool", "restaurant"],
        "best_for": ["family_with_children", "beach_holiday"],
        "trade_offs": [
            "Di chuyển đảo/cáp treo cần tính vào lịch trình.",
            "Nếu đi với người lớn tuổi nên chọn lịch nhẹ và kiểm tra phương án di chuyển.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Nha Trang Spa & Dining Stay",
        "option_type": "stay",
        "destinations": ["Nha Trang"],
        "amenities": ["spa", "pool", "restaurant", "beach"],
        "best_for": ["relaxed_couple_or_family"],
        "trade_offs": [
            "Ít tập trung vào vui chơi trẻ em hơn option VinWonders.",
            "Cần kiểm tra gói ăn uống/spa có bao gồm trong rate plan không.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Resort & Spa Ha Long",
        "option_type": "stay",
        "destinations": ["Ha Long"],
        "amenities": ["spa", "pool", "beach", "restaurant"],
        "best_for": ["relaxed_couple_or_family", "short_trip_from_hanoi"],
        "trade_offs": [
            "Hợp nghỉ dưỡng ngắn ngày hơn là lịch vui chơi dày.",
            "Cần kiểm tra chính sách hủy và phụ thu theo ngày cuối tuần/cao điểm.",
        ],
        "confidence": "medium",
    },
    {
        "name": "VinWonders Nam Hoi An Cultural & Family Day",
        "option_type": "activity",
        "destinations": ["Nam Hoi An"],
        "amenities": ["kids", "theme_park", "restaurant"],
        "best_for": ["family_with_children", "culture_light_activity"],
        "trade_offs": [
            "Phù hợp vui chơi trong ngày, cần ghép với chỗ ở nếu muốn nghỉ dưỡng.",
            "Nếu bay đến Đà Nẵng cần tính thêm thời gian di chuyển vào Nam Hội An.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Nam Hoi An Beach Resort",
        "option_type": "stay",
        "destinations": ["Nam Hoi An"],
        "amenities": ["beach", "pool", "restaurant", "spa"],
        "best_for": ["beach_holiday", "relaxed_couple_or_family"],
        "trade_offs": [
            "Xa trung tâm Đà Nẵng hơn, hợp nghỉ dưỡng hơn city trip.",
            "Cần kiểm tra combo phòng/vé vui chơi nếu muốn đi VinWonders.",
        ],
        "confidence": "medium",
    },
]


class ChatbotService:
    """Small deterministic assistant for the prototype chatbot."""

    def reply(self, message: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
        profile = profile or {}
        updates = parse_trip_profile(message)
        profile_update = update_trip_profile(profile, updates)
        current_profile = profile_update["profile"]

        used_tools = ["update_trip_profile", "detect_realtime_claim_risk", "validate_user_constraints"]
        realtime_risk = detect_realtime_claim_risk(message)
        validation = validate_user_constraints(current_profile)

        if realtime_risk["risk_level"] == "high":
            handoff = handoff_to_human("realtime_or_policy_claim", current_profile)
            used_tools.append("handoff_to_human")
            return {
                "reply": build_risk_reply(handoff, realtime_risk, current_profile),
                "profile": current_profile,
                "suggestions": ["Kiểm tra trên MyVinpearl", "Cho tôi ngày đi cụ thể", "Tư vấn option an toàn hơn"],
                "cards": [],
                "confidence": "low",
                "needs_followup": True,
                "used_tools": used_tools,
                "safety_notice": realtime_risk["safe_response_hint"],
            }

        if not validation["can_rank"]:
            questions = generate_followup_questions(current_profile, max_questions=4)
            used_tools.append("generate_followup_questions")
            return {
                "reply": build_followup_reply(current_profile, questions, validation),
                "profile": current_profile,
                "suggestions": questions[:3],
                "cards": [],
                "confidence": validation["confidence"],
                "needs_followup": True,
                "used_tools": used_tools,
                "safety_notice": None,
            }

        ranked = rank_resort_options(current_profile, KNOWLEDGE_BASE)
        used_tools.append("rank_resort_options")
        cards = [format_recommendation_card(option) for option in ranked["shortlist"]]
        source_candidates = search_vinpearl_pages(
            current_profile.get("priority", "resort package"),
            destination=current_profile.get("destination"),
            category="resort",
            limit=3,
        )
        used_tools.extend(["format_recommendation_card", "search_vinpearl_pages"])

        return {
            "reply": build_recommendation_reply(current_profile, cards, ranked, source_candidates),
            "profile": current_profile,
            "suggestions": ["Đổi điểm đến", "Ưu tiên vui chơi", "Ưu tiên nghỉ dưỡng nhẹ"],
            "cards": cards,
            "confidence": ranked["confidence"],
            "needs_followup": ranked["needs_followup"],
            "used_tools": used_tools,
            "safety_notice": (
                "Các gợi ý là shortlist hỗ trợ quyết định, chưa xác nhận giá/phòng trống/voucher realtime."
            ),
        }


def parse_trip_profile(message: str) -> dict[str, Any]:
    """Extract simple profile updates from a Vietnamese free-text message."""
    text = message or ""
    normalized = normalize_text(text)
    updates: dict[str, Any] = {}

    for destination, aliases in DESTINATION_ALIASES.items():
        if any(normalize_text(alias) in normalized for alias in aliases):
            updates["destination"] = destination
            break

    if contains_any(text, GROUP_KEYWORDS):
        updates["group"] = text
    if contains_any(text, BUDGET_KEYWORDS) or extract_budget_amounts(text):
        updates["budget"] = text
    if contains_any(text, DATE_KEYWORDS):
        updates["dates"] = text

    priorities = [
        priority for priority, aliases in PRIORITY_ALIASES.items() if any(normalize_text(alias) in normalized for alias in aliases)
    ]
    if priorities:
        updates["priority"] = ", ".join(dict.fromkeys(priorities))

    if contains_any(text, ["voucher", "pearl club", "hoi vien", "hội viên"]):
        updates["voucher_or_membership"] = text

    return updates


def build_followup_reply(profile: dict[str, Any], questions: list[str], validation: dict[str, Any]) -> str:
    summary = summarize_profile(profile)
    question_items = "".join(f"<li>{question}</li>" for question in questions)
    contradiction = ""
    if validation["contradictions"]:
        contradiction = "<p><strong>Lưu ý:</strong> " + " ".join(validation["contradictions"]) + "</p>"
    return (
        f"<p>Mình đã ghi nhận: {summary}</p>"
        f"{contradiction}"
        "<p>Để match chỗ ở hoặc điểm vui chơi sát hơn, bạn cho mình thêm vài thông tin:</p>"
        f"<ol>{question_items}</ol>"
    )


def build_risk_reply(handoff: dict[str, Any], risk: dict[str, Any], profile: dict[str, Any]) -> str:
    context = summarize_profile(profile)
    missing = ", ".join(risk["missing_context"])
    return (
        f"<p>Mình đã ghi nhận: {context}</p>"
        "<p><strong>Mình chưa thể xác nhận chắc chắn</strong> giá, phòng trống, voucher hoặc hủy miễn phí vì cần dữ liệu realtime.</p>"
        f"<p>Thông tin cần kiểm tra: {missing}.</p>"
        f"<p>{handoff['message']}</p>"
    )


def build_recommendation_reply(
    profile: dict[str, Any],
    cards: list[dict[str, Any]],
    ranked: dict[str, Any],
    source_candidates: dict[str, Any],
) -> str:
    summary = summarize_profile(profile)
    if not cards:
        return (
            f"<p>Mình đã ghi nhận: {summary}</p>"
            "<p>Hiện chưa có option đủ khớp. Bạn có thể đổi điểm đến hoặc nới priority để mình gợi ý lại.</p>"
        )

    card_html = "".join(
        "<div class='chat-card'>"
        f"<strong>{index}. {card['option']}</strong>"
        f"<p>{card['why_it_fits']}</p>"
        f"<p><strong>Trade-off:</strong> {' '.join(card['trade_off'])}</p>"
        f"<p><strong>Confidence:</strong> {card['confidence']}</p>"
        "</div>"
        for index, card in enumerate(cards, start=1)
    )
    source_hint = ""
    if source_candidates.get("candidate_urls"):
        source_hint = f"<p>Nguồn nên kiểm tra tiếp: {source_candidates['candidate_urls'][0]}</p>"

    return (
        f"<p>Dựa trên profile: {summary}</p>"
        "<p>Đây là shortlist mình thấy match nhất:</p>"
        f"{card_html}"
        "<p><strong>Policy guard:</strong> chưa xác nhận giá/phòng trống/voucher realtime. Trước khi đặt nên kiểm tra trên Vinpearl/MyVinpearl hoặc CSKH.</p>"
        f"{source_hint}"
        f"<p>Độ tin cậy tổng: <strong>{ranked['confidence']}</strong>.</p>"
    )


def summarize_profile(profile: dict[str, Any]) -> str:
    parts = []
    labels = {
        "destination": "điểm đến",
        "dates": "ngày/số đêm",
        "group": "nhóm đi",
        "budget": "ngân sách",
        "priority": "ưu tiên",
    }
    for field, label in labels.items():
        if profile.get(field):
            parts.append(f"{label}: {profile[field]}")
    return "; ".join(parts) if parts else "chưa có đủ thông tin chuyến đi"
