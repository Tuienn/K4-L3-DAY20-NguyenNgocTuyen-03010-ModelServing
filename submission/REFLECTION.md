# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Nguyễn Ngọc Tuyền
**MSSV:** 2A202603010
**Cohort:** K4-L3 (the cohort label in this repository name; confirm before submission)
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime _(rubric 1, 2 — 10 điểm)_

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Fedora Linux 7.2.8-200.fc44.x86_64; Python 3.14.7
- **CPU:** 12th Gen Intel Core i5-1240P
- **Cores:** 12 physical / 16 logical
- **CPU extensions:** AVX2; AVX-512 not detected
- **RAM:** 23.1 GB
- **Accelerator:** CPU only
- **llama.cpp asset đã tải:** `llama-b10488-bin-ubuntu-x64.tar.gz` (CPU build)
- **Model đã dùng:** Qwen3.5 0.8B (`LAB_MODEL=qwen35-0.8b`)
- **Quantization:** Q4_K_M + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** Local Linux machine (the exact device type is unconfirmed).
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

The first benchmark attempt could not reach the local server from the sandbox, so it was rerun outside the sandbox. The probe, runtime, and both Qwen weights were already present; no additional download or model change was needed.

---

## 2. Đo lường _(rubric 3, 4, 5 — 20 điểm)_

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
| ------------ | --------: | --------: | ----------------: | ----------------: | -------------------: | -------------: |
| Q4_K_M       |      0.50 |      2043 |         204 / 360 |       61.0 / 62.5 |   4024 / 4298 / 4298 |           16.4 |
| UD-Q2_K_XL   |      0.39 |      2033 |         410 / 492 |       57.4 / 59.0 |   4076 / 4117 / 4117 |           17.4 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

Across ten prompts, Q2 decoded 1.06× faster and used 0.11 GB less disk, but its TTFT P50 was about twice Q4's (410 vs 204 ms). On one fixed question, both quant outputs hallucinated the TTFT/TPOT definitions and were truncated at the 96-token limit. This single trial cannot establish a general quality gap; the modest speed gain alone is not a reason to prefer Q2.

---

## 3. Serving under load _(rubric 8, 9, 10 — 20 điểm)_

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users |              RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
| ----: | ---------------: | -------: | -------: | -------: | ---------------: | -------: |
|    10 | 0.41 | 21000 | 31000 | 39000 | 8.2 | 0 |
|    50 | 0.41 | 24000 | 51000 | 51000 | 10.9 | 0 |

- **Offered load tăng 5×, throughput thực tăng:** 1.00× (20% of linear scaling)
- **P95 tăng:** 1.65×
- **Effective concurrency ở 50 users:** 10.9 vs `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.82 / 4 slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

By 50 users the server was saturated: 5× offered users produced 1.00× RPS, P95 rose 1.65×, effective concurrency reached 10.9, and metrics showed 3.82 busy slots with 46 deferred requests. At a trial P95 SLO of 30 seconds, neither run qualifies; aggregate CSVs do not reveal exact request-level goodput. I would first test the measured six-thread setting (19.4 vs 17.2 tok/s at 12 threads) under the same load.

---

## 4. Integration _(rubric 12, 13 — 15 điểm)_

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day                   | Piece                                                        | Real hay stub? |
| --------------------- | ------------------------------------------------------------ | -------------- |
| N16 Cloud/IaC         | Not implemented in this toy pipeline                         | stub           |
| N17 Data pipeline     | Not implemented in this toy pipeline                         | stub           |
| N18 Lakehouse         | Not implemented in this toy pipeline                         | stub           |
| N19 Vector + features | In-memory toy documents and keyword overlap; no vector index | stub           |
| N20 Serving           | `llama-server`                                               | real           |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 4753.8 ms
- **stage chiếm nhiều nhất:** llm (100% of 4754.0 ms total)

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

LLM took 4753.8 ms of 4754.0 ms total, as expected for token generation on this CPU. The 0.0 ms embedding figure means no embedding server ran; keyword retrieval rounded to 0.0 ms. All three answers hit the 64-token limit and were truncated. I would first reduce unnecessary answer length, then measure the latency and completeness trade-off; cutting latency in half is not established by this run.

---

## 5. The single change that mattered most _(rubric 11 — 10 điểm)_

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Reduced llama.cpp threads from the 12-physical-core default to 6.

```
before:  17.2 tok/s (`-t 12`, tg128)
after:   19.4 tok/s (`-t 6`, tg128)
speedup: 1.13×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

_Giải thích như đang nói với bạn ngồi cạnh. Bám vào **cơ chế**, không phải "vibes":
memory bandwidth? vector width? cache residency? scheduling? queueing? Nếu kết quả
**khác** với kỳ vọng từ deck — nói rõ, và giải thích vì sao. Grader thưởng điểm cho
lập luận đúng về một kết quả bất ngờ, hơn là một con số đẹp không được giải thích._

The measured curve peaks at six threads: 19.4 tok/s versus 17.2 at 12, 14.5 at 16, and 9.5 at 32. On this small model, adding workers past six likely adds scheduling and synchronization cost without enough independent work; contention for shared memory bandwidth and the i5's mixed P/E cores may also contribute. Those are explanations consistent with the curve, not separately measured causes.

---

## 6. Bonus _(optional — tối đa 10 điểm)_

Không thực hiện bonus.

---

## 7. Điều làm bạn ngạc nhiên nhất _(optional)_

Optional section; no separate observation recorded.

---

## 8. Self-check trước khi push

- [ ] `hardware.json` committed
- [ ] `models/active.json` committed
- [ ] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [ ] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [ ] `benchmarks/02-server-results.md` committed (`make load-report`)
- [ ] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [ ] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [ ] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [ ] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [ ] 5 screenshots trong `submission/screenshots/` (not yet present)
- [ ] `make verify` → **exit 0**
- [ ] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab** (not yet confirmed)
- [ ] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI _(xem `docs/RULES.md` §3)_

I used OpenAI Codex to inspect the lab instructions and scripts, organize the execution plan, and draft this reflection from repository metadata and generated reports. Any analysis drafted with AI assistance will be reviewed and corrected by me against the raw measurements; I am responsible for the final account and can explain the conclusions.
