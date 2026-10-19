# Fedora and EPEL review spec

`pantheon-gpu.spec` here is the spec to submit for Fedora package review (and
from there EPEL 10). It is not used by the release workflow: COPR keeps
building `../pantheon-gpu.spec`.

How it differs from the COPR spec:

- `Source0` uses `%{pypi_source pantheon_gpu}`, so the tarball is the one on
  PyPI and its checksum can be verified by a reviewer.
- It has a `%check` that runs `pantheon --version` and the CPU mock backend
  (`--platform mock --test baseline_metrics`). The default build flags are
  unset there, because the workloads pass them on to the C++ compiler at run
  time, where the hardening and LTO plugins are not installed.
- `%pyproject_save_files -l` marks `LICENSE` and `NOTICE` as license files.
- `pantheon-gpu` is a symlink to `pantheon` instead of a second copy of the
  launcher (rpmlint `files-duplicate`).
- `pantheon-gpu.rpmlintrc` filters `devel-file-in-non-devel-package`. The
  kernel sources are the payload that gets compiled for the GPU that is
  present, so they cannot go in a `-devel` package.

## Verified

Built from the PyPI 1.2.4 sdist (sha256
`bc4202962bc15a54d9163729cad0c5ef954193f1506f88cbb9de3eb8363e9d57`), noarch,
including `%check`, in `fedora:43` and in `almalinux:10` with EPEL 10 and CRB.
Each result was then installed into a clean container with `dnf install` and
run with `pantheon --version` and the mock backend. EPEL 9 is not a target:
there is no `python3-pandas` in RHEL 9 AppStream, CRB or EPEL 9, and its
setuptools is older than the build needs.

## Warnings left on purpose

- `no-manual-page-for-binary` for `pantheon` and `pantheon-gpu`. A manual page
  is a SHOULD in the guidelines. Add one if the reviewer asks.

## Questions a reviewer is likely to raise

- **nvidia-ml-py.** Upstream metadata requires it and Fedora does not package
  it (neither `python-nvidia-ml-py` nor `python-pynvml` exists). The spec turns
  the dependency generator off and declares the requirements by hand. NVIDIA
  telemetry is therefore unavailable in the Fedora package unless that binding
  is packaged separately, which is a second, small review.
- **Weak dependencies of pandas** make a full install large (about 270
  packages, 1.1 GB on EL10). That comes from `python3-pandas`, not from this
  package.
- **Package name.** `pantheon-gpu` is the application name, not a library, so
  the `python3-` prefix is not used. The module is not meant to be imported by
  other packages.

## Submitting

1. A Fedora Account System account, with the packager group requested. A new
   packager needs a sponsor; a review swap (reviewing someone else's package)
   is the usual way to find one.
2. File the review request in Red Hat Bugzilla (product Fedora, component
   Package Review) with links to the spec and the SRPM, and a
   `fedora-review` run attached.
3. After approval: request the repository, build in Koji for rawhide, then
   request the `epel10` branch and submit through Bodhi.
4. Packit or release-monitoring.org can open the update for each release.
