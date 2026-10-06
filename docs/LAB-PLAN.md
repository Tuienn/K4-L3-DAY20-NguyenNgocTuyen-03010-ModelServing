# Kế hoạch Day 20 — Qwen3.5 0.8B, base track

Phạm vi: CP0–CP8 theo `docs/CHECKPOINTS.md`, hướng tới đủ bằng chứng cho 100 điểm
base. Mỗi checkpoint có đúng một commit, chỉ commit sau khi hoàn tất đầu ra và
nhận xét của checkpoint đó. Không thực hiện CP-Bonus hay các target bonus.
Đây là kế hoạch thực hiện; chưa chạy benchmark hoặc tạo các commit checkpoint.

## Cấu hình và nguyên tắc chung

- Model: `LAB_MODEL=qwen35-0.8b`.
- Primary: `Qwen3.5-0.8B-Q4_K_M.gguf`; compare: `Qwen3.5-0.8B-UD-Q2_K_XL.gguf`.
- Dùng llama.cpp prebuilt theo bản pin của repo (`b10488`), không compile.
- Hiện `hardware.json` ghi Linux, i5-1240P, 12 physical / 16 logical cores,
  RAM 23.1 GB, CPU only. `models/active.json` đã chọn đúng Qwen; cả hai file đang
  untracked. CP0 cần xác nhận runtime và hai weights thực sự dùng được.
- CPU có P-core/E-core: thread tốt nhất không nhất thiết bằng 12. Đo thực tế,
  không suy diễn rằng mọi physical core có hiệu năng như nhau.
- Khởi đầu với cấu hình mặc định của script, `LAB_PARALLEL=4`, reasoning off.
  CP1 giữ baseline; CP2 sweep threads; CP3–CP6 giữ cùng cấu hình server để so load.
- Chạy lệnh ở repo root, dùng `.venv/bin/python` cho script cần dependencies.
  `.env` không được tự đọc; dùng biến môi trường trực tiếp.
- Khi đo: cắm nguồn, giữ chế độ nguồn ổn định, giảm tác vụ nền và không chạy thêm
  inference/benchmark cạnh tranh CPU. Ghi lại cấu hình, hạn chế và lần chạy lại.
- Chỉ stage đầu ra của checkpoint hiện tại. Giữ JSON raw do script sinh cùng report
  nếu có. Không commit weights, runtime, `.venv`, `.env` hay token.
- Số liệu và screenshot phải từ lần chạy thật. Nhận xét dựa trên kết quả của máy này;
  khai báo dùng AI ở REFLECTION §9 và tự kiểm tra mình giải thích được lập luận.
- File kế hoạch này sẽ đi cùng commit CP0, không tạo commit riêng cho kế hoạch.

## CP0 — Setup (~20 phút, 10 điểm)

Chạy hoặc xác nhận lại setup đã có:

```bash
export LAB_MODEL=qwen35-0.8b
make probe
make setup
cat models/active.json
```

Xác nhận manifest chọn đúng `model_key`, primary/compare, hai weights tồn tại và runtime
đã tải đúng platform. Chụp `submission/screenshots/01-hardware-probe.png` từ output
probe thật. Nếu tải bị chặn, theo `docs/MANUAL-DOWNLOAD.md`; không thay model.

Commit `hardware.json`, `models/active.json`, screenshot 01 và kế hoạch này.

**Commit:** `lab(cp0): set up Qwen3.5 0.8B and record hardware`

## CP1 — Baseline và so quantization (~20 phút, 20 điểm)

1. Chạy `make bench`: 10 prompt mỗi quant, lưu TTFT/TPOT riêng và E2E percentiles.
2. Chụp `submission/screenshots/02-bench.png`, có cả hai quant và cột TTFT/TPOT.
3. Thử chất lượng tuần tự: `make serve` cho Q4, hỏi một câu cố định và lưu câu trả lời;
   Ctrl-C rồi chạy `.venv/bin/python labs/02-serve/serve.py --compare` cho Q2,
   gửi cùng câu hỏi với cùng tham số sinh. Tắt server so sánh sau khi xong.
4. Có thể lưu prompt, tham số, hai câu trả lời và nhận xét ngắn ở
   `benchmarks/01-quality-comparison.md` để chứng minh đánh đổi chất lượng.
5. Điền “Your observation” trong `benchmarks/01-quickstart-results.md`:
   tốc độ Q2/Q4, mức giảm dung lượng, chất lượng quan sát và lựa chọn phù hợp.

Hoàn tất khi cả hai quant có số đo hợp lệ, report không còn placeholder bắt buộc,
nhận xét phân biệt thời gian load với latency request. Percentile từ 10 prompt có
giới hạn độ tin cậy; không diễn giải P99 như kết luận thống kê chắc chắn.

