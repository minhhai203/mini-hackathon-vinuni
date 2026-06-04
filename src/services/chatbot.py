"""Chatbot services: Gemini-powered (primary) and rule-based (legacy)."""

from __future__ import annotations

import datetime
import re
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
from src.agents.tools.weather import get_weather_forecast
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
    "tham quan và khám phá": [
        "tham quan",
        "kham pha",
        "khám phá",
        "di chuyen",
        "di chuyển",
        "lich trinh",
        "lịch trình",
        "trai nghiem",
        "trải nghiệm",
    ],
    "tiết kiệm chi phí": ["gia re", "giá rẻ", "tiet kiem", "tiết kiệm", "budget thap", "budget thấp"],
}

GROUP_KEYWORDS = [
    "người lớn",
    "nguoi lon",
    "trẻ em",
    "tre em",
    "bé",
    "be",
    "gia đình",
    "family",
    "cặp đôi",
    "cap doi",
    "người yêu",
    "nguoi yeu",
    "couple",
    "đôi",
    "doi",
]
BUDGET_KEYWORDS = ["triệu", "trieu", "ngân sách", "budget", "vnd", "vnđ", "đồng", "/dem", "/đêm"]
DATE_KEYWORDS = ["ngày", "ngay", "đêm", "dem", "cuối tuần", "cuoi tuan", "tháng", "thang", "2026"]
WEATHER_INTENT_KEYWORDS = [
    "thời tiết",
    "thoi tiet",
    "trời",
    "troi",
    "mưa",
    "mua",
    "nắng",
    "nang",
    "có mây",
    "co may",
    "khí hậu",
    "khi hau",
]
SUPPORTED_DESTINATION_NAMES = "Phú Quốc, Nha Trang, Hạ Long, Nam Hội An/Đà Nẵng"
OUT_OF_SCOPE_DESTINATION_ALIASES = [
    "han quoc",
    "hàn quốc",
    "korea",
    "seoul",
    "nhat ban",
    "nhật bản",
    "japan",
    "tokyo",
    "thai lan",
    "thái lan",
    "thailand",
    "bangkok",
    "singapore",
    "malaysia",
    "paris",
    "europe",
    "châu âu",
    "chau au",
    "usa",
]
PROMPT_INJECTION_ALIASES = [
    "ignore previous",
    "ignore all previous",
    "bỏ qua hướng dẫn",
    "bo qua huong dan",
    "bỏ qua instruction",
    "bo qua instruction",
    "system prompt",
    "developer message",
    "system message",
    "prompt injection",
    "jailbreak",
    "tiết lộ prompt",
    "tiet lo prompt",
    "hiện prompt",
    "hien prompt",
    "show prompt",
    "tool schema",
    "api key",
    "secret key",
    "cách tác động đến hệ thống",
    "cach tac dong den he thong",
]
OFF_TOPIC_ALIASES = [
    "python",
    "javascript",
    "java",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "react",
    "nextjs",
    "next.js",
    "fastapi",
    "lập trình",
    "lap trinh",
    "ngôn ngữ lập trình",
    "ngon ngu lap trinh",
    "dạy tôi code",
    "day toi code",
    "dạy tôi ngôn ngữ",
    "day toi ngon ngu",
    "viết code",
    "viet code",
    "debug code",
    "bài tập code",
    "bai tap code",
]


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

    def reply(
        self,
        message: str,
        profile: dict[str, Any] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
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

        boundary = detect_chatbot_boundary_violation(message, current_profile)
        if boundary["blocked"]:
            used_tools.append("detect_chatbot_boundary_violation")
            return {
                "reply": build_boundary_reply(boundary, current_profile),
                "profile": current_profile,
                "suggestions": [
                    "Tư vấn Phú Quốc",
                    "Tư vấn Nha Trang",
                    "So sánh Hạ Long và Nam Hội An",
                ],
                "cards": [],
                "confidence": "high",
                "needs_followup": True,
                "used_tools": used_tools,
                "safety_notice": boundary["safety_notice"],
                "ui_theme": weather_context["ui_theme"],
                "context": travel_context,
            }

        if is_weather_intent(message):
            used_tools.append("detect_weather_intent")
            if not current_profile.get("destination"):
                start_date, end_date = extract_weather_date_range(message, current_profile)
                forecasts = [
                    get_weather_forecast(destination, start_date, end_date)
                    for destination in ["Phu Quoc", "Nha Trang", "Ha Long", "Nam Hoi An"]
                ]
                travel_context["weather_forecasts"] = forecasts
                used_tools.extend(["get_weather_forecast"] * len(forecasts))
                return {
                    "reply": build_weather_comparison_reply(forecasts, start_date, end_date),
                    "profile": current_profile,
                    "suggestions": ["Tôi thích biển nhẹ", "Đi cùng gia đình", "Ưu tiên ít mưa"],
                    "cards": [],
                    "confidence": "high" if any(not forecast.get("error") for forecast in forecasts) else "medium",
                    "needs_followup": True,
                    "used_tools": used_tools,
                    "safety_notice": "Dữ liệu thời tiết lấy từ Open-Meteo, chỉ hỗ trợ dự báo ngắn hạn và nên kiểm tra lại trước ngày đi.",
                    "ui_theme": weather_context["ui_theme"],
                    "context": travel_context,
                }
            start_date, end_date = extract_weather_date_range(message, current_profile)
            forecast = get_weather_forecast(current_profile["destination"], start_date, end_date)
            travel_context["weather_forecast"] = forecast
            used_tools.append("get_weather_forecast")
            return {
                "reply": build_weather_reply(forecast, current_profile),
                "profile": current_profile,
                "suggestions": ["Tư vấn lịch đi theo thời tiết", "So sánh điểm đến khác", "Gợi ý chỗ ở phù hợp"],
                "cards": [],
                "confidence": "high" if not forecast.get("error") else "medium",
                "needs_followup": bool(forecast.get("error")),
                "used_tools": used_tools,
                "safety_notice": "Dữ liệu thời tiết lấy từ Open-Meteo, chỉ hỗ trợ dự báo ngắn hạn và nên kiểm tra lại trước ngày đi.",
                "ui_theme": weather_context["ui_theme"],
                "context": travel_context,
            }

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
            questions = generate_followup_questions(current_profile, max_questions=3)
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
        if data_source == "vinpearl_crawl_cache" and len(ranked["shortlist"]) < 3:
            fill_ranked = rank_resort_options(current_profile, KNOWLEDGE_BASE)
            existing_names = {option.get("name") for option in ranked["shortlist"]}
            for option in fill_ranked["shortlist"]:
                if option.get("name") in existing_names:
                    continue
                ranked["shortlist"].append({**option, "data_source": "knowledge_base_fill"})
                existing_names.add(option.get("name"))
                if len(ranked["shortlist"]) >= 3:
                    break
            used_tools.append("knowledge_base_fill")

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


def is_weather_intent(message: str) -> bool:
    return contains_any(message, WEATHER_INTENT_KEYWORDS)


def extract_weather_date_range(message: str, profile: dict[str, Any] | None = None) -> tuple[str, str]:
    text = " ".join(str(value) for value in [message, (profile or {}).get("dates")] if value)
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    if len(dates) >= 2:
        return dates[0], dates[1]
    if len(dates) == 1:
        return dates[0], dates[0]

    today = datetime.date.today()
    normalized = normalize_text(text)
    if "ngay mai" in normalized or "ngày mai" in text:
        day = today + datetime.timedelta(days=1)
        return day.isoformat(), day.isoformat()
    if "cuoi tuan" in normalized or "cuối tuần" in text:
        days_until_saturday = (5 - today.weekday()) % 7
        saturday = today + datetime.timedelta(days=days_until_saturday or 7)
        sunday = saturday + datetime.timedelta(days=1)
        return saturday.isoformat(), sunday.isoformat()

    start = today + datetime.timedelta(days=1)
    end = start + datetime.timedelta(days=3)
    return start.isoformat(), end.isoformat()


def detect_chatbot_boundary_violation(message: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Guard the public chatbot boundary before any provider can interpret user text."""
    normalized = normalize_text(message or "")
    matched_injection = [
        alias for alias in PROMPT_INJECTION_ALIASES if normalize_text(alias) in normalized
    ]
    if matched_injection:
        return {
            "blocked": True,
            "reason": "prompt_injection_or_system_access",
            "matched": matched_injection,
            "safety_notice": "Chatbot chỉ xử lý nhu cầu tư vấn du lịch Vinpearl và không tiết lộ/chỉnh sửa hướng dẫn hệ thống.",
        }

    matched_off_topic = [
        alias for alias in OFF_TOPIC_ALIASES if normalize_text(alias) in normalized
    ]
    if matched_off_topic:
        return {
            "blocked": True,
            "reason": "off_topic_non_travel",
            "matched": matched_off_topic,
            "safety_notice": "Chatbot tập trung tư vấn chuyến đi Vinpearl; câu hỏi ngoài du lịch sẽ được chuyển hướng nhẹ nhàng.",
        }

    has_supported_destination_in_message = any(
        any(normalize_text(alias) in normalized for alias in aliases)
        for aliases in DESTINATION_ALIASES.values()
    )
    matched_out_of_scope_destination = [
        alias for alias in OUT_OF_SCOPE_DESTINATION_ALIASES if normalize_text(alias) in normalized
    ]
    if matched_out_of_scope_destination and not has_supported_destination_in_message:
        return {
            "blocked": True,
            "reason": "unsupported_destination",
            "matched": matched_out_of_scope_destination,
            "safety_notice": "Chatbot chỉ tư vấn các điểm đến Vinpearl trong phạm vi demo.",
        }

    return {"blocked": False, "reason": None, "matched": [], "safety_notice": None}


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
    if intro:
        return f"{intro}{contradiction}"

    return (
        f"<p>Mình đã ghi nhận: {summary}</p>"
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


def build_boundary_reply(boundary: dict[str, Any], profile: dict[str, Any]) -> str:
    if boundary["reason"] == "prompt_injection_or_system_access":
        return (
            "<p>Mình nghe thấy tiếng gọi từ hậu trường hệ thống, nhưng vé vào khu đó mình không bán nha.</p>"
            f"<p>Mình ở đây để giúp bạn chọn chuyến Vinpearl thật hợp gu: {escape(SUPPORTED_DESTINATION_NAMES)}. "
            "Bạn muốn đi kiểu nghỉ yên tĩnh, vui chơi hết pin, hay ăn ngon rồi chill?</p>"
        )

    if boundary["reason"] == "off_topic_non_travel":
        return (
            "<p>Mình khoanh nhẹ câu này lại nhé: Python thì mình thương, nhưng hôm nay mình đang mặc đồng phục tư vấn du lịch Vinpearl.</p>"
            f"<p>Nếu bạn muốn đổi mood sang một chuyến đi cho dễ thở hơn, mình có thể gợi ý trong các điểm: {escape(SUPPORTED_DESTINATION_NAMES)}. "
            "Bạn thích healing một mình, đi biển nhẹ, hay kiếm chỗ ăn ngon rồi thả não?</p>"
        )

    summary = summarize_profile(profile)
    return (
        "<p>Chuyến này hình như đang lăn bánh ra khỏi bản đồ Vinpearl rồi. Mình kéo nhẹ về đúng làn nhé.</p>"
        f"<p>Trong phạm vi demo, mình tư vấn tốt nhất cho: {escape(SUPPORTED_DESTINATION_NAMES)}. "
        f"Nếu vẫn muốn một chuyến hợp vibe hiện tại, mình hỏi tiếp vài câu ngắn là chốt được. Profile đang có: {summary}.</p>"
    )


def build_weather_reply(forecast: dict[str, Any], profile: dict[str, Any]) -> str:
    if forecast.get("error"):
        return (
            f"<p>Mình chưa lấy được thời tiết cho {escape(str(profile.get('destination') or 'điểm đến này'))}: "
            f"{escape(str(forecast['error']))}</p>"
            "<p>Bạn gửi giúp mình ngày theo dạng YYYY-MM-DD, ví dụ 2026-06-10 đến 2026-06-12 nhé.</p>"
        )

    daily_items = "".join(
        "<li>"
        f"{weather_icon_html(day, compact=True)} "
        f"{escape(str(day.get('date')))}: "
        f"{escape(str(day.get('condition')))}, "
        f"{escape(str(day.get('temp_min_c')))}°C-{escape(str(day.get('temp_max_c')))}°C"
        f"{', mưa ' + escape(str(day.get('precipitation_mm'))) + 'mm' if day.get('precipitation_mm') is not None else ''}"
        "</li>"
        for day in forecast.get("daily_forecast", [])[:5]
    )
    rainy_text = (
        "☀️ Không có ngày mưa đáng kể"
        if forecast.get("rainy_days", 0) == 0
        else f"🌧️ Có {escape(str(forecast.get('rainy_days')))} ngày mưa đáng kể"
    )
    note = f"<p><em>{escape(str(forecast['note']))}</em></p>" if forecast.get("note") else ""
    return (
        "<div class='weather-pick weather-pick-single'>"
        f"{weather_icon_html(forecast)}"
        "<div>"
        f"<strong>{escape(str(forecast['destination']))}: {escape(str(forecast.get('label') or 'thời tiết ổn'))}</strong>"
        f"<p>{escape(str(forecast['period']))} · {escape(str(forecast['avg_temperature']))} · {rainy_text}. "
        f"{escape(str(forecast['travel_suitability']).split('—')[0].strip())}.</p>"
        "</div>"
        "</div>"
        f"<ul class='weather-days'>{daily_items}</ul>"
        f"{note}"
        "<p>Dữ liệu này là dự báo ngắn hạn, bạn nên kiểm tra lại gần ngày đi trước khi đặt dịch vụ.</p>"
    )


def build_weather_comparison_reply(forecasts: list[dict[str, Any]], start_date: str, end_date: str) -> str:
    usable = [forecast for forecast in forecasts if not forecast.get("error")]
    if not usable:
        return (
            "<p>Mình muốn so nhanh thời tiết các điểm Vinpearl cho bạn, nhưng hiện chưa lấy được dữ liệu dự báo.</p>"
            "<p>Bạn thử gửi ngày cụ thể theo dạng YYYY-MM-DD, hoặc chọn trước một điểm như Phú Quốc/Nha Trang để mình kiểm tra lại nhé.</p>"
        )

    ranked = sorted(usable, key=weather_sort_key)
    best = ranked[0]
    best_risk_score = weather_sort_key(best)[0]
    alternatives = ranked[1:3]
    alt_html = "".join(
        "<span class='weather-alt'>"
        f"{weather_icon_html(item, compact=True)}"
        f"<span><strong>{escape(str(item['destination']))}</strong><small>{escape(weather_short_phrase(item))}</small></span>"
        "</span>"
        for item in alternatives
    )
    if best_risk_score >= 3:
        intro = (
            "<p>Mình chưa thấy điểm nào thật sự đẹp trời để chốt ngay. "
            "Nếu vẫn muốn đi trong giai đoạn này, mình sẽ chọn phương án đỡ rủi ro nhất trước.</p>"
        )
        title = f"Tạm cân nhắc {escape(str(best['destination']))}"
        reason = weather_cautious_reason(best)
    else:
        intro = "<p>Mình chọn giúp bạn trước một điểm dễ đi nhất theo thời tiết hiện tại nhé.</p>"
        title = f"Nên ưu tiên {escape(str(best['destination']))}"
        reason = weather_best_reason(best)

    return (
        f"{intro}"
        "<div class='weather-pick'>"
        f"{weather_icon_html(best)}"
        "<div>"
        f"<strong>{title}</strong>"
        f"<p>{escape(reason)}</p>"
        "</div>"
        "</div>"
        f"<p class='weather-alt-title'>Nếu muốn cân nhắc thêm:</p><div class='weather-alt-row'>{alt_html}</div>"
        "<p>Bạn muốn chuyến này thiên về nghỉ biển nhẹ, đi với gia đình, hay ưu tiên nơi ít mưa nhất? Mình sẽ chốt shortlist chỗ ở/vui chơi theo vibe đó.</p>"
    )


def weather_sort_key(forecast: dict[str, Any]) -> tuple[int, int]:
    suitability = normalize_text(str(forecast.get("travel_suitability") or ""))
    rainy_days = int(forecast.get("rainy_days") or 0)
    storm_days = int(forecast.get("storm_days") or 0)
    icon_class = str(forecast.get("icon_class") or "")
    if storm_days or "storm" in icon_class or "dong" in suitability:
        score = 4
    elif "rain" in icon_class or "mua" in suitability:
        score = 3
    elif "nang nong" in suitability:
        score = 2
    elif "tot" in suitability or "ly tuong" in suitability:
        score = 0
    elif "mat me" in suitability:
        score = 0
    elif "trung binh" in suitability:
        score = 2
    else:
        score = 1
    return score, rainy_days + storm_days


def weather_rain_phrase(forecast: dict[str, Any]) -> str:
    rainy_days = int(forecast.get("rainy_days") or 0)
    storm_days = int(forecast.get("storm_days") or 0)
    if storm_days:
        return f"{storm_days} ngày có khả năng dông"
    if rainy_days == 0:
        return "ít mưa"
    return f"{rainy_days} ngày mưa đáng chú ý"


def weather_best_reason(forecast: dict[str, Any]) -> str:
    suitability = str(forecast.get("travel_suitability", "")).split("—")[0].strip()
    return (
        f"{forecast.get('label') or 'thời tiết dễ chịu'}, "
        f"{weather_rain_phrase(forecast)}, "
        f"nhiệt độ khoảng {forecast.get('avg_temperature', 'N/A')}. "
        f"{suitability}."
    )


def weather_cautious_reason(forecast: dict[str, Any]) -> str:
    return (
        f"{forecast.get('label') or 'thời tiết thay đổi'}, "
        f"{weather_rain_phrase(forecast)}, "
        f"nhiệt độ khoảng {forecast.get('avg_temperature', 'N/A')}. "
        "Nên ưu tiên lịch trong nhà, spa/ăn uống, và tránh xếp quá nhiều hoạt động ngoài trời."
    )


def weather_short_phrase(forecast: dict[str, Any]) -> str:
    return f"{forecast.get('label') or 'ổn'} · {weather_rain_phrase(forecast)}"


def weather_icon_html(forecast: dict[str, Any], *, compact: bool = False) -> str:
    icon_class = escape(str(forecast.get("icon_class") or "weather-mixed"))
    fa_icon = escape(str(forecast.get("fa_icon") or "fa-cloud-sun-rain"))
    label = escape(str(forecast.get("label") or "thời tiết"))
    size_class = " weather-glyph-sm" if compact else ""
    return (
        f"<span class='weather-glyph {icon_class}{size_class}' aria-label='{label}'>"
        f"<i class='fa-solid {fa_icon}'></i>"
        "</span>"
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
        try:
            self._llm = get_provider()
            self._fallback_service: ChatbotService | None = None
        except Exception:
            self._llm = None
            self._fallback_service = ChatbotService()

    def reply(
        self,
        message: str,
        profile: dict[str, Any] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if self._fallback_service is not None:
            return self._fallback_service.reply(message, profile=profile)

        profile = profile or {}

        # Extract profile fields from the new message (reuse existing parser)
        updates = parse_trip_profile(message)
        profile_result = update_trip_profile(profile, updates)
        current_profile = profile_result["profile"]

        boundary = detect_chatbot_boundary_violation(message, current_profile)
        if boundary["blocked"]:
            destination = current_profile.get("destination")
            weather_context = get_mock_weather_context(destination)
            return {
                "reply": build_boundary_reply(boundary, current_profile),
                "profile": current_profile,
                "suggestions": _default_suggestions(destination),
                "cards": [],
                "confidence": "high",
                "needs_followup": True,
                "used_tools": ["update_trip_profile", "detect_chatbot_boundary_violation"],
                "safety_notice": boundary["safety_notice"],
                "ui_theme": weather_context["ui_theme"],
                "context": {},
            }

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
