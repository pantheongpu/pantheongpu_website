# TLB Avalanche

## Overview
The `tlb_avalanche` test is a specialized Memory Management Unit (MMU) stressor. It forces a near 100% Translation Lookaside Buffer (TLB) miss rate to choke the hardware page-table walkers.



## Execution Mechanics
Instead of sequential memory reads, this kernel utilizes a fast, on-die Linear Congruential Generator (LCG) to calculate pseudo-random jumps across the entire VRAM allocation. 

* It specifically targets address boundaries larger than standard (4KB) and huge (2MB) pages.
* By ensuring every single memory access lands on a completely different virtual memory page, the TLB is never able to cache the virtual-to-physical address translation.

## Target Subsystems
* **Primary Target:** Translation Lookaside Buffer (TLB) and hardware page-table walkers.
* **Secondary Target:** VRAM allocation table limits.

## Failure Symptoms
!!! warning "Expected Behavior"
    Throughput on this test will look absolutely abysmal (often fractions of a GB/s) compared to standard reads. This confirms the queue is successfully overwhelmed.

!!! danger "Critical Failures"
    * **Severe System Stutter:** The host OS may freeze as the PCIe bus gets flooded with page-fault translation requests.
    * **Driver Timeout:** The GPU takes too long to resolve the physical addresses and is reset by the operating system.
