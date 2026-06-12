#!/usr/bin/env python3
"""Generate the public release page from a GitHub Release payload."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-json", required=True, type=Path)
    parser.add_argument("--releases-json", type=Path)
    parser.add_argument("--assets-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repo", default="saqibkh/pantheongpu_website")
    return parser.parse_args()


def format_date(value: str) -> str:
    if not value:
        return "Unknown"

    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value

    parsed = parsed.astimezone(timezone.utc)
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def format_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024

    return f"{size} B"


def asset_format(name: str) -> str:
    if name.endswith(".deb"):
        return ".deb"
    if name.endswith(".tar.gz"):
        return ".tar.gz"
    if name.endswith(".zip"):
        return ".zip"
    return name


def asset_label(tag: str, name: str) -> str:
    if name.endswith(".deb"):
        return f"Pantheon {tag} Debian Package"
    if name.endswith(".tar.gz"):
        return f"Pantheon {tag} Tarball"
    if name.endswith(".zip"):
        return f"Pantheon {tag} ZIP Bundle"
    if name == "SHA256SUMS":
        return f"Pantheon {tag} Checksums"
    return name


def asset_sort_value(name: str) -> tuple[int, str]:
    if name.endswith(".deb"):
        return (0, name)
    if name.endswith(".tar.gz"):
        return (1, name)
    if name.endswith(".zip"):
        return (2, name)
    if name == "SHA256SUMS":
        return (3, name)
    return (4, name)


def release_notes(body: str) -> str:
    body = body.strip()
    if not body:
        return "See the GitHub release for details."

    lines = []
    for line in body.splitlines():
        if line.startswith("#"):
            lines.append(f"##{line}")
        else:
            lines.append(line)
    return "\n".join(lines)


def release_sort_value(release: dict) -> str:
    return release.get("published_at") or release.get("created_at") or ""


def build_release_section(release: dict, assets_dir: Path, repo: str, latest: bool = False) -> str:
    tag = release["tag_name"]
    name = release.get("name") or tag
    date = format_date(release.get("published_at") or release.get("created_at") or "")
    notes = release_notes(release.get("body") or "")

    downloadable_assets = []
    for asset in release.get("assets", []):
        asset_name = asset.get("name", "")
        if not (
            asset_name.endswith(".deb")
            or asset_name.endswith(".tar.gz")
            or asset_name.endswith(".zip")
            or asset_name == "SHA256SUMS"
        ):
            continue

        local_path = assets_dir / asset_name
        size = local_path.stat().st_size if local_path.exists() else int(asset.get("size") or 0)
        downloadable_assets.append((asset_name, size))

    downloadable_assets.sort(key=lambda item: asset_sort_value(item[0]))

    rows = []
    for asset_name, size in downloadable_assets:
        url = f"https://github.com/{repo}/releases/download/{tag}/{asset_name}"
        rows.append(
            f"| [{asset_label(tag, asset_name)}]({url}) | `{asset_format(asset_name)}` | {format_size(size)} |"
        )

    downloads = "\n".join(rows) if rows else "| No downloadable assets found. | | |"
    latest_label = " (Latest)" if latest else ""

    return f"""## {name}{latest_label}
**Release Date:** {date}

### Release Notes
{notes}

### Downloads
| File | Format | Size |
| :--- | :--- | :--- |
{downloads}
"""


def build_page(release: dict, assets_dir: Path, repo: str, releases: list[dict] | None = None) -> str:
    all_releases = releases or [release]
    releases_by_tag = {item["tag_name"]: item for item in all_releases if item.get("tag_name")}
    releases_by_tag[release["tag_name"]] = release
    sorted_releases = sorted(releases_by_tag.values(), key=release_sort_value, reverse=True)

    sections = []
    for index, item in enumerate(sorted_releases):
        sections.append(build_release_section(item, assets_dir, repo, latest=index == 0))

    release_sections = "\n---\n\n".join(sections)

    return f"""# Releases

Download stable binary builds of the Pantheon GPU toolkit. The newest release is listed first.

---

{release_sections}
"""


def main() -> None:
    args = parse_args()
    release = json.loads(args.release_json.read_text(encoding="utf-8"))
    releases = None
    if args.releases_json:
        releases = json.loads(args.releases_json.read_text(encoding="utf-8"))
    args.output.write_text(build_page(release, args.assets_dir, args.repo, releases), encoding="utf-8")


if __name__ == "__main__":
    main()
