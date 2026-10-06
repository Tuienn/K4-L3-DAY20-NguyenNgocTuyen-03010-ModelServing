# Serving configuration

- llama.cpp prebuilt b10488, asset llama-b10488-bin-ubuntu-x64.tar.gz.
- Model: Qwen3.5 0.8B Q4_K_M, CPU only (`ngl=0`).
- Threads: 12; context: 2048 total; parallel slots: 4; continuous batching enabled.
- Reasoning: off; host: 127.0.0.1; port: 8080; Prometheus metrics enabled.
- CP3–CP6 use this same configuration. The 6-thread winner from CP2 is a separate
  llama-bench measurement; it was not applied to these load runs.
- Smoke returned HTTP completion, decoded 33 tokens, and increased
  `llamacpp:tokens_predicted_total` from 0 to 33.
- The smoke answer misdefined goodput; this proves endpoint operation, not factual
  correctness. See raw output in `evidence/cp3-smoke.txt`.
- Screenshot unavailable: connected computer-use tools expose no desktop/browser.
  Raw stdout/stderr is retained without synthesizing an image.
