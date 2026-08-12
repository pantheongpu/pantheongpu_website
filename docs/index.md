---
hide:
  - navigation
  - toc
---

<div class="pantheon-hero" markdown>

# GPU stress testing and diagnostics

Pantheon tests GPU compute, memory, cache, interconnect, and power behavior. Run focused workloads, capture telemetry, and keep the results for comparison.

<div class="pantheon-hero__actions">
  <a href="release/" class="md-button md-button--primary">Download Pantheon</a>
  <a href="benchmarks/" class="md-button">View benchmarks</a>
</div>
</div>

<div class="pantheon-signal-grid" markdown>

<div class="pantheon-signal"><span>45 workloads</span><small>focused stress tests</small></div>
<div class="pantheon-signal"><span>CUDA + ROCm</span><small>NVIDIA and AMD support</small></div>
<div class="pantheon-signal"><span>Local reports</span><small>exportable telemetry</small></div>
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
VERSION=1.0.13
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
cache, or to remove a portable installation on RHEL, Fedora, Rocky Linux,
AlmaLinux, or another Linux distribution, run:

```bash
curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh
```

This leaves CUDA, ROCm, system compilers, and benchmark reports stored outside
Pantheon's installation and cache directories untouched.

??? info "Alternative: install from the release bundle"
    The release bundle contains the Debian package and an `install.sh` helper for
    RHEL-family and other Linux distributions.

    ```bash
    VERSION=1.0.13
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
