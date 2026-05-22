---
hide:
  - navigation
---

# PANTHEON

<div align="center">
  <img src="assets/logo.png" class="home-logo" alt="Pantheon Logo">
  <h3>Universal GPU Stress & Diagnostics Suite</h3>
  <p>
    <a href="release/" class="md-button md-button--primary">
       Latest Release
    </a>
    <a href="benchmarks/" class="md-button">
       Live Benchmarks
    </a>
  </p>
</div>

---

## Why Pantheon?

Pantheon is a cross-platform (CUDA/ROCm) stress testing tool designed to isolate and hammer specific GPU subsystems. Unlike generic benchmarks, Pantheon targets specific silicon limits to expose hardware degradation, thermal throttling, and architecture bottlenecks.

<div class="grid cards" markdown>

-   **VRAM & Infinity Fabric**
    ---
    Target Memory/GDDR memory and interconnects with aggressive crosstalk patterns to detect bit flips and signal integrity loss.
    
    *Test: `memory_write_agg`, `memory_tsv_thrasher`*

-   **Physical Matrix Cores**
    ---
    Push hardware Tensor and Matrix cores to their absolute thermal limits using universal FP16/WMMA intrinsics.
    
    *Test: `mma_virus`, `tensor_virus`*

-   **VRM Transients (dI/dt)**
    ---
    Oscillate maximum load at 10Hz to induce high current transients, testing your power supply and voltage regulators.
    
    *Test: `pulse_virus`, `voltage`*

-   **MMU & TLB Avalanche**
    ---
    Force near 100% Translation Lookaside Buffer misses with random page-boundary jumps to choke hardware page-table walkers.
    
    *Test: `tlb_avalanche`*

-   **ECC & RAS Validation**
    ---
    Continuously read pristine patterns to expose the latency jitter of active ECC scrubbing and silent data corruption.
    
    *Test: `ras_validator`*

-   **Hardware Scheduler**
    ---
    Spam micro-kernels across 64 concurrent streams to force the GPU dispatcher into multiplexing mode and trigger context switch locks.
    
    *Test: `scheduler`*

</div>

## Quick Start

```bash
# Ubuntu/Debian system packages
sudo apt-get update
sudo apt-get install -y python3-venv python3-tk python3-pip

# Install one GPU compiler stack:
# NVIDIA CUDA:
sudo apt-get install -y nvidia-cuda-toolkit
# AMD ROCm/HIP:
# sudo apt-get install -y hipcc

# Source checkout only: install Python dependencies in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Source checkout: run the Python entry point
python3 pantheon.py --test all --duration 30 --verify

# Release archive: run the bundled executable instead
./pantheon --test all --duration 30 --verify
```
