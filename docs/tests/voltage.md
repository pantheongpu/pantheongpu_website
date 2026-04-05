# Voltage Virus

## Overview
The `voltage` kernel acts as an ALU hammer that targets the Logic Rail (VDD_GFX) to induce severe di/dt (current over time) droop.

## Execution Mechanics
Instead of maximizing memory throughput or standard compute, this virus utilizes volatile math to force rapid ALU state switching.
 
* It forces the states to switch violently between 0 and 1.
* By preventing the compiler from pre-calculating or optimizing out the volatile results, the Arithmetic Logic Units are kept at maximum switching activity, drawing rapid gulps of power.

## Target Subsystems
* **Primary Target:** Logic Power Rail (VDD_GFX).

## Failure Symptoms
!!! danger "Critical Failures"
    * **Clock Stretching:** The voltage regulators fail to keep up with the rapid switching, resulting in silent performance degradation as the card stretches clock cycles to maintain stability.
    * **Driver Crashes:** Hard hangs due to localized undervolting on the die.
