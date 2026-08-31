#!/usr/bin/env python3
"""Build a Debian package from the Pantheon wheel.

This produces the package served from pantheongpu.com's own apt repository.
It is deliberately not a Debian-archive-quality source package: that needs an
ITP bug, a Developer to sponsor the upload, and a decision about the CUDA
toolchain, which is not in Debian main. This is the vendor-repository route
that NVIDIA, Docker and Grafana use, and it works today.

The package installs the Python modules under dist-packages and depends on
Debian's own python3-* packages rather than vendoring them, so the archive's
security updates apply. pandas and numpy are imported at module scope, so they
are Depends; pynvml and psutil are imported inside try/except and the tool
degrades without them, so they are Recommends.

Nothing is written under /usr at runtime: kernels compile into the user's
cache directory on first run, which is why g++ and make are dependencies.
"""

import argparse
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from email.utils import formatdate
from pathlib import Path

PACKAGE = "pantheon-gpu"
MODULE = "pantheon_gpu"

CONTROL = """\
Package: {package}
Version: {version}
Architecture: all
Maintainer: Pantheon <noreply@pantheongpu.com>
Section: contrib/utils
Priority: optional
Depends: python3 (>= 3.9), python3-numpy, python3-pandas, g++, make
Recommends: python3-pynvml, python3-psutil, python3-openpyxl
Suggests: nvidia-cuda-toolkit
Homepage: https://pantheongpu.com
Installed-Size: {installed_size}
Description: GPU stress testing and diagnostics for NVIDIA CUDA and AMD ROCm
 Pantheon runs targeted stress and diagnostic workloads against a GPU and
 reports throughput, thermals, power, clocks and error state.
 .
 The workloads ship as source and are compiled for the installed toolkit on
 first run, into a per-user cache. A CUDA or ROCm toolchain is therefore
 needed to run anything against real hardware; --platform mock exercises the
 tooling on a machine with no GPU at all.
"""

WRAPPER = """\
#!/usr/bin/python3
import sys

from pantheon_gpu._entry import main

if __name__ == "__main__":
    sys.exit(main())
"""


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"{args[0]} failed: {result.stderr.strip()[:400]}")
    return result


def directory_size_kib(root: Path) -> int:
    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    return max(1, total // 1024)


def build(wheel: Path, outdir: Path, workdir: Path) -> Path:
    version = wheel.name.split("-")[1]
    if workdir.exists():
        shutil.rmtree(workdir)
    root = workdir / f"{PACKAGE}_{version}"
    site = root / "usr/lib/python3/dist-packages"
    site.mkdir(parents=True)

    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            # .dist-info describes a wheel install; dpkg tracks this one.
            if name.startswith(f"{MODULE}/"):
                archive.extract(name, site)

    bindir = root / "usr/bin"
    bindir.mkdir(parents=True)
    # Both names: the documentation says "pantheon", while distributions
    # namespace by project and "pantheon" is elementary OS's desktop.
    for name in (PACKAGE, "pantheon"):
        target = bindir / name
        target.write_text(WRAPPER, encoding="utf-8")
        target.chmod(0o755)

    docdir = root / "usr/share/doc" / PACKAGE
    docdir.mkdir(parents=True)
    for name in ("LICENSE", "NOTICE"):
        source = site / MODULE / name
        if source.exists():
            shutil.copy2(source, docdir / name)
    changelog = (
        f"{PACKAGE} ({version}) stable; urgency=low\n\n"
        f"  * Pantheon {version}. See https://github.com/pantheongpu/pantheon\n\n"
        f" -- Pantheon <noreply@pantheongpu.com>  {formatdate(0, localtime=False)}\n"
    )
    with gzip.GzipFile(docdir / "changelog.gz", "wb", mtime=0) as handle:
        handle.write(changelog.encode("utf-8"))

    debian = root / "DEBIAN"
    debian.mkdir()
    (debian / "control").write_text(
        CONTROL.format(package=PACKAGE, version=version,
                       installed_size=directory_size_kib(root)),
        encoding="utf-8")

    # md5sums lets `dpkg -V` and debsums notice a modified install.
    lines = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and debian not in path.parents:
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.relative_to(root)}")
    (debian / "md5sums").write_text("\n".join(lines) + "\n", encoding="utf-8")

    outdir.mkdir(parents=True, exist_ok=True)
    deb = outdir / f"{PACKAGE}_{version}_all.deb"
    run("dpkg-deb", "--root-owner-group", "--build", str(root), str(deb))
    return deb


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, help="built pantheon_gpu wheel")
    parser.add_argument("--outdir", type=Path, default=Path("dist"))
    parser.add_argument("--workdir", type=Path, default=Path("build/deb"))
    args = parser.parse_args()

    if not args.wheel.exists():
        raise SystemExit(f"no such wheel: {args.wheel}")

    deb = build(args.wheel, args.outdir, args.workdir)
    size = deb.stat().st_size / 1024
    print(f"Built {deb.name} ({size:.0f} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
