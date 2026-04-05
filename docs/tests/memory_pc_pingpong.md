# Pseudo-Channel Ping-Pong

## Overview
The `memory_pc_pingpong` kernel tests the internal routing logic of the GPU by forcing data to physically cross the Infinity Fabric crossbar switches.



## Execution Mechanics
To stress the crossbar, data must move between completely different physical memory stacks.

* The kernel reads data from the first half of the allocated VRAM.
* It performs a bitwise inversion (`~`) on the registers to simulate a small workload.
* It then writes that data to an offset that is exactly half of the total allocation.
* This massive jump virtually guarantees the read and write operations land on different physical channels/stacks, forcing the data to travel across the internal fabric.

## Target Subsystems
* **Primary Target:** Infinity Fabric / Crossbar network.
* **Secondary Target:** Unified Memory Controllers.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Interconnect Throttling:** The fabric overheats and downclocks, causing a severe drop in measured gigabytes-per-second.
    * **Fabric Instability:** Data corruption across the internal SoC routing.
