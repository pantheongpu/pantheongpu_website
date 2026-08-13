# Graph Replay

`graph_replay` captures a compact GPU kernel sequence once, instantiates it as
an execution graph, then repeatedly replays that graph. It tests graph capture,
instantiation, launch, synchronization, and deterministic replay output.

```bash
pantheon --test graph_replay --duration 60 --gpu 0 --mem 25 --verify --profile
```

Pantheon uses the portable HIP graph API. On NVIDIA, the CUDA build maps this
to CUDA Graphs. On AMD ROCm, it uses HIP Graphs. If the installed driver or
runtime cannot capture the sequence, the test exits with the underlying runtime
error instead of reporting a proxy result.

## What it exercises

- Stream capture of the kernel sequence.
- Execution graph instantiation and repeated graph launches.
- Launch and synchronization overhead under sustained replay.
- Input integrity and deterministic replay output with `--verify`.

The reported `graph-steps/s` value is the rate of the captured sequence, not a
model inference or training throughput measurement.
