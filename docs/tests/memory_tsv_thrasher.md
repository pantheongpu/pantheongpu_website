# TSV Toggle-Rate Thrasher

## Overview
The `memory_tsv_thrasher` is a severe electrical stress test. It induces massive current spikes (di/dt) and crosstalk directly on the physical interposer Through-Silicon Vias (TSVs).

## Execution Mechanics
Data Bus Inversion (DBI) is a hardware feature designed to save power by minimizing the number of bits flipped during a transmission. This kernel actively fights it:

* It alternates between driving the entire 128-bit vector completely HIGH (`0xFFFFFFFF`) and completely LOW (`0x00000000`).
* By writing in alternating waves, it forces the maximum number of physical trace state-changes per clock cycle.
* This maximizes DBI stress and causes severe electrical interference across the interposer.

## Target Subsystems
* **Primary Target:** Interposer TSVs and Memory PHY logic.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Physical Bus Crashes:** The extreme current spikes cause the physical memory PHY to desync or crash.
    * **Signal Integrity Errors:** Driver timeouts triggered by unrecoverable transmission errors.
