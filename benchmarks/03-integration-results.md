# 03 - Integrate: RAG pipeline run

Host `Linux-x86_64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries
Generation limit: `64` tokens per query;
temperature: `0.3`. Answers may be truncated at this limit.

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 3700.0 | 3700.1 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 4454.7 | 4454.8 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 6106.8 | 6107.0 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **4753.8** · total **4754.0**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the context provided, **Goodput** is more useful than raw throughput because it **ignores SLOs (Service Level Objectives)** when calculating throughput at saturation.

Here is the breakdown of why this makes Goodput superior:

1.  **SLO Compliance**: The context states that Goodput

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation in GPU memory** caused by storing the Key-Value (KV) cache in non-contiguous pages.

By separating the KV cache into non-contiguous pages, the model avoids the wasted space that would occur if KV entries were stored contiguously in a single contiguous

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps when **prefill is compute-bound and decode is memory-bound**.

The context explicitly states: "Disaggregated serving splits prefill and decode onto separate pools because prefill is compute-bound and decode is memory-bandwidth-bound." This indicates that the system needs to separate these two operations


## Which N16-N19 pieces are real

N16 (hạ tầng/cloud): stub, pipeline chạy localhost; N17 (data pipeline): stub, không có
DAG/job riêng; N18 (lakehouse): stub, dữ liệu là `TOY_DOCS` trong bộ nhớ; N19 (vector
search/features): stub, đang dùng keyword overlap, không gọi embedding hoặc vector index.
N20 llama-server là phần thật, nhận yêu cầu qua API chat completions.

LLM chiếm 4753.8 ms trên tổng 4754.0 ms trung bình (100%), phù hợp với kỳ vọng rằng
sinh token là phần tốn thời gian trên cấu hình CPU này. `embed` là 0.0 ms vì lần chạy
này không có embedding server; retrieval keyword cũng gần như không đáng kể (trung bình
0.0 ms sau làm tròn). Ba câu đều chạm giới hạn 64 token, nên nếu cần giảm mạnh latency,
tôi sẽ thử rút ngắn đầu ra LLM trước và đo lại, đồng thời kiểm tra đánh đổi về độ đầy
đủ câu trả lời; không thể khẳng định cách này sẽ giảm một nửa khi chưa đo. System prompt
được giữ nguyên từng byte giữa các query, có thể hỗ trợ prefix caching, nhưng lần chạy
này không đo riêng lợi ích cache.
