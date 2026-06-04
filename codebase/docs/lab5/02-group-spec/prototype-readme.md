# Prototype README — Vinpearl AI Resort & Package Fit Assistant

## 1. Prototype là gì?

Prototype là một module demo nhỏ cho build slice trong `spec-final.md`:

```text
User nhập trip profile ngắn
-> AI gợi ý top 2-3 resort/package Vinpearl phù hợp
-> AI giải thích lý do, trade-off, policy guard và confidence
-> AI fallback/handoff khi input mâu thuẫn hoặc policy/availability không chắc.
```

## 2. Cách chạy demo hiện tại

Mở trực tiếp file static:

```text
02-group-spec/prototype-demo/index.html
```

Không cần cài dependency, không cần server, không có API thật.

## 3. Prototype chứng minh gì?

| Thành phần | Prototype thể hiện |
|---|---|
| User cụ thể | Khách gia đình/cặp đôi lần đầu hoặc ít kinh nghiệm đặt Vinpearl |
| Task hẹp | Chọn resort/package phù hợp, không booking/payment thật |
| AI decision | Rank top 2-3 option theo điểm đến, ngân sách, nhóm đi, ưu tiên |
| Output | Shortlist card có lý do, điều kiện cần kiểm tra, confidence, next step |
| Auto/Aug | Augmentation: AI gợi ý, user quyết định cuối |
| Trust UX | Confidence badge, fallback, cảnh báo không có realtime availability/API |
| Four paths | Happy, Low-confidence, Failure, Correction |

## 4. Những gì cần chỉnh để khớp final spec

Prototype hiện tại base từ bản V4 "Deal & Trip Fit". Trước demo Day 06 nên chỉnh:

- Đổi tên UI thành `Vinpearl AI Resort & Package Fit Assistant`.
- Đổi card từ "deal" sang "resort/package".
- Mỗi card thêm:
  - `Best for`: gia đình, cặp đôi, nghỉ biển, vui chơi, yên tĩnh.
  - `Trade-off`: xa trung tâm, nhiều add-on, phụ thu trẻ em, restriction.
  - `Policy guard`: cancellation, voucher, child surcharge, restriction.
- Giữ hard constraint theo điểm đến: chọn Hạ Long thì không hiện Phú Quốc/Nha Trang.
- Failure demo chính:
  - Budget thấp + muốn villa/premium.
  - Hỏi chắc chắn voucher/cancellation/availability khi prototype không có source/API.

## 5. Demo flow 3-5 phút

**Người demo:** Cả nhóm.

1. Mở problem: Vinpearl có nhiều khu/gói, user không biết chọn cái nào và sợ chi phí/restriction/policy bất ngờ.
2. Happy path: nhập đủ điểm đến, ngày, nhóm đi, budget, ưu tiên -> AI trả 2-3 option.
3. Low-confidence path: thiếu ngày/budget/tuổi trẻ em -> AI hỏi lại, không đoán.
4. Failure path: hỏi voucher/cancellation chắc chắn hoặc input mâu thuẫn -> AI show confidence thấp + handoff.
5. Correction path: user đổi điểm đến/ưu tiên/số người -> AI cập nhật shortlist.

## 6. Không nằm trong prototype

- Không booking/payment thật.
- Không kiểm tra price/availability realtime.
- Không login membership thật.
- Không gọi API Vinpearl thật.
- Không so sánh giá OTA thật.
- Không làm full itinerary nhiều ngày có map/weather.

## 7. Evidence/provenance

Prototype bám theo:

- `02-group-spec/spec-final.md`
- `02-group-spec/thin-spec-final.md`
- `02-group-spec/prompt-tests-or-failure-log.md`
- `02-group-spec/evidence/vinpearl-hotel-search-no-results.png`
- `02-group-spec/evidence/vinpearl-loading-stuck.mov`
- Public evidence links được ghi trực tiếp trong `spec-final.md` và `thin-spec-final.md`
