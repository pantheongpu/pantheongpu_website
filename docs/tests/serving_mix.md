# Serving Mix

`serving_mix` creates mixed execution pressure representative of requests with
different prompt and generation demands.

```bash
pantheon --test serving_mix --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Compute | Mixed projection-style work. |
| Memory | Synthetic request working-set reads. |
| Telemetry | Power, clocks, cache/DRAM behavior, and throttling. |
| Result | Synthetic requests per second. |

This is not an HTTP server or queueing benchmark. Measure TTFT, inter-token
latency, and production concurrency using the actual serving stack separately.
