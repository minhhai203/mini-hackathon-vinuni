# Tóm tắt những gì đã thực hiện

## 1. Chatbot tư vấn du lịch Vinpearl bằng Gemini 2.5 Flash Lite

**Vấn đề ban đầu:** Dự án chỉ có một `ChatbotService` rule-based (dùng logic if/else thuần túy), không dùng LLM thực sự. `LLMService` chỉ là stub rỗng.

**Những gì đã làm:**
- Cài đặt `google-genai` (SDK mới thay thế `google-generativeai` đã bị deprecated) và `httpx`
- Tích hợp model **Gemini 2.5 Flash Lite** vào `src/services/llm.py` thông qua `GeminiService`
- Chatbot có **system prompt** định nghĩa persona là nhân viên tư vấn Vinpearl — thân thiện, chuyên nghiệp, trả lời theo ngôn ngữ của khách (Việt/Anh)
- Đọc `GOOGLE_API_KEY` và `GEMINI_MODEL` từ file `.env` (xử lý riêng vì không có prefix `APP_` như các biến khác)

**File liên quan:**
- `src/services/llm.py` — GeminiService với function calling loop
- `src/config.py` — đọc env vars + parser `.env` thủ công cho non-prefixed keys

---

## 2. Tool tra thời tiết thực tế (Open-Meteo API)

**Vấn đề:** Chatbot cũ chỉ dùng `get_mock_weather_context` — dữ liệu thời tiết giả, không phản ánh thực tế.

**Những gì đã làm:**
- Tạo `src/agents/tools/weather.py` — gọi **Open-Meteo API** (miễn phí, không cần API key)
- Tool nhận 3 tham số: `destination`, `start_date`, `end_date` (định dạng YYYY-MM-DD)
- Trả về: nhiệt độ min/max, tổng lượng mưa, số ngày mưa, tốc độ gió, dự báo từng ngày, và đánh giá mức độ phù hợp du lịch (`travel_suitability`)
- Hỗ trợ tối đa **16 ngày tương lai** (giới hạn của Open-Meteo forecast API), tự động thông báo nếu ngày vượt quá phạm vi
- Map tọa độ GPS cho 4 điểm đến Vinpearl: Phú Quốc, Nha Trang, Hạ Long, Nam Hội An

**Cách hoạt động:** Gemini tự quyết định khi nào cần gọi tool này thông qua **function calling** — model nhận kết quả JSON từ API và dùng nó để đưa ra tư vấn thực tế.

**File liên quan:**
- `src/agents/tools/weather.py`

---

## 3. Gợi ý điểm đến dựa trên thời tiết (khi user chưa biết đi đâu)

**Vấn đề:** Khi người dùng không biết muốn đi đâu, chatbot chỉ hỏi thêm thông tin mà không chủ động gợi ý.

**Những gì đã làm:**
- Bổ sung vào system prompt một **quy trình bắt buộc** (mandatory flow):
  1. Nếu chưa có ngày đi → hỏi ngày
  2. Ngay khi có ngày → gọi `get_weather_forecast` **4 lần liên tiếp** cho cả 4 điểm đến: Phú Quốc, Nha Trang, Hạ Long, Nam Hội An
  3. So sánh kết quả: số ngày mưa, nhiệt độ, đánh giá phù hợp
  4. Xếp hạng và giải thích, sau đó hỏi ưu tiên của khách để tư vấn sâu hơn
- Prompt dùng từ "BẮT BUỘC" và "PHẢI" để model không bỏ qua bước tra thời tiết

**Kết quả kiểm thử:** Model gọi đúng 4 tool calls và tự tổng hợp so sánh giữa các điểm đến.

**File liên quan:**
- `src/services/llm.py` — phần system prompt

---

## 4. Định dạng hiển thị thân thiện hơn (section + emoji thay vì bảng)

