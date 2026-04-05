# Memory Thermal Asymmetry

## Overview
The `memory_thermal_asym` virus is unique: it creates a severe physical temperature gradient across the silicon package by hammering a tiny, isolated memory region while simultaneously drawing maximum compute power.

## Execution Mechanics
* **Extreme Compute Burn:** The threads execute a heavy `pragma unroll 32` loop of Fused Multiply-Add (FMA) instructions to generate massive die heat.
* **Localized Writes:** Instead of sweeping across the entire VRAM, it uses a modulo operator to trap all memory writes inside a small, isolated buffer.
* This forces the GPU die to heat up uniformly, but concentrates all memory traffic (and memory heat) onto typically 1 or 2 physical Memory stacks.

## Target Subsystems
* **Primary Target:** Memory Thermal dissipation and physical package gradients.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Localized Hotspot Spikes:** The active memory stack overheats significantly faster than the rest of the VRAM.
    * **Memory Controller Crash:** The severe temperature difference causes clock stretching or instability on the specific active channel.
