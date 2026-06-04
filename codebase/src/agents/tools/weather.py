"""Real weather forecast tool using the Open-Meteo API (no API key required)."""

from __future__ import annotations

import datetime

import httpx

VINPEARL_LOCATIONS: dict[str, dict] = {
    "Phu Quoc": {"latitude": 10.2899, "longitude": 103.9840, "name": "Phú Quốc"},
    "Nha Trang": {"latitude": 12.2388, "longitude": 109.1967, "name": "Nha Trang"},
    "Ha Long": {"latitude": 20.9101, "longitude": 107.1839, "name": "Hạ Long"},
    "Nam Hoi An": {"latitude": 15.8801, "longitude": 108.3380, "name": "Nam Hội An"},
    "Da Nang": {"latitude": 16.0544, "longitude": 108.2022, "name": "Đà Nẵng"},
    "Hoi An": {"latitude": 15.8801, "longitude": 108.3380, "name": "Hội An"},
}

# WMO weather code → Vietnamese description
_WMO_DESCRIPTIONS: dict[int, str] = {
    0: "trời trong, nắng đẹp",
    1: "chủ yếu trong xanh",
    2: "có mây một phần",
    3: "nhiều mây, u ám",
    45: "sương mù",
    48: "sương mù đặc",
    51: "mưa phùn nhẹ",
    53: "mưa phùn vừa",
    55: "mưa phùn nặng",
    61: "mưa nhẹ",
    63: "mưa vừa",
    65: "mưa to",
    80: "mưa rào nhẹ",
    81: "mưa rào vừa",
    82: "mưa rào nặng",
    95: "dông",
    96: "dông kèm mưa đá nhỏ",
    99: "dông kèm mưa đá lớn",
}

_FORECAST_MAX_DAYS = 16


def _weather_visual_for_code(code: int | None, precipitation_mm: float | None = None) -> dict[str, str]:
    if code is None:
        return {"icon": "🌦️", "icon_class": "weather-mixed", "fa_icon": "fa-cloud-sun", "label": "thay đổi"}
    if code == 0:
        return {"icon": "☀️", "icon_class": "weather-sun", "fa_icon": "fa-sun", "label": "nắng đẹp"}
    if code in {1, 2}:
        return {"icon": "🌤️", "icon_class": "weather-partly", "fa_icon": "fa-cloud-sun", "label": "nắng nhẹ, có mây"}
    if code == 3:
        return {"icon": "☁️", "icon_class": "weather-cloud", "fa_icon": "fa-cloud", "label": "nhiều mây"}
    if code in {45, 48}:
        return {"icon": "🌫️", "icon_class": "weather-fog", "fa_icon": "fa-smog", "label": "sương mù"}
    if 51 <= code <= 65 or 80 <= code <= 82:
        if precipitation_mm is not None and precipitation_mm < 2:
            return {"icon": "🌦️", "icon_class": "weather-mixed", "fa_icon": "fa-cloud-sun-rain", "label": "mưa nhẹ thoáng qua"}
        return {"icon": "🌧️", "icon_class": "weather-rain", "fa_icon": "fa-cloud-rain", "label": "có mưa"}
    if code >= 95:
        if precipitation_mm is not None and precipitation_mm < 2:
            return {"icon": "🌦️", "icon_class": "weather-mixed", "fa_icon": "fa-cloud-sun-rain", "label": "dông nhẹ, mưa ít"}
        return {"icon": "⛈️", "icon_class": "weather-storm", "fa_icon": "fa-cloud-bolt", "label": "dông/mưa lớn"}
    return {"icon": "🌦️", "icon_class": "weather-mixed", "fa_icon": "fa-cloud-sun-rain", "label": "thay đổi"}


def _wmo_icon(code: int) -> str:
    return _weather_visual_for_code(code)["icon"]


def _wmo_label(code: int) -> str:
    if code in _WMO_DESCRIPTIONS:
        return _WMO_DESCRIPTIONS[code]
    if code == 0:
        return _WMO_DESCRIPTIONS[0]
    if code in {1, 2, 3}:
        return _WMO_DESCRIPTIONS.get(code, "có mây")
    if 51 <= code <= 65 or 80 <= code <= 82:
        return "có mưa"
    if code >= 95:
        return "dông"
    return "không xác định"


def _resolve_location(destination: str) -> tuple[dict, str]:
    """Return (location_dict, canonical_key) for a destination string."""
    dest_lower = destination.lower()
    for key, loc in VINPEARL_LOCATIONS.items():
        if key.lower() in dest_lower or dest_lower in key.lower():
            return loc, key
    # Default to Phu Quoc when unrecognised
    return VINPEARL_LOCATIONS["Phu Quoc"], "Phu Quoc"


