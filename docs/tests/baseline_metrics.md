# Baseline Metrics

## Overview
The `baseline_metrics` target isn't actually a stress test; it is an idle diagnostic. 

## Execution Mechanics
* This kernel does literally nothing. 
* It exists to provide a valid execution target for the Pantheon host script, ensuring the GPU is fully initialized and awake while the Hardware Monitor captures resting metrics (temperature, power, clocks) before the violent stressors begin.

## Target Subsystems
* **Primary Target:** Baseline System Health.

## Failure Symptoms
!!! danger "Critical Failures"
    * **High Resting Power:** If your GPU pulls significant wattage or hits high temperatures during this idle test, you have aggressive background processes running or a damaged cooling mount.
