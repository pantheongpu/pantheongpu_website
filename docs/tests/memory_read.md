# Memory Read (Standard)

## Overview
The `memory_read` test establishes the baseline sequential read bandwidth of the GPU's memory subsystem. 

## Execution Mechanics
This kernel uses volatile reads decomposed into 32-bit chunks. 

* It utilizes a standard 4x unroll per thread.
* **Architecture Fix:** Attempting to execute single 128-bit vector loads on unaligned buffers can cause segmentation faults on specific AMD RDNA hardware. This kernel decomposes the fetch into smaller, safer chunks to ensure cross-platform stability.

## Target Subsystems
* **Primary Target:** Sequential VRAM Read Bandwidth.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Low Throughput:** Just like the write test, low throughput signifies memory controller degradation or ECC intervention.