Commit report, JSON raw tương ứng nếu có, bằng chứng so chất lượng và screenshot 02.

**Commit:** `lab(cp1): benchmark both Qwen quantizations and compare quality`

## CP2 — Tune thread count (~15 phút, nguồn cho rubric 11)

Chạy `make tune` khi không có server/load khác chạy. Điền “Your explanation” trong
`benchmarks/01-tuning-tg128.md`, xác định knee, thread tốt nhất và cơ chế khả dĩ:
memory bandwidth, cache, SMT, P-core/E-core hoặc oversubscription.

Lưu before = throughput ở physical-core default, after = throughput ở thread tốt
nhất, speedup = after / before, cùng đơn vị tok/s. Dùng cùng quant và metric `tg128`.
Nếu default đã tốt nhất, báo đúng speedup 1×; không chọn baseline tùy ý để làm đẹp số.
Giữ report CP1 nguyên để không mất baseline.

Commit report tuning và JSON raw nếu có. Có thể thêm ảnh `06-tune.png`.

**Commit:** `lab(cp2): measure thread tuning and explain the throughput curve`

## CP3 — Serving và smoke (~10 phút, 15 điểm)

- Terminal 1: `make serve` với primary Q4, mặc định 4 slots; giữ chạy đến hết CP6.
- Terminal 2: `make smoke`.
- Chụp `submission/screenshots/03-serve-and-smoke.png`: server listen, câu trả lời
  thật và `llamacpp:tokens_predicted_total` khác 0. Có thể chia terminal để đủ nội dung.
- Nếu đổi port, dùng cùng `LAB_SERVER_PORT` trong mọi terminal/lệnh tiếp theo.

Hoàn tất khi `/v1/chat/completions` và `/metrics` hoạt động. Ghi cấu hình server
đang dùng vào `benchmarks/02-serving-config.md`: model, runtime, threads, slots,
context, backend, port; phân biệt cấu hình benchmark với cấu hình server nếu khác.

Commit screenshot 03 và bản ghi cấu hình server.

**Commit:** `lab(cp3): verify serving endpoint and nonzero token metrics`

## CP4 — Load test và continuous batching (~15 phút, 10 điểm)

1. Giữ server CP3. Terminal 2 chạy `make load-10` đủ 60 giây; chụp
   `submission/screenshots/04-locust-10.png`.
2. Terminal 2 chạy `make load-50` đủ 60 giây. Terminal 3 chạy `make metrics`
   ngay khi load-50 bắt đầu để thời gian lấy metrics chồng lên load.
3. Chụp `submission/screenshots/05-locust-50.png`. Cả hai ảnh Locust cần thấy
   request count, RPS, median/50%, 95% và 99%.
4. Điền “Your observation” trong `benchmarks/02-server-batching-u50.md`:
   peak busy slots so với 4 slots, processing/deferred và bằng chứng batching.

Hoàn tất khi có dữ liệu cả hai mức users và peak `n_busy_slots_per_decode` rõ ràng
lớn hơn 1. Nếu không có bằng chứng batching, kiểm tra overlap và chạy lại load-50
cùng metrics; cập nhật ảnh/nhận xét theo đúng lần chạy mới. Không đổi knobs giữa
load-10 và load-50.

Commit `locust-10_stats.csv`, `locust-50_stats.csv`, `02-server-batching-u50.md`,
`02-server-metrics-u50.csv`, JSON report nếu có và screenshots 04–05.

**Commit:** `lab(cp4): capture 10 and 50 user loads with batching metrics`

## CP5 — Đọc saturation (~15 phút, 10 điểm)

Chạy `make load-report`, điền “Your reading” trong `benchmarks/02-server-results.md`.
Phân tích RPS tăng bao nhiêu lần, P95 tăng bao nhiêu lần, failures, và
effective concurrency = RPS × latency trung bình **tính bằng giây**, so với 4 slots.

Kết hợp busy/deferred metrics với latency để lập luận queueing; không coi việc
P95 tăng đơn lẻ là phép đo trực tiếp queue time. Hai mức load chỉ cho bằng chứng
về vùng saturation, không xác định chính xác một ngưỡng users.
Nêu SLO latency dùng để bàn về goodput và knob ưu tiên cùng lý do; không gọi peak
RPS là goodput nếu chưa đo số request đạt SLO.

Commit report saturation và JSON raw nếu có, bảo đảm số liệu khớp CSV ở CP4.

**Commit:** `lab(cp5): analyze saturation queueing and goodput tradeoffs`

