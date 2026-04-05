# Memory Write (Standard)

## Overview
The `memory_write` test is the baseline benchmark for sequential VRAM write bandwidth. It uses Non-Temporal Stores to fill Memory bandwidth without polluting the L2 Cache.

## Execution Mechanics
The kernel pushes data using a standard 16x unrolled loop.

* It writes a Rail-to-Rail Pattern, alternating between completely low (`0x00000000`) and completely high (`0xFFFFFFFF`) states.
* Using the cross-platform `store_nt` wrapper, it forces the hardware to write directly to the memory modules instead of staging the data in the local caches.

## Target Subsystems
* **Primary Target:** Sequential VRAM Write Bandwidth.

## Failure Symptoms
!!! warning "Expected Behavior"
    Throughput should be within roughly 85-90% of your card's theoretical maximum bandwidth limit.

!!! danger "Critical Failures"
    * **Degraded Throughput:** Exceptionally low gigabytes-per-second indicates memory controller instability or aggressive background Error Correction Code (ECC) kicking in.
