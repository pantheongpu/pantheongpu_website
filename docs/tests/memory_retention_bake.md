# Memory Retention Bake

## Overview
The `memory_retention_bake` is a specialized diagnostic that tests for thermal charge leakage within the physical memory cells. It verifies if the Memory capacitors can retain their electrical charge under extreme silicon temperatures.



## Execution Mechanics
Unlike standard memory tests, the memory controllers are intentionally left idle during the stress phase:

1. **Payload Injection:** A highly distinct payload (`0x12345678`, `0x9ABCDEF0`, etc.) is written to the entire VRAM allocation.
2. **The Bake Phase:** A pure ALU power virus is launched. This generates massive localized die heat without touching the memory interface.
3. **Verification:** After the bake duration finishes, the payload is read back to detect any bit flips or corrupted blocks caused by thermal leakage.

## Target Subsystems
* **Primary Target:** Physical Memory Capacitors and memory cell integrity.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Corrupted Blocks:** The test will output `[FAIL] Thermal Charge Leakage Detected` if the heat caused the capacitors to lose their state before the hardware refresh cycle could recharge them.
