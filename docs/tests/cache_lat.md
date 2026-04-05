# Cache Latency

## Overview
The `cache_lat` test evaluates the interconnect and cache hierarchy by forcing worst-case scenario memory reads.

## Execution Mechanics
Modern GPUs rely heavily on hardware prefetchers that predict what memory will be accessed next. This kernel defeats them entirely through pointer-chasing. 

* It uses Linear Congruential Generator (LCG) constants to build a randomized memory traversal map.
* Because every read explicitly depends on the address retrieved by the *previous* read, the hardware cannot pre-fetch data, stalling the pipeline and exposing the true physical latency of the cache interconnects.

## Target Subsystems
* **Primary Target:** L1/L2 Cache Latency and Interconnects.
