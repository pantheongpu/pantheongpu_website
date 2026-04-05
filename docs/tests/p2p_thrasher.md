# P2P Thrasher

## Overview
The `p2p_thrasher` is designed to overwhelm the physical interconnect bridges between multiple GPUs. It hammers the fabric with DMA operations using bidirectional transfers to force continuous cross-die traffic.

## Execution Mechanics
The kernel bypasses the host CPU entirely to perform massive, simultaneous asynchronous peer-to-peer (P2P) memory copies.

* Initiates bidirectional Device-to-Device transfers without staging through system RAM.
* Floods the PCIe Root Complex and specialized bridges like NVLink or Infinity Fabric.
* Runs concurrently across all available links to maximize cross-die traffic and synchronization overhead.

## Target Subsystems
* **Primary Target:** NVLink, AMD Infinity Fabric, and PCIe Root Complex.
* **Secondary Target:** DMA/Copy Engines.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Degraded Routing:** Severe drops in throughput (GB/s) indicate fabric routing bottlenecks or thermal throttling on the interconnect bridges.
    * **Physical Link Crashes:** Complete driver timeouts caused by poorly seated PCIe risers or degraded NVLink connectors.