**Vấn đề:** Chatbot trả kết quả so sánh dưới dạng Markdown table — khó đọc trên mobile, không thân thiện với người dùng lớn tuổi.

**Những gì đã làm:**
- Cấm dùng table/bảng trong system prompt (`KHÔNG dùng bảng/table`)
- Yêu cầu mỗi điểm đến là một **section riêng** với heading `### 🏝️ [Tên]`
- Định nghĩa bộ emoji theo điều kiện thời tiết:
  - ☀️ nắng đẹp / 🌦️ mưa rải rác / 🌧️ mưa nhiều / ⛈️ dông bão
  - ✅ lý tưởng / ⚠️ trung bình / ❌ không lý tưởng
- Điều chỉnh tone: "viết như người bạn đồng hành, không phải robot"

**File liên quan:**
- `src/services/llm.py` — phần system prompt (sau đó chuyển vào `src/providers/base.py`)

---

## 5. Provider abstraction layer (hỗ trợ nhiều LLM)

**Vấn đề:** Toàn bộ logic LLM bị gắn chặt với Gemini — người dùng khác muốn dùng OpenAI hoặc mô hình local (Ollama, LM Studio) không thể thay thế dễ dàng.

**Những gì đã làm:**

Tạo thư mục `src/providers/` với 4 file:

| File | Vai trò |
|------|---------|
| `base.py` | Abstract class `LLMProvider` + system prompt dùng chung + weather tool schema + `execute_tool()` |
| `google.py` | `GoogleProvider` — dùng `google-genai` SDK, hỗ trợ Gemini function calling |
| `openai_provider.py` | `OpenAICompatibleProvider` — dùng `openai` SDK, hỗ trợ cả OpenAI cloud lẫn local server (Ollama, LM Studio, vLLM) |
| `__init__.py` | `get_provider()` factory — đọc `LLM_PROVIDER` từ `.env` và trả về provider phù hợp |

**Cách chuyển đổi provider — chỉ cần sửa `.env`:**

```bash
# Google Gemini (mặc định)
LLM_PROVIDER=google
GOOGLE_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash-lite

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

# Ollama (local)
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama3.1

# LM Studio (local)
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=tên-model-đang-load
```

**Các file khác được cập nhật:**
- `src/services/llm.py` → shim backward-compat, re-export từ providers
- `src/services/chatbot.py` → `GeminiChatbotService` đổi tên thành `AIChatbotService`, dùng `get_provider()`
- `src/api/routes.py` → import `AIChatbotService`
- `src/config.py` → thêm `LLM_PROVIDER`, `OPENAI_*`, `LOCAL_LLM_*`
- `requirements.txt` → thêm `google-genai`, `openai`, `httpx`
- `.env.example` → cập nhật đầy đủ hướng dẫn cho cả 3 provider

---

## Tổng quan kiến trúc sau khi hoàn thiện

```
src/
├── providers/
│   ├── __init__.py          ← get_provider() factory
│   ├── base.py              ← LLMProvider (abstract) + prompt + tool schema
│   ├── google.py            ← GoogleProvider
│   └── openai_provider.py  ← OpenAICompatibleProvider (OpenAI + local)
├── agents/
│   └── tools/
│       └── weather.py       ← get_weather_forecast() — Open-Meteo API
├── services/
│   ├── llm.py               ← backward-compat shim
│   └── chatbot.py           ← AIChatbotService (dùng get_provider())
├── api/
│   └── routes.py            ← POST /api/chat
└── config.py                ← đọc tất cả env vars
```

**Luồng xử lý một request:**
```
User message
    → AIChatbotService.reply()
        → get_provider()          [đọc LLM_PROVIDER từ .env]
        → provider.chat()         [gửi message + history cho LLM]
            → LLM quyết định gọi get_weather_forecast()
            → weather.py gọi Open-Meteo API
            → LLM nhận kết quả và sinh câu trả lời
        → trả về ChatResponse
    → FastAPI route → frontend
```
