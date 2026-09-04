# Memory Hammer

## Overview
`memory_hammer` repeatedly reads pairs of **aggressor** addresses that bracket an
untouched **victim**, then verifies the entire buffer. It looks for cells that
change value because of activity on neighbouring rows rather than because
anything wrote to them. Nothing is written during the hammer phase, so any
difference found at verification is a disturbance.

## Execution Mechanics
Two aggressors sit `2 × --hammer_stride` elements apart with the victim between
them. Alternating between the two is what forces a row to close and reopen;
hammering a single address would sit on an open row buffer and disturb nothing.

`--hammer_stride` defaults to 32768 elements (512 KiB). The stride that places
two aggressors in the same bank on different rows depends on the DRAM address
mapping, which is not public for most parts — so the stride is a knob to
**sweep**, not a value that is correct out of the box.

!!! warning "The cache problem — read this before trusting a result"
    A hammer only disturbs a victim if its reads actually reach DRAM. GPU caches
    will answer a tight loop over two addresses forever, and a cached read
    disturbs nothing. Choosing a cache-bypassing load instruction is **not
    sufficient**: if the aggressor working set fits in L2, the reads are still
    served on-chip.

    Every thread therefore walks several aggressor pairs spread across the whole
    allocation (`--hammer_pairs`, default 8), so the aggregate footprint exceeds
    L2. Startup prints the comparison:

    ```
    -> Aggressor Set: ~14 MiB vs L2 2 MiB (exceeds L2)
    ```

    If that line reads `FITS IN L2 - reads will be cache hits`, the run is not
    hammering anything. Raise `--hammer_pairs`. On a 12 GB Ampere card one pair
    per thread sustains ~5.7e10 reads/s (cache speed) while eight pairs drop to
    ~2.2e10 reads/s — the card's DRAM bandwidth.

## Target Subsystems
* **Primary Target:** DRAM row-to-row disturbance between physically adjacent cells.
* **Secondary:** Memory controller behaviour under repeated single-row access.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Disturbed cell:** Reported with the victim index and an `XOR` mask of the
      flipped bits.
    * **A victim that flips only at one particular stride is the interesting
      case.** It suggests a genuine neighbour relationship rather than a weak
      cell, which would fail regardless of stride.
    * Confirm any hit by re-running at the same stride and by running
      `memory_retention` over the same region. A cell failing both is weak, not
      disturbed.

!!! note "Honest limits"
    Without the physical address mapping, Pantheon cannot prove a read opened a
    given row or that two addresses share a bank. The metric is named
    `aggressor-reads/s` — what is actually measured — rather than
    "activations/s", which would imply a DRAM-level guarantee this test cannot
    make. A `PASS` means no disturbance was observed **at this stride**, not that
    the part is immune.

## Usage
```bash
pantheon --test memory_hammer --duration 60 --gpu 0 --mem 50
```

Sweeping the stride, recording every hit. These are options of the workload
binary, so run it directly:

```bash
# From a source checkout (./build); a pip, apt or COPR install compiles into
# ~/.cache/pantheongpu/builds/<version>/<platform>-<target>/ instead:
BIN=./build/memory_hammer
# BIN="$(ls -d ~/.cache/pantheongpu/builds/*/*/ | tail -n 1)memory_hammer"
for s in 8192 16384 32768 65536; do
  "$BIN" 0 60 50 --verify --hammer_stride $s --fault_map hammer_$s.csv
done
```

## Result
`Throughput` reports `aggressor-reads/s`, and startup reports the aggressor
footprint against L2. Read the two together — a high read rate with a footprint
that fits in L2 means the cache absorbed the run.
