# Memory Cache Fracture

## Overview
The `memory_cache_fracture` test is designed to overload the Unified Memory Controller (UMC) queues by forcing massive amounts of uncoalesced memory reads.

## Execution Mechanics
Normally, a GPU wavefront (or warp) fetches data in a single, large coalesced transaction if threads access contiguous memory.

* This kernel forces every thread in the wavefront to request a memory address separated by exactly 256 bytes.
* Because of this specific offset, the UMC physically cannot merge the requests.
* A single instruction forces 64 completely separate, independent cache-line fetches.

## Target Subsystems
* **Primary Target:** UMC Queues and Cache Arbiters.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Queue Overload:** The memory controller queues overflow, causing extremely low bandwidth or a total hardware lockup.
