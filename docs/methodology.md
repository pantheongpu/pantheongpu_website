# Benchmark Methodology

Pantheon results are workload-specific measurements. Use them to compare the same test under comparable conditions, not as one universal GPU score.

## What a result records

Each benchmark record identifies the Pantheon version, workload, GPU, platform, runtime, and measurement units. When the collector can provide them, records also include driver and toolkit versions, memory allocation, peak temperature and power, average clock, and PCIe state.

The available metrics depend on the workload. Bandwidth tests report transferred data per second, latency tests report operation or access rates, and compute tests report their own unit. A blank metric means that workload does not expose a meaningful value in that column.

<!-- TOOLKIT_COVERAGE:START -->
## Toolkit and driver coverage

Every published benchmark records the toolkit and driver it ran under.
This table is generated from the live dataset and lists the versions
that have real hardware results behind them.

| Platform | Toolkit | Driver versions | GPU models tested |
| --- | --- | --- | --- |
| CUDA | 12.0 | 595.84, 595.97, 596.36 | 2 |
| CUDA | 12.4 | 550.127.08, 565.57.01, 570.195.03, 570.211.01, 580.105.08, 580.126.09 | 6 |
| CUDA | 12.6 | 560.94 | 1 |
| CUDA | 12.8 | 570.148.08, 570.195.03, 580.105.08 | 7 |
| CUDA | 12.9 | 595.91.07 | 1 |
| CUDA | 13.0 | 595.71, 595.91.07, 595.97 | 7 |
| CUDA | 13.2 | 595.91.07, 596.36 | 6 |
| CUDA | 13.3 | 595.91.07 | 1 |

No AMD ROCm hardware runs have been published yet; ROCm support is
currently validated through the compile matrix in the Pantheon
repository rather than through published benchmark results.
<!-- TOOLKIT_COVERAGE:END -->

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

Use the [benchmark submission form](https://github.com/pantheongpu/pantheongpu_website/issues/new?template=benchmark-submission.yml) to contribute a run. Include the command, raw result report, GPU and software information, and any verification or RAS warning. Remove serial numbers and other sensitive identifiers before sharing artifacts publicly.
