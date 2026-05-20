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

The CI workflow runs on every push and pull request. It installs the Python
dependencies, runs the pytest suite, regenerates benchmark data, and builds the
MkDocs site in strict mode. The deploy workflow repeats those checks before
publishing to GitHub Pages from `main`.

## Deployment

Pushing to `main` runs the GitHub Actions workflow in
`.github/workflows/deploy.yml`. The workflow installs dependencies, regenerates
`docs/assets/web_data.json`, verifies the site, and publishes the MkDocs site
to GitHub Pages.
