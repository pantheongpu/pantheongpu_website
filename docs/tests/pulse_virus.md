# Pulse Virus

## Overview
The `pulse_virus` does not test sustained heat; it tests electrical transients. It induces maximum dI/dt (Change in Current over Time) to stress the power supply and voltage regulators.



## Execution Mechanics
The test toggles the GPU at exactly 10Hz between two extreme states:

1. **The Spike:** Launches a massive wave of FMA math to instantly spike the GPU to 100% load.
2. **The Droop:** Immediately issues a 50-millisecond sleep command, dropping the GPU load to 0% and forcing the VRMs to rapidly cut voltage.

## Target Subsystems
* **Primary Target:** GPU VRMs (Voltage Regulator Modules) and motherboard PCIe power delivery.
* **Secondary Target:** Host Power Supply Unit (PSU) transient response.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Instant System Shutdown:** The rapid power draw spikes trigger the PSU's Over-Current Protection (OCP), completely cutting power to the server.
    * **Audio Crackling / USB Drops:** The motherboard's 12V rail becomes unstable under the transient load, temporarily disabling peripheral devices.
