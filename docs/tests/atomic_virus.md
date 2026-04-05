# Atomic Virus

## Overview
The `atomic_virus` is designed to overwhelm the L2 Cache Arbiters. It hammers memory with Atomic operations using a wide stride to force continuous "Read-Modify-Write" cycles.



## Execution Mechanics
The kernel allocates roughly 60% of the available VRAM to ensure the working set spills out of the ultra-fast L1 cache and forces continuous trips to L2.

* Threads perform an `atomicAdd` on wide-strided memory addresses.
* This forces the hardware to lock the cache line, read the value, update it, write it back, and unlock it.
* By doing this concurrently across millions of threads, the internal fabric handling cache coherency is pushed to its absolute limit.

## Target Subsystems
* **Primary Target:** L2 Cache Arbiters and Render Output Units (ROPs).
* **Secondary Target:** Cache coherency fabric.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Erratic Performance:** Severe drops in MAPS (Million Atomic Operations Per Second) indicate the arbiters are thermal-throttling or dropping requests.
    * **Application Crashes:** Cache locking mechanisms fail, causing a segmentation fault or unhandled memory exception.
