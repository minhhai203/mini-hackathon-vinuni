"""Mock travel context tools for weather, news, and review signals."""

from __future__ import annotations

from typing import Any

from src.agents.tools.text_utils import normalize_text


DESTINATION_CONTEXT = {
    "phu quoc": {
        "display_name": "Phu Quoc",
        "weather": "Nắng biển, hợp lịch vui chơi ngoài trời buổi sáng và nghỉ hồ bơi buổi chiều.",
        "temperature_c": 30,
        "ui_theme": "theme-beach",
        "news": [
            "Nhu cầu combo nghỉ dưỡng + VinWonders/Safari thường cao vào cuối tuần.",
            "Gia đình có trẻ em nên kiểm tra vé combo và phụ thu theo độ tuổi.",
        ],
        "reviews": {
            "positive": ["Nhiều hoạt động cho trẻ em", "Hợp nghỉ dưỡng khép kín", "Có biển và tiện ích vui chơi"],
            "watchouts": ["Lịch dễ bị quá dày", "Cần kiểm tra điều kiện voucher/vé combo"],
        },
    },
    "nha trang": {
        "display_name": "Nha Trang",
        "weather": "Nắng nhẹ ven biển, hợp kết hợp nghỉ đảo, hồ bơi và hoạt động VinWonders.",
        "temperature_c": 29,
        "ui_theme": "theme-sea",
        "news": [
            "Nha Trang hợp nhóm muốn vừa nghỉ biển vừa có hoạt động vui chơi.",
            "Nếu đi với người lớn tuổi nên giữ lịch nhẹ và kiểm tra phương án di chuyển.",
        ],
        "reviews": {
            "positive": ["Biển đẹp", "Nhiều lựa chọn nghỉ dưỡng", "Dễ kết hợp ăn uống và vui chơi"],
            "watchouts": ["Cần tính thời gian di chuyển đảo/cáp treo", "Nên kiểm tra gói ăn uống đi kèm"],
        },
    },
    "ha long": {
        "display_name": "Ha Long",
        "weather": "Mát hơn về chiều, hợp nghỉ dưỡng ngắn ngày và ngắm vịnh.",
        "temperature_c": 27,
        "ui_theme": "theme-bay",
        "news": [
            "Hạ Long hợp chuyến ngắn từ Hà Nội hoặc nhóm ưu tiên nghỉ dưỡng nhẹ.",
            "Cuối tuần/cao điểm nên kiểm tra phụ thu và chính sách hủy sớm.",
        ],
        "reviews": {
            "positive": ["View vịnh đẹp", "Hợp nghỉ dưỡng ngắn ngày", "Không cần lịch quá dày"],
            "watchouts": ["Ít hoạt động công viên hơn Phú Quốc/Nha Trang", "Cần kiểm tra giá cuối tuần"],
        },
    },
    "nam hoi an": {
        "display_name": "Nam Hoi An",
        "weather": "Nắng ấm, hợp lịch biển nhẹ kết hợp văn hóa và VinWonders Nam Hội An.",
        "temperature_c": 30,
        "ui_theme": "theme-heritage",
        "news": [
            "Nam Hội An hợp nhóm muốn kết hợp nghỉ biển, văn hóa và vui chơi trong ngày.",
            "Nếu bay đến Đà Nẵng cần tính thêm thời gian di chuyển.",
        ],
        "reviews": {
            "positive": ["Không gian nghỉ dưỡng rộng", "Có hoạt động văn hóa/vui chơi", "Hợp gia đình"],
            "watchouts": ["Xa trung tâm Đà Nẵng hơn", "Nên kiểm tra combo phòng + vé"],
        },
    },
}


def _resolve_destination(destination: str | None) -> dict[str, Any]:
    normalized = normalize_text(destination or "")
    if "phu quoc" in normalized:
        return DESTINATION_CONTEXT["phu quoc"]
    if "nha trang" in normalized:
        return DESTINATION_CONTEXT["nha trang"]
    if "ha long" in normalized:
        return DESTINATION_CONTEXT["ha long"]
    if "hoi an" in normalized or "da nang" in normalized:
        return DESTINATION_CONTEXT["nam hoi an"]
    return {
        "display_name": destination or "Vinpearl",
        "weather": "Chưa có điểm đến cụ thể, nên giữ lịch linh hoạt và kiểm tra thời tiết trước khi đặt.",
        "temperature_c": None,
        "ui_theme": "theme-default",
        "news": ["Cần chọn điểm đến trước để lọc resort, vui chơi và chính sách phù hợp."],
        "reviews": {
            "positive": ["Có thể cá nhân hóa khi có thêm điểm đến và ưu tiên"],
            "watchouts": ["Thiếu điểm đến làm confidence thấp"],
        },
    }


def get_mock_weather_context(destination: str | None) -> dict[str, Any]:
    context = _resolve_destination(destination)
    return {
        "destination": context["display_name"],
        "condition_summary": context["weather"],
        "temperature_c": context["temperature_c"],
        "ui_theme": context["ui_theme"],
        "source": "mock_weather_context",
    }


def get_mock_news_context(destination: str | None) -> dict[str, Any]:
    context = _resolve_destination(destination)
    return {
        "destination": context["display_name"],
        "signals": context["news"],
        "source": "mock_news_context",
    }


def get_mock_review_signals(destination: str | None) -> dict[str, Any]:
    context = _resolve_destination(destination)
    return {
        "destination": context["display_name"],
        "positive": context["reviews"]["positive"],
        "watchouts": context["reviews"]["watchouts"],
        "source": "mock_review_summary",
    }
