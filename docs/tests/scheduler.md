# Scheduler Virus

## Overview
The `scheduler` virus is designed to lock up the GPU's command processor. The goal is not to stress the ALUs, but to force the hardware dispatcher into rapid context switching.

## Execution Mechanics
It utilizes a "Micro Kernel"—a deliberately tiny workload designed to finish almost instantly.

* The host script creates 64 independent, asynchronous streams.
* It spams the micro-kernel across all 64 streams using only 1 Block and 64 Threads per launch.
* This forces maximum fragmentation on the Streaming Multiprocessors (SMs) and forces hardware queues (like NVIDIA Hyper-Q or AMD ACEs) into aggressive multiplexing mode.

## Target Subsystems
* **Primary Target:** Hardware Schedulers and Asynchronous Compute Engines (ACEs).
* **Secondary Target:** Context memory allocations.

## Failure Symptoms
!!! warning "Expected Behavior"
    Performance is measured in KIPS (Thousand Kernel Issues Per Second).

!!! danger "Critical Failures"
    * **Dispatcher Lockup:** The GPU scheduler physically hangs, requiring a hard reboot of the host machine.
    * **Massive KIPS Drops:** The driver's software queue becomes overwhelmed and stops submitting work to the hardware.
