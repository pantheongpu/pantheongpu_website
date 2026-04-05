# SFU Virus

## Overview
The `sfu_stress` targets the Special Function Units (SFU) by hammering the transcendental math pipelines. 



## Execution Mechanics
Transcendental math relies on high-latency, low-throughput instructions. 

* The kernel forces a continuous chain of SIN, COS, EXP, LOG, and RSQRT calculations.
* These specific units often share power rails with Texture units or Tensor cores, meaning stressing them can reveal hidden power-delivery bottlenecks.

## Target Subsystems
* **Primary Target:** Special Function Units (SFU).
