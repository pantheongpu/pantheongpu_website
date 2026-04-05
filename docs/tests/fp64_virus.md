# FP64 Chokehold

## Overview
The `fp64_virus` exposes the physical Double Precision (FP64) ALU limits of the GPU.

## Execution Mechanics
Because consumer gaming GPUs often drastically limit their FP64 performance compared to enterprise datacenter accelerators, this test acts as a physical chokehold.
 
* It forces deep unrolled loops of Double Precision Fused Multiply-Add operations.
* This exposes whether the die is artificially fused to limit FP64 throughput or if it has genuine, unthrottled datacenter capabilities.

## Target Subsystems
* **Primary Target:** FP64 (Double Precision) ALUs.
