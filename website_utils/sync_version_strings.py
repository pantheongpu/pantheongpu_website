#!/usr/bin/env python3
"""Keep the version literals the site and packaging carry in step with the
newest release.

The channels themselves are always right: the release workflow reads VERSION
from the source checkout and passes it to PyPI, the apt builder, the COPR spec
and the container build. What drifted was the prose and the defaults around
them: the homepage hero said "v1.2.0 now on PyPI, apt, COPR and Docker" two
releases after 1.2.0 shipped, the install page quoted 1.2.0 in its examples,
and the packaging files kept 1.2.0 as their fallback. Each is a literal that
nothing regenerated.

    python3 website_utils/sync_version_strings.py --version 1.2.2
    python3 website_utils/sync_version_strings.py --check   # exit 1 on drift

The release workflow runs the first form right after it renders
docs/release.md; the regression suite runs the second against the version at
the top of that page, so a release cannot land with the old number still on
the homepage.

Deliberately not covered: packaging/aur/PKGBUILD. Its pkgver moves together
with its sha256sums when an AUR submission is made, and a pkgver bump on its
own would leave the file lying about the checksum.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PAGE = "docs/release.md"
SEMVER = r"\d+\.\d+\.\d+"

# (path, [(pattern, replacement-with-{v}), ...]). Patterns are anchored to the
# exact phrasing so an unrelated version string in the same file is left alone.
TARGETS: list[tuple[str, list[tuple[str, str]]]] = [
    ("docs/index.md", [
        (rf"\bv{SEMVER} now on\b", "v{v} now on"),
    ]),
    ("docs/getting-started.md", [
        (rf"a version \(`{SEMVER}`\)", "a version (`{v}`)"),
        (rf"\(`{SEMVER}-cuda", "(`{v}-cuda"),
        (rf"(?m)^(\s*)VERSION={SEMVER}$", r"\g<1>VERSION={v}"),
    ]),
    ("packaging/rpm/pantheon-gpu.spec", [
        (rf"(?m)^(Version:\s*){SEMVER}$", r"\g<1>{v}"),
    ]),
    ("packaging/docker/Dockerfile.cuda", [
        (rf"(?m)^(ARG PANTHEON_WHEEL=pantheon_gpu-){SEMVER}(-py3-none-any\.whl)$", r"\g<1>{v}\g<2>"),
    ]),
    ("packaging/docker/Dockerfile.rocm", [
        (rf"(?m)^(ARG PANTHEON_WHEEL=pantheon_gpu-){SEMVER}(-py3-none-any\.whl)$", r"\g<1>{v}\g<2>"),
    ]),
]


def latest_release_version(root: Path = ROOT) -> str:
    """The version the generated release page calls Latest."""
    page = (root / RELEASE_PAGE).read_text(encoding="utf-8")
    match = re.search(rf"^## Pantheon v({SEMVER}) \(Latest\)", page, re.M)
    if not match:
        raise SystemExit(f"{RELEASE_PAGE} has no '(Latest)' release heading")
    return match.group(1)


def literals(root: Path = ROOT) -> dict[str, list[str]]:
    """Every version each covered file currently carries, per file."""
    found: dict[str, list[str]] = {}
    for rel, rules in TARGETS:
        text = (root / rel).read_text(encoding="utf-8")
        versions: list[str] = []
        for pattern, _ in rules:
            for match in re.finditer(pattern, text):
                hit = re.search(SEMVER, match.group(0))
                if hit:
                    versions.append(hit.group(0))
        found[rel] = versions
    return found


def sync(version: str, root: Path = ROOT) -> list[str]:
    """Rewrite every covered literal to ``version``. Returns the files changed."""
    if not re.fullmatch(SEMVER, version):
        raise SystemExit(f"not a release version: {version!r}")
    changed: list[str] = []
    for rel, rules in TARGETS:
        path = root / rel
        before = path.read_text(encoding="utf-8")
        after = before
        for pattern, replacement in rules:
            after = re.sub(pattern, replacement.replace("{v}", version), after)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(rel)
    return changed


def drift(version: str, root: Path = ROOT) -> dict[str, list[str]]:
    """Files whose literals do not all equal ``version``, with what they say."""
    return {rel: versions for rel, versions in literals(root).items()
            if not versions or any(v != version for v in versions)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--version", help="release version to write, e.g. 1.2.2")
    parser.add_argument("--check", action="store_true",
                        help="report drift against the release page and exit 1 if any")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    if args.check:
        latest = latest_release_version(args.root)
        stale = drift(latest, args.root)
        if stale:
            for rel, versions in stale.items():
                print(f"{rel}: says {', '.join(versions) or 'nothing'}; release page says {latest}")
            return 1
        print(f"all version literals match {latest}")
        return 0

    if not args.version:
        parser.error("--version is required unless --check is given")
    changed = sync(args.version, args.root)
    print(f"updated {len(changed)} file(s) to {args.version}: {', '.join(changed) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
