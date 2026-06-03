from src.services.chatbot import ChatbotService, parse_trip_profile


def test_parse_trip_profile_extracts_core_fields():
    profile = parse_trip_profile(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert profile["destination"] == "Phu Quoc"
    assert "Gia đình" in profile["group"]
    assert "15-20 triệu" in profile["budget"]
    assert "vui chơi cho trẻ em" in profile["priority"]


def test_chatbot_asks_followup_for_incomplete_profile():
    service = ChatbotService()

    result = service.reply("Tư vấn du lịch Phú Quốc")

    assert result["needs_followup"] is True
    assert result["cards"] == []
    assert "Bạn dự định đi ngày nào" in result["reply"]
    assert result["profile"]["destination"] == "Phu Quoc"
    assert "budget" not in result["profile"]


def test_chatbot_recommends_when_profile_is_complete():
    service = ChatbotService()

    result = service.reply(
        "Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em."
    )

    assert result["needs_followup"] is False
    assert result["cards"]
    assert "Phu Quoc" in result["cards"][0]["option"]
    assert "rank_resort_options" in result["used_tools"]
    assert result["safety_notice"]


def test_chatbot_refuses_realtime_confirmation():
    service = ChatbotService()

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
