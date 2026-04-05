# MMA Virus

## Overview
The `mma_virus` leverages physical Warp Matrix Multiply and Accumulate (WMMA) instructions to push hardware Matrix Cores to their absolute thermal limits.



## Execution Mechanics
Instead of relying on standard FP16 instructions which may be mapped to vector ALUs, this kernel explicitly calls physical matrix math intrinsics.
 
* It initializes discrete memory fragments and forces synchronous matrix multiplication across the warp.
* This achieves massive power density, as matrix cores perform orders of magnitude more calculations per clock cycle than standard vector cores.

## Target Subsystems
* **Primary Target:** Physical Matrix/Tensor Cores.
