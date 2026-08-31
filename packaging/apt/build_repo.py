#!/usr/bin/env python3
"""Build the apt repository served from pantheongpu.com/apt.

apt will not install from an unsigned repository without being told to, so the
Release file is signed when a key is available. The private key never lives in
this repository: the release workflow imports it from a secret, and this script
only asks gpg to use it.

The pool lives under docs/ so the existing Pages deploy publishes it. Packages
are small -- the wheel ships kernel sources, not built binaries -- so keeping
past versions in the pool costs little and lets people pin one.
"""

import argparse
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUITE = "stable"
COMPONENT = "main"
# The package is Architecture: all, but apt clients ask for their own
# architecture as well, so publish an index under each.
ARCHITECTURES = ("all", "amd64", "arm64")
ORIGIN = "Pantheon"


def run(*args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise SystemExit(f"{args[0]} failed: {result.stderr.strip()[:400]}")
    return result


def hash_block(root: Path, names, algorithm):
    lines = []
    for name in names:
        path = root / name
        data = path.read_bytes()
        digest = hashlib.new(algorithm, data).hexdigest()
        lines.append(f" {digest} {len(data)} {name}")
    return "\n".join(lines)


def build(debs, repo_root: Path, sign_key: str | None) -> None:
    pool = repo_root / "pool" / COMPONENT / "p" / "pantheon-gpu"
    pool.mkdir(parents=True, exist_ok=True)
    for deb in debs:
        shutil.copy2(deb, pool / deb.name)

    dists = repo_root / "dists" / SUITE
    if dists.exists():
        shutil.rmtree(dists)

    index_names = []
    for arch in ARCHITECTURES:
        arch_dir = dists / COMPONENT / f"binary-{arch}"
        arch_dir.mkdir(parents=True)
        # Paths in Packages must be relative to the repository root, so scan
        # from there rather than from the pool.
        scan = run("dpkg-scanpackages", "--multiversion",
                   str(pool.relative_to(repo_root)), cwd=repo_root)
        packages = scan.stdout
        (arch_dir / "Packages").write_text(packages, encoding="utf-8")
        with gzip.GzipFile(arch_dir / "Packages.gz", "wb", mtime=0) as handle:
            handle.write(packages.encode("utf-8"))
        rel = f"{COMPONENT}/binary-{arch}"
        index_names += [f"{rel}/Packages", f"{rel}/Packages.gz"]

    release = "\n".join([
        f"Origin: {ORIGIN}",
        f"Label: {ORIGIN}",
        f"Suite: {SUITE}",
        f"Codename: {SUITE}",
        f"Architectures: {' '.join(ARCHITECTURES)}",
        f"Components: {COMPONENT}",
        "Description: Pantheon GPU stress testing and diagnostics",
        # A fixed date keeps the file byte-stable when nothing changed, so the
        # data-freshness check in CI does not see a diff on every run.
        "Date: Thu, 01 Jan 1970 00:00:00 UTC",
        "MD5Sum:", hash_block(dists, index_names, "md5"),
        "SHA256:", hash_block(dists, index_names, "sha256"),
        "",
    ])
    (dists / "Release").write_text(release, encoding="utf-8")

    if not sign_key:
        for stale in ("Release.gpg", "InRelease"):
            (dists / stale).unlink(missing_ok=True)
        print("  unsigned: no signing key given, apt will need [trusted=yes]")
        return

    run("gpg", "--batch", "--yes", "--local-user", sign_key,
        "--armor", "--detach-sign", "--output", str(dists / "Release.gpg"),
        str(dists / "Release"))
    run("gpg", "--batch", "--yes", "--local-user", sign_key,
        "--clearsign", "--output", str(dists / "InRelease"),
        str(dists / "Release"))
    export = run("gpg", "--batch", "--yes", "--armor", "--export", sign_key)
    (repo_root / "pantheon-archive-keyring.asc").write_text(
        export.stdout, encoding="utf-8")
    print(f"  signed with {sign_key}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("debs", nargs="+", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("docs/apt"))
    parser.add_argument(
        "--sign-key", default=os.environ.get("PANTHEON_APT_SIGN_KEY") or None,
        help="gpg key id or uid to sign the Release file with")
    args = parser.parse_args()

    missing = [d for d in args.debs if not d.exists()]
    if missing:
        raise SystemExit(f"no such package(s): {missing}")

    args.repo_root.mkdir(parents=True, exist_ok=True)
    build(args.debs, args.repo_root, args.sign_key)
    print(f"Repository written to {args.repo_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
