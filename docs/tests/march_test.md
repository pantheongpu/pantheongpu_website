# March Test

## Overview
`march_test` runs a **March C-** sequence over VRAM. The bandwidth workloads read
and write in whatever order goes fastest; a march applies a fixed, ordered
read-then-write sequence to every cell, so the *order* of operations is itself
part of the test.

That ordering is what makes it different. Bandwidth tests find cells that cannot
hold a value. A march finds cells whose value depends on what happened to a
neighbouring cell just before, coupling faults that are invisible to any test
touching memory in parallel or in arbitrary order.

## Execution Mechanics
March C- is six elements, run in both address directions. `w0` writes zeros,
`r0` reads and expects zeros, `⇑` ascends and `⇓` descends:

| # | Element | Catches |
| :--- | :--- | :--- |
| 0 | `⇑ (w0)` | n/a (initialisation) |
| 1 | `⇑ (r0, w1)` | Stuck-at-1, transition faults |
| 2 | `⇑ (r1, w0)` | Stuck-at-0, transition faults |
| 3 | `⇓ (r0, w1)` | Coupling faults, descending |
| 4 | `⇓ (r1, w0)` | Coupling faults, descending |
| 5 | `⇓ (r0)` | Final verification |

Running both directions is what separates March C- from a simple write/read
pass: a coupling fault between two cells is only exposed from one direction.

A march is inherently sequential and a GPU is not, so each thread is given a
**private contiguous chunk** and marches it in order. The ordered sequence is
preserved within a chunk while chunks run in parallel. Startup reports
`Chunk/thread` so the ordered run length is visible; the host caps the thread
count so no chunk falls below 4096 elements, since coupling faults need a run of
addresses to appear.

## Target Subsystems
* **Primary Target:** DRAM cell integrity: stuck-at, transition, and coupling faults.
* **Secondary:** Address ordering behaviour within a contiguous region.

## Failure Symptoms
!!! danger "Critical Failures"
    * **March error:** Reported with the element index, expected and actual
      values, and an `XOR` mask naming the flipped bits.
    * **Which element failed tells you the fault class.** A failure at element 1
      or 2 is a stuck-at or transition fault. A failure only in the descending
      elements (3, 4) points at a coupling fault.
    * One bit position failing across many unrelated addresses indicates a stuck
      data lane rather than a defective cell.

!!! note "Coverage boundary"
    Coupling faults *between* chunks are not covered. Sweeping `--grid_size`
    moves the chunk boundaries.

## Usage
```bash
pantheon --test march_test --duration 60 --gpu 0 --mem 50
```

Record every failing address rather than the capped console sample.
`--fault_map` is an option of the workload binary, not of the `pantheon`
command, so run the binary directly:

```bash
# From a source checkout, where make puts the binaries in ./build:
./build/march_test 0 60 50 --verify --fault_map march_faults.csv

# From a pip, apt or COPR install the binaries are compiled on first run into
# ~/.cache/pantheongpu/builds/<version>/<platform>-<target>/ (for example
# 1.2.0/cuda-86). Run the one for your card from there:
"$(ls -d ~/.cache/pantheongpu/builds/*/*/ | tail -n 1)march_test" 0 60 50 --verify --fault_map march_faults.csv
```

## Result
`Throughput` reports `march-ops/s`, read and write operations across all march
elements. It is a progress metric, not a bandwidth figure: the ordered access
pattern is deliberately not the fastest way to move data.
