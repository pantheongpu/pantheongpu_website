#!/usr/bin/env python3
"""Build an installable wheel from a Pantheon source tree.

Pantheon is Python plus 47 C++ kernels. The kernels are not compiled here:
the runner already builds them on first use into a per-user cache, keyed by
version and platform, which is what makes a single pure-Python wheel work for
both CUDA and ROCm across every distribution. Precompiling would mean a matrix
of CUDA and ROCm versions against glibc baselines, and users would still hit
mismatches.

The source tree is staged into a package rather than installed flat. Pantheon
ships a module called `monitor`, and putting a name that common at the top of
site-packages invites a collision with someone else's package.

Nothing in the source tree is modified. The one import that assumes a flat
layout is rewritten in the staged copy, and the build-cache location is set by
the console entry point rather than by patching the runner.
"""

import argparse
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

PACKAGE = "pantheon_gpu"

# Shipped inside the package: the runner locates these relative to its own
# __file__, so they must sit beside it.
DATA_DIRS = ("kernels",)
DATA_FILES = ("Makefile", "VERSION")
MODULES = ("pantheon.py", "monitor.py")


def read_version(source: Path) -> str:
    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)*", version):
        raise SystemExit(f"VERSION does not look like a release: {version!r}")
    return version


def stage(source: Path, work: Path) -> Path:
    pkg = work / PACKAGE
    pkg.mkdir(parents=True)

    for name in MODULES:
        shutil.copy2(source / name, pkg / name)
    for name in DATA_FILES:
        shutil.copy2(source / name, pkg / name)
    for name in DATA_DIRS:
        shutil.copytree(source / name, pkg / name)

    # The runner imports its telemetry module assuming both sit at the top
    # level. Inside a package that has to be relative.
    runner = pkg / "pantheon.py"
    text = runner.read_text(encoding="utf-8")
    if "from monitor import" not in text:
        raise SystemExit("expected 'from monitor import' in pantheon.py; layout changed")
    text = text.replace("from monitor import", "from .monitor import", 1)
    runner.write_text(text, encoding="utf-8")

    (pkg / "__init__.py").write_text('"""Pantheon GPU stress and diagnostics suite."""\n',
                                     encoding="utf-8")

    # An installed package lives somewhere the user cannot write, so kernels
    # must build into a per-user cache. The runner already supports this via
    # PANTHEON_BUILD_CACHE_DIR; setting it here avoids modifying the runner.
    (pkg / "_entry.py").write_text(textwrap.dedent('''\
        """Console entry point for an installed Pantheon."""

        import os


        def main():
            # site-packages is not writable, and the runner defaults to building
            # beside its own source unless told otherwise. Respect an explicit
            # override so a user can still choose the location.
            if not os.environ.get("PANTHEON_BUILD_CACHE_DIR", "").strip():
                cache = os.environ.get("XDG_CACHE_HOME", "").strip() or os.path.join(
                    os.path.expanduser("~"), ".cache")
                os.environ["PANTHEON_BUILD_CACHE_DIR"] = os.path.join(
                    cache, "pantheongpu", "builds")

            from . import pantheon
            return pantheon.main()
        '''), encoding="utf-8")
    return pkg


def write_pyproject(work: Path, version: str) -> None:
    (work / "pyproject.toml").write_text(textwrap.dedent(f'''\
        [build-system]
        requires = ["setuptools>=68"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "pantheon-gpu"
        version = "{version}"
        description = "GPU stress testing and diagnostics for NVIDIA CUDA and AMD ROCm"
        readme = "README.md"
        requires-python = ">=3.9"
        license = {{ text = "Apache-2.0" }}
        dependencies = [
            "psutil",
            "pandas",
            "openpyxl",
            "numpy",
            "nvidia-ml-py",
        ]

        [project.urls]
        Homepage = "https://pantheongpu.com"
        Source = "https://github.com/pantheongpu/pantheon"

        [project.scripts]
        pantheon = "{PACKAGE}._entry:main"

        [tool.setuptools]
        packages = ["{PACKAGE}"]
        include-package-data = true

        [tool.setuptools.package-data]
        "{PACKAGE}" = ["Makefile", "VERSION", "kernels/**/*"]
        '''), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="Pantheon source checkout")
    ap.add_argument("--outdir", type=Path, default=Path("dist"))
    ap.add_argument("--workdir", type=Path, default=Path("build/wheel"))
    args = ap.parse_args()

    source = args.source.resolve()
    for required in (*MODULES, *DATA_FILES, *DATA_DIRS):
        if not (source / required).exists():
            raise SystemExit(f"{source} does not look like a Pantheon tree: missing {required}")

    version = read_version(source)
    work = args.workdir.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    stage(source, work)
    write_pyproject(work, version)
    shutil.copy2(source / "README.md", work / "README.md")
    for extra in ("LICENSE", "NOTICE"):
        if (source / extra).exists():
            shutil.copy2(source / extra, work / extra)

    args.outdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--sdist",
         "--outdir", str(args.outdir.resolve())],
        cwd=work,
    )
    if result.returncode:
        return result.returncode

    built = sorted(args.outdir.glob(f"pantheon_gpu-{version}*"))
    print(f"\nBuilt {len(built)} artifact(s) for {version}:")
    for path in built:
        print(f"  {path.name}  ({path.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
