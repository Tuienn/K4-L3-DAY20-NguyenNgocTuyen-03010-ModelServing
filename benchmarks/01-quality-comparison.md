# Quality comparison

Identical prompt; temperature 0, seed 42, max_tokens 96.

Define TTFT and TPOT in two short sentences. Explain which one measures prefill and which measures decode.

## Q4_K_M

**TTFT** stands for **Time-to-First-Fill**, which measures the time required to complete the initial data transfer from the server to the client's local storage.

**TPOT** stands for **Time-to-First-Output**, which measures the time required to complete the final data transfer from the client's local storage to the server's display.

**TTFT** measures **prefill** (the initial load of data), while **TPOT** measures

## UD-Q2_K_XL

**TTFT** stands for **Time-to-Full** and measures the time required to **fill** the entire output string, often used in streaming or real-time processing.

**TPOT** stands for **Time-to-Prefill** and measures the time required to **fill** the output string, often used in streaming or real-time processing.

**TPOT** stands for **Time-to-Prefill** and measures the time required to **fill** the output

