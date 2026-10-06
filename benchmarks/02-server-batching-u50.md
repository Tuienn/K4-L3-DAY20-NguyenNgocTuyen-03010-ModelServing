# 02 - Continuous batching under load (u50)

Host `Linux-x86_64` · `--parallel 4` · 30 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.82 of 4 slots (95%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 2434 |

Highest sampled value was **3.82 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

Trong mẫu metrics 50-user, giá trị trung bình cao nhất là 3.82/4 busy slots; cùng lúc
server xử lý 4 request và có 46 request deferred. Điều này cho thấy các decode step
đã gộp nhiều request đồng thời và hàng đợi cũng hình thành. Effective concurrency
10.9 ở report load tính cả request đang chờ nên lớn hơn 4 slots; hai số đo khác nhau
về ý nghĩa, không mâu thuẫn: gauge server mô tả mức bận decode, còn effective
concurrency gồm cả queue.
