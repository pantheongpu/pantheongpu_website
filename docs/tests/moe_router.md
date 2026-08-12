# MoE Router

`moe_router` stresses sparse Top-K-style routing and gated accumulation, which
are local execution components of mixture-of-experts inference.

```bash
pantheon --test moe_router --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Routing | Deterministic sparse expert-selection pressure. |
| Compute | Gated projection-style accumulation. |
| Memory | Synthetic expert-state working-set reads. |
| Result | Synthetic routed tokens per second. |

This is a single-GPU routing diagnostic. It does not include multi-GPU
all-to-all communication or a framework-specific MoE implementation.
