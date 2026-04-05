# Integer Virus

## Overview
The `int_virus` stresses a completely different physical datapath than the standard floating-point tests by focusing entirely on the INT32 ALUs.

## Execution Mechanics
It saturates the INT32 units using intensive bitwise operations.

* The loop consists of complex integer logic including bit-bashing, bitwise rotations, and XOR cascades.
* This forces the integer execution units to draw maximum current, often exposing flaws in shared register files.

## Target Subsystems
* **Primary Target:** INT32 Execution Units.
