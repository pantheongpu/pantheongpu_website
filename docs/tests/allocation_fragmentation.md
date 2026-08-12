# Allocation Fragmentation

`allocation_fragmentation` is a runtime-focused diagnostic for memory-management
pressure. It uses a synthetic working set to exercise allocation-like reuse and
state churn while Pantheon records device telemetry and profiling artifacts.

```bash
pantheon --test allocation_fragmentation --duration 60 --gpu 0 --mem 25 --verify --profile
```

| Area | What it tests |
| --- | --- |
| Runtime memory path | Repeated working-set setup and reuse pressure. |
| VRAM | Allocation-sized memory pressure selected with `--mem`. |
| Telemetry | Power, clocks, thermals, memory usage, cache/DRAM counters, and throttling with `--profile`. |
| Result | Synthetic allocation events per second. |

Use it to compare runtime stability across drivers and configurations. It does
not emulate the allocator or eviction policy of a particular framework.
