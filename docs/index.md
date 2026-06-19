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

The Debian package is the simplest installation path for Ubuntu and Debian systems.

### 1. Install prerequisites

Install the basic build tools:

```bash
sudo apt-get update
sudo apt-get install -y make g++
```

Then install the compiler for your GPU platform. You only need one:

=== "NVIDIA CUDA"

    ```bash
    sudo apt-get install -y nvidia-cuda-toolkit
    ```

=== "AMD ROCm/HIP"

    ```bash
    sudo apt-get install -y hipcc
    ```

### 2. Install Pantheon

Download and install the latest Debian package:

```bash
VERSION=1.0.12
wget "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.deb"
sudo apt install "./pantheongpu_${VERSION}_amd64.deb"
```

To uninstall the Debian package later:

```bash
sudo apt-get remove pantheongpu
```

### 3. Verify the installation

Run a short hardware inventory test:

```bash
pantheon --test baseline_metrics --duration 10
```

Then run a targeted stress test on GPU 0:

```bash
pantheon --test fp64_virus --duration 30 --gpu 0
```

!!! note
    Pantheon automatically detects CUDA, ROCm/HIP, or mock mode. Run the `pantheon`
    command directly; you do not need to pass `--platform cuda`.

### Completely remove Pantheon

The native package command above removes Pantheon's package-managed files.
To also remove runtime-created files and the current user's compiled workload
cache—or to remove a portable installation on RHEL, Fedora, Rocky Linux,
AlmaLinux, or another Linux distribution—run:

```bash
curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh
```

This leaves CUDA, ROCm, system compilers, and benchmark reports stored outside
Pantheon's installation and cache directories untouched.

??? info "Alternative: install from the release bundle"
    The release bundle contains the Debian package and an `install.sh` helper for
    RHEL-family and other Linux distributions.

    ```bash
    VERSION=1.0.12
    wget "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.tar.gz"
    tar -xzf "pantheongpu_${VERSION}_amd64.tar.gz"
    cd "pantheongpu_${VERSION}_amd64"
    sudo apt install "./packages/pantheongpu_${VERSION}_amd64.deb"
    ```

    Uninstall a Debian package installation with:

    ```bash
    sudo apt-get remove pantheongpu
    ```

    On RHEL-family and other Linux systems, install the portable bundle with
    `sudo ./install.sh`. Remove that installation with:

    ```bash
    sudo rm -f /usr/local/bin/pantheon && sudo rm -rf /opt/pantheongpu
    ```

    Use the complete-removal command above if you also want to clear the
    current user's compiled workload cache.

!!! tip "Build cache"
    First-run workload builds are cached under
    `${XDG_CACHE_HOME:-$HOME/.cache}/pantheongpu/builds/`.
    Set `PANTHEON_BUILD_CACHE_DIR` to choose another writable cache directory.
