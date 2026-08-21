# Releases

Download stable binary builds of the Pantheon GPU toolkit. The newest release is listed first.

---

## Pantheon v1.0.15 (Latest)
**Release Date:** August 21, 2026

### Release Notes
#### What's changed

- Added reliable AMD Instinct MI450 build-target handling for both `gfx1250` and `gfx1251`, including ROCm architecture strings with feature suffixes.
- Made the transformer stress workload portable by default on MI450 systems without requiring the optional `rocWMMA` headers.
- Improved raw Nsight trace import handling while retaining RAS and PCIe reliability snapshots for every workload.
- Kept binary package, checksum, GLIBC, installation, and Linux compatibility validation as required release gates.


### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.15 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.15/pantheongpu_1.0.15_amd64.deb) | `.deb` | 33.6 MB |
| [Pantheon v1.0.15 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.15/pantheongpu_1.0.15_amd64.tar.gz) | `.tar.gz` | 67.2 MB |
| [Pantheon v1.0.15 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.15/pantheongpu_1.0.15_amd64.zip) | `.zip` | 67.2 MB |
| [Pantheon v1.0.15 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.15/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.14
**Release Date:** August 15, 2026

### Release Notes
#### What's changed

- Added AI diagnostic workloads for inference, training, runtime behavior, and graph replay, including focused tests for decode, prefill, KV-cache churn, attention, quantized GEMM, routing, and serving mixes.
- Expanded `--profile` with richer NVIDIA and AMD hardware counters, timeline traces, separate artifacts for every workload and GPU, and a portable HTML summary report.
- Hardened workload launch configuration and verification paths across CUDA, HIP, and mock execution.
- Added native package and portable installation workflows with matching uninstall support for Debian, Ubuntu, Fedora, RHEL-family, and similar Linux distributions.
- Updated documentation for the expanded workload catalog, profiling output, installation, and removal.


### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.14 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.14/pantheongpu_1.0.14_amd64.deb) | `.deb` | 33.5 MB |
| [Pantheon v1.0.14 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.14/pantheongpu_1.0.14_amd64.tar.gz) | `.tar.gz` | 67.1 MB |
| [Pantheon v1.0.14 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.14/pantheongpu_1.0.14_amd64.zip) | `.zip` | 67.1 MB |
| [Pantheon v1.0.14 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.14/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.13
**Release Date:** June 18, 2026

### Release Notes
#### What's Changed
* [codex] Fix source and AMD execution paths by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/9



### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.13 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.13/pantheongpu_1.0.13_amd64.deb) | `.deb` | 33.4 MB |
| [Pantheon v1.0.13 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.13/pantheongpu_1.0.13_amd64.tar.gz) | `.tar.gz` | 66.8 MB |
| [Pantheon v1.0.13 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.13/pantheongpu_1.0.13_amd64.zip) | `.zip` | 66.8 MB |
| [Pantheon v1.0.13 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.13/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.12
**Release Date:** June 18, 2026

### Release Notes
#### What's Changed
* [codex] Prepare Pantheon 1.0.12 release by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/8



### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.12 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.12/pantheongpu_1.0.12_amd64.deb) | `.deb` | 33.4 MB |
| [Pantheon v1.0.12 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.12/pantheongpu_1.0.12_amd64.tar.gz) | `.tar.gz` | 66.8 MB |
| [Pantheon v1.0.12 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.12/pantheongpu_1.0.12_amd64.zip) | `.zip` | 66.8 MB |
| [Pantheon v1.0.12 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.12/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.10
**Release Date:** June 16, 2026

### Release Notes
#### What's Changed
* pantheon tuning params by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/5
* Debian binary release by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/6
* Debian binary release by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/7



### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.10 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.deb) | `.deb` | 87.4 MB |
| [Pantheon v1.0.10 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.tar.gz) | `.tar.gz` | 174.8 MB |
| [Pantheon v1.0.10 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.zip) | `.zip` | 174.8 MB |
| [Pantheon v1.0.10 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.10/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.8
**Release Date:** May 21, 2026

### Release Notes
#### What's Changed
* INitial Commit by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/1
* Package Nuitka release archives by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/2
* Update VERSION by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/3
* Automate by @saqibkh in https://github.com/pantheongpu/pantheongpu/pull/4

#### New Contributors
* @saqibkh made their first contribution in https://github.com/pantheongpu/pantheongpu/pull/1


### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.8 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.8/pantheon-1.0.8.tar.gz) | `.tar.gz` | 181.1 KB |
| [Pantheon v1.0.8 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.8/pantheon-1.0.8.zip) | `.zip` | 247.6 KB |
| [Pantheon v1.0.8 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.8/SHA256SUMS) | `SHA256SUMS` | 173 B |

---

## v1.0.7
**Release Date:** April 6, 2026

### Release Notes
### Pantheon v1.0.7 - SDC Validation & FP64 Fixes
What's New in this Release:
This update introduces critical diagnostic enhancements for memory integrity and patches the double-precision compute stressor.

- Active SDC Catching (--verify): Added the --verify flag to actively hunt for Silent Data Corruption (SDC). Instead of just generating extreme heat and waiting for a hardware crash or driver timeout, Pantheon will now actively validate the data payloads returning from the GPU. If the hardware ECC fails to catch a bit-flip caused by thermal or electrical stress, Pantheon will immediately flag the corrupted block.

- fp64_virus Patched: Fixed the execution and reporting logic for the Double Precision Chokehold (fp64_virus). The kernel now properly saturates the FP64 datapath, accurately exposing physical and artificial silicon limits (such as the strict 1/64th FP64 throttle implemented on consumer NVIDIA GeForce cards).

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.7 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.7/pantheon-1.0.7.tar.gz) | `.tar.gz` | 131.2 MB |
| [Pantheon v1.0.7 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.7/pantheon-1.0.7.zip) | `.zip` | 131.2 MB |
