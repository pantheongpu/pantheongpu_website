# RAS Validator

## Overview
The `ras_validator` is an active ECC (Error-Correcting Code) scrubber stress test. It is designed to detect silent data corruption or expose the latency jitter of active hardware memory scrubbing.

## Execution Mechanics
This test operates in two distinct phases:

1. **Pristine Initialization:** It fills the VRAM with a highly distinct alternating bit pattern (`0xAAAA5555`).
2. **Aggressive Scrubbing:** It continuously reads the memory back using 8x unrolled Non-Temporal loads. 
    * By using Non-Temporal loads, it actively bypasses the L1/L2 caches and forces physical DRAM fetches on every cycle.

## Target Subsystems
* **Primary Target:** Hardware ECC scrubbing engines and Unified Memory Controllers (UMCs).
* **Secondary Target:** Physical Memory/GDDR modules.

## Failure Symptoms
If the hardware ECC successfully corrects a Single-Bit Error (CE), the throughput will momentarily drop as the hardware injects stall cycles. 

!!! danger "Critical Failures"
    * **Uncorrectable Errors (UE):** If a Double-Bit Error occurs or the hardware ECC fails entirely, the software will log the corrupted payload and report silent data corruption to the host.
