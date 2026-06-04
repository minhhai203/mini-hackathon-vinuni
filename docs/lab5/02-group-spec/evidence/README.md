# Evidence Files

Các file này là self-use evidence do Nguyễn Đức Thành - 2A202600838 bổ sung cho app/web Vinpearl.

| File | Mô tả | Path liên quan |
|---|---|---|
| `vinpearl-hotel-search-no-results.png` | Màn hình chọn khách sạn tuyến Hà Nội - Phú Quốc, khoảng 11/06-30/06, nhưng hệ thống báo "Không có kết quả tìm kiếm phù hợp". | Low-confidence / Failure |
| `vinpearl-loading-stuck.mov` | Screen recording cho thấy app/web bị kẹt ở trạng thái loading trong một số tính năng, khiến user không thực hiện được thao tác tiếp. | Failure |

Ý nghĩa với SPEC:

- AI/prototype không được bịa availability khi hệ thống trả empty state.
- Cần có recovery path: hỏi lại, gợi ý chỉnh bộ lọc/ngày/điểm đến, hoặc handoff CSKH.
- Confidence phải thấp khi dữ liệu booking/availability không chắc.
