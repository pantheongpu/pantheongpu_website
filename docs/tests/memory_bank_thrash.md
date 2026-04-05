# Memory Bank Thrasher

## Overview
The `memory_bank_thrash` virus forces continuous row-buffer misses, completely destroying standard sequential memory performance.



## Execution Mechanics
Modern memory is highly optimized for sequential reads where a single "row" is opened and read continuously. This kernel maliciously defeats that optimization:

* It forces threads to stride across exact 2MB memory boundaries (131,072 `uint4` elements).
* This specific offset is a common threshold that maps back to the same physical memory channel and bank, but lands on a completely different page.
* The memory controller is forced to constantly close the active row, precharge the bank, and open a new row for almost every single read request.

## Target Subsystems
* **Primary Target:** Memory Row Buffers and Memory Controller scheduling logic.

## Failure Symptoms
!!! warning "Expected Behavior"
    Throughput drops significantly compared to standard reads as the memory controller stalls while waiting for row precharge cycles.

!!! danger "Critical Failures"
    * **High Latency Stalls:** If the memory controller's internal queue management fails to handle the massive influx of page-misses, the driver will hang.
