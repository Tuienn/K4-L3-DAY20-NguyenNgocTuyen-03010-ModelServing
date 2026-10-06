"""Capture an identical deterministic question against both local quantizations."""
import json
import pathlib
import sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import labkit

payload = {
    "model": "local",
    "messages": [{"role": "user", "content":
        "Define TTFT and TPOT in two short sentences. Explain which one measures prefill and which measures decode."}],
    "max_tokens": 96,
    "temperature": 0,
    "seed": 42,
}
active = labkit.load_active()
results = []
for role in ("primary", "compare"):
    model = str(labkit.repo_root() / active[f"{role}_model"])
    with labkit.serve_bg(model, port=8098) as base:
        response = httpx.post(f"{base}/v1/chat/completions", json=payload, timeout=120)
        response.raise_for_status()
        body = response.json()
    results.append({"quant": active[f"{role}_quant"], "response": body})
    print(active[f"{role}_quant"], body["choices"][0]["message"]["content"], flush=True)

out = labkit.repo_root() / "benchmarks" / "01-quality-comparison.json"
out.write_text(json.dumps({"payload": payload, "results": results}, ensure_ascii=False, indent=2))
md = "# Quality comparison\n\nIdentical prompt; temperature 0, seed 42, max_tokens 96.\n\n"
md += payload["messages"][0]["content"] + "\n\n"
for result in results:
    md += "## " + result["quant"] + "\n\n" + result["response"]["choices"][0]["message"]["content"] + "\n\n"
out.with_suffix(".md").write_text(md)
