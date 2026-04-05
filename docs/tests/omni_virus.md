# Omni Virus

## Overview
The `omni_virus` is Pantheon's ultimate TDP (Thermal Design Power) saturator. Unlike targeted micro-benchmarks that test a single datapath, this kernel forces simultaneous execution across four completely independent hardware units.



## Execution Mechanics
To prevent the hardware scheduler from bottlenecking, the Omni Virus launches four separate asynchronous streams, allowing the GPU's command processor to multiplex the workloads perfectly across the Compute Units (CUs).

1. **Memory Stream:** Sweeps Memory with Non-Temporal stores to bypass L2 cache.
2. **Tensor Stream:** Spams Half-Precision (FP16) FMA instructions on physical matrix cores.
3. **Vector Stream:** Executes standard FP32 math.
4. **SFU Stream:** Calculates complex transcendental functions (SIN, COS, RSQRT) which execute on the dedicated Special Function Units.

## Target Subsystems
* **Primary Target:** Global VRM (Voltage Regulator Module) network and total package power delivery.
* **Secondary Target:** Hardware dispatchers and asynchronous compute engines (ACEs).

## Failure Symptoms
Because this test attempts to draw the absolute maximum rated wattage of the silicon, it frequently exposes power delivery flaws.

!!! danger "Critical Failures"
    * **Instant Black Screen / Shutdown:** Your Power Supply Unit (PSU) tripped its Over-Current Protection (OCP).
    * **Severe Clock Stretching:** The VRMs cannot maintain stable voltage under full load, forcing the GPU to artificially lower its clock speed to prevent a crash.
