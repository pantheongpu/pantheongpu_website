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
VERSION=1.0.12

# Ubuntu/Debian runtime prerequisites
sudo apt-get update
sudo apt-get install -y make g++

# Install one GPU compiler stack:
# NVIDIA CUDA:
sudo apt-get install -y nvidia-cuda-toolkit
# AMD ROCm/HIP:
# sudo apt-get install -y hipcc

# Choose one install path. Direct Debian package:
wget "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.deb"
sudo apt install "./pantheongpu_${VERSION}_amd64.deb"

# Or from the release bundle:
wget "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.tar.gz"
tar -xzf "pantheongpu_${VERSION}_amd64.tar.gz"
cd "pantheongpu_${VERSION}_amd64"
sudo apt install "./packages/pantheongpu_${VERSION}_amd64.deb"

# Run installed commands
pantheon --test baseline_metrics --duration 10
pantheon --test fp64_virus --duration 30 --gpu 0
```

Pantheon auto-detects CUDA, ROCm/HIP, or mock mode at runtime. For normal installed use, run the `pantheon` command directly from your shell and do not pass `--platform cuda`.

The release bundle also includes `install.sh` for RHEL-family and other Linux distributions that cannot install the Debian package directly. First-run workload builds are cached under `/opt/pantheongpu/cache/builds/`; set `PANTHEON_BUILD_CACHE_DIR` to use a user-writable cache instead.
