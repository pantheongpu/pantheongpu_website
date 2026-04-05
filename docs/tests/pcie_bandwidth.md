# PCIe Bandwidth Thrasher

## Overview
The `pcie_bandwidth` test stresses the motherboard interconnect by forcing massive bidirectional transfers between the CPU and GPU. It detects bad riser cables, unstable PCIe generations (Gen4/Gen5), and driver timeouts.



## Execution Mechanics
To hit peak Direct Memory Access (DMA) speeds, this kernel bypasses standard pageable memory.

* It allocates "pinned" (page-locked) memory on the Host (CPU side).
* It creates two independent execution streams to allow for asynchronous overlap.
* The benchmark aggressively ping-pongs a large 256MB buffer, simultaneously executing Host-to-Device (H2D) and Device-to-Host (D2H) memory copies.

## Target Subsystems
* **Primary Target:** PCIe Bus Interface and Motherboard traces.
* **Secondary Target:** CPU-side memory controller.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Low FPS / Stuttering:** Dropping link speeds under load (e.g., falling from `Gen4 x16` to `Gen3 x8`) due to physical degradation or poor mounting pressure.
    * **Audio Crackling:** PCIe bus contention causing interrupts on the host operating system.
