# AI Workloads

Pantheon includes controlled GPU stress tests for modern AI execution paths.
They measure synthetic diagnostic work, not model quality or end-to-end serving
performance.

## Inference

```bash
pantheon --test inference --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Workload | Focus |
| --- | --- |
| `llm_decode` | Synthetic dependent KV-cache gather and projection pressure. |
| `llm_prefill` | Synthetic long-context causal-scan and projection pressure. |
| `kv_cache_churn` | Synthetic paged/ragged cache-update pressure. |
| `fused_attention` | Attention-style compute and memory proxy. It is not a fused-attention kernel. |
| `rope_stress` | RoPE-style rotary-position math proxy. |
| `quantized_gemm` | Packed low-precision projection proxy. It is not a full GEMM benchmark. |
| `serving_mix` | Mixed-request pressure proxy. It does not model a production scheduler or queue. |
| `speculative_decode` | Draft/verify execution proxy. It does not run draft and target models. |
| `moe_router` | Sparse Top-K routing proxy. It does not perform expert all-to-all communication. |

## Training, runtime, and auxiliary AI

| Workload | Command | Focus |
| --- | --- | --- |
| `transformer_train_step` | `pantheon --test training --duration 60 --gpu 0 --mem 50 --verify --profile` | Transformer forward/backward and optimizer-style proxy. |
| `allocation_fragmentation` | `pantheon --test allocation_fragmentation --duration 60 --gpu 0 --mem 25 --verify --profile` | Allocates and frees device memory in a pattern that fragments the heap and measures how the allocator copes; an allocation refused while well under budget is the signal. The GPU itself stays almost idle by design. |
| `graph_replay` | `pantheon --test graph_replay --duration 60 --gpu 0 --mem 25 --verify --profile` | Actual CUDA Graph or HIP Graph capture, instantiation, and replay test. |
| `rag_embedding` | `pantheon --test ai_auxiliary --duration 60 --gpu 0 --mem 50 --verify --profile` | RAG embedding projection proxy. |
| `vision_encoder` | `pantheon --test ai_auxiliary --duration 60 --gpu 0 --mem 50 --verify --profile` | Vision-encoder projection proxy. |

`--mem` selects the percentage of free VRAM used by the synthetic working set.
Start at 25% if the GPU has other active workloads.

!!! note
    Use Pantheon to isolate hardware and runtime behavior. Measure production
    throughput, queueing, time to first token, inter-token latency, and model
    accuracy with the actual serving framework and model separately.
