# Pantheon: Universal GPU Stress & Diagnostics Suite

Pantheon is a cross-platform (CUDA/ROCm) stress testing tool designed to isolate and hammer specific GPU subsystems. Unlike generic benchmarks (Furmark, 3DMark), Pantheon allows you to test specific silicon limits.

## Website Dashboard

Pantheon includes a built-in web dashboard to visualize your benchmark results and compare different GPUs.

### 1. Install Dependencies
The dashboard is built with MkDocs. You need to install the material theme:
```bash
pip install mkdocs-material
```

### 2. Generate Data
The website reads from docs/assets/web_data.json. You must generate this file from your local database/ reports:
```bash
# parse local results and update the website JSON
python3 website_utils/generate_web_data.py
```