def _assess_suitability(avg_max: float | None, rainy_days: int, total_days: int, storm_days: int = 0) -> str:
    if avg_max is None or total_days == 0:
        return "Không đủ dữ liệu để đánh giá"
    if storm_days:
        return "Cần cân nhắc — có khả năng dông, nên giữ lịch linh hoạt và ưu tiên hoạt động trong nhà"
    rain_ratio = rainy_days / total_days
    if rain_ratio > 0.6:
        return "Không lý tưởng — nhiều mưa, nên cân nhắc thời gian khác hoặc chuẩn bị áo mưa"
    if rain_ratio > 0.3:
        return "Trung bình — có thể có mưa, nên mang theo áo mưa"
    if avg_max > 35:
        return "Nắng nóng — tránh hoạt động ngoài trời lúc giữa trưa, uống nhiều nước"
    if avg_max >= 28:
        return "Tốt — nắng đẹp, phù hợp cho hoạt động ngoài trời và biển"
    return "Mát mẻ — thời tiết dễ chịu"


def get_weather_forecast(destination: str, start_date: str, end_date: str) -> dict:
    """
    Fetch weather forecast for a Vinpearl destination over a date range.

    Uses the Open-Meteo public API (no key required, up to 16-day forecast).

    Args:
        destination: Destination name — Phu Quoc | Nha Trang | Ha Long | Nam Hoi An
        start_date:  ISO date string, e.g. "2026-06-10"
        end_date:    ISO date string, e.g. "2026-06-15"

    Returns:
        dict with weather summary, daily breakdown, and travel suitability.
    """
    location, loc_key = _resolve_location(destination)

    try:
        today = datetime.date.today()
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
    except ValueError as exc:
        return {"error": f"Định dạng ngày không hợp lệ: {exc}", "destination": destination}

    if end < today:
        return {
            "error": "Khoảng thời gian đã qua. Vui lòng nhập ngày trong tương lai.",
            "destination": location["name"],
        }

    # Clamp start to today; cap end to forecast window
    effective_start = max(start, today)
    max_forecast_date = today + datetime.timedelta(days=_FORECAST_MAX_DAYS)
    effective_end = min(end, max_forecast_date)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
        "timezone": "Asia/Bangkok",
        "start_date": effective_start.isoformat(),
        "end_date": effective_end.isoformat(),
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get("https://api.open-meteo.com/v1/forecast", params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"error": f"Lỗi kết nối API thời tiết: {exc}", "destination": location["name"]}

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    temp_max_list = daily.get("temperature_2m_max", [])
    temp_min_list = daily.get("temperature_2m_min", [])
    precip_list = daily.get("precipitation_sum", [])
    code_list = daily.get("weathercode", [])
    wind_list = daily.get("windspeed_10m_max", [])

    if not dates:
        return {"error": "Không có dữ liệu thời tiết cho khoảng thời gian này.", "destination": location["name"]}

    daily_summaries = [
        {
            "date": dates[i],
            "temp_max_c": temp_max_list[i] if i < len(temp_max_list) else None,
            "temp_min_c": temp_min_list[i] if i < len(temp_min_list) else None,
            "precipitation_mm": precip_list[i] if i < len(precip_list) else None,
            "condition": _wmo_label(code_list[i]) if i < len(code_list) else "không xác định",
            **_weather_visual_for_code(
                code_list[i] if i < len(code_list) else None,
                precip_list[i] if i < len(precip_list) else None,
            ),
            "windspeed_kmh": wind_list[i] if i < len(wind_list) else None,
        }
        for i in range(len(dates))
    ]

    valid_max = [t for t in temp_max_list if t is not None]
    valid_min = [t for t in temp_min_list if t is not None]
    valid_precip = [p for p in precip_list if p is not None]

    avg_max = sum(valid_max) / len(valid_max) if valid_max else None
    avg_min = sum(valid_min) / len(valid_min) if valid_min else None
    rainy_days = sum(1 for p in valid_precip if p > 5)
    storm_days = sum(1 for code in code_list if code >= 95)
    total_precip = round(sum(valid_precip), 1)
    significant_codes = [
        code
        for code, precip in zip(code_list, precip_list, strict=False)
        if precip is not None and (precip >= 2 or code < 51)
    ]
    dominant_code = significant_codes[0] if significant_codes else (code_list[0] if code_list else 2)
    visual = _weather_visual_for_code(dominant_code, total_precip)

    result: dict = {
        "destination": location["name"],
        "period": f"{effective_start.isoformat()} → {effective_end.isoformat()}",
        **visual,
        "avg_temperature": (
            f"{avg_min:.1f}°C – {avg_max:.1f}°C" if avg_max is not None and avg_min is not None else "N/A"
        ),
        "total_precipitation_mm": total_precip,
        "rainy_days": rainy_days,
        "storm_days": storm_days,
        "travel_suitability": _assess_suitability(avg_max, rainy_days, len(dates), storm_days),
        "daily_forecast": daily_summaries[:7],  # cap at 7 days for concise output
    }

    if end > max_forecast_date:
        result["note"] = (
            f"Open-Meteo chỉ cung cấp dự báo tối đa 16 ngày (đến {max_forecast_date.isoformat()}). "
            "Dữ liệu sau ngày đó chưa có sẵn."
        )

    return result
