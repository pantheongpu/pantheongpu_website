# Benchmark Methodology

Pantheon results are workload-specific measurements. Use them to compare the same test under comparable conditions, not as one universal GPU score.

## What a result records

Each benchmark record identifies the Pantheon version, workload, GPU, platform, runtime, and measurement units. When the collector can provide them, records also include driver and toolkit versions, memory allocation, peak temperature and power, average clock, and PCIe state.

The available metrics depend on the workload. Bandwidth tests report transferred data per second, latency tests report operation or access rates, and compute tests report their own unit. A blank metric means that workload does not expose a meaningful value in that column.

The explorer carries **Mem Type** and **Mem Vendor** columns. Pantheon 1.2.1
and later report them for each GPU: the memory type (GDDR6, GDDR7, HBM3 and so
on) and the vendor (Samsung, SK hynix, Micron) are read from the driver's own
memory information table on NVIDIA and from `rocm-smi` on AMD. Results from
earlier releases, and cards whose driver does not expose the table, read N/A
in both columns, and a value can be present for the vendor and absent for the
type.

Read those values as the vendor the board's VBIOS was configured for -- one
value per card, not a survey of the chips. A repaired card fitted with another
vendor's memory would still report the original, so the declared vendor is
what the column means; the memory diagnostics are what measure the chips
themselves.

<!-- TOOLKIT_COVERAGE:START -->
## Toolkit and driver coverage

Every published benchmark records the toolkit and driver it ran under.
This table is generated from the live dataset and lists the versions
that have real hardware results behind them.

| Platform | Toolkit | Driver versions | GPU models tested |
| --- | --- | --- | --- |
| CUDA | 12.0 | 595.84, 595.97, 595.99.02, 596.36 | 2 |
| CUDA | 12.1 | 550.163.01 | 1 |
| CUDA | 12.4 | 550.127.08, 565.57.01, 570.195.03, 570.211.01, 580.105.08, 580.126.09 | 6 |
| CUDA | 12.6 | 560.94 | 1 |
| CUDA | 12.8 | 570.148.08, 570.158.01, 570.195.03, 575.57.08, 580.65.06, 580.95.05, 580.105.08, 580.126.09, 580.126.20, 580.159.03, 580.159.04, 580.173.02, 595.71.05, 595.84, 610.57.04 | 23 |
| CUDA | 12.9 | 595.91.07 | 1 |
| CUDA | 13.0 | 595.71, 595.91.07, 595.97 | 7 |
| CUDA | 13.2 | 595.91.07, 596.36, 610.88 | 9 |
| CUDA | 13.3 | 595.91.07 | 1 |
| ROCm | 7.2.0 | not recorded | 2 |
<!-- TOOLKIT_COVERAGE:END -->

## Reproducing a result

For a useful comparison, keep the workload, Pantheon version, duration, memory setting, driver, toolkit, and GPU power settings the same. Leave the GPU otherwise idle and record ambient cooling conditions when thermal behavior matters.

Run a targeted workload with a fixed duration:

```bash
pantheon --test memory_write --duration 120 --mem 50 --verify
```

Use `--profile` when you also need the per-workload counter and trace reports. Normal runs still capture before-and-after reliability snapshots, including available RAS and PCIe error information.

A profiled run collects roughly 160 hardware counters per workload. Each value is the median across the launches of the kernel that owned the profiled runtime, not an average over the whole run, and every counter block records which kernel it describes along with that kernel's launch count and share of runtime. Read a counter as a property of that kernel.

Counters are kept in the published reports rather than in the explorer table: there are too many to show as columns, and carrying them in the table's data file would multiply its size several times over for a figure almost nobody filters on.

Profiling is expensive and does not change what a score means. Measured at `--duration 300`, a profiled workload takes about 3.6 times as long as an unprofiled one, and profiled scores agree with unprofiled scores to within a fraction of a percent on every workload tested except `tensor_virus`, which runs about 1% slower under the profiler.

## Verification and reliability

`--verify` checks workload-specific output where verification is implemented. A successful verification result means the test completed its defined correctness check. It does not certify the GPU for every possible workload or operating condition.

Pantheon compares the available reliability data before and after every workload. Driver support varies by vendor, GPU, operating system, and permissions. Treat unsupported counters as unavailable, not as evidence that an error count is zero.

## Scores that changed between releases

Some releases change what a workload measures. A result from the new release is then a different measurement from an older one, even on the same card, and the two should not be compared or joined into one trend. [Per-card history](gpu-history.md) draws them as separate series.

| Release | Workloads | What changed |
| --- | --- | --- |
| 1.2.3 | `voltage`, `incinerator`, `fp64_virus`, `pulse_virus`, `tensor_virus`, `sfu_stress`, `memory_thermal_asym`, `memory_retention_bake`, `mma_virus`, `omni_virus` | Reworked. The arithmetic in these tests could saturate, which left their verification vacuous and their power draw low; it is now bounded. `mma_virus` and `omni_virus` also run the vendor BF16 GEMM by default (`--gemm 0` selects the old path). Scores and power draw changed on purpose: on an A10G the change runs from -51% (`mma_virus`) to +227% (`voltage`). |
| 1.2.3 | `galpat` | Compares all four 32-bit lanes of every cell it reads, where it compared one. The same card scores about 6% lower. |

A build of the source tree between the 1.2.2 and 1.2.3 releases reports 1.2.2 although it scores the new way, so a 1.2.2 result from a source checkout can sit on the wrong side of the line.

## Comparing results fairly

- Compare like with like: the same workload and equivalent command line settings.
- Prefer runs with the same Pantheon release and a similar duration.
- Do not compare a result with one from before the release that changed its workload (see above).
- Check the driver, toolkit, clock, temperature, power, and throttle fields before drawing conclusions.
- Do not rank unrelated workloads by their displayed number or unit.
- Keep raw JSON reports when submitting or discussing a result so others can inspect the context.

## Submitting a benchmark

Use the [benchmark submission form](https://github.com/pantheongpu/pantheongpu_website/issues/new?template=benchmark-submission.yml) to contribute a run. Include the command, raw result report, GPU and software information, and any verification or RAS warning. Remove serial numbers and other sensitive identifiers before sharing artifacts publicly.
