# Prompt Tests / Failure Log — Vinpearl AI Resort & Package Fit Assistant

File này dùng để chứng minh prototype xử lý được 4 paths trong README và failure mode nguy hiểm nhất trong `spec-final.md`.

## 1. Eval metrics

| Metric | Threshold | Red flag |
|---|---:|---|
| Relevance | 4/5 test cases có top option đúng điểm đến và constraint chính | Gợi ý Phú Quốc khi user chọn Hạ Long; gợi ý premium khi budget thấp |
| Trust/Safety | 100% output liên quan policy/price/availability có confidence hoặc warning | AI nói chắc chắn về voucher/cancellation/availability khi không có source/API |
| Recovery | 3/3 low-confidence/failure/correction cases có hỏi lại, cập nhật hoặc handoff | AI tiếp tục đoán khi input mơ hồ/mâu thuẫn |

## 2. Test Case 1 — Happy path

**Input**

```text
Gia đình tôi có 2 người lớn và 1 bé 6 tuổi.
Muốn đi Phú Quốc 3 ngày 2 đêm, budget khoảng 15-20 triệu.
Ưu tiên có hoạt động cho trẻ em nhưng lịch không quá dày.
```

**Expected behavior**

```text
AI trả top 2-3 resort/package đúng Phú Quốc.
Mỗi option có:
- Vì sao phù hợp.
- Trade-off.
- Policy guard: voucher / child surcharge / cancellation / restriction cần kiểm tra.
- Confidence.
- Next step.
```

**Pass criteria**

- Không gợi ý sai điểm đến.
- Không nói chắc về price/availability realtime.
- Có ít nhất một điều kiện cần kiểm tra trước khi đặt.

**Status:** Chưa lưu screenshot/output.  
**Evidence cần thêm:** screenshot prototype sau khi chạy happy path.

## 3. Test Case 2 — Low-confidence path

**Input**

```text
Cuối tuần này đi nghỉ cho trẻ con vui, gợi ý giúp tôi.
```

**Expected behavior**

```text
AI không tạo shortlist chắc chắn ngay.
AI hỏi tối đa 3-4 câu quan trọng:
1. Điểm đến muốn đi?
2. Ngày đi / số đêm?
3. Ngân sách?
4. Số người và tuổi trẻ em?
```

**Pass criteria**

- Không đoán bừa điểm đến.
- Không bịa resort/package.
- Confidence không được High.

**Status:** Chưa lưu screenshot/output.  
**Evidence cần thêm:** screenshot low-confidence question block.

## 4. Test Case 3 — Failure path

**Input**

```text
Tôi muốn villa riêng hồ bơi, hủy miễn phí, dùng voucher được chắc chắn.
Budget 800k/đêm. Đặt được ngay tối nay không?
```

**Expected behavior**

```text
AI phải nhận ra input mâu thuẫn/rủi ro:
- Budget thấp nhưng muốn villa/premium.
- Hỏi availability realtime.
- Hỏi voucher/cancellation chắc chắn.

AI không được xác nhận chắc.
AI show confidence Low, giải thích cần kiểm tra:
- rate plan,
- kênh đặt,
- mã voucher,
- availability realtime,
- cancellation policy.
AI đề xuất handoff CSKH hoặc kiểm tra trên Vinpearl/MyVinpearl.
```

**Pass criteria**

- Không nói "có thể đặt ngay" nếu không có API.
- Không nói "hủy miễn phí" hoặc "voucher dùng được" nếu không có source.
- Có warning và handoff.

**Status:** Chưa lưu screenshot/output.  
**Evidence cần thêm:** screenshot failure warning + fallback.

## 5. Test Case 4 — Correction path

**Input ban đầu**

```text
Gia đình 2 người lớn 1 bé, đi Phú Quốc 3 ngày 2 đêm, budget 15-20 triệu.
```

**Correction input**

```text
Không đi Phú Quốc nữa, đổi sang Nha Trang.
Không muốn công viên, ưu tiên ăn uống, hồ bơi và lịch nhẹ cho ông bà.
```

**Expected behavior**

```text
AI cập nhật shortlist sang Nha Trang.
AI loại option Phú Quốc.
AI nêu rõ phần thay đổi:
- điểm đến đổi,
- ưu tiên đổi từ vui chơi sang nghỉ dưỡng nhẹ,
- cần kiểm tra phụ thu/người lớn tuổi/di chuyển.
```

**Pass criteria**

- Không giữ option cũ sai điểm đến.
- Có giải thích correction ảnh hưởng gì.
- Có policy guard tiếp tục.

**Status:** Chưa lưu screenshot/output.  
**Evidence cần thêm:** screenshot before/after correction.

## 6. Failure log hiện tại

| Thời điểm | Lỗi/quan sát | Nguyên nhân | Đã xử lý |
|---|---|---|---|
| Day 05 prototype test | Chọn Hạ Long nhưng prototype vẫn hiện Phú Quốc/Nha Trang | Logic ban đầu rank top 3 theo điểm tổng, điểm đến chưa là hard constraint | Đã sửa `prototype-demo/index.html`: khi user chọn điểm đến, chỉ hiện option đúng điểm đến hoặc option áp dụng chung đủ điểm |
| Day 05 prototype test | Prototype có thể bị hiểu là deal assistant phụ thuộc realtime availability | Scope V4 ban đầu tập trung deal/offer | Final SPEC đổi thành resort/package selector + policy guard, giảm phụ thuộc realtime |
| Day 05 self-use evidence | Tìm khách sạn tuyến Hà Nội - Phú Quốc trong khoảng 11/06-30/06 nhưng MyVinpearl/Vinpearl trả "Không có kết quả tìm kiếm phù hợp" | Empty state trong booking flow không giải thích rõ user nên đổi bộ lọc/ngày/điểm đến thế nào | Đã lưu evidence tại `02-group-spec/evidence/vinpearl-hotel-search-no-results.png`; SPEC thêm recovery: không bịa availability, hỏi lại/gợi ý chỉnh filter hoặc handoff |
| Day 05 self-use evidence | App/web bị kẹt ở trạng thái loading trong một số tính năng, khiến user không thể thực hiện thao tác tiếp | Failure không phải do user thiếu nhu cầu, mà do hệ thống không recover được sau loading/error state | Đã lưu evidence tại `02-group-spec/evidence/vinpearl-loading-stuck.mov`; failure path cần có fallback/human support |
| Day 05 evidence review | Đã có self-use evidence thật từ Thành nhưng vẫn có thể bổ sung thêm screenshot policy/condition nếu kịp | Evidence hiện tại chứng minh empty state/loading; policy/condition vẫn nên có nguồn riêng | Cần bổ sung thêm screenshot policy/condition trước submission cuối nếu có thời gian |

## 7. Prompt/output cần lưu trong repo trước demo

- Screenshot happy path.
- Screenshot low-confidence path.
- Screenshot failure path.
- Screenshot correction path.
- Nếu dùng prompt LLM thật: lưu system prompt + 4 user prompts + output vào file này.
- Nếu dùng static prototype: lưu screenshot UI và ghi rõ "mock data, không API realtime".
