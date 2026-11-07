# Pantheon GPU Website

This repository contains the MkDocs website for Pantheon, a cross-platform
CUDA/ROCm GPU stress and diagnostics suite. The site publishes documentation,
release links, and a live benchmark dashboard generated from Pantheon report
JSON files.

## Community

Use [GitHub Discussions](https://github.com/pantheongpu/pantheongpu_website/discussions)
for questions, result showcases, and workload ideas. Use the repository's issue
forms for benchmark submissions and reproducible hardware regressions. See
[Community](docs/community.md) for the reporting and Discord-launch policy.

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

## Installing Pantheon and Downloading Releases

Pantheon's source is public at
[`pantheongpu/pantheon`](https://github.com/pantheongpu/pantheon). That
repository carries only source, tests, and docs and builds no releases. This
repository is the release host: the Release workflow checks out a tag of the
source repository, builds the packages, and publishes them on the
[Releases page](https://github.com/pantheongpu/pantheongpu_website/releases).

The [Getting Started](https://pantheongpu.com/getting-started/) page lists
every install route (PyPI, conda-forge, the apt repository, Fedora COPR, the
container images, a release download, and building from source) and always
shows the current version. The most common ones:

```bash
pipx install pantheon-gpu                   # PyPI
conda install -c conda-forge pantheon-gpu   # conda-forge
docker run --rm -t --gpus all -v "$PWD:/reports" \
  ghcr.io/pantheongpu/pantheon:latest --test baseline_metrics --duration 10
```

Each GitHub Release also carries the Debian package
(`pantheon-gpu_<version>_all.deb`), the Python wheel and source distribution
(`pantheon_gpu-<version>-py3-none-any.whl` and `pantheon_gpu-<version>.tar.gz`),
source archives, and `SHA256SUMS`. To install the latest Debian package from the
Releases page:

```bash
gh release download --repo pantheongpu/pantheongpu_website --pattern 'pantheon-gpu_*_all.deb'
sudo apt install ./pantheon-gpu_*_all.deb
pantheon --test baseline_metrics --duration 10
```

Uninstall the way the package was installed:

```bash
pipx uninstall pantheon-gpu                    # PyPI or a downloaded wheel
conda remove pantheon-gpu                      # conda-forge
sudo apt-get remove pantheon-gpu               # Debian package or apt repository
docker rmi ghcr.io/pantheongpu/pantheon:latest # container image
```

Releases up to v1.0.19 shipped as a Debian package named `pantheongpu`. Remove
one of those with:

```bash
sudo apt-get remove pantheongpu
```

For a portable installation made with `sudo ./install.sh` from one of those
older bundles, on RHEL, Fedora, Rocky Linux, AlmaLinux, or another Linux
distribution:

```bash
sudo rm -f /usr/local/bin/pantheon && sudo rm -rf /opt/pantheongpu
```

To completely remove any installation type and the current user's compiled
workload cache:

```bash
curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh
```

## Publishing a Release

1. Bump `VERSION` in `pantheongpu/pantheon` (via pull request) and tag it
   `vX.Y.Z`.
2. Run the **Release** workflow here with `ref=vX.Y.Z` and `dry_run=true`. It
   builds the packages and renders the release page without publishing.
3. Run it again with `dry_run=false` to publish the GitHub Release, the apt
   repository, the PyPI upload, the container images, the COPR build, and the
   regenerated `docs/release.md`.

`CLAUDE.md` has the full checklist, including the version strings that must
change in the same pull request.

## Mirror Pantheon Releases (legacy)

Releases up to v1.0.19 were built in the older `pantheongpu/pantheongpu`
repository, which cannot be read without a token. The `Mirror Pantheon Release`
workflow still exists to copy those releases into this repository's GitHub
Releases page. Newer releases do not use it. It can run manually, and it also
listens for the `pantheongpu_released` repository dispatch event.

To run it:

1. Open **Actions** in `pantheongpu/pantheongpu_website`.
2. Select **Mirror Pantheon Release**.
3. Click **Run workflow**.
4. Leave `tag` blank to mirror the latest `pantheongpu/pantheongpu` release, or
   enter a tag like `v1.0.19`.
5. Set `overwrite` only if the mirrored website release already exists and
   should be recreated.

The workflow copies release notes plus these source release assets:

- `*.deb`
- `*.tar.gz`
- `*.zip`
- `SHA256SUMS`, when present

After mirroring the GitHub Release, the workflow also regenerates
`docs/release.md`, proposes that page update to `main` as a pull request, and
deploys the MkDocs site to GitHub Pages. The release page is generated from
releases that exist in this public website repo, so releases that were not
mirrored do not produce broken public download links.

Before publishing, the workflow validates that the bundles do not contain
source-tree paths such as `pantheon.py`, `tuning.py`, `monitor.py`, `kernels/`,
`tests/`, `website_utils/`, or `.git/`.

Because `pantheongpu/pantheongpu` needs authentication, add this repository
secret under **Settings -> Secrets and variables -> Actions**:

```text
PANTHEON_SOURCE_REPO_TOKEN
```

The token must belong to a GitHub account that can read `pantheongpu/pantheongpu`.
A classic personal access token with `repo` scope is the most reliable option.
For a fine-grained token, grant repository access to `pantheongpu/pantheongpu` and
set **Contents** to **Read-only**. The Release workflow uses the same secret to
mirror each release tag back to the source repository.

For automatic mirroring from the older repository, configure the
`PANTHEON_WEBSITE_RELEASE_TOKEN` secret in `pantheongpu/pantheongpu` with permission
to create repository dispatch events in `pantheongpu/pantheongpu_website`.

## Deployment

Pushing to `main` runs the GitHub Actions workflow in
`.github/workflows/deploy.yml`. The workflow installs dependencies, regenerates
`docs/assets/web_data.json`, verifies the site, and publishes the MkDocs site
to GitHub Pages.
