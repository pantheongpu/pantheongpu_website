# Speculative Decode

`speculative_decode` stresses alternating draft and verification-style work to
exercise a different compute and cache mix from ordinary autoregressive decode.

```bash
pantheon --test speculative_decode --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Execution | Repeated draft/verify-style work phases. |
| Memory | Synthetic token-state and cache reads. |
| Telemetry | Cache, DRAM, power, clock, and thermal response. |
| Result | Synthetic verified tokens per second. |

It does not implement a particular draft model, acceptance policy, or serving
runtime; use it to compare underlying hardware behavior.
