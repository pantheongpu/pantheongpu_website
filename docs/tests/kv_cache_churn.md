---
title: KV Cache Churn
---

# KV Cache Churn

`kv_cache_churn` targets the mutable memory-management path behind KV caching.
It performs sparse reads and updates over synthetic pages with changing offsets,
which is useful for investigating the cache pressure created by ragged requests.

```bash
pantheon --test kv_cache_churn --gpu 0 --duration 60 --mem 50 --verify --profile
```

| Area | What the workload exercises |
| --- | --- |
| Cache layout | Mutable synthetic pages sized from free VRAM. |
| Access pattern | Pseudo-random page selection, sparse reads, and token-like appends. |
| Verification | `--verify` detects invalid cache entries after the update phase. |
| Result | Cache updates per second, reported as `cache-updates/s`. |

This test does not emulate a specific runtime allocator, eviction policy,
request queue, or model architecture. Use it as a controlled cache and memory
stress test alongside an end-to-end serving benchmark.
