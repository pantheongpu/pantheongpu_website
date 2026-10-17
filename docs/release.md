# Releases

Download stable releases of the Pantheon GPU toolkit. The newest release is listed first.

---

## Pantheon v1.2.4 (Latest)
**Release Date:** October 17, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.2.4

**Changes since v1.2.3:**

- Start each NVIDIA workload with only its own card visible (#41)
- Report a driver with an older NVENC API as a skip in media_enc_virus (#42)
- Skip the matrix workloads cleanly on AMD parts with no matrix instructions (#40)
- Choose the default GEMM format from the part: no BF16 default below Ampere (#39)
- Integrations: point the image tags at 1.2.3 (#38)

**Turing and Volta (T4, T4G, V100):** 1.2.3 ran `mma_virus` and `omni_virus` on a BF16 GEMM path these cards handle about 40 times slower, without saying so. 1.2.4 chooses the default from the card: below Ampere (compute capability 8.0) both tests keep the WMMA tensor stream and print why. Do not use 1.2.3 results for these two workloads on those cards. Ampere and later are unchanged.

**Multi-GPU NVIDIA hosts:** each workload now starts with only its own card visible. Before, a stray context on GPU 0 could cause random out-of-memory failures when every card was tested at once.

**AMD parts without matrix cores (RDNA2, gfx9 before MFMA):** `mma_virus`, `omni_virus` and `transformer_virus` now skip with a reason instead of failing to build.

Install from PyPI (`pipx install pantheon-gpu`), the apt or
COPR repositories, the container image
(`ghcr.io/pantheongpu/pantheon:1.2.4`), or the wheel below:

```
pip install pantheon_gpu-1.2.4-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Kernels compile on first run into a per-user cache (roughly a
minute, once) and need a CUDA or ROCm toolchain; use
`--platform mock` to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.2.4 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/pantheon-gpu_1.2.4_all.deb) | `.deb` | 202.8 KB |
| [Pantheon v1.2.4 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/pantheon_gpu-1.2.4-py3-none-any.whl) | `.whl` | 386.2 KB |
| [Pantheon v1.2.4 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/pantheon-1.2.4-source.tar.gz) | `.tar.gz` | 366.2 KB |
| [Pantheon v1.2.4 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/pantheon_gpu-1.2.4.tar.gz) | `.tar.gz` | 300.2 KB |
| [Pantheon v1.2.4 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/pantheon-1.2.4-source.zip) | `.zip` | 496.3 KB |
| [Pantheon v1.2.4 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.4/SHA256SUMS) | `SHA256SUMS` | 484 B |

---

## Pantheon v1.2.3
**Release Date:** October 13, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.2.3

**Changes since v1.2.2:**

- Build fused_attention on ROCm, and compile every kernel for HIP in CI (#37)
- Fix PCIe AER collection, combined thermal throttle labels, and the --suite docs (#31)
- Correct the README's Efficiency formula and throttle reason labels (#33)
- Keep the operator's home directory out of published reports (#29)
- Fix missing sensors, kernel verification, and skipped-workload exit status (#35)
- Fix verdicts: thermal throttling, skipped and failed workloads, hung tests, PCIe error counters, dmesg blame (#34)
- Follow-up to #26: working memory stream and no crash in omni_virus, fixed BF16 GEMM, safe chain constants (#28)
- Fix power stress in omni_virus and the arithmetic tests, add a vendor GEMM tensor stream (#26)
- Add a Grafana dashboard for the node check's Prometheus metrics (#27)
- Add Prometheus metrics, a Kubernetes Job and Helm chart, and an Apptainer definition (#24)
- Compile the workloads ahead of time: --build-only, PANTHEON_PLATFORM, PANTHEON_CUDA_ARCH (#25)
- Add integrations: a node check, Slurm, NHC and ReFrame (#23)
- README: say how to install a release (#22)
- Test only the cards a job was given: honour CUDA_VISIBLE_DEVICES (#21)
- Remove the percentiles and the baselines file; keep the grouped verdict (#20)
- End every run with a verdict, percentiles against the public database, and a quick suite (#18)
- Report memory temperature and thermal throttling correctly on NVIDIA (#17)
- Document what --profile actually requires and what its counters mean (#16)

**Scores that are not comparable with 1.2.2:**

Ten workloads were reworked in #26 and #28, so their scores and power draw changed on purpose: `voltage`, `incinerator`, `fp64_virus`, `pulse_virus`, `tensor_virus`, `sfu_stress`, `memory_thermal_asym`, `memory_retention_bake`, `mma_virus` and `omni_virus`. Do not set a 1.2.3 result for these beside a 1.2.2 result. `galpat` also changes: it now checks all four 32-bit lanes of every cell it reads instead of one, so the same card scores about 6% lower. `mma_virus` now runs the vendor BF16 GEMM by default; `--gemm 0` selects the old WMMA path. On an A10G, none of the other 35 workloads moved by more than 0.4%.

**AMD:** every kernel now compiles with ROCm 6.4 and 7.2, including `fused_attention`, which did not build on any ROCm release before. We have not yet run this release on AMD hardware.

Install from PyPI (`pipx install pantheon-gpu`), the apt or
COPR repositories, the container image
(`ghcr.io/pantheongpu/pantheon:1.2.3`), or the wheel below:

```
pip install pantheon_gpu-1.2.3-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Kernels compile on first run into a per-user cache (roughly a
minute, once) and need a CUDA or ROCm toolchain; use
`--platform mock` to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.2.3 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/pantheon-gpu_1.2.3_all.deb) | `.deb` | 201.0 KB |
| [Pantheon v1.2.3 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/pantheon_gpu-1.2.3-py3-none-any.whl) | `.whl` | 383.7 KB |
| [Pantheon v1.2.3 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/pantheon-1.2.3-source.tar.gz) | `.tar.gz` | 361.1 KB |
| [Pantheon v1.2.3 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/pantheon_gpu-1.2.3.tar.gz) | `.tar.gz` | 297.5 KB |
| [Pantheon v1.2.3 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/pantheon-1.2.3-source.zip) | `.zip` | 490.6 KB |
| [Pantheon v1.2.3 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.3/SHA256SUMS) | `SHA256SUMS` | 484 B |

---

## Pantheon v1.2.2
**Release Date:** September 9, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.2.2

**Changes since v1.2.1:**

- Keep counters with the same name but different units apart (#14)

Install from PyPI (`pipx install pantheon-gpu`), the apt or
COPR repositories, the container image
(`ghcr.io/pantheongpu/pantheon:1.2.2`), or the wheel below:

```
pip install pantheon_gpu-1.2.2-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Kernels compile on first run into a per-user cache (roughly a
minute, once) and need a CUDA or ROCm toolchain; use
`--platform mock` to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.2.2 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/pantheon-gpu_1.2.2_all.deb) | `.deb` | 168.8 KB |
| [Pantheon v1.2.2 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/pantheon_gpu-1.2.2-py3-none-any.whl) | `.whl` | 334.8 KB |
| [Pantheon v1.2.2 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/pantheon-1.2.2-source.tar.gz) | `.tar.gz` | 259.7 KB |
| [Pantheon v1.2.2 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/pantheon_gpu-1.2.2.tar.gz) | `.tar.gz` | 244.1 KB |
| [Pantheon v1.2.2 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/pantheon-1.2.2-source.zip) | `.zip` | 377.3 KB |
| [Pantheon v1.2.2 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.2/SHA256SUMS) | `SHA256SUMS` | 484 B |

---

## Pantheon v1.2.1
**Release Date:** September 9, 2026

### Release Notes
Source: https://github.com/pantheongpu/pantheon/tree/v1.2.1

**Changes since v1.2.0:**

- Report a missing openpyxl as an optional extra, not a failed write (#13)
- Attribute profile counters to the kernel that owned the run (#12)
- Point the banner and final summary at GitHub Discussions (#9)
- Bump version to 1.2.1 (#8)
- Report the declared memory type and vendor of each GPU (#7)
- List every suite in the --test help text (#6)
- Add funding metadata: .well-known manifest pointer and FUNDING.yml (#5)

Install from PyPI (`pipx install pantheon-gpu`), the apt or
COPR repositories, the container image
(`ghcr.io/pantheongpu/pantheon:1.2.1`), or the wheel below:

```
pip install pantheon_gpu-1.2.1-py3-none-any.whl
pantheon --test baseline_metrics --duration 10
```

Kernels compile on first run into a per-user cache (roughly a
minute, once) and need a CUDA or ROCm toolchain; use
`--platform mock` to exercise the tooling with no GPU.

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.2.1 Debian Package](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/pantheon-gpu_1.2.1_all.deb) | `.deb` | 168.2 KB |
| [Pantheon v1.2.1 Python Wheel](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/pantheon_gpu-1.2.1-py3-none-any.whl) | `.whl` | 334.2 KB |
| [Pantheon v1.2.1 Source Tarball](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/pantheon-1.2.1-source.tar.gz) | `.tar.gz` | 258.2 KB |
| [Pantheon v1.2.1 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/pantheon_gpu-1.2.1.tar.gz) | `.tar.gz` | 243.5 KB |
| [Pantheon v1.2.1 Source ZIP](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/pantheon-1.2.1-source.zip) | `.zip` | 375.8 KB |
| [Pantheon v1.2.1 Checksums](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.1/SHA256SUMS) | `SHA256SUMS` | 484 B |

---

## Pantheon v1.2.0
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
| [Pantheon v1.2.0 Source Distribution](https://github.com/pantheongpu/pantheongpu_website/releases/download/v1.2.0/pantheon_gpu-1.2.0.tar.gz) | `.tar.gz` | 237.4 KB |
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
**Full Changelog**: `v1.0.13...v1.0.14`

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
* [codex] Fix source and AMD execution paths by @saqibkh


**Full Changelog**: `v1.0.12...v1.0.13`

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
* [codex] Prepare Pantheon 1.0.12 release by @saqibkh


**Full Changelog**: `v1.0.11...v1.0.12`

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
* pantheon tuning params by @saqibkh
* Debian binary release by @saqibkh
* Debian binary release by @saqibkh


**Full Changelog**: `v1.0.8...v1.0.10`

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
* INitial Commit by @saqibkh
* Package Nuitka release archives by @saqibkh
* Update VERSION by @saqibkh
* Automate by @saqibkh

#### New Contributors
* @saqibkh made their first contribution

**Full Changelog**: `v1.0.7...v1.0.8`

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

