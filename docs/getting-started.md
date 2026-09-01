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

Pantheon is open source. Building from source lets you read exactly what will
run on your hardware; the PyPI or Debian package is quicker if you just want
to run it.

=== "PyPI"

    ```bash
    pipx install pantheon-gpu
    ```

    Installs a `pantheon` command on your PATH. `pipx` keeps it in its own
    environment, which is what recent Ubuntu and Debian releases require of
    anything installed outside the system package manager; `pip install --user
    pantheon-gpu` works too where that restriction does not apply. Add the
    `reports` extra (`pipx install "pantheon-gpu[reports]"`) for spreadsheet
    export.

    The wheel carries the kernel sources rather than prebuilt binaries, so the
    first run compiles the workloads for your GPU into a per-user cache. That
    takes a minute or so once, and needs `make`, a C++ compiler, and the CUDA
    or ROCm toolkit from the tabs above.

=== "Docker"

    ```bash
    docker run --rm --gpus all -v "$PWD:/reports" \
      ghcr.io/pantheongpu/pantheon:latest --test tensor_virus --duration 60
    ```

    The image carries the CUDA 12.8 toolchain, so nothing is installed on the
    host beyond the NVIDIA driver and the NVIDIA Container Toolkit. Kernels
    still compile for the GPU actually present on first run; mount
    `/root/.cache` as well to keep the compiled cache across containers.
    Reports land in the directory mounted at `/reports`.

    Tags: `latest`, a version (`1.2.0`), or a version pinned to its toolchain
    (`1.2.0-cuda12.8`).

    On AMD hardware use the ROCm variant, which carries the ROCm 6.4
    toolchain instead and needs the device nodes rather than `--gpus`:

    ```bash
    docker run --rm --device=/dev/kfd --device=/dev/dri --group-add video \
      -v "$PWD:/reports" \
      ghcr.io/pantheongpu/pantheon:latest-rocm --test tensor_virus --duration 60
    ```

=== "Fedora / RHEL (COPR)"

    ```bash
    sudo dnf install 'dnf-command(copr)'
    sudo dnf copr enable saqibkhanpantheongpu/pantheon-gpu
    sudo dnf install pantheon-gpu
    ```

    Built for Fedora 43/44 and EPEL 10 (RHEL, Rocky and Alma 10). EPEL 9 is
    not built: its Python stack cannot satisfy the build's setuptools floor —
    use pipx or the Docker image there. Add the CUDA or ROCm toolkit
    separately for real hardware.

=== "Build from source"

    ```bash
    git clone https://github.com/pantheongpu/pantheon.git
    cd pantheon
    pip install -r requirements.txt
    make PLATFORM=CUDA -j$(nproc)     # or PLATFORM=HIP for AMD
    ```

    There is no build-time auto-detection, so pass `PLATFORM=` explicitly. Use
    `PLATFORM=MOCK` to build a CPU backend that needs no GPU at all, which is
    useful for trying the tooling before committing hardware to it.

    Run it from the checkout with `python3 pantheon.py` in place of the
    `pantheon` command used below.

=== "APT (Debian, Ubuntu)"

    ```bash
    curl -fsSL https://pantheongpu.com/apt/pantheon-archive-keyring.asc \
      | sudo tee /usr/share/keyrings/pantheon-archive-keyring.asc > /dev/null
    echo "deb [signed-by=/usr/share/keyrings/pantheon-archive-keyring.asc] https://pantheongpu.com/apt stable main" \
      | sudo tee /etc/apt/sources.list.d/pantheon.list
    sudo apt update && sudo apt install pantheon-gpu
    ```

    Installs both `pantheon` and `pantheon-gpu`; they are the same program.
    Telemetry and spreadsheet export come from `Recommends` and `Suggests`, so
    apt pulls them by default and they can be left out on a minimal install.

    The workloads compile on first run, which is why the package depends on
    `g++` and `make`. Add the CUDA or ROCm toolkit separately for real
    hardware.

=== "Install the package"

    ```bash
    VERSION=1.2.0
    BASE="https://github.com/pantheongpu/pantheongpu_website/releases/download/v${VERSION}"
    wget "${BASE}/pantheon_gpu-${VERSION}-py3-none-any.whl"
    wget "${BASE}/SHA256SUMS" && sha256sum --ignore-missing -c SHA256SUMS
    pipx install "./pantheon_gpu-${VERSION}-py3-none-any.whl"
    ```

    Installs a `pantheon` command on your PATH. `pipx` keeps it in its own
    environment, which is what recent Ubuntu and Debian releases require of
    anything installed outside the system package manager; `pip install --user`
    works too where that restriction does not apply.

    The wheel carries the kernel sources rather than prebuilt binaries, so the
    first run compiles the workloads for your GPU into a per-user cache. That
    takes a minute or so once, and needs `make`, a C++ compiler, and the CUDA or
    ROCm toolkit from the tabs above.


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

Remove a package installation with:

```bash
pipx uninstall pantheon-gpu
```

Releases up to v1.0.19 shipped as a Debian package instead. Remove one of those with:

```bash
sudo apt-get remove pantheongpu
```

To also remove PantheonGPU runtime-created files and the current user's compiled workload cache, or to remove a portable installation on RHEL-family systems:

```bash
curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh
```

This leaves CUDA, ROCm, system compilers, and benchmark reports outside PantheonGPU's installation and cache directories untouched.
