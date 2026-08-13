# All-Reduce

`all_reduce` validates a two-rank GPU sum-and-broadcast collective. Pantheon
initializes GPU 0 with `1` and its peer GPU with `2`, reduces the values to `3`,
then confirms that both ranks receive the same result.

```bash
pantheon --test all_reduce --duration 60 --gpu 0 --verify --profile
```

## Transport behavior

When the selected GPU pair exposes bidirectional peer access, Pantheon uses
direct peer DMA. If peer access is unavailable, it uses a host-staged fallback
and identifies that mode in the result output. The fallback is useful for
correctness and topology diagnosis, but its throughput is not a direct P2P
bandwidth result.

## Verification

`--verify` checks the complete output buffer on both GPUs. For a verification
self-test, add `--inject_error`; Pantheon corrupts one value on the peer rank,
reports `Verification: FAIL`, and exits non-zero.

## Requirements

- At least two visible GPUs.
- The chosen GPU and its next visible peer GPU must be accessible to the
  runtime.
- CUDA or ROCm/HIP runtime support. The workload uses portable HIP APIs.
