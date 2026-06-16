# Releases

Download stable binary builds of the Pantheon GPU toolkit. The newest release is listed first.

---

## Pantheon v1.0.10 (Latest)
**Release Date:** June 12, 2026

### Release Notes
#### What's Changed
* pantheon tuning params by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/5
* Debian binary release by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/6
* Debian binary release by @saqibkh in https://github.com/saqibkh/pantheongpu/pull/7


**Full Changelog**: https://github.com/saqibkh/pantheongpu/compare/v1.0.8...v1.0.10

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
| [Pantheon v1.0.10 Debian Package](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.deb) | `.deb` | 87.4 MB |
| [Pantheon v1.0.10 Tarball](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.tar.gz) | `.tar.gz` | 174.8 MB |
| [Pantheon v1.0.10 ZIP Bundle](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.10/pantheongpu_1.0.10_amd64.zip) | `.zip` | 174.8 MB |
| [Pantheon v1.0.10 Checksums](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.10/SHA256SUMS) | `SHA256SUMS` | 303 B |

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
| [Pantheon v1.0.8 Tarball](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.8/pantheon-1.0.8.tar.gz) | `.tar.gz` | 181.1 KB |
| [Pantheon v1.0.8 ZIP Bundle](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.8/pantheon-1.0.8.zip) | `.zip` | 247.6 KB |
| [Pantheon v1.0.8 Checksums](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.8/SHA256SUMS) | `SHA256SUMS` | 173 B |

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
| [Pantheon v1.0.7 Tarball](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.7/pantheon-v1.0.7-linux-x86_64.tar.gz) | `.tar.gz` | 131.2 MB |
| [Pantheon v1.0.7 ZIP Bundle](https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.7/pantheon-v1.0.7-linux-x86_64.zip) | `.zip` | 131.2 MB |

