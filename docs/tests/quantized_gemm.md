# Quantized GEMM

`quantized_gemm` exercises packed low-precision values, dequantization-like
math, and projection-style arithmetic relevant to quantized inference paths.

```bash
pantheon --test quantized_gemm --duration 60 --gpu 0 --mem 50 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Precision path | Packed low-precision unpacking and scaling proxy. |
| Compute | Dense projection-style arithmetic. |
| Memory | Repeated reads through a synthetic weight/context working set. |
| Result | Synthetic quantized operations per second. |

Use it for comparative hardware diagnostics. It does not claim a specific INT4,
INT8, FP8, or FP4 model-kernel implementation or accuracy result.
