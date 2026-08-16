---
hide:
  - navigation
---

# Benchmark Methodology

Pantheon results are workload-specific measurements. Use them to compare the same test under comparable conditions, not as one universal GPU score.

## What a result records

Each benchmark record identifies the Pantheon version, workload, GPU, platform, runtime, and measurement units. When the collector can provide them, records also include driver and toolkit versions, memory allocation, peak temperature and power, average clock, and PCIe state.

The available metrics depend on the workload. Bandwidth tests report transferred data per second, latency tests report operation or access rates, and compute tests report their own unit. A blank metric means that workload does not expose a meaningful value in that column.

## Reproducing a result

For a useful comparison, keep the workload, Pantheon version, duration, memory setting, driver, toolkit, and GPU power settings the same. Leave the GPU otherwise idle and record ambient cooling conditions when thermal behavior matters.

Run a targeted workload with a fixed duration:

```bash
pantheon --test memory_write --duration 120 --mem 50 --verify
```

Use `--profile` when you also need the per-workload counter and trace reports. Normal runs still capture before-and-after reliability snapshots, including available RAS and PCIe error information.

## Verification and reliability

`--verify` checks workload-specific output where verification is implemented. A successful verification result means the test completed its defined correctness check. It does not certify the GPU for every possible workload or operating condition.

Pantheon compares the available reliability data before and after every workload. Driver support varies by vendor, GPU, operating system, and permissions. Treat unsupported counters as unavailable, not as evidence that an error count is zero.

## Comparing results fairly

- Compare like with like: the same workload and equivalent command line settings.
- Prefer runs with the same Pantheon release and a similar duration.
- Check the driver, toolkit, clock, temperature, power, and throttle fields before drawing conclusions.
- Do not rank unrelated workloads by their displayed number or unit.
- Keep raw JSON reports when submitting or discussing a result so others can inspect the context.

## Submitting a benchmark

Use the [benchmark submission form](https://github.com/saqibkh/pantheongpu_website/issues/new?template=benchmark-submission.yml) to contribute a run. Include the command, raw result report, GPU and software information, and any verification or RAS warning. Remove serial numbers and other sensitive identifiers before sharing artifacts publicly.
