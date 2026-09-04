# RT Virus

## Overview
The `rt_virus` is designed to overwhelm the dedicated Ray Tracing intersection engines. It hammers the RT cores with billions of non-coherent ray-triangle tests to force continuous Bounding Volume Hierarchy (BVH) traversal.

!!! note "Requires the NVIDIA OptiX SDK (or HIP-RT on AMD)"
    NVIDIA's OptiX headers are proprietary and cannot be redistributed, so
    official Pantheon builds skip `rt_virus` by default and report `SKIP`.
    To run it on NVIDIA hardware, download the free
    [OptiX SDK](https://developer.nvidia.com/designworks/optix/download) and
    point `OPTIX_PATH` at its `include` directory; the build cache picks the
    change up and rebuilds automatically:

    ```bash
    OPTIX_PATH=/opt/NVIDIA-OptiX-SDK-8.0.0/include pantheon --test rt_virus --duration 60
    ```

    On AMD hardware, build with `ENABLE_HIPRT=1` instead.

## Execution Mechanics
The kernel generates a massively complex, randomized BVH in VRAM and floods the RT cores.

* Spams non-coherent ray-triangle intersection tests to defeat ray sorting optimizations.
* Forces the hardware to continuously traverse the BVH tree.
* Maxes out the specialized RT silicon block completely independently of the primary ALUs.

## Target Subsystems
* **Primary Target:** Dedicated Ray Tracing (RT) Cores / Intersection Engines.
* **Secondary Target:** L1/L2 Cache (due to continuous BVH traversal).

## Failure Symptoms
!!! danger "Critical Failures"
    * **Rendering Artifacts:** If used alongside graphical output, causes severe visual corruption and incorrect shadow/lighting calculations.
    * **Supplementary Thermal Overload:** When run in parallel with ALU viruses, it adds enough extra wattage from the RT cores to overwhelm the cooling loop.
