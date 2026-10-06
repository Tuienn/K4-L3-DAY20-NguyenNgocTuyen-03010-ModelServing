# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Linux-x86_64` · llama.cpp `b10488`
CPU: **12 physical · 16 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 17.1 | 88% |
| 6 | 19.4 | 100% |
| 12 | 17.2 | 88% |
| 16 | 14.5 | 74% |
| 32 | 9.5 | 49% |

**Best**: `-t 6` at 19.4 tok/s
**Slowest tested**: `-t 32` at 9.5 tok/s (2.05x spread)
**Against the physical-core default** (`-t 12`, 17.2 tok/s): 1.13x

Use this in your run:

```bash
LAB_N_THREADS=6 make bench
```

## Your explanation

Throughput đạt đỉnh ở 6 threads (19.45 tok/s), cao hơn cấu hình mặc định 12 threads
khoảng 13%; sau điểm này, kết quả giảm còn 14.48 tok/s ở 16 threads và 9.47 tok/s ở
32 threads. Knee của phép đo vì vậy nằm quanh 6 threads, thấp hơn 12 physical cores.
Một khả năng là các thread bổ sung tranh chấp băng thông bộ nhớ/cache khi decode; CPU
có P-core/E-core nên số thread không đồng nghĩa với cùng lượng năng lực tính toán.
Đây là giả thuyết phù hợp với đường cong, chưa phải nguyên nhân được cô lập bằng phép
đo riêng.
