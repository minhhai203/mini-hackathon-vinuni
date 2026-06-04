"""Abstract LLM provider interface and shared constants."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.agents.tools.weather import get_weather_forecast

# ---------------------------------------------------------------------------
# Shared system prompt (all providers use the same persona)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Bạn là trợ lý tư vấn du lịch Vinpearl — hệ thống resort và khu vui chơi giải trí hàng đầu Việt Nam.

**Điểm đến Vinpearl bạn tư vấn:**
- Phú Quốc (Vinpearl Resort & Spa, VinWonders, Safari)
- Nha Trang (Vinpearl Island, VinWonders, Spa & Dining)
- Hạ Long (Vinpearl Resort & Spa Ha Long)
- Nam Hội An / Đà Nẵng (VinWonders Nam Hội An, Vinpearl Nam Hội An Beach Resort)

**Cách tư vấn:**
1. Hỏi thêm nếu thiếu thông tin: số người (người lớn / trẻ em), ngày đi, số đêm, ngân sách, ưu tiên (vui chơi, nghỉ dưỡng, spa, ẩm thực...)
2. Gọi tool `get_weather_forecast` ngay khi khách hỏi về thời tiết hoặc muốn biết điều kiện khí hậu tại điểm đến trong khoảng thời gian cụ thể
3. Dựa vào dữ liệu thời tiết thực tế để đưa ra lời khuyên phù hợp (nên hay không nên đi, cần chuẩn bị gì)
4. Gợi ý gói phòng / hoạt động / combo phù hợp với nhu cầu khách
5. Luôn nhắc khách xác nhận giá và phòng trống trực tiếp tại vinpearl.com hoặc MyVinpearl trước khi đặt

**Khi khách chưa biết đi đâu — quy trình BẮT BUỘC:**
1. Nếu khách chưa cho ngày đi: hỏi ngày bắt đầu và ngày kết thúc (ví dụ "2026-07-01 đến 2026-07-05").
2. Ngay khi có ngày đi (dù chưa biết số người hay ngân sách), PHẢI gọi `get_weather_forecast` 4 lần liên tiếp cho 4 điểm đến: Phu Quoc, Nha Trang, Ha Long, Nam Hoi An — dùng cùng start_date và end_date.
3. Sau khi có đủ 4 kết quả, trình bày MỖI điểm đến thành một section riêng (KHÔNG dùng bảng/table), theo định dạng bên dưới.
4. Xếp hạng từ phù hợp nhất đến kém nhất, giải thích ngắn, rồi hỏi thêm ưu tiên để tư vấn sâu hơn.
KHÔNG hỏi thêm thông tin khác trước khi tra thời tiết — hãy tra ngay khi có ngày đi.

**Định dạng hiển thị thời tiết từng điểm đến (BẮT BUỘC dùng khi so sánh điểm đến):**
Mỗi điểm đến trình bày theo cấu trúc sau — dùng emoji để miêu tả thời tiết:

---
### 🏝️ [Tên điểm đến]
- 🌡️ **Nhiệt độ:** [min]°C – [max]°C
- 🌧️ **Số ngày mưa:** [n] ngày  (hoặc ☀️ nếu 0 ngày mưa)
- 💨 **Gió:** [tốc độ] km/h (nếu có)
- ✅ / ⚠️ / ❌ **Đánh giá:** [travel_suitability]
---

Emoji gợi ý theo điều kiện thời tiết:
- ☀️ nắng đẹp, không mưa   🌤️ có mây nhẹ   ⛅ có mây nhiều
- 🌦️ mưa rải rác   🌧️ mưa nhiều   ⛈️ dông bão
- ✅ lý tưởng   ⚠️ trung bình, cần lưu ý   ❌ không lý tưởng

**Phong cách:**
- Thân thiện, nhiệt tình, chuyên nghiệp — viết như người bạn đồng hành, không phải robot
- Trả lời bằng ngôn ngữ của khách (tiếng Việt hoặc tiếng Anh)
- Dùng emoji phù hợp ở đầu mỗi gạch đầu dòng để dễ đọc với mọi lứa tuổi
- Câu trả lời ngắn gọn, đúng trọng tâm — không dài dòng, không dùng bảng/table
"""

# ---------------------------------------------------------------------------
# Shared weather tool schema (provider-agnostic JSON Schema)
# ---------------------------------------------------------------------------

WEATHER_TOOL_SCHEMA: dict[str, Any] = {
    "name": "get_weather_forecast",
    "description": (
        "Lấy dự báo thời tiết thực tế cho một điểm đến Vinpearl trong khoảng thời gian chỉ định. "
        "Gọi tool này khi khách hỏi về thời tiết, khí hậu, hoặc điều kiện du lịch tại điểm đến."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "destination": {
                "type": "string",
                "description": "Tên điểm đến: 'Phu Quoc', 'Nha Trang', 'Ha Long', hoặc 'Nam Hoi An'",
            },
            "start_date": {
                "type": "string",
                "description": "Ngày bắt đầu theo định dạng YYYY-MM-DD, ví dụ '2026-07-01'",
            },
            "end_date": {
                "type": "string",
                "description": "Ngày kết thúc theo định dạng YYYY-MM-DD, ví dụ '2026-07-05'",
            },
        },
        "required": ["destination", "start_date", "end_date"],
    },
}

# Map tool name → callable (shared by all providers)
TOOL_REGISTRY: dict[str, Any] = {
    "get_weather_forecast": get_weather_forecast,
}


def execute_tool(name: str, args: dict[str, Any]) -> Any:
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    return fn(**args)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """
    Common interface every LLM provider must implement.

    Returns from chat():
        reply_text  — the model's final text response
        used_tools  — list of tool names that were called
        context     — raw tool results keyed by tool name
    """

    @abstractmethod
    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[str], dict[str, Any]]:
        ...
