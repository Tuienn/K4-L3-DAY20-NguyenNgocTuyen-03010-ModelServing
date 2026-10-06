# 02 - Serve: load test + saturation reading

Host `Linux-x86_64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=12` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 24 | 0.41 | 21000 | 31000 | 39000 | 8.2 | 0.0% |
| 50 | 21 | 0.41 | 24000 | 51000 | 51000 | 10.9 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.00x** (20% of linear) |
| P95 latency | **1.65x** |
| Effective concurrency at 50 users | 10.9 vs `--parallel 4` slots (occupancy/slot ratio 2.71) |

**Saturated.** Throughput delivered only 1.00x for 5x the offered load, and effective concurrency (10.9) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.00x while P95 moved 1.65x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

Trong hai mức tải đã đo, server đã bão hòa ở vùng 10–50 users: tăng users 5× nhưng
RPS gần như không đổi (tỷ lệ 1.00×), trong khi P95 tăng từ 31 s lên 51 s. Ở 50 users,
effective concurrency là 10.9, gồm cả request trong hàng đợi; metrics server đồng
thời ghi nhận 4 request processing và 46 deferred. Hai mức tải này chỉ khoanh vùng
bão hòa, không xác định chính xác ngưỡng users. Nếu đặt SLO thử nghiệm là P95 ≤30 s,
cả hai lần đo đều chưa đạt; report aggregate không cho biết chính xác số request
đạt SLO nên chưa thể báo goodput theo request. Tôi sẽ thử `threads=6` trước vì sweep
`tg128` trên cùng máy đo được 19.4 tok/s so với 17.2 tok/s ở 12 threads; cần chạy
load test lại để xác nhận tác động lên P95 và goodput của server.
