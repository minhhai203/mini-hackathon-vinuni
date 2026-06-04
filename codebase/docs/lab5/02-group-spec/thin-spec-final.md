# Thin SPEC Final — Vinpearl AI Resort & Package Fit Assistant

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

## 1. Track, product/app và user

**Track:** B — Travel & Hospitality  
**Product/app thật:** Vinpearl.com / MyVinpearl — kênh chính thức để tìm hiểu, chọn resort/package và đặt kỳ nghỉ Vinpearl.  
**User cụ thể:** Khách du lịch gia đình/cặp đôi lần đầu hoặc ít kinh nghiệm đặt Vinpearl, đang phân vân chọn khu resort/gói nghỉ dưỡng cho chuyến đi 2-5 ngày.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Gần đúng. Nhóm là user du lịch phổ thông, nhưng user thật có áp lực tiền, lịch gia đình, trẻ em/người lớn tuổi và rủi ro đặt phòng thật. Cần bổ sung 2-3 screenshot self-use và nếu kịp, 1-2 phỏng vấn nhanh.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Vinpearl/MyVinpearl có nhiều điểm đến, khách sạn, ưu đãi và dịch vụ đặt phòng/vé máy bay/tour trong cùng hệ sinh thái. | [Vinpearl official](https://vinpearl.com/vi/app-vinpearl-huong-dan-dang-ky), [Google Play - MyVinpearl](https://play.google.com/store/apps/details?id=net.cloudhms.booking.vinpearl) | User bị decision paralysis khi phải chọn giữa nhiều khu/gói | Build slice là resort/package selector, không phải chatbot chung |
| Ưu đãi/package có điều kiện áp dụng theo voucher, membership, thời gian đặt/lưu trú hoặc kênh đặt. Review public cũng phản ánh pain về voucher theo kênh và trade-off khi ở resort tích hợp. | [Tổng hợp ưu đãi Vinpearl](https://vinpearl.com/vi/tong-hop-uu-dai-vinpearl-thang-5-san-ngay-keo-lo), [Member Day Vinpearl](https://vinpearl.com/vi/member-day-uu-dai-doc-quyen-nhan-ngay-hotel-credit), [Booking.com Nam Hội An reviews](https://www.booking.com/reviews/vn/hotel/vinpearl-nam-hoi-an-resort-and-villas.en-gb.html?page=2), [Booking.com Nha Trang reviews](https://www.booking.com/reviews/vn/hotel/vinpearl-resort-spa.en-gb.html?page=2) | User sợ chọn nhầm vì không hiểu trade-off/điều kiện trước khi đặt | Mỗi card phải có trade-off và policy guard |
| Self-use MyVinpearl/Vinpearl: tìm khách sạn tuyến Hà Nội - Phú Quốc trong khoảng 11/06-30/06 nhưng màn hình trả "Không có kết quả tìm kiếm phù hợp"; screen recording khác cho thấy flow bị kẹt loading. | `02-group-spec/evidence/vinpearl-hotel-search-no-results.png`, `02-group-spec/evidence/vinpearl-loading-stuck.mov` | User có thể gặp empty state/loading stuck ngay trong booking flow và không biết bước phục hồi tiếp theo. | Prototype phải có failure recovery: không bịa availability, hỏi lại/đề xuất chỉnh bộ lọc, hoặc handoff CSKH. |
| Agoda công bố booking bot vì user ở bước booking thường quay lại property page để kiểm tra promo code, cancellation policy và chênh lệch giá; Traveloka/Klook cho thấy hủy/đổi/refund là workflow có điều kiện theo từng booking/activity. | [TravelMole - Agoda booking bot](https://www.travelmole.com/news/agoda-launches-ai-powered-booking-bot/), [Traveloka Help](https://www.traveloka.com/en-sg/help/hotel/accommodation-product-information/pay-near-stay-date/cancellation-reschedule/how-to-cancel), [Klook Blog](https://www.klook.com/en-AU/blog/how-to-book-with-klook/) | AI có giá trị khi giảm uncertainty trước khi user trả tiền | Thêm confidence/source/handoff cho case không chắc |
| V4 có prototype static đã thể hiện input -> shortlist -> confidence/fallback -> 4 paths | `02-group-spec/prototype-demo/` | Day 06 có thể build module nhỏ, không cần API thật | Dùng static prototype làm base, đổi nội dung sang final scope |
| Design decision của nhóm sau synthesis: AI chỉ augment quyết định, có explainability, correction loop và human review/handoff. | `02-group-spec/spec-final.md`, `02-group-spec/prompt-tests-or-failure-log.md` | User cần hiểu vì sao AI gợi ý và sửa được output | Output phải có reason/trade-off và correction path |

## 3. Pain statement

```text
User khách du lịch gia đình/cặp đôi lần đầu đặt Vinpearl đang gặp khó ở bước chọn khu resort hoặc package,
vì Vinpearl có nhiều điểm đến, nhiều khu/gói/ưu đãi, nhiều điều kiện về voucher, phụ thu, cancellation, restriction và kênh đặt; ngoài ra flow tìm kiếm có thể trả empty state hoặc kẹt loading mà không giúp user recover rõ ràng,
dẫn tới user mất thời gian so sánh, sợ chọn nhầm, không biết tổng chi phí/rủi ro thật, hoặc bỏ dở trước booking.
Bằng chứng chính là self-use evidence của Thành về "không có kết quả tìm kiếm phù hợp" và loading stuck, V3 evidence về decision paralysis/expectation gap, V2 evidence về booking confidence/policy.
```

## 4. Build slice

```text
Cho khách du lịch gia đình/cặp đôi lần đầu đặt Vinpearl đang phân vân chọn khu resort hoặc gói nghỉ dưỡng,
prototype sẽ dùng AI để hỏi 4 thông tin ngắn: đi với ai, điểm đến/ngày đi, ngân sách, ưu tiên chuyến đi,
tạo ra top 2-3 resort/package phù hợp kèm lý do, trade-off, chi phí/restriction cần biết và confidence,
và xử lý failure mode "input mâu thuẫn hoặc policy/availability không chắc" bằng cách hỏi lại, show source/condition, hoặc handoff CSKH/human review.
```

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:** Chọn resort/package ảnh hưởng tới tiền thật, kỳ vọng chuyến đi, policy, voucher, cancellation và phụ thu. AI sai có thể làm user đặt nhầm hoặc mất quyền lợi. Vì vậy AI chỉ hỗ trợ ra quyết định, không tự book, tự thanh toán hoặc tự xác nhận policy realtime.  
**Human role:** decider / rescuer / reviewer

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User nhập đủ: Phú Quốc/Nha Trang/Hạ Long, ngày đi, 2 người lớn + trẻ em, budget, ưu tiên gia đình/nghỉ biển/vui chơi. AI trả top 2-3 resort/package đúng điểm đến, có lý do, trade-off, confidence, policy guard. |
| Low-confidence | User nhập "cuối tuần này đi nghỉ cho trẻ con vui" nhưng thiếu điểm đến/ngày/budget/tuổi trẻ em. AI hỏi tối đa 3-4 câu quan trọng, không đoán bừa. |
| Failure | User nhập mâu thuẫn như "budget thấp nhưng muốn villa riêng/premium" hoặc hỏi "voucher này chắc chắn dùng được và hủy miễn phí không?". AI không xác nhận chắc, show confidence thấp, hỏi lại thông tin cần xác minh hoặc handoff CSKH. |
| Correction | User đổi constraint: không đi Phú Quốc nữa, đổi sang Nha Trang; hoặc không muốn công viên, ưu tiên ăn uống/spa; hoặc tăng số người. AI cập nhật shortlist và ghi rõ phần thay đổi ảnh hưởng tới option cũ. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user hỏi một thông tin có rủi ro tài chính như "gói này có hủy miễn phí và dùng voucher không?" nhưng prototype thiếu kênh đặt, rate plan, mã voucher hoặc availability realtime,
AI có thể hallucinate policy/price/availability,
hậu quả là user tin sai, đặt nhầm, mất tiền, mất voucher hoặc khiếu nại với Vinpearl.
Prototype sẽ xử lý bằng confidence badge, source/condition, hỏi lại thông tin thiếu, không auto-book, và handoff CSKH/human review khi confidence thấp.
Owner kiểm thử path này là Nguyễn Đức Thành - 2A202600838.
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Mai Hạnh - 2A202600883 | Research / evidence | 2-3 screenshot self-use vinpearl.com/MyVinpearl; link review/policy/competitor |
| Đặng Minh Hải - 2A202600713 | SPEC | `thin-spec-final.md`, final problem statement, checklist theo template |
| Hoàng Phúc Quân - 2A202600560 | Prototype | Static demo thể hiện resort/package selector + policy guard |
| Nguyễn Đức Thành - 2A202600838 | Test / failure path | 4 test cases và screenshot/output cho happy, low-confidence, failure, correction |
| Cả nhóm | Demo script / repo | Script demo 3-5 phút, checklist file nộp, copy bản nhóm vào repo cá nhân |
