# Pantheon GPU Website

This repository contains the MkDocs website for Pantheon, a cross-platform
CUDA/ROCm GPU stress and diagnostics suite. The site publishes documentation,
release links, and a live benchmark dashboard generated from Pantheon report
JSON files.

## Repository Layout

- `docs/` - MkDocs pages, styles, JavaScript, images, and generated web assets.
- `database/` - Raw `pantheon_report_*.json` benchmark reports.
- `website_utils/generate_web_data.py` - Converts raw reports into
  `docs/assets/web_data.json`.
- `mkdocs.yml` - Site navigation, theme, analytics, CSS, and JavaScript config.
- `.github/workflows/deploy.yml` - GitHub Pages deployment workflow.

## Local Setup

Use a virtual environment if possible:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Generate Benchmark Data

The benchmark dashboard reads from `docs/assets/web_data.json`. Regenerate it
after adding or updating reports in `database/`:

```bash
python3 website_utils/generate_web_data.py
```

The generator keeps the best score per GPU, test, and Pantheon version. When a
report does not include a real GPU UUID, it falls back to GPU metadata so
different cards are not collapsed into the same benchmark row.

## Run the Site Locally

```bash
mkdocs serve
```

Then open the local URL printed by MkDocs, usually
`http://127.0.0.1:8000/`.

## Build Check

```bash
python3 -m pytest
python3 -m mkdocs build --strict
```

Use this before opening a pull request or publishing changes.

## Continuous Integration

The CI workflow runs on every push, pull request, and manual dispatch. It
installs the Python dependencies on Python 3.11 and 3.12, runs `pip check`,
runs the pytest suite, regenerates benchmark data, verifies that
`docs/assets/web_data.json` has no uncommitted drift, and builds the MkDocs
site in strict mode. The deploy workflow repeats the same data freshness,
test, and build checks before publishing to GitHub Pages from `main`.

If CI reports that `docs/assets/web_data.json` is out of sync, regenerate and
commit it:

```bash
python3 website_utils/generate_web_data.py
git add docs/assets/web_data.json
```

## Public Binary Downloads

Pantheon source code stays in the private `saqibkh/pantheongpu` repository.
Public users should download binary artifacts from this website repository's
GitHub Releases. The current public binary release is `v1.0.12`:

```bash
VERSION=1.0.12
wget "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.deb"
sudo apt install "./pantheongpu_${VERSION}_amd64.deb"
pantheon --test baseline_metrics --duration 10
```

Release bundles are binary-only and must not include private source files such
as `pantheon.py`, `tuning.py`, `monitor.py`, `kernels/`, `tests/`,
`website_utils/`, or `.git/`.

## Mirror Pantheon Releases

The `Mirror Pantheon Release` workflow copies binary release artifacts from the
main `saqibkh/pantheongpu` repo into this website repo's GitHub Releases page.
It can run manually, and it also listens for the `pantheongpu_released`
repository dispatch event emitted by the Pantheon release workflow.

To run it:

1. Open **Actions** in `saqibkh/pantheongpu_website`.
2. Select **Mirror Pantheon Release**.
3. Click **Run workflow**.
4. Leave `tag` blank to mirror the latest `saqibkh/pantheongpu` release, or
   enter a tag like `v1.0.12`.
5. Set `overwrite` only if the mirrored website release already exists and
   should be recreated.

The workflow copies release notes plus these source release assets:

- `*.deb`
- `*.tar.gz`
- `*.zip`
- `SHA256SUMS`, when present

After mirroring the GitHub Release, the workflow also regenerates
`docs/release.md`, commits that page update back to the selected branch, runs
the website checks, and deploys the MkDocs site to GitHub Pages. Run the
workflow from `main` when the public site should be updated immediately. The
release page is generated from releases that exist in this public website repo,
so private source releases that were not mirrored do not produce broken public
download links.

Before publishing, the workflow validates that binary bundles do not contain
private source repository paths such as `pantheon.py`, `tuning.py`, `monitor.py`,
`kernels/`, `tests/`, `website_utils/`, or `.git/`.

If `saqibkh/pantheongpu` is private, add this repository secret under
**Settings -> Secrets and variables -> Actions**:

```text
PANTHEON_SOURCE_REPO_TOKEN
```

The token must belong to a GitHub account that can read `saqibkh/pantheongpu`.
A classic personal access token with `repo` scope is the most reliable option.
For a fine-grained token, grant repository access to `saqibkh/pantheongpu` and
set **Contents** to **Read-only**.

For automatic mirroring from the source repository, configure the
`PANTHEON_WEBSITE_RELEASE_TOKEN` secret in `saqibkh/pantheongpu` with permission
to create repository dispatch events in `saqibkh/pantheongpu_website`.

## Deployment

Pushing to `main` runs the GitHub Actions workflow in
`.github/workflows/deploy.yml`. The workflow installs dependencies, regenerates
`docs/assets/web_data.json`, verifies the site, and publishes the MkDocs site
to GitHub Pages.
