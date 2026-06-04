# Mini Hackathon VinUni

## Project Structure

- `src/agents`: LangGraph agent graph, state, nodes, and tools
- `src/api`: FastAPI routes
- `src/models`: Pydantic schemas
- `src/services`: business logic
- `src/static`: existing frontend UI
- `tests`: pytest suite
- `scripts`: AI usage logging hooks
- `docs`: guidebook and architecture notes
- `eval`: evaluation artifacts
- `presentation`: demo day slides

## Run

```bash
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
```

---

## Destination Crawler

Tool crawl dữ liệu du lịch từ bất kỳ URL nào, lưu kết quả dạng JSON có cấu trúc vào `data/raw/destinations/`.

### Cài đặt (chỉ cần làm 1 lần)

```bash
pip install crawl4ai
crawl4ai-setup
```

> `crawl4ai-setup` tải headless browser (Chromium) — cần kết nối internet, mất khoảng 1–2 phút.

### Cách dùng nhanh — dán link vào file rồi chạy

**Bước 1:** Mở file `src/agents/tools/destination_crawler.py`, tìm phần `URLS_TO_CRAWL` và dán link vào:

```python
URLS_TO_CRAWL = [
    "https://www.klook.com/vi/blog/dia-diem-du-lich-da-nang/",
    "https://www.traveloka.com/vi-vn/...",
    "https://vi.wikipedia.org/wiki/Phú_Quốc",
]
```

**Bước 2:** Chạy file:

```bash
cd "c:\Users\Huawei\AI in Action\mini-hackathon-vinuni"
python src/agents/tools/destination_crawler.py
```

### Cách dùng — truyền link qua terminal (không cần sửa file)

```bash
python src/agents/tools/destination_crawler.py https://link1.com https://link2.com
```

### Output

Mỗi URL tạo ra 1 file `.json` trong `data/raw/destinations/`. Ví dụ:

```
data/raw/destinations/
  www-klook-com-vi-blog-dia-diem-du-lich-da-nang.json
  vi-wikipedia-org-wiki-phu-quoc.json
```

Cấu trúc JSON mỗi file:

```json
{
  "name":        "Tên địa điểm (lấy từ <title> trang web)",
  "url":         "https://...",
  "location":    "Vị trí địa lý (nếu tìm thấy trong nội dung)",
  "description": "Mô tả tổng quan",
  "highlights":  ["Điểm nổi bật 1", "Điểm nổi bật 2"],
  "activities":  ["Tour kayak", "Lặn biển", "Tham quan"],
  "amenities":   ["Hồ bơi", "Spa", "Nhà hàng"],
  "price_info":  ["500.000 VND/đêm"],
  "tips":        ["Nên đi vào mùa khô tháng 11–4"],
  "raw_text":    "Toàn bộ nội dung trang (dùng cho LLM phân tích thêm)",
  "success":     true,
  "source":      "crawl4ai",
  "cached_at":   "2026-06-04T08:00:00Z"
}
```

### Dùng trong Python code

```python
from src.agents.tools.destination_crawler import (
    crawl_and_cache_destination,   # crawl + lưu cache
    load_cached_destination_page,  # đọc cache của 1 URL
    load_all_cached_destinations,  # đọc toàn bộ cache
)

# Crawl và lưu (tự động dùng cache nếu đã crawl rồi)
result = crawl_and_cache_destination("https://example.com/phu-quoc")
print(result["result"]["name"])
print(result["path"])           # đường dẫn file JSON

# Force crawl lại (bỏ qua cache cũ)
result = crawl_and_cache_destination("https://example.com/phu-quoc", force=True)

# Đọc toàn bộ dữ liệu đã crawl
all_data = load_all_cached_destinations()
for dest in all_data:
    print(dest["name"], dest["activities"])
```

### Lưu ý

| Tình huống | Kết quả |
|---|---|
| URL đã crawl trước đó | Dùng cache, không crawl lại |
| Trang dùng JavaScript (React/SPA) | Cần `crawl4ai` (headless browser) |
| Trang chặn bot | Có thể thất bại, thử URL khác |
| `crawl4ai` chưa cài | Tự động fallback dùng urllib |
