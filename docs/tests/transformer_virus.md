# Transformer Virus

## Overview
The `transformer_virus` is designed to overwhelm the hardware Transformer Engines. It hammers the die with Warp-Group Matrix Multiply-Accumulate operations to force continuous maximum-density compute cycles.

## Execution Mechanics
The kernel discards high-level APIs to execute relentless operations at highly dense FP8 or FP4 precisions.

* Leverages low-level PTX (`wgmma`) and AMD MFMA compiler intrinsics directly.
* Bypasses traditional warp synchronization by using asynchronous hardware barriers.
* Forces the maximum possible transistor switching rate within the Tensor Cores without relying on VRAM fetches.

## Target Subsystems
* **Primary Target:** Hardware Transformer Engines / 4th+ Gen Tensor Cores.
* **Secondary Target:** Core Voltage Delivery (VRM).

## Failure Symptoms
!!! danger "Critical Failures"
    * **Maximum Voltage Droop:** Triggers the card's lowest voltage/frequency curve state instantly as it attempts to survive the localized current draw.
    * **Severe Clock Stretching:** The silicon cannot safely supply current to the dense matrix regions, aggressively dropping clocks despite low overall board temperatures.
