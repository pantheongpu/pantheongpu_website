---
title: LLM Prefill
---

# LLM Prefill

`llm_prefill` is a throughput-oriented diagnostic workload for long prompts. It
combines projection-like math with tiled causal scans over a synthetic context
store, creating a different memory and compute mix from token-by-token decode.

```bash
pantheon --test llm_prefill --gpu 0 --duration 60 --mem 50 --verify --profile
```

| Area | What the workload exercises |
| --- | --- |
| Context store | A synthetic context store sized from free VRAM. |
| Attention path | Tiled causal scans through the context window. |
| Compute | Projection and attention-score-like FMA work. |
| Result | Synthetic prompt token iterations per second, reported as `prompt-tokens/s`. |

The workload helps isolate how longer contexts affect cache, DRAM, clocks,
power, and thermals. It is not a substitute for measuring a particular model,
attention implementation, precision, batching policy, or serving engine.
