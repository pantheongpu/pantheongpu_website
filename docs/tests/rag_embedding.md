# RAG Embedding

`rag_embedding` applies dense embedding-vector projection pressure relevant to
retrieval and RAG front ends.

```bash
pantheon --test rag_embedding --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Compute | Dense embedding projection-style arithmetic. |
| Memory | Repeated reads through a synthetic embedding working set. |
| Telemetry | Compute, cache, DRAM, power, clock, and thermal behavior. |
| Result | Synthetic embedding vectors per second. |

It does not benchmark a model, vector database, embedding quality, or retrieval
latency. Use it to isolate the underlying GPU execution path.
