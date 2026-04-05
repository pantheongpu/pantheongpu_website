# Memory Read (Aggressive)

## Overview
The `memory_read_agg` kernel maximizes read operations using heavily unrolled, volatile pointer accesses. It forces continuous, direct memory fetches without caching.

## Execution Mechanics
To prevent the compiler from optimizing the memory requests away, the kernel casts the memory buffer to `volatile unsigned int*`.

* It utilizes a manual 16x unroll factor within the thread block.
* By aggressively chaining the volatile reads, it ensures the memory controllers are completely saturated with fetch requests, keeping the read queues full at all times.

## Target Subsystems
* **Primary Target:** Memory Controllers and VRAM Read Bandwidth.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Stuttering or Black Screens:** The aggressive read operations overwhelm the controller, triggering a driver reset.
    * **Memory ECC Errors:** Physical degradation causing read errors at high utilization.
