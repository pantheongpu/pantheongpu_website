---
title: Getting Started | PantheonGPU
description: Install PantheonGPU and run your first GPU health, diagnostics, and performance validation workloads.
---

<div class="page-intro" markdown>
<p class="page-intro__eyebrow">Getting started</p>

# Install PantheonGPU and run a first validation

PantheonGPU automatically detects CUDA, ROCm/HIP, or mock mode. Run the `pantheon` command directly after installation.
</div>

## Install on Ubuntu or Debian

Install the basic build tools:

```bash
sudo apt-get update
sudo apt-get install -y make g++
```

Install the compiler for your platform. You only need one:

=== "NVIDIA CUDA"

    ```bash
    sudo apt-get install -y nvidia-cuda-toolkit
    ```

=== "AMD ROCm/HIP"

    ```bash
    sudo apt-get install -y hipcc
    ```

Download and install the latest Debian package:

```bash
VERSION=1.0.18
wget "https://github.com/pantheongpu/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.deb"
sudo apt install "./pantheongpu_${VERSION}_amd64.deb"
```

## Run a first test

Run a short inventory test:

```bash
pantheon --test baseline_metrics --duration 10
```

Then run a targeted stress test on GPU 0:

```bash
pantheon --test fp64_virus --duration 30 --gpu 0
```

## Profiling and reports

Use `--verify` to validate workload output. Use `--profile` to collect performance counters, traces, and a per-workload HTML summary:

```bash
pantheon --test llm_decode --duration 60 --gpu 0 --verify --profile
```

See [Test Documentation](tests/index.md) for workload guidance, [Releases and Downloads](release.md) for other installation methods, and [Reports](reports.md) for output details.

## Uninstall

Remove a Debian package installation with:

```bash
sudo apt-get remove pantheongpu
```

To also remove PantheonGPU runtime-created files and the current user's compiled workload cache, or to remove a portable installation on RHEL-family systems:

```bash
curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh
```

This leaves CUDA, ROCm, system compilers, and benchmark reports outside PantheonGPU's installation and cache directories untouched.
