# GALPAT (Galloping Pattern)

## Overview
`galpat` writes a uniform background across a region, flips **one** cell to the
opposite value, then reads that cell alternately against every other cell in the
region. The single flipped cell "gallops" against its neighbours, which exposes
a cell whose value can be pulled by a specific *other* cell.

A march tests each cell against the operations applied to it in address order.
GALPAT tests each cell against **every other cell in the region**, which is what
catches address-decoder faults and coupling between cells far apart in address
space but adjacent in the physical array.

## Execution Mechanics
The cost is quadratic: a full GALPAT over N cells is O(N²) reads. Running it
across an entire GPU allocation cannot finish, which is why this workload is
region-bounded by design.

| Flag | Default | Meaning |
| :--- | :--- | :--- |
| `--region_offset` | 0 | First element of the region under test |
| `--region_size` | 1048576 | Number of elements in the region |
| `--region_chunk` | 512 | Gallop window each thread covers |

The region is **clamped** into the allocation rather than rejected, so a region
running past the end of memory shrinks instead of failing the run.

The intended use is as a **second stage**. Sweep memory with the linear tests
(`march_test`, `memory_hammer`), record failing addresses with the workload
binaries' `--fault_map` option, then aim `galpat` at the implicated region for
the expensive exhaustive check.

## Target Subsystems
* **Primary Target:** Address-decoder faults and cell-to-cell coupling within a region.
* **Secondary:** Sense-amplifier behaviour under repeated opposite-value reads.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Gallop error:** Reported with the element index and an `XOR` mask of the
      flipped bits.
    * A cell that fails only when galloped against one specific partner points at
      a decoder or coupling fault rather than a weak cell.

!!! note "Coverage boundary"
    A `PASS` covers only the region that was tested. Startup prints the exact
    `Region: [offset, end)` — read it before concluding anything about the rest
    of memory.

## Usage
```bash
pantheon --test galpat --duration 60 --gpu 0 --mem 50
```

Aimed at a region another test has already implicated. These are options of
the workload binary, so run it directly:

```bash
# From a source checkout:
./build/galpat 0 60 50 --verify --region_offset 4194304 --region_size 65536 \
  --fault_map galpat_region.csv

# From a pip, apt or COPR install the binaries are compiled on first run into
# ~/.cache/pantheongpu/builds/<version>/<platform>-<target>/ (for example
# 1.2.0/cuda-86). Run the one for your card from there:
"$(ls -d ~/.cache/pantheongpu/builds/*/*/ | tail -n 1)galpat" 0 60 50 --verify \
  --region_offset 4194304 --region_size 65536 --fault_map galpat_region.csv
```

## Result
`Throughput` reports `gallop-reads/s`. Because coverage is quadratic in region
size, this number is only comparable between runs that used the same
`--region_size`.
