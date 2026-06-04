"""Chatbot services: Gemini-powered (primary) and rule-based (legacy)."""

from __future__ import annotations

from html import escape
from typing import Any

from src.agents.tools import (
    detect_realtime_claim_risk,
    format_recommendation_card,
    generate_followup_questions,
    get_mock_news_context,
    get_mock_review_signals,
    get_mock_weather_context,
    handoff_to_human,
    rank_resort_options,
    search_vinpearl_pages,
    update_trip_profile,
    validate_user_constraints,
)
from src.agents.tools.extraction import extract_budget_amounts
from src.agents.tools.text_utils import contains_any, normalize_text
from src.services.llm import LLMResult, LLMService
from src.services.vinpearl_data import load_vinpearl_options_from_cache


DESTINATION_ALIASES = {
    "Phu Quoc": ["phu quoc", "phú quốc"],
    "Nha Trang": ["nha trang"],
    "Ha Long": ["ha long", "hạ long"],
    "Nam Hoi An": ["nam hoi an", "nam hội an", "hoi an", "hội an", "da nang", "đà nẵng"],
}

PRIORITY_ALIASES = {
    "vui chơi cho trẻ em": ["tre em", "trẻ em", "kids", "vinwonders", "safari", "vui choi", "vui chơi"],
    "nghỉ biển": ["bien", "biển", "beach", "bai bien", "bãi biển"],
    "spa và nghỉ dưỡng nhẹ": [
        "spa",
        "nghi duong",
        "nghỉ dưỡng",
        "thu gian",
        "thư giãn",
        "yen tinh",
        "yên tĩnh",
        "lich nhe",
        "lịch nhẹ",
        "lich trinh nhe",
        "lịch trình nhẹ",
        "di cham",
        "đi chậm",
        "ong ba",
        "ông bà",
    ],
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
        "image_url": "assets/destination-phuquoc.png",
        "context_badges": ["Stay", "VinWonders", "Beach"],
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
        "image_url": "assets/destination-phuquoc.png",
        "context_badges": ["Activity", "Safari", "Inside Vin"],
        "best_for": ["family_with_children"],
        "trade_offs": [
            "Phù hợp làm hoạt động trong ngày hơn là thay thế chỗ ở.",
            "Cần kiểm tra giờ mở cửa và combo vé theo ngày đi.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Grand World Phu Quoc Evening Walk",
        "option_type": "activity",
        "destinations": ["Phu Quoc"],
        "amenities": ["restaurant", "kids", "theme_park"],
        "image_url": "assets/hero-1.png",
        "context_badges": ["Activity", "Evening", "Outside resort"],
        "best_for": ["family_with_children", "light_evening_plan"],
        "trade_offs": [
            "Hợp đi chơi buổi tối, không thay thế chỗ ở.",
            "Nên kiểm tra phương tiện di chuyển và giờ hoạt động theo ngày đi.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Nha Trang Island Stay",
        "option_type": "stay_and_activity",
        "destinations": ["Nha Trang"],
        "amenities": ["kids", "theme_park", "beach", "pool", "restaurant"],
        "image_url": "assets/destination-nhatrang.png",
        "context_badges": ["Stay", "Island", "VinWonders"],
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
        "image_url": "assets/destination-nhatrang.png",
        "context_badges": ["Stay", "Spa", "Dining"],
        "best_for": ["relaxed_couple_or_family"],
        "trade_offs": [
            "Ít tập trung vào vui chơi trẻ em hơn option VinWonders.",
            "Cần kiểm tra gói ăn uống/spa có bao gồm trong rate plan không.",
        ],
        "confidence": "medium",
    },
    {
        "name": "VinWonders Nha Trang Day Pass",
        "option_type": "activity",
        "destinations": ["Nha Trang"],
        "amenities": ["kids", "theme_park", "beach"],
        "image_url": "assets/destination-nhatrang.png",
        "context_badges": ["Activity", "Theme park", "Inside Vin"],
        "best_for": ["family_with_children"],
        "trade_offs": [
            "Phù hợp làm điểm vui chơi chính trong ngày.",
            "Cần tính thời gian di chuyển và kiểm tra vé/combo theo ngày.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Vinpearl Resort & Spa Ha Long",
        "option_type": "stay",
        "destinations": ["Ha Long"],
        "amenities": ["spa", "pool", "beach", "restaurant"],
        "image_url": "assets/destination-halong.png",
        "context_badges": ["Stay", "Bay view", "Relax"],
        "best_for": ["relaxed_couple_or_family", "short_trip_from_hanoi"],
        "trade_offs": [
            "Hợp nghỉ dưỡng ngắn ngày hơn là lịch vui chơi dày.",
            "Cần kiểm tra chính sách hủy và phụ thu theo ngày cuối tuần/cao điểm.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Ha Long Bay Light Cruise Add-on",
        "option_type": "activity",
        "destinations": ["Ha Long"],
        "amenities": ["restaurant", "beach"],
        "image_url": "assets/destination-halong.png",
        "context_badges": ["Activity", "Bay", "Outside Vin"],
        "best_for": ["short_trip_from_hanoi", "relaxed_couple_or_family"],
        "trade_offs": [
            "Hoạt động ngoài khu Vin, cần kiểm tra lịch tàu và thời tiết.",
            "Không phù hợp nếu muốn ở hoàn toàn trong resort.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Ha Long Pool & Spa Slow Weekend",
        "option_type": "stay",
        "destinations": ["Ha Long"],
        "amenities": ["spa", "pool", "restaurant"],
        "image_url": "assets/destination-halong.png",
        "context_badges": ["Stay", "Slow trip", "Spa"],
        "best_for": ["relaxed_couple_or_family"],
        "trade_offs": [
            "Ít hoạt động trẻ em hơn Phú Quốc/Nha Trang.",
            "Nên kiểm tra phụ thu cuối tuần và điều kiện hủy.",
        ],
        "confidence": "medium",
    },
    {
        "name": "VinWonders Nam Hoi An Cultural & Family Day",
        "option_type": "activity",
        "destinations": ["Nam Hoi An"],
        "amenities": ["kids", "theme_park", "restaurant"],
        "image_url": "assets/destination-danang.png",
        "context_badges": ["Activity", "Culture", "Inside Vin"],
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
        "image_url": "assets/destination-danang.png",
        "context_badges": ["Stay", "Beach", "Relax"],
        "best_for": ["beach_holiday", "relaxed_couple_or_family"],
        "trade_offs": [
            "Xa trung tâm Đà Nẵng hơn, hợp nghỉ dưỡng hơn city trip.",
            "Cần kiểm tra combo phòng/vé vui chơi nếu muốn đi VinWonders.",
        ],
        "confidence": "medium",
    },
    {
        "name": "Hoi An Old Town Evening Add-on",
        "option_type": "activity",
        "destinations": ["Nam Hoi An"],
        "amenities": ["restaurant", "kids"],
        "image_url": "assets/destination-danang.png",
        "context_badges": ["Activity", "Old town", "Outside Vin"],
        "best_for": ["culture_light_activity", "relaxed_couple_or_family"],
        "trade_offs": [
            "Hoạt động ngoài khu Vin nên cần tính thời gian di chuyển.",
            "Nếu đi với trẻ nhỏ/người lớn tuổi nên giữ lịch nhẹ.",
        ],
        "confidence": "medium",
    },
]


class ChatbotService:
    """Small deterministic assistant for the prototype chatbot."""

    def __init__(
        self,
        llm_service: LLMService | None = None,
        *,
        crawl_cache_dir: str | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.crawl_cache_dir = crawl_cache_dir

    def reply(self, message: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
        profile = profile or {}
        updates = parse_trip_profile(message)
        profile_update = update_trip_profile(profile, updates)
        current_profile = profile_update["profile"]

        used_tools = ["update_trip_profile", "detect_realtime_claim_risk", "validate_user_constraints"]
        realtime_risk = detect_realtime_claim_risk(message)
        validation = validate_user_constraints(current_profile)
        weather_context = get_mock_weather_context(current_profile.get("destination"))
        news_context = get_mock_news_context(current_profile.get("destination"))
        review_signals = get_mock_review_signals(current_profile.get("destination"))
        travel_context = {
            "weather": weather_context,
            "news": news_context,
            "reviews": review_signals,
        }
        used_tools.extend(["get_mock_weather_context", "get_mock_news_context", "get_mock_review_signals"])

        if realtime_risk["risk_level"] == "high":
            handoff = handoff_to_human("realtime_or_policy_claim", current_profile)
            used_tools.append("handoff_to_human")
            llm_result = self.llm_service.generate_chatbot_copy(
                mode="risk",
                user_message=message,
                profile=current_profile,
                travel_context=travel_context,
                safety_notice=realtime_risk["safe_response_hint"],
            )
            used_tools.extend(llm_used_tools(llm_result))
            return {
                "reply": build_risk_reply(handoff, realtime_risk, current_profile, llm_text=llm_result.text),
                "profile": current_profile,
                "suggestions": ["Kiểm tra trên MyVinpearl", "Cho tôi ngày đi cụ thể", "Tư vấn option an toàn hơn"],
                "cards": [],
                "confidence": "low",
                "needs_followup": True,
                "used_tools": used_tools,
                "safety_notice": realtime_risk["safe_response_hint"],
                "ui_theme": weather_context["ui_theme"],
                "context": travel_context,
            }

        if not validation["can_rank"] and not can_recommend_with_partial_profile(current_profile, validation):
            questions = generate_followup_questions(current_profile, max_questions=4)
            used_tools.append("generate_followup_questions")
            llm_result = self.llm_service.generate_chatbot_copy(
                mode="followup",
                user_message=message,
                profile=current_profile,
                followup_questions=questions,
                travel_context=travel_context,
            )
            used_tools.extend(llm_used_tools(llm_result))
            return {
                "reply": build_followup_reply(current_profile, questions, validation, llm_text=llm_result.text),
                "profile": current_profile,
                "suggestions": questions[:3],
                "cards": [],
                "confidence": validation["confidence"],
                "needs_followup": True,
                "used_tools": used_tools,
                "safety_notice": None,
                "ui_theme": weather_context["ui_theme"],
                "context": travel_context,
            }

        recommendation_options = self.recommendation_options()
        if recommendation_options:
            used_tools.extend(["load_cached_vinpearl_pages", "extract_resort_info"])
            data_source = "vinpearl_crawl_cache"
        else:
            recommendation_options = KNOWLEDGE_BASE
            used_tools.append("knowledge_base_fallback")
            data_source = "knowledge_base"

        ranked = rank_resort_options(current_profile, recommendation_options)
        used_tools.append("rank_resort_options")
        cards = [
            format_recommendation_card(option, policy_guard=option.get("policy_guard"))
            for option in ranked["shortlist"]
        ]
        source_candidates = search_vinpearl_pages(
            current_profile.get("priority", "resort package"),
            destination=current_profile.get("destination"),
            category="resort",
            limit=3,
        )
        used_tools.extend(["format_recommendation_card", "search_vinpearl_pages"])
        questions = generate_followup_questions(current_profile, max_questions=2)
        used_tools.append("generate_followup_questions")
        needs_followup = ranked["needs_followup"] or bool(validation["missing_fields"])
        llm_result = self.llm_service.generate_chatbot_copy(
            mode="recommendation",
            user_message=message,
            profile=current_profile,
            cards=cards,
            followup_questions=questions if validation["missing_fields"] else [],
            travel_context=travel_context,
            safety_notice="Các gợi ý là shortlist hỗ trợ quyết định, chưa xác nhận giá/phòng trống/voucher realtime.",
        )
        used_tools.extend(llm_used_tools(llm_result))

        return {
            "reply": build_recommendation_reply(
                current_profile,
                cards,
                ranked,
                source_candidates,
                travel_context=travel_context,
                followup_questions=questions if validation["missing_fields"] else [],
                llm_text=llm_result.text,
            ),
            "profile": current_profile,
            "suggestions": ["Đổi điểm đến", "Ưu tiên vui chơi", "Ưu tiên nghỉ dưỡng nhẹ"],
            "cards": cards,
            "confidence": ranked["confidence"],
            "needs_followup": needs_followup,
            "used_tools": used_tools,
            "safety_notice": (
                "Các gợi ý là shortlist hỗ trợ quyết định, chưa xác nhận giá/phòng trống/voucher realtime."
            ),
            "ui_theme": weather_context["ui_theme"],
            "context": travel_context,
            "data_source": data_source,
        }

    def recommendation_options(self) -> list[dict[str, Any]]:
        """Prefer crawled official data when it exists, otherwise let caller fallback."""
        return load_vinpearl_options_from_cache(self.crawl_cache_dir)


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


def can_recommend_with_partial_profile(profile: dict[str, Any], validation: dict[str, Any]) -> bool:
    """Allow ranking when the core intent is clear but budget/date is uncertain."""
    missing = set(validation["missing_fields"])
    has_core_intent = bool(profile.get("destination") and profile.get("priority"))
    soft_missing_only = missing.issubset({"dates", "budget", "group"})
    return has_core_intent and soft_missing_only and not validation["contradictions"]


def llm_used_tools(result: LLMResult) -> list[str]:
    if result.used_provider:
        return ["openai_responses_api"]
    if result.error == "LLM is not configured.":
        return ["llm_fallback_not_configured"]
    return ["llm_fallback_error"]


def llm_paragraph(llm_text: str) -> str:
    if not llm_text:
        return ""
    escaped_lines = [escape(line.strip()) for line in llm_text.splitlines() if line.strip()]
    if not escaped_lines:
        return ""
    return "".join(f"<p>{line}</p>" for line in escaped_lines[:3])


def build_followup_reply(
    profile: dict[str, Any],
    questions: list[str],
    validation: dict[str, Any],
    *,
    llm_text: str = "",
) -> str:
    summary = summarize_profile(profile)
    question_items = "".join(f"<li>{escape(question)}</li>" for question in questions)
    contradiction = ""
    if validation["contradictions"]:
        contradiction = "<p><strong>Lưu ý:</strong> " + escape(" ".join(validation["contradictions"])) + "</p>"
    intro = llm_paragraph(llm_text)
    return (
        f"{intro or f'<p>Mình đã ghi nhận: {summary}</p>'}"
        f"{contradiction}"
        "<p>Để match chỗ ở hoặc điểm vui chơi sát hơn, bạn cho mình thêm vài thông tin:</p>"
        f"<ol>{question_items}</ol>"
    )


def build_risk_reply(
    handoff: dict[str, Any],
    risk: dict[str, Any],
    profile: dict[str, Any],
    *,
    llm_text: str = "",
) -> str:
    context = summarize_profile(profile)
    missing = escape(", ".join(risk["missing_context"]))
    intro = llm_paragraph(llm_text)
    return (
        f"{intro or f'<p>Mình đã ghi nhận: {context}</p>'}"
        "<p><strong>Mình chưa thể xác nhận chắc chắn</strong> giá, phòng trống, voucher hoặc hủy miễn phí vì cần dữ liệu realtime.</p>"
        f"<p>Thông tin cần kiểm tra: {missing}.</p>"
        f"<p>{escape(handoff['message'])}</p>"
    )


def build_recommendation_reply(
    profile: dict[str, Any],
    cards: list[dict[str, Any]],
    ranked: dict[str, Any],
    source_candidates: dict[str, Any],
    *,
    travel_context: dict[str, Any],
    followup_questions: list[str],
    llm_text: str = "",
) -> str:
    summary = summarize_profile(profile)
    if not cards:
        return (
            f"<p>Mình đã ghi nhận: {summary}</p>"
            "<p>Hiện chưa có option đủ khớp. Bạn có thể đổi điểm đến hoặc nới priority để mình gợi ý lại.</p>"
        )

    weather = travel_context["weather"]
    reviews = travel_context["reviews"]
    context_html = (
        "<div class='chat-context-strip'>"
        f"<span>{escape(weather['condition_summary'])}</span>"
        f"<span>Review signal: {escape(', '.join(reviews['positive'][:2]))}</span>"
        "</div>"
    )
    card_html = "".join(
        "<div class='chat-card'>"
        f"{build_card_image(card)}"
        "<div class='chat-card-content'>"
        f"<div class='chat-card-kicker'>{escape(card.get('option_type', 'recommendation'))} · {escape(card.get('destination') or 'Vinpearl')}</div>"
        f"<strong>{index}. {escape(card['option'])}</strong>"
        f"<div class='chat-card-badges'>{build_badges(card.get('context_badges') or [])}</div>"
        f"<p>{escape(card['why_it_fits'])}</p>"
        f"<p><strong>Trade-off:</strong> {escape(' '.join(card['trade_off']))}</p>"
        f"<p><strong>Confidence:</strong> {escape(card['confidence'])}</p>"
        "</div>"
        "</div>"
        for index, card in enumerate(cards, start=1)
    )
    source_hint = ""
    if source_candidates.get("candidate_urls"):
        source_hint = f"<p>Nguồn nên kiểm tra tiếp: {escape(source_candidates['candidate_urls'][0])}</p>"
    followup_html = ""
    if followup_questions:
        question_items = "".join(f"<li>{escape(question)}</li>" for question in followup_questions)
        followup_html = (
            "<p><strong>Mình vẫn có thể gợi ý trước, nhưng để match tốt hơn bạn bổ sung thêm:</strong></p>"
            f"<ol>{question_items}</ol>"
        )

    return (
        f"{llm_paragraph(llm_text) or f'<p>Dựa trên profile: {summary}</p>'}"
        f"{context_html}"
        "<p>Đây là top 3 chỗ ở/điểm vui chơi match nhất:</p>"
        f"{card_html}"
        f"{followup_html}"
        "<p><strong>Policy guard:</strong> chưa xác nhận giá/phòng trống/voucher realtime. Trước khi đặt nên kiểm tra trên Vinpearl/MyVinpearl hoặc CSKH.</p>"
        f"{source_hint}"
        f"<p>Độ tin cậy tổng: <strong>{ranked['confidence']}</strong>.</p>"
    )


def build_card_image(card: dict[str, Any]) -> str:
    image_url = card.get("image_url")
    if not image_url:
        return ""
    return f"<img class='chat-card-image' src='{escape(image_url)}' alt='{escape(card['option'])}'>"


def build_badges(badges: list[str]) -> str:
    return "".join(f"<span>{escape(badge)}</span>" for badge in badges[:4])


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
            parts.append(f"{label}: {escape(str(profile[field]))}")
    return "; ".join(parts) if parts else "chưa có đủ thông tin chuyến đi"


# ---------------------------------------------------------------------------
# Gemini-powered chatbot (primary)
# ---------------------------------------------------------------------------

class AIChatbotService:
    """Vinpearl travel consultant — provider is selected via LLM_PROVIDER in .env."""

    def __init__(self) -> None:
        from src.providers import get_provider  # local import avoids circular deps at module load
        self._llm = get_provider()

    def reply(
        self,
        message: str,
        profile: dict[str, Any] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        profile = profile or {}

        # Extract profile fields from the new message (reuse existing parser)
        updates = parse_trip_profile(message)
        profile_result = update_trip_profile(profile, updates)
        current_profile = profile_result["profile"]

        reply_text, used_tools, context_data = self._llm.chat(message, history=history)

        destination = current_profile.get("destination")
        weather_context = get_mock_weather_context(destination)

        context: dict[str, Any] = {}
        if "get_weather_forecast" in context_data:
            context["weather_forecast"] = context_data["get_weather_forecast"]

        return {
            "reply": reply_text,
            "profile": current_profile,
            "suggestions": _default_suggestions(destination),
            "cards": [],
            "confidence": "high",
            "needs_followup": not bool(current_profile.get("destination")),
            "used_tools": used_tools,
            "safety_notice": (
                "Giá, phòng trống và voucher cần xác nhận trực tiếp tại vinpearl.com hoặc MyVinpearl."
            ),
            "ui_theme": weather_context["ui_theme"],
            "context": context,
        }


# Backward-compat alias
GeminiChatbotService = AIChatbotService


def _default_suggestions(destination: str | None) -> list[str]:
    if destination == "Phu Quoc":
        return ["Xem gói VinWonders Phú Quốc", "Thời tiết Phú Quốc tháng tới?", "Combo gia đình có trẻ em"]
    if destination == "Nha Trang":
        return ["Gói spa Nha Trang", "Thời tiết Nha Trang tuần này?", "VinWonders Nha Trang"]
    if destination == "Ha Long":
        return ["Nghỉ dưỡng Hạ Long cuối tuần", "Thời tiết Hạ Long?", "Cruise add-on Hạ Long"]
    if destination == "Nam Hoi An":
        return ["VinWonders Nam Hội An", "Thời tiết Đà Nẵng?", "Kết hợp Hội An cổ trấn"]
    return ["Tư vấn Phú Quốc", "Tư vấn Nha Trang", "So sánh các điểm đến Vinpearl"]
