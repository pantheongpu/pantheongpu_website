# Releases

Download stable releases of the Pantheon GPU toolkit. The newest release is listed first.

---

## Pantheon v1.2.0 (Latest)
**Release Date:** August 31, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.2.0

**Changes since v1.1.0:**

- Make bring-your-own-OptiX usable: cache key, docs, and a skip message that says what to do (#3)

Install from PyPI (`pipx install pantheon-gpu`), the apt or
COPR repositories, the container image
(`ghcr.io/pantheongpu/pantheon:1.2.0`), or the wheel below:

```
pip install pantheon_gpu-1.2.0-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Kernels compile on first run into a per-user cache (roughly a
minute, once) and need a CUDA or ROCm toolchain; use
`--platform mock` to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.2.0 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon-gpu_1.2.0_all.deb) | `.deb` | 163.9 KB |
| [Pantheon v1.2.0 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon_gpu-1.2.0-py3-none-any.whl) | `.whl` | 328.6 KB |
| [Pantheon v1.2.0 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon-1.2.0-source.tar.gz) | `.tar.gz` | 249.6 KB |
| [Pantheon v1.2.0 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon_gpu-1.2.0.tar.gz) | `.tar.gz` | 237.3 KB |
| [Pantheon v1.2.0 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon-1.2.0-source.zip) | `.zip` | 366.6 KB |
| [Pantheon v1.2.0 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/SHA256SUMS) | `SHA256SUMS` | 484 B |

---

## Pantheon v1.1.0
**Release Date:** August 30, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.1.0

Install the wheel (kernels compile on first run into a per-user cache;
expect roughly a minute the first time):

```
pip install pantheon_gpu-1.1.0-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Requires a CUDA or ROCm toolchain at first run. Use `--platform mock`
to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.1.0 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.1.0/pantheon_gpu-1.1.0-py3-none-any.whl) | `.whl` | 328.1 KB |
| [Pantheon v1.1.0 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.1.0/pantheon-1.1.0-source.tar.gz) | `.tar.gz` | 249.2 KB |
| [Pantheon v1.1.0 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.1.0/pantheon_gpu-1.1.0.tar.gz) | `.tar.gz` | 236.3 KB |
| [Pantheon v1.1.0 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.1.0/pantheon-1.1.0-source.zip) | `.zip` | 366.2 KB |
| [Pantheon v1.1.0 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.1.0/SHA256SUMS) | `SHA256SUMS` | 389 B |

---

## Pantheon v1.0.19
**Release Date:** August 27, 2026

### Release Notes
#### What's Changed
* Fault maps and a time-based memory retention workload by @saqibkh
* Fold the memory _agg twins into --init_pattern by @saqibkh
* Audit fixes: unreleased hardware, fictional metrics, broken verification, CI hardening by @saqibkh
* Bound launch parameters that could hang the GPU by @saqibkh
* Make the tree publishable: OptiX optional, NOTICE, export script by @saqibkh
* Stop CI running the whole matrix twice per commit by @saqibkh
* Kill the whole process tree, not just the launched process by @saqibkh
* Release v1.0.19 by @saqibkh


**Full Changelog**: `v1.0.18...v1.0.19`

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.19 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.19/pantheongpu_1.0.19_amd64.deb) | `.deb` | 33.7 MB |
| [Pantheon v1.0.19 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.19/pantheongpu_1.0.19_amd64.tar.gz) | `.tar.gz` | 67.4 MB |
| [Pantheon v1.0.19 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.19/pantheongpu_1.0.19_amd64.zip) | `.zip` | 67.4 MB |
| [Pantheon v1.0.19 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.19/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.18
**Release Date:** August 26, 2026

### Release Notes
#### What's Changed
* Kernel verification hardening: coverage holes, uninitialized lanes, UB, and accounting fixes by @saqibkh


**Full Changelog**: `v1.0.17...v1.0.18`

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.18 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.18/pantheongpu_1.0.18_amd64.deb) | `.deb` | 33.6 MB |
| [Pantheon v1.0.18 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.18/pantheongpu_1.0.18_amd64.tar.gz) | `.tar.gz` | 67.3 MB |
| [Pantheon v1.0.18 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.18/pantheongpu_1.0.18_amd64.zip) | `.zip` | 67.3 MB |
| [Pantheon v1.0.18 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.18/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.17
**Release Date:** August 26, 2026

### Release Notes
**Full Changelog**: `v1.0.16...v1.0.17`

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.17 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.17/pantheongpu_1.0.17_amd64.deb) | `.deb` | 33.6 MB |
| [Pantheon v1.0.17 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.17/pantheongpu_1.0.17_amd64.tar.gz) | `.tar.gz` | 67.3 MB |
| [Pantheon v1.0.17 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.17/pantheongpu_1.0.17_amd64.zip) | `.zip` | 67.3 MB |
| [Pantheon v1.0.17 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.17/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.16
**Release Date:** August 22, 2026

### Release Notes
**Full Changelog**: `v1.0.15...v1.0.16`

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.16 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.16/pantheongpu_1.0.16_amd64.deb) | `.deb` | 33.6 MB |
| [Pantheon v1.0.16 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.16/pantheongpu_1.0.16_amd64.tar.gz) | `.tar.gz` | 67.2 MB |
| [Pantheon v1.0.16 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.16/pantheongpu_1.0.16_amd64.zip) | `.zip` | 67.2 MB |
| [Pantheon v1.0.16 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.16/SHA256SUMS) | `SHA256SUMS` | 303 B |

---

## Pantheon v1.0.14
**Release Date:** August 15, 2026

### Release Notes
**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.13...v1.0.14

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
* [codex] Fix source and AMD execution paths by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/9


**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.12...v1.0.13

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
* [codex] Prepare Pantheon 1.0.12 release by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/8


**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.11...v1.0.12

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
* pantheon tuning params by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/5
* Debian binary release by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/6
* Debian binary release by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/7


**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.8...v1.0.10

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
* INitial Commit by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/1
* Package Nuitka release archives by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/2
* Update VERSION by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/3
* Automate by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/4

#### New Contributors
* @saqibkh made their first contribution in https://github.com/saqibkh/pantheongpu/pull/1

**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.7...v1.0.8

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
| [Pantheon v1.0.7 Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.7/pantheon-v1.0.7-linux-x86_64.tar.gz) | `.tar.gz` | 131.2 MB |
| [Pantheon v1.0.7 ZIP Bundle](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.0.7/pantheon-v1.0.7-linux-x86_64.zip) | `.zip` | 131.2 MB |

