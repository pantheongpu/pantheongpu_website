---
title: LLM Decode
---

# LLM Decode

`llm_decode` is a latency-oriented diagnostic workload for autoregressive LLM
generation. It combines dependent reads through a synthetic KV-cache window
with small projection-like fused multiply-add work.

```bash
pantheon --test llm_decode --gpu 0 --duration 60 --mem 50 --verify --profile
```

| Area | What the workload exercises |
| --- | --- |
| KV cache | Dependent, strided gathers through a bounded history window. |
| Compute | Small projection-like FMA chains. |
| Telemetry | Cache and DRAM activity, SM behavior, power, clocks, thermals, and throttling with `--profile`. |
| Result | Synthetic token iterations per second, reported as `tokens/s`. |

`--mem` reserves a percentage of currently free VRAM for the synthetic KV-cache
store. Start with `--mem 25` on a machine that is serving other workloads.

!!! note
    This is an inference-path stress test, not an end-to-end model benchmark.
    It does not include model weights, a tokenizer, a request queue, network
    latency, time-to-first-token, or a specific serving runtime.

Use it to compare relative hardware and configuration behavior, and validate
absolute serving performance separately with the model and runtime you deploy.
