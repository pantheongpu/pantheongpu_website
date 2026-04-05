# Incinerator

## Overview
The `incinerator` is a localized power virus that targets multiple sub-units simultaneously. It combines dense Vector ALU math with extreme Local Data Share (LDS) thrashing to maximize physical die temperature.

## Execution Mechanics
Instead of just spamming math instructions, this kernel forces simultaneous congestion across the die:

* **Vector Unit Stress:** Continuously loops Fused Multiply-Add (FMA) instructions.
* **SRAM Stress:** Threads constantly read, modify, and write back to shared memory (LDS). 
* **Intentional Congestion:** It uses an XOR bitwise operation on the thread indices to intentionally cause massive SRAM bank conflicts, generating excess heat through hardware stalls.

## Target Subsystems
* **Primary Target:** Vector ALUs and Shared Memory (L1/LDS) arrays.
* **Secondary Target:** Silicon thermal dissipation limits.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Aggressive Core Clock Drops:** The silicon will rapidly hit its `[THERMAL]` throttle limit, dropping clocks to base frequencies to prevent physical melting.
    * **General Instability:** Arithmetic errors due to extreme localized heat expanding the silicon traces.
