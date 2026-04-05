# Media Enc Virus

## Overview
The `media_enc_virus` is designed to overwhelm the hardware video encoders. It hammers the multimedia silicon blocks with uncompressible data to force continuous encoding at maximum supported resolutions.

## Execution Mechanics
The kernel feeds a continuous stream of high-entropy, randomized noise into the hardware video encoders (NVENC/VCN).

* Generates uncompressible data frames entirely in memory to prevent PCIe bottlenecking.
* Forces continuous encoding at maximum supported resolutions and bitrates (e.g., AV1, HEVC).
* Bypasses the primary CUDA/HIP compute cores entirely, acting as a perfectly orthogonal stressor.

## Target Subsystems
* **Primary Target:** Hardware Video Encoders (NVENC / VCN).
* **Secondary Target:** Edge silicon thermal dissipation.

## Failure Symptoms
!!! danger "Critical Failures"
    * **Encoding Failures:** Dropped frames, corrupted output streams, or hard encoder lockups (often requiring a full GPU reset to clear).
    * **Supplementary Heat Load:** Exposes poor thermal pad coverage on the edges of the GPU die where encoders are physically located.
