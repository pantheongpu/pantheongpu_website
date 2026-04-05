# Tensor Virus

## Overview
The `tensor_virus` uses Half-Precision (FP16) mathematics to deeply saturate the Tensor and Matrix cores. 

## Execution Mechanics
* It executes an FP16 hammer using a universal Fused Multiply-Add (FMA) loop. 
* To ensure continuous saturation across both AMD and NVIDIA architectures, it relies on universal hardware intrinsics.
* The instructions continuously flip polarity to prevent values from converging, ensuring the datapaths cannot aggressively power-gate.

## Target Subsystems
* **Primary Target:** Tensor Cores and FP16 compute pipelines.
