# Fused Attention

`fused_attention` exercises the combined memory and arithmetic pressure of a
causal attention path using a synthetic context working set.

```bash
pantheon --test fused_attention --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Context access | Repeated windowed reads through synthetic attention state. |
| Compute | Attention-score and projection-style fused arithmetic. |
| Telemetry | SM activity, cache behavior, DRAM traffic, clocks, power, and thermals. |
| Result | Synthetic attention tiles per second. |

It isolates hardware behavior of an attention-like path. It does not implement
or validate a framework's FlashAttention kernel or model output.
