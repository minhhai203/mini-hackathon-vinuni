# Prototype Demo — Vinpearl AI Resort & Package Fit Assistant

Đây là module demo nhỏ bám theo thin SPEC của nhóm.

## Cách chạy

Mở trực tiếp file:

```text
02-group-spec/prototype-demo/index.html
```

Không cần cài dependency, không cần chạy server.

## Prototype chứng minh gì?

- AI decision: tạo shortlist 2-3 option Vinpearl phù hợp.
- Auto/Aug: augmentation, user vẫn quyết định booking/payment.
- Four paths: Happy, Low-confidence, Failure, Correction.
- Failure mode chính: AI không được khẳng định deal/price/availability realtime.
- Trust UX: confidence, điều kiện cần kiểm tra, fallback, learning signal.

## Dữ liệu trong demo

Dữ liệu là mock data rút từ evidence public và self-use evidence trong:

- `02-group-spec/spec-final.md`
- `02-group-spec/thin-spec-final.md`
- `02-group-spec/prompt-tests-or-failure-log.md`
- `02-group-spec/evidence/`

Prototype không tích hợp API MyVinpearl thật và không kiểm tra availability realtime.
