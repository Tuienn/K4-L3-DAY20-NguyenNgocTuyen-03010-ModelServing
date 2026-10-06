# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Linux-x86_64` · llama.cpp `b10488`
Settings: `threads=12` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2043 | 204 / 360 | 61.0 / 62.5 | 4024 / 4298 / 4298 | 16.4 |
| UD-Q2_K_XL | 0.39 | 2033 | 410 / 492 | 57.4 / 59.0 | 4076 / 4117 / 4117 | 17.4 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.06x faster** than `Q4_K_M` here, for 0.11 GB less on disk.

## Your observation

Trên lần chạy này, `UD-Q2_K_XL` nhỏ hơn 0.11 GB và decode nhanh hơn khoảng 1.06×,
nhưng TTFT P50 khoảng gấp đôi (410 ms so với 204 ms); E2E P50 gần nhau (4076 ms so
với 4024 ms). Ở prompt chất lượng đã thử, cả hai bản đều giải thích sai TTFT/TPOT và
câu trả lời bị cắt ở giới hạn 96 token, nên một mẫu này chưa đủ để kết luận bản nào
giữ chất lượng tốt hơn. Q2 có lợi về dung lượng và decode trong phép đo này, nhưng
đánh đổi TTFT; cần xem câu trả lời đầy đủ trên nhiều prompt trước khi quyết định
chấp nhận đánh đổi đó.
