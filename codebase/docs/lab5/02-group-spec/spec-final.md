# Spec Final — Vinpearl AI Resort & Package Fit Assistant

Track B: Travel & Hospitality | Product/app: Vinpearl.com / MyVinpearl

## 1. Track, product/app và user

**Track:** B — Travel & Hospitality  
**Product/app thật:** Vinpearl.com / MyVinpearl — kênh chính thức để tìm hiểu, chọn resort/package và đặt kỳ nghỉ Vinpearl.  
**Prototype đề xuất:** Vinpearl AI Resort & Package Fit Assistant.  
**User cụ thể:** Khách du lịch gia đình/cặp đôi lần đầu hoặc ít kinh nghiệm đặt Vinpearl, đang phân vân chọn khu resort/gói nghỉ dưỡng cho chuyến đi 2-5 ngày.  
**Nhóm có phải user thật không?** Gần đúng. Nhóm là user du lịch phổ thông, nhưng user thật có áp lực tiền, lịch gia đình, trẻ em/người lớn tuổi và rủi ro đặt phòng thật. Cần bổ sung 2-3 screenshot self-use và nếu kịp, 1-2 phỏng vấn nhanh.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Vinpearl/MyVinpearl có nhiều điểm đến, khách sạn, ưu đãi và dịch vụ đặt phòng/vé máy bay/tour trong cùng hệ sinh thái. | [Vinpearl official](https://vinpearl.com/vi/app-vinpearl-huong-dan-dang-ky), [Google Play - MyVinpearl](https://play.google.com/store/apps/details?id=net.cloudhms.booking.vinpearl) | Decision paralysis khi phải chọn giữa nhiều khu/gói | Build slice là resort/package selector, không phải chatbot chung |
| Ưu đãi/package có điều kiện áp dụng theo voucher, membership, thời gian đặt/lưu trú hoặc kênh đặt. Review public cũng phản ánh pain về voucher theo kênh và trade-off khi ở resort tích hợp. | [Tổng hợp ưu đãi Vinpearl](https://vinpearl.com/vi/tong-hop-uu-dai-vinpearl-thang-5-san-ngay-keo-lo), [Member Day Vinpearl](https://vinpearl.com/vi/member-day-uu-dai-doc-quyen-nhan-ngay-hotel-credit), [Booking.com Nam Hội An reviews](https://www.booking.com/reviews/vn/hotel/vinpearl-nam-hoi-an-resort-and-villas.en-gb.html?page=2), [Booking.com Nha Trang reviews](https://www.booking.com/reviews/vn/hotel/vinpearl-resort-spa.en-gb.html?page=2) | User sợ chọn nhầm vì không hiểu trade-off/điều kiện trước khi đặt | Mỗi card phải có trade-off và policy guard |
| Self-use MyVinpearl/Vinpearl: tìm khách sạn tuyến Hà Nội - Phú Quốc trong khoảng 11/06-30/06 nhưng màn hình trả "Không có kết quả tìm kiếm phù hợp". Một screen recording khác cho thấy flow bị kẹt ở trạng thái loading, không thực hiện được thao tác tiếp. | `02-group-spec/evidence/vinpearl-hotel-search-no-results.png`, `02-group-spec/evidence/vinpearl-loading-stuck.mov` | Ngay cả khi user chọn khoảng thời gian rộng, hệ thống vẫn có thể trả empty state hoặc kẹt loading; user không biết nên đổi bộ lọc, đổi ngày, hay chuyển kênh nào. | SPEC phải có failure/low-confidence recovery: không bịa availability, giải thích trạng thái không chắc, gợi ý chỉnh bộ lọc/ngày/điểm đến, hoặc handoff CSKH. |
| Agoda công bố booking bot vì user ở bước booking thường quay lại property page để kiểm tra promo code, cancellation policy và chênh lệch giá; Traveloka/Klook cho thấy hủy/đổi/refund là workflow có điều kiện theo từng booking/activity. | [TravelMole - Agoda booking bot](https://www.travelmole.com/news/agoda-launches-ai-powered-booking-bot/), [Traveloka Help](https://www.traveloka.com/en-sg/help/hotel/accommodation-product-information/pay-near-stay-date/cancellation-reschedule/how-to-cancel), [Klook Blog](https://www.klook.com/en-AU/blog/how-to-book-with-klook/) | AI có giá trị khi giảm uncertainty trước khi user trả tiền | Thêm confidence/source/handoff |
| Prototype static đã thể hiện flow input -> shortlist -> confidence/fallback -> 4 paths. | `02-group-spec/prototype-demo/` | Day 06 có thể build module nhỏ, không cần API thật | Dùng prototype static làm bản demo cho resort/package selector |
| Design decision của nhóm sau synthesis: AI chỉ augment quyết định, có explainability, correction loop và human review/handoff. | `02-group-spec/thin-spec-final.md`, `02-group-spec/prompt-tests-or-failure-log.md` | User cần hiểu vì sao AI gợi ý và sửa được output | Output phải có reason/trade-off và correction path |

## 3. Evidence -> Insight -> Opportunity

```text
Evidence nổi bật nhất:
Vinpearl có nhiều khu resort/gói nghỉ dưỡng, trong khi user lần đầu đặt thường không biết chọn khu nào, gói nào bao gồm gì, chi phí/restriction nào cần biết. Self-use evidence từ Thành cho thấy flow tìm khách sạn có thể trả empty state dù chọn khoảng thời gian rộng hoặc bị kẹt loading. Evidence public từ Vinpearl, Google Play, Booking.com và các travel platform khác cho thấy policy/promo/cancellation, voucher theo kênh đặt và expectation gap là những điểm user dễ do dự trước checkout hoặc thất vọng sau khi lưu trú.

Insight:
User không chỉ thiếu thông tin về resort.
Họ thật ra cần một công cụ hỗ trợ ra quyết định đáng tin: khu/gói nào hợp với profile chuyến đi của mình, trade-off là gì, chi phí/ràng buộc nào có thể gây bất ngờ, và thông tin nào cần kiểm tra với nguồn/human.

Opportunity:
AI có thể augment bước chọn khu/gói bằng cách hỏi 4 thông tin ngắn, rank top 2-3 option, giải thích lý do, hiển thị trade-off/policy guard/confidence, và fallback khi input mâu thuẫn hoặc policy/availability không chắc.
```

## 4. Pain statement

```text
User là khách du lịch gia đình/cặp đôi lần đầu đặt Vinpearl đang gặp khó ở bước chọn khu resort hoặc package,
vì Vinpearl có nhiều điểm đến, nhiều khu/gói/ưu đãi, nhiều điều kiện về voucher, phụ thu, cancellation, restriction và kênh đặt; ngoài ra flow tìm kiếm có thể trả empty state hoặc kẹt loading mà không giúp user recover rõ ràng,
dẫn tới user mất thời gian so sánh, sợ chọn nhầm, không biết tổng chi phí/rủi ro thật, hoặc bỏ dở trước booking.
Bằng chứng chính là self-use evidence của Thành về "không có kết quả tìm kiếm phù hợp" và loading stuck, cộng với evidence public về decision paralysis, expectation gap, booking confidence và policy/voucher theo từng kênh đặt.
```

## 5. Build slice

```text
Cho khách du lịch gia đình/cặp đôi lần đầu đặt Vinpearl đang phân vân chọn khu resort hoặc gói nghỉ dưỡng,
prototype sẽ dùng AI để hỏi 4 thông tin ngắn: đi với ai, điểm đến/ngày đi, ngân sách, ưu tiên chuyến đi,
tạo ra top 2-3 resort/package phù hợp kèm lý do, trade-off, chi phí/restriction cần biết và confidence,
và xử lý failure mode "input mâu thuẫn hoặc policy/availability không chắc" bằng cách hỏi lại, show source/condition, hoặc handoff CSKH/human review.
```

## 6. Auto/Aug decision

- [x] **Augmentation:** AI gợi ý/so sánh/cảnh báo, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:** Chọn resort/package ảnh hưởng tới tiền thật, kỳ vọng chuyến đi, policy, voucher, cancellation và phụ thu. AI sai có thể làm user đặt nhầm hoặc mất quyền lợi. Vì vậy AI chỉ hỗ trợ ra quyết định, không tự book, tự thanh toán hoặc tự xác nhận policy realtime.  
**Human role:** User là decider; CSKH/resort staff là rescuer khi policy/voucher/availability không chắc; nhóm test là reviewer của failure paths.

## 7. AI response contract

Mỗi response chính phải có cấu trúc:

```text
1. Need summary
   - Điểm đến, nhóm đi, số đêm, ngân sách, ưu tiên, ràng buộc.

2. Top 2-3 resort/package
   - Tên option.
   - Vì sao phù hợp.
   - Trade-off chính.
   - Confidence.

3. Policy guard
   - Cancellation / refund.
   - Voucher / membership.
   - Child surcharge / extra guest.
   - Restriction hoặc chi phí hay phát sinh.
   - Source/condition nếu có.

4. Next action
   - Chọn option.
   - Hỏi lại thông tin thiếu.
   - Kiểm tra trên Vinpearl/MyVinpearl.
   - Gửi CSKH/human review nếu confidence thấp.
```

AI không được:

- Không tự book/tự thanh toán.
- Không khẳng định giá/phòng trống/availability realtime nếu không có API.
- Không xác nhận voucher/cancellation chắc chắn nếu thiếu source.
- Không gợi ý option sai điểm đến khi user đã chọn điểm đến.
- Không trả lời kiểu brochure chung chung.

## 8. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User nhập đủ: Phú Quốc/Nha Trang/Hạ Long, ngày đi, 2 người lớn + trẻ em, budget, ưu tiên gia đình/nghỉ biển/vui chơi. AI trả top 2-3 resort/package đúng điểm đến, có lý do, trade-off, confidence, policy guard. |
| Low-confidence | User nhập "cuối tuần này đi nghỉ cho trẻ con vui" nhưng thiếu điểm đến/ngày/budget/tuổi trẻ em. AI hỏi tối đa 3-4 câu quan trọng, không đoán bừa. |
| Failure | User nhập mâu thuẫn như "budget thấp nhưng muốn villa riêng/premium" hoặc hỏi "voucher này chắc chắn dùng được và hủy miễn phí không?". AI không xác nhận chắc, show confidence thấp, hỏi lại thông tin cần xác minh hoặc handoff CSKH. |
| Correction | User đổi constraint: không đi Phú Quốc nữa, đổi sang Nha Trang; hoặc không muốn công viên, ưu tiên ăn uống/spa; hoặc tăng số người. AI cập nhật shortlist và ghi rõ phần thay đổi ảnh hưởng tới option cũ. |

## 9. Failure mode nguy hiểm nhất

```text
Nếu user hỏi một thông tin có rủi ro tài chính như "gói này có hủy miễn phí và dùng voucher không?" nhưng prototype thiếu kênh đặt, rate plan, mã voucher hoặc availability realtime,
AI có thể hallucinate policy/price/availability,
hậu quả là user tin sai, đặt nhầm, mất tiền, mất voucher hoặc khiếu nại với Vinpearl.
Prototype sẽ xử lý bằng confidence badge, source/condition, hỏi lại thông tin thiếu, không auto-book, và handoff CSKH/human review khi confidence thấp.
Owner kiểm thử path này là Nguyễn Đức Thành - 2A202600838.
```

Top 3 failure modes:

| Failure mode | Trigger | Hậu quả | Mitigation |
|---|---|---|---|
| Hallucinate price/availability/policy | User hỏi thông tin realtime hoặc quyền lợi cụ thể | Mất tiền, mất trust, khiếu nại | Show confidence thấp, nói rõ cần kiểm tra trên app/CSKH |
| Gợi ý sai resort/package | User có constraint rõ nhưng AI ưu tiên option khác điểm đến/budget | User đặt nhầm khu, trải nghiệm kém | Điểm đến/budget/ràng buộc chính là hard constraint; nếu không đủ option thì nói không đủ data |
| Bỏ sót chi phí/restriction | User đi với trẻ em/người lớn tuổi/voucher | Bị bất ngờ khi check-in hoặc khi thanh toán | Policy guard bắt buộc có child surcharge, voucher, cancellation, restriction |

## 10. Eval metrics

| Metric | Threshold | Red flag |
|---|---:|---|
| Relevance | 4/5 test cases có top option đúng điểm đến và constraint chính | Gợi ý Phú Quốc khi user chọn Hạ Long; gợi ý premium khi budget thấp |
| Trust/Safety | 100% output liên quan policy/price/availability có confidence hoặc warning | AI nói chắc chắn về voucher/cancellation/availability khi không có source/API |
| Recovery | 3/3 low-confidence/failure/correction cases có hỏi lại, cập nhật hoặc handoff | AI tiếp tục đoán khi input mơ hồ/mâu thuẫn |

Precision/Recall:

- Ưu tiên **precision** với price, availability, voucher, cancellation, policy.
- Chấp nhận bỏ sót một option tốt hơn là gợi ý sai hoặc xác nhận sai quyền lợi.

## 11. ROI 3 kịch bản

| Kịch bản | Giả định | ROI logic |
|---|---|---|
| Conservative | AI đúng 60-70%, chỉ dùng như guided checklist | Giảm nhẹ thời gian research và câu hỏi lặp về chọn khu/gói |
| Realistic | AI đúng 75-85%, shortlist tốt và phát hiện missing info | Tăng confidence trước booking, giảm bỏ cuộc và giảm CSKH ticket trước mua |
| Optimistic | AI học từ correction signal, policy guard ổn định | Tăng conversion/upsell package, giảm complaint về voucher/policy/restriction, tạo first-party demand insight |

## 12. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Mai Hạnh - 2A202600883 | Research / evidence | 2-3 screenshot self-use vinpearl.com/MyVinpearl; link review/policy/competitor |
| Đặng Minh Hải - 2A202600713 | SPEC | `spec-final.md`, final problem statement, final scorecard |
| Hoàng Phúc Quân - 2A202600560 | Prototype | Cập nhật static demo thành resort/package selector + policy guard |
| Nguyễn Đức Thành - 2A202600838 | Test / failure path | 4 test cases và screenshot/output cho happy, low-confidence, failure, correction |
| Cả nhóm | Demo script / repo | Script demo 3-5 phút, checklist file nộp, copy bản nhóm vào repo cá nhân |

## 13. Backlog không build trong Day 06

- Booking/payment thật.
- Availability/price API realtime.
- Login membership thật.
- So sánh giá thật với OTA.
- Review aggregator tự động.
- Cảnh báo fanpage giả mạo tự động.
- Full itinerary nhiều ngày có map/weather.
- Dashboard B2B demand insight.
- Chatbot CSKH tổng quát cho toàn bộ Vinpearl.