## CP6 — RAG integration (~15 phút, 15 điểm)

Chạy `make pipeline` với server CP3 còn chạy. Chọn pipeline toy có sẵn cho base:
không cần nối hệ thống N16–N19 thật hoặc khởi động embedding server bonus.

Hoàn tất khi cả 3 query có context được retrieve, câu trả lời và timings
embed/retrieve/llm/total. Điền “Which N16-N19 pieces are real” trong
`benchmarks/03-integration-results.md`: N16–N19 là stub theo implementation thực tế,
N20 llama-server là real. Với keyword retrieval, embed 0 ms phản ánh bước embedding
không chạy, không phải embedding model nhanh vô hạn.

Ghi mean latency của 3 query, stage chiếm nhiều nhất và tỷ lệ trên total. Giải thích
vai trò system prompt giống nhau từng byte đối với prefix caching; không khẳng định
đã đo hiệu quả cache nếu chưa có bằng chứng.

Commit report integration và JSON raw nếu có. Ảnh `08-pipeline.png` là tùy chọn.

**Commit:** `lab(cp6): run RAG pipeline and document real versus stub stages`

## CP7 — Reflection và verify (~30 phút, 20 điểm)

Điền thông tin cá nhân, ngày nộp và REFLECTION §1–§5 từ bằng chứng đã có:

- §1: hardware/runtime/model/backend và setup story thực tế.
- §2: thay nhãn primary mặc định của Gemma bằng **Q4_K_M**; compare là **UD-Q2_K_XL**.
- §3: số liệu load, batching, saturation khớp CP4–CP5.
- §4: mean stage timings và khai báo real/stub khớp CP6.
- §5: before/after từ CP2 và giải thích cơ chế; phân biệt kết quả đo với giả thuyết.
- §6: ghi “Không thực hiện bonus”; §7 tùy chọn; §8 cập nhật self-check trung thực;
  §9 khai báo AI đã dùng để đọc đề/lập kế hoạch và các hỗ trợ phát sinh.

Kiểm tra đủ 5 screenshot bắt buộc, chữ đọc được, ưu tiên mỗi ảnh dưới 2 MB.
Thay hết placeholder bắt buộc trong các report. Đối chiếu số giữa REFLECTION và
report, không sửa tay số liệu sinh từ script.

Stage các thay đổi CP7, chạy `make verify` đến exit 0 rồi tạo commit. Verifier dùng
`git ls-files` nên có thể nhận file đã stage; pass chưa thay thế việc commit thật.
Sau commit chạy lại `make verify` và kiểm tra `git status --short` để xác nhận bằng
chứng nằm trong commit. Nếu cần sửa trước commit, sửa và verify lại rồi mới commit.

**Commit:** `lab(cp7): complete reflection and pass submission verification`

## CP8 — Chuẩn bị và nộp (~5 phút)

Để CP8 cũng có một commit chứa thay đổi thực, tạo `submission/SUBMISSION.md` ghi
tên repo, URL public thật, branch và mã commit CP7 đã verify; đây là ghi chú bổ sung,
không phải file bắt buộc của đề. Kiểm tra repo public và đúng tên
`K4-L3-DAY20-NguyenNgocTuyen-03010-ModelServing` nếu đúng thông tin cá nhân.

**Commit:** `lab(cp8): record public repository and submission checklist`

Sau commit CP8: chạy `make verify` lần cuối, push toàn bộ CP0–CP8 lên branch nộp,
kiểm tra GitHub có đủ commit/artifact, rồi paste URL public vào ô Day 20 trên VinUni
LMS. Chỉ tick “đã nộp LMS” khi thao tác thực sự hoàn tất; việc push không thay thế LMS.

Deadline mặc định: **23:59 ngày làm lab, UTC+7** (06/10/2026 nếu nộp trong ngày của
workspace), trừ thông báo khác của coach. Giữ repo public đến lúc công bố điểm.
Grader chấm commit cuối trước deadline; không viết lại lịch sử sau deadline.

## Nguồn đối chiếu

`README.md`, `docs/GUIDE.md`, `docs/CHECKPOINTS.md`, `docs/RUBRIC.md`,
`docs/RULES.md`, `docs/SUBMISSION.md`, `docs/HARDWARE-GUIDE.md`,
`docs/MANUAL-DOWNLOAD.md`, `docs/CLOUD.md`, `docs/labs/00-setup.md` đến
`03-integrate.md`, `submission/REFLECTION.md`, `submission/screenshots/README.md`.
Đã đối chiếu thêm `Makefile`, `.env.example`, `.gitignore` và script verify/tuning
để lệnh, cấu hình và thứ tự stage/verify/commit khớp implementation của repo.
