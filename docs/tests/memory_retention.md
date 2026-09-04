# Memory Retention

## Overview
`memory_retention` writes a known payload into VRAM, leaves it completely
untouched for a chosen interval, then verifies it. It exposes cells that lose
their charge with **time**.

## How It Differs From Memory Retention Bake
The two share a name but look for different defects.

| | [Memory Retention Bake](memory_retention_bake.md) | `memory_retention` |
| :--- | :--- | :--- |
| During the hold | Runs an ALU burn to heat the die | Nothing touches the payload |
| Finds | Cells that fail when **hot** | Cells that fail after **time** |
| Variable | Temperature | `--retention_delay` |

A cell can pass one and fail the other. Marginal cells often only fail past a
particular retention interval, which is why the delay is a knob to sweep rather
than a fixed value.

## Execution Mechanics
1. **Payload injection:** the allocation is filled using `--init_pattern`, so
   retention can be compared across data backgrounds.
2. **The hold:** the process sleeps for `--retention_delay` (defaulting to
   `--duration`). Nothing reads or writes the payload.
3. **Verification:** the payload is read back with non-temporal access, so a
   cached copy cannot mask a leaked cell.

!!! note "Why the wait lives inside the binary"
    Device memory is released when the process exits. An external tool cannot
    write a payload, wait, and read it back across separate invocations, because
    the allocation does not survive the first one. The idle period therefore has
    to live inside the workload, with the delay exposed as a knob.

## Target Subsystems
* **Primary Target:** DRAM charge retention over time, unrefreshed by any access.
* **Secondary:** Pattern-dependent retention, via `--init_pattern`.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Retention error:** Reported with the element index and an `XOR` mask
      naming the flipped bits.
    * One bit position failing across many unrelated addresses points at a data
      lane rather than a cell.
    * Sweeping the delay narrows the retention margin: the shortest delay that
      reproduces a failure is that cell's effective retention limit.

## Usage
```bash
pantheon --test memory_retention --duration 60 --gpu 0 --mem 50
```

Sweeping the interval and recording every failing address. These are options
of the workload binary, so run it directly:

```bash
# From a source checkout:
./build/memory_retention 0 300 50 --verify --retention_delay 300 \
  --fault_map retention_300s.csv

# From a pip, apt or COPR install the binaries are compiled on first run into
# ~/.cache/pantheongpu/builds/<version>/<platform>-<target>/ (for example
# 1.2.0/cuda-86). Run the one for your card from there:
"$(ls -d ~/.cache/pantheongpu/builds/*/*/ | tail -n 1)memory_retention" 0 300 50 --verify \
  --retention_delay 300 --fault_map retention_300s.csv
```

## Result
`Throughput` reports `retained-MiB`, the size of the payload held and verified.
Nothing is transferred during the hold, so a bandwidth figure would be
meaningless here.
