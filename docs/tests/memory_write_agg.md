# Memory Write (Aggressive)

## Overview
The `memory_write_agg` test pushes VRAM and Infinity Fabric bandwidth to the absolute limit while intentionally maximizing electrical noise on the bus.



## Execution Mechanics
This kernel modifies a standard sequential write by introducing three aggressive changes:

1. **Crosstalk Pattern:** It rapidly alternates writing `0xAAAAAAAA` (10101010...) and `0x55555555` (01010101...). Switching between these forces every single bit on the physical bus to flip relative to its neighbor, maximizing Inter-Symbol Interference (ISI) and crosstalk.
2. **Massive Unrolling:** It utilizes a 64x unroll factor to ensure the instruction pipeline consists of nothing but pure `STORE` commands.
3. **Cache Bypass:** It leverages Non-Temporal (NT) stores to write directly to the Memory modules, bypassing the L2 cache entirely.

## Target Subsystems
* **Primary Target:** VRAM modules and interconnect fabric.
* **Secondary Target:** Unified Memory Controllers (UMCs).

## Failure Symptoms
!!! danger "Critical Failures"
    * **System Freeze / Driver Timeout:** The electrical noise causes signal integrity to collapse, hanging the memory controller.
    * **Visual Artifacts:** Bit flips occur on the bus before reaching the physical memory cells.
