from src.services.chatbot import ChatbotService, parse_trip_profile
from src.services.llm import LLMResult, LLMService


def make_service() -> ChatbotService:
    return ChatbotService(llm_service=LLMService(enabled=False), crawl_cache_dir="tests/fixtures/no-crawl-cache")


def test_parse_trip_profile_extracts_core_fields():
    profile = parse_trip_profile(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert profile["destination"] == "Phu Quoc"
    assert "Gia đình" in profile["group"]
    assert "15-20 triệu" in profile["budget"]
    assert "vui chơi cho trẻ em" in profile["priority"]


def test_chatbot_asks_followup_for_incomplete_profile():
    service = make_service()

    result = service.reply("Tư vấn du lịch Phú Quốc")

    assert result["needs_followup"] is True
    assert result["cards"] == []
    assert "Bạn dự định đi ngày nào" in result["reply"]
    assert result["profile"]["destination"] == "Phu Quoc"
    assert "budget" not in result["profile"]


def test_chatbot_recommends_when_profile_is_complete():
    service = make_service()

    result = service.reply(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert result["needs_followup"] is False
    assert len(result["cards"]) == 3
    assert "Phu Quoc" in result["cards"][0]["option"]
    assert result["cards"][0]["image_url"]
    assert result["ui_theme"] == "theme-beach"
    assert "weather" in result["context"]
    assert "rank_resort_options" in result["used_tools"]
    assert "get_mock_weather_context" in result["used_tools"]
    assert result["safety_notice"]
    assert result["data_source"] == "knowledge_base"
    assert "knowledge_base_fallback" in result["used_tools"]


def test_chatbot_prefers_crawled_cache_when_available(tmp_path):
    cache_file = tmp_path / "vinpearl-phu-quoc.json"
    cache_file.write_text(
        """
        {
          "requested_url": "https://vinpearl.com/vi/phu-quoc",
          "success": true,
          "title": "Vinpearl Discovery Phu Quoc",
          "markdown": "# Vinpearl Discovery Phú Quốc\\nKhu resort biển cho gia đình có bãi biển, hồ bơi, VinWonders và hoạt động cho trẻ em. Voucher và phụ thu trẻ em cần kiểm tra theo từng gói."
        }
        """,
        encoding="utf-8",
    )
    service = ChatbotService(llm_service=LLMService(enabled=False), crawl_cache_dir=str(tmp_path))

    result = service.reply(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert result["data_source"] == "vinpearl_crawl_cache"
    assert "load_cached_vinpearl_pages" in result["used_tools"]
    assert "extract_resort_info" in result["used_tools"]
    assert result["cards"][0]["option"] == "Vinpearl Discovery Phú Quốc"
    assert result["cards"][0]["context_badges"][0] == "Official crawl"


def test_chatbot_can_recommend_with_uncertain_budget():
    service = make_service()

    result = service.reply("Đi Nha Trang, ưu tiên nghỉ biển và vui chơi cho trẻ em.")

    assert result["needs_followup"] is True
    assert len(result["cards"]) == 3
    assert "Ngân sách dự kiến" in result["reply"]
    assert result["ui_theme"] == "theme-sea"


def test_chatbot_understands_light_schedule_correction():
    service = make_service()

    result = service.reply(
        "lịch nhẹ",
        profile={
            "destination": "Phu Quoc",
            "dates": "Tôi muốn nghỉ 2 đêm",
            "group": "2 lớn, 2 bé",
            "budget": "10tr",
        },
    )

    assert result["needs_followup"] is False
    assert result["cards"]
    assert result["profile"]["priority"] == "spa và nghỉ dưỡng nhẹ"
    assert "Ưu tiên chính" not in result["reply"]


def test_chatbot_refuses_realtime_confirmation():
    service = make_service()

    result = service.reply(
        "Tôi muốn villa, voucher dùng được chắc chắn và còn phòng tối nay không?",
        profile={
            "destination": "Phu Quoc",
            "dates": "tối nay",
            "group": "2 người lớn",
            "budget": "20 triệu",
            "priority": "villa riêng tư",
        },
    )

    assert result["confidence"] == "low"
    assert result["needs_followup"] is True
    assert "chưa thể xác nhận chắc chắn" in result["reply"]
    assert "handoff_to_human" in result["used_tools"]


class FakeLLMService:
    def generate_chatbot_copy(self, **kwargs):
        return LLMResult(text="LLM đã viết lời dẫn cá nhân hóa.", used_provider=True, provider="openai")


def test_chatbot_uses_llm_copy_when_configured():
    service = ChatbotService(llm_service=FakeLLMService())

    result = service.reply(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert "LLM đã viết lời dẫn cá nhân hóa." in result["reply"]
    assert "openai_responses_api" in result["used_tools"]
    assert result["cards"]
