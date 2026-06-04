# Day06 - Travel & Hospitality - Vinpearl AI Assistant

Repo nộp bài nhóm cho **Batch 02 - Day 06 AI Product Hackathon**.

## Sản phẩm

**Vinpearl AI Resort & Package Fit Assistant** là prototype AI hỗ trợ khách du lịch gia đình/cặp đôi lần đầu đặt Vinpearl chọn resort, gói nghỉ dưỡng hoặc điểm vui chơi phù hợp trước khi booking.

Sản phẩm không thay người dùng đặt phòng hay thanh toán. AI chỉ đóng vai trò **augmentation**: hỏi nhanh nhu cầu chuyến đi, tạo shortlist top 2-3 option, giải thích lý do phù hợp, cảnh báo trade-off/policy guard/confidence, và hỏi lại hoặc handoff CSKH khi thông tin real-time như giá, voucher, hủy phòng hoặc availability chưa chắc chắn.

## Thành Viên Và Phân Công

| Thành viên | Mã học viên | Phụ trách | Bằng chứng / đầu ra |
|---|---|---|---|
| Mai Hạnh | 2A202600883 | Research / evidence | Screenshot self-use Vinpearl/MyVinpearl, link review/policy/competitor |
| Đặng Minh Hải | 2A202600713 | SPEC / repo / backend-agent integration | `spec/spec.md`, problem statement, scorecard, README, API/chatbot flow |
| Hoàng Phúc Quân | 2A202600560 | Prototype UI | Resort/package selector, chatbot UI, planner/checklist, policy guard display |
| Nguyễn Đức Thành | 2A202600838 | Test / failure path | 4 test cases: happy, low-confidence, failure, correction; evidence empty-state/loading |
| Cả nhóm | Demo script / final handoff | Demo 3-5 phút, checklist nộp bài, Q&A |


## Cấu Trúc Repo

```text
.
├── README.md          # README nộp bài Day06
├── spec/
│   └── spec.md        # SPEC sản phẩm final
└── codebase/          # Toàn bộ code prototype hiện tại
    ├── README.md      # Hướng dẫn chạy chi tiết
    ├── src/           # FastAPI backend, agent, tools, services
    ├── frontend/      # Next.js UI + legacy Vinpearl static UI
    ├── tests/         # pytest suite
    ├── scripts/       # crawler/logging scripts
    ├── data/          # cached crawl data / demo data
    └── docs/          # docs, evidence, Day05 group-spec archive
```

## Demo Slice

Một người dùng đang phân vân chọn kỳ nghỉ Vinpearl sẽ chat tự nhiên với AI:

1. AI hỏi hoặc tự rút ra điểm đến, xuất phát, nhóm đi, thời gian, ngân sách và ưu tiên.
2. AI rank top 2-3 resort/package/điểm vui chơi phù hợp.
3. UI hiển thị recommendation card có ảnh, lý do phù hợp và next action.
4. Trace mode có thể bật để xem trade-off, confidence, policy guard và source/debug info.
5. Nếu user hỏi thông tin rủi ro như giá/phòng trống/voucher/cancellation realtime, AI không bịa mà cảnh báo cần kiểm tra trên Vinpearl/MyVinpearl hoặc CSKH.

## Demo Paths

| Path | Input demo | Expected behavior |
|---|---|---|
| Happy path | `Gia đình 2 người lớn 1 bé đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu, ưu tiên vui chơi cho trẻ em.` | AI trả top option đúng Phú Quốc, có lý do phù hợp và card gợi ý. |
| Low-confidence | `Cuối tuần này đi nghỉ cho trẻ con vui.` | AI hỏi thêm điểm đến/ngày/budget/tuổi trẻ em, không đoán bừa. |
| Failure path | `Voucher này chắc chắn dùng được và còn phòng tối nay không?` | AI cảnh báo không thể xác nhận realtime, gợi ý kiểm tra MyVinpearl/CSKH. |
| Correction path | `Không đi Phú Quốc nữa, đổi sang Nha Trang, ưu tiên spa và ăn uống.` | AI cập nhật profile và shortlist theo constraint mới. |

## Cách Chạy Nhanh

Chạy từ thư mục `codebase/`.

```bash
cd codebase
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Điền key thật vào `codebase/.env`:

```text
OPENAI_API_KEY="your_real_key_here"
OPENAI_MODEL="gpt-4.1-mini"
LLM_ENABLED="true"
```

Terminal 1 - backend:

```bash
cd codebase
source .venv/bin/activate
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - frontend:

```bash
cd codebase/frontend
npm install
cp .env.example .env.local
npm run dev
```

Open:

```text
http://127.0.0.1:3000/
```

## Kiểm Thử

```bash
cd codebase
python -m pytest -q
python -m compileall -q src tests scripts

cd frontend
npm run build
```

## API / Tools / Data

- **Backend:** FastAPI, Pydantic, Uvicorn.
- **Frontend:** Next.js, React, static Vinpearl-inspired legacy UI.
- **AI provider:** OpenAI-compatible provider through env `OPENAI_API_KEY`, fallback deterministic logic for demo reliability.
- **Tools:** weather tool, Vinpearl crawl/cache loader, recommendation/ranking, policy guard, source discovery, prompt-injection/boundary guard.
- **Data:** cached official Vinpearl crawl data in `codebase/data/raw/vinpearl/`; crawler script in `codebase/scripts/crawl_vinpearl.py`.

## Tài Liệu

- Final SPEC: `spec/spec.md`
- Codebase instructions: `codebase/README.md`
- Technical guide: `codebase/docs/guide/`

## Scope Không Build

- Không booking/payment thật.
- Không xác nhận room availability, price, voucher, cancellation realtime nếu không có API/source.
- Không login MyVinpearl.
- Không so sánh giá live với OTA.
