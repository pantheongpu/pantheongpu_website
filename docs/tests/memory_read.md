# Memory Read (Standard)

## Overview
The `memory_read` test establishes the baseline sequential read bandwidth of the GPU's memory subsystem. 

## Execution Mechanics
Each thread issues 128-bit (`uint4`) loads in a coalesced grid-stride loop,
unrolled 16 deep, and XORs every value into a register accumulator so the
compiler cannot drop the loads.

* The accumulator is written back only when it equals a sentinel it practically
  never matches, which keeps the sink at zero cost.
* The buffer comes from the runtime allocator, so the vector loads are aligned
  on both vendors; no decomposition into smaller chunks is needed.

## Target Subsystems
* **Primary Target:** Sequential VRAM Read Bandwidth.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Low Throughput:** Just like the write test, low throughput signifies memory controller degradation or ECC intervention.
