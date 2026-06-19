import json
import importlib.util
import re
from pathlib import Path

from website_utils.generate_web_data import main as generate_web_data


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_benchmark_page_does_not_load_table_script_twice():
    benchmarks = read("docs/benchmarks.md")

    assert "tables.js" not in benchmarks


def test_benchmark_script_is_scoped_to_benchmark_page():
    tables_js = read("docs/js/tables.js")

    assert 'document.getElementById("benchmarkTable")' in tables_js
    assert "if (!table) return;" in tables_js
    assert "getBenchmarkAssetUrl" in tables_js


def test_chart_script_only_fetches_when_chart_targets_exist():
    charts_js = read("docs/js/charts.js")
    benchmarks = read("docs/benchmarks.md")
    comparisons = read("docs/benchmark-comparisons.md")

    assert 'elementId: "chart-memory-read"' in charts_js
    assert 'elementId: "chart-memory"' in charts_js
    assert 'elementId: "chart-pcie"' in charts_js
    assert 'elementId: "chart-p2p"' not in charts_js
    assert 'elementId: "chart-tensor"' in charts_js
    assert 'elementId: "chart-fp64"' in charts_js
    assert 'elementId: "chart-integer"' in charts_js
    assert 'elementId: "chart-mma"' in charts_js
    assert 'elementId: "chart-rt"' in charts_js
    assert 'elementId: "chart-scheduler"' in charts_js
    assert "BENCHMARK_CHARTS.some" in charts_js
    assert "getChartAssetUrl" in charts_js
    assert 'id="chart-memory-read"' not in benchmarks
    assert 'id="chart-memory"' not in benchmarks
    assert "benchmark-comparisons.md" in benchmarks
    assert 'id="chart-memory-read"' in comparisons
    assert 'id="chart-memory"' in comparisons
    assert 'id="chart-pcie"' in comparisons
    assert 'id="chart-p2p"' not in comparisons
    assert 'id="chart-tensor"' not in benchmarks
    assert 'id="chart-fp64"' not in benchmarks
    assert 'id="chart-tensor"' in comparisons
    assert 'id="chart-fp64"' in comparisons
    assert 'id="chart-integer"' in comparisons
    assert 'id="chart-mma"' in comparisons
    assert 'id="chart-rt"' in comparisons
    assert 'id="chart-scheduler"' in comparisons


def test_performance_comparisons_are_nested_under_database_nav():
    mkdocs = read("mkdocs.yml")

    assert "  - Performance Database:" in mkdocs
    assert "    - Live Benchmarks: benchmarks.md" in mkdocs
    assert "    - Comparisons: benchmark-comparisons.md" in mkdocs


def test_performance_pages_disclose_data_provenance():
    benchmarks = read("docs/benchmarks.md")
    comparisons = read("docs/benchmark-comparisons.md")

    for page in (benchmarks, comparisons):
        assert '!!! note "Data provenance"' in page
        assert "third-party cloud and community systems" in page
        assert "Vast.ai and RunPod" in page
        assert "not collected, certified, or endorsed by NVIDIA, AMD, or their employees" in page


def test_research_reports_page_is_available():
    mkdocs = read("mkdocs.yml")
    reports = read("docs/reports.md")
    article = read("docs/reports/silicon-segregation.md")
    tensor_article = read("docs/reports/tensor-lineage.md")

    assert "  - Research & Reports:" in mkdocs
    assert "    - Overview: reports.md" in mkdocs
    assert '    - "Silicon Segregation": reports/silicon-segregation.md' in mkdocs
    assert '    - "Tracing the Tensor Lineage": reports/tensor-lineage.md' in mkdocs
    assert "# Research & Reports" in reports
    assert "Long-form analysis, papers, benchmark notes" in reports
    assert "## Featured" in reports
    assert "## Archive" in reports
    assert "## Suggested Report Format" in reports
    assert "Silicon Segregation" in reports
    assert "Tracing the Tensor Lineage" in reports
    assert "# Silicon Segregation: What Low-Level Telemetry Reveals About Enterprise vs. Consumer GPUs" in article
    assert "By Saqib Khan" in article
    assert "https://www.linkedin.com/in/saqib-khan-2a0ab164/" in article
    assert "## 1. The FP64 Chasm: Artificial Silicon Fusing" in article
    assert article.count('class="report-figure"') >= 3
    assert article.count('class="report-chart-svg"') >= 3
    assert "FP64 throughput exposes the enterprise precision unlock." in article
    assert "FP64 Throughput (TFLOPS)" in article
    assert "publishes public binary releases" in article
    assert "fully open-source" not in article
    assert "## The Takeaway" in article
    assert "https://pantheongpu.com/" in article
    assert "# Tracing the Tensor Lineage: How Ampere, Hopper, and Blackwell Scale at the Silicon Level" in tensor_article
    assert "By Saqib Khan" in tensor_article
    assert "https://www.linkedin.com/in/saqib-khan-2a0ab164/" in tensor_article
    assert "## 1. The Tensor Core Explosion and Plateau" in tensor_article
    assert tensor_article.count('class="report-figure"') >= 3
    assert tensor_article.count('class="report-chart-svg"') >= 3
    assert "Atomic throughput is where Blackwell's cache fabric makes the biggest jump." in tensor_article
    assert "Atomic Throughput (MAPS)" in tensor_article
    assert "## 5. Thermal Density and the Death of Air Cooling" in tensor_article
    assert "572,143 MAPS" in tensor_article
    assert "https://pantheongpu.com/" in tensor_article


def test_benchmark_charts_follow_table_filters_and_expected_units():
    charts_js = read("docs/js/charts.js")
    tables_js = read("docs/js/tables.js")

    assert "window.renderBenchmarkCharts = renderBenchmarkCharts" in charts_js
    assert 'window.renderBenchmarkCharts(filtered)' in tables_js
    assert 'testName: "memory_read_agg"' in charts_js
    assert 'testName: "memory_write_agg"' in charts_js
    assert 'testName: "pcie_bandwidth"' in charts_js
    assert 'testName: "p2p_thrasher"' not in charts_js
    assert 'testName: "tensor_virus"' in charts_js
    assert 'testName: "fp64_virus"' in charts_js
    assert 'testName: "int_virus"' in charts_js
    assert 'testName: "mma_virus"' in charts_js
    assert 'testName: "rt_virus"' in charts_js
    assert 'testName: "scheduler"' in charts_js
    assert 'title: "Memory Read Bandwidth"' in charts_js
    assert 'title: "Memory Write Bandwidth"' in charts_js
    assert 'title: "PCIe Bandwidth"' in charts_js
    assert 'title: "Ray Tracing Throughput"' in charts_js
    assert "d.unit === expectedUnit" in charts_js
    assert "chart-empty" in charts_js
    assert "chart-container--empty" in charts_js
    assert "Best reported result per GPU" in charts_js
    assert "sort((a, b) => b[1] - a[1])" in charts_js
    assert "dataLabels" in charts_js
    assert "enabled: true" in charts_js
    assert "formatter: value => `${formatChartValue(value)}${unit ? ` ${unit}` : \"\"}`" in charts_js
    assert "offsetX: 8" in charts_js
    assert "textAnchor: 'start'" in charts_js
    assert "background: {" not in charts_js
    assert 'const compact = window.matchMedia("(max-width: 600px)").matches;' in charts_js
    assert "maxWidth: compact ? 112 : 180" in charts_js
    assert "right: compact ? 52 : 96" in charts_js
    assert "chartThemeObserver" in charts_js
    assert 'document.body.getAttribute("data-md-color-scheme")' in charts_js
    assert "chartThemeObserver.observe(document.body" in charts_js


def test_throughput_formatting_uses_row_unit_not_hardcoded_bandwidth():
    tables_js = read("docs/js/tables.js")

    assert 'formatMetric(val, row.unit)' in tables_js
    assert '`${val} GB/s`' not in tables_js


def test_export_button_is_labeled_as_csv():
    benchmarks = read("docs/benchmarks.md")
    tables_js = read("docs/js/tables.js")

    assert "Export CSV" in benchmarks
    assert "Export Excel" not in benchmarks
    assert "Export to CSV" in tables_js


def test_home_quick_start_uses_valid_install_commands():
    index = read("docs/index.md")
    mkdocs = read("mkdocs.yml")

    assert "sudo pip install" not in index
    assert "nvidia-cuda-toolkit (replace" not in index
    assert "python3 -m venv .venv" not in index
    assert "python -m pip install -r requirements.txt" not in index
    assert "python3 pantheon.py" not in index
    assert "pantheon-tuning" not in index
    assert "./pantheon --test all" not in index
    assert "### 1. Install prerequisites" in index
    assert "### 2. Install Pantheon" in index
    assert "### 3. Verify the installation" in index
    assert '=== "NVIDIA CUDA"' in index
    assert '=== "AMD ROCm/HIP"' in index
    assert "  - pymdownx.tabbed:" in mkdocs
    assert "      alternate_style: true" in mkdocs
    assert '??? info "Alternative: install from the release bundle"' in index
    assert "sudo apt-get install -y make g++" in index
    assert "sudo apt-get install -y nvidia-cuda-toolkit" in index
    assert "sudo apt-get install -y hipcc" in index
    assert "VERSION=1.0.12" in index
    assert "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.deb" in index
    assert "https://github.com/saqibkh/pantheongpu_website/releases/download/v${VERSION}/pantheongpu_${VERSION}_amd64.tar.gz" in index
    assert 'sudo apt install "./pantheongpu_${VERSION}_amd64.deb"' in index
    assert 'sudo apt install "./packages/pantheongpu_${VERSION}_amd64.deb"' in index
    assert "pantheon --test baseline_metrics --duration 10" in index
    assert "pantheon --test fp64_virus --duration 30 --gpu 0" in index
    assert "Pantheon automatically detects CUDA, ROCm/HIP, or mock mode." in index
    assert "you do not need to pass `--platform cuda`" in index
    assert "install.sh" in index
    assert "PANTHEON_BUILD_CACHE_DIR" in index
    assert index.count("sudo apt-get remove pantheongpu") >= 2
    assert "sudo rm -f /usr/local/bin/pantheon && sudo rm -rf /opt/pantheongpu" in index
    assert "curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh" in index
    assert '${XDG_CACHE_HOME:-$HOME/.cache}/pantheongpu/builds/' in index


def test_clean_uninstall_script_covers_package_portable_and_cache_files():
    uninstall = read("docs/uninstall.sh")
    docker_test = read("tests/test_uninstall_in_docker.sh")
    workflow = read(".github/workflows/ci.yml")

    assert "apt-get purge -y pantheongpu" in uninstall
    assert "dpkg --purge pantheongpu" in uninstall
    assert "/usr/local/bin/pantheon" in uninstall
    assert "rm -rf /opt/pantheongpu" in uninstall
    assert 'rm -rf "${cache_home}/pantheongpu"' in uninstall
    assert "SUDO_USER" in uninstall
    assert "ubuntu:24.04" in docker_test
    assert "apt-get remove -y pantheongpu" in docker_test
    assert "sh /workspace/docs/uninstall.sh" in docker_test
    assert "uninstall-smoke:" in workflow


def test_readme_pairs_install_commands_with_native_uninstall_commands():
    readme = read("README.md")

    assert 'sudo apt install "./pantheongpu_${VERSION}_amd64.deb"' in readme
    assert "sudo apt-get remove pantheongpu" in readme
    assert "sudo ./install.sh" in readme
    assert "sudo rm -f /usr/local/bin/pantheon && sudo rm -rf /opt/pantheongpu" in readme
    assert "curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh" in readme


def test_mkdocs_points_to_pantheongpu_repository():
    mkdocs = read("mkdocs.yml")

    assert "repo_url: https://github.com/saqibkh/pantheongpu" in mkdocs
    assert "repo_name: saqibkh/pantheongpu" in mkdocs
    assert "saqibkh/pantheon\n" not in mkdocs


def test_site_declares_compact_favicon_assets():
    mkdocs = read("mkdocs.yml")
    favicon = ROOT / "docs/assets/favicon.ico"
    favicon_png = ROOT / "docs/assets/favicon.png"

    assert "favicon: assets/favicon.ico" in mkdocs
    assert favicon.exists()
    assert favicon.read_bytes()[:4] == b"\x00\x00\x01\x00"
    assert favicon.stat().st_size < 50_000
    assert favicon_png.exists()
    assert favicon_png.stat().st_size < 50_000


def test_home_logo_uses_uncropped_responsive_class():
    index = read("docs/index.md")
    css = read("docs/css/extra.css")

    assert 'class="home-logo"' in index
    assert ".home-logo" in css
    assert "object-fit: contain" in css
    assert "height: auto" in css


def test_benchmark_table_has_mobile_scroll_wrapper():
    benchmarks = read("docs/benchmarks.md")
    css = read("docs/css/extra.css")

    assert 'class="benchmark-table-wrap"' in benchmarks
    assert ".benchmark-table-wrap" in css
    assert "overflow-x: auto" in css


def test_filter_controls_expose_menu_state():
    benchmarks = read("docs/benchmarks.md")
    tables_js = read("docs/js/tables.js")

    assert 'aria-controls="gpuMenu"' in benchmarks
    assert 'aria-expanded="false"' in benchmarks
    assert 'aria-haspopup="true"' in benchmarks
    assert "closeBenchmarkMenus" in tables_js
    assert 'event.key === "Escape"' in tables_js


def test_benchmark_search_responds_to_all_input_changes_and_reports_result_count():
    benchmarks = read("docs/benchmarks.md")
    tables_js = read("docs/js/tables.js")

    assert 'type="search"' in benchmarks
    assert "onkeyup=" not in benchmarks
    assert 'id="benchmarkStatus"' in benchmarks
    assert 'searchInput.addEventListener("input", applyFilters)' in tables_js
    assert "${filtered.length} ${filteredLabel} shown out of ${bestRuns.length}" in tables_js


def test_benchmark_sort_headers_are_keyboard_accessible():
    tables_js = read("docs/js/tables.js")
    css = read("docs/css/extra.css")

    assert 'button.className = "benchmark-sort-button"' in tables_js
    assert 'th.setAttribute("aria-sort", sortDirectionFor(col.key))' in tables_js
    assert 'button.addEventListener("click", () => sortData(col.key))' in tables_js
    assert ".benchmark-sort-button:focus-visible" in css


def test_benchmark_version_filter_defaults_to_all_versions():
    tables_js = read("docs/js/tables.js")

    assert 'buildCheckboxMenu("versionMenu", versions);' in tables_js
    assert "latestVersion" not in tables_js
    assert 'buildCheckboxMenu("versionMenu", versions, latestVersion' not in tables_js


def test_benchmark_table_sorts_versions_semantically_latest_first():
    tables_js = read("docs/js/tables.js")

    assert "let currentSort = { key: 'version', dir: 'desc' };" in tables_js
    assert "function normalizeVersion" in tables_js
    assert "function compareVersions" in tables_js
    assert 'String(value).replace(/^v/i, "")' in tables_js
    assert "part.match(/\\d+/)" in tables_js
    assert "parseInt(match[0], 10)" in tables_js
    assert "versions.sort((a, b) => compareVersions(b, a));" in tables_js
    assert 'if (currentSort.key !== "version")' in tables_js
    assert "const versionCompare = compareVersions(a.version || \"Legacy\", b.version || \"Legacy\");" in tables_js
    assert "if (versionCompare !== 0) return -versionCompare;" in tables_js


def test_unknown_version_fp64_result_is_not_published():
    web_data = read("docs/assets/web_data.json")

    assert not (ROOT / "database/pantheon_report_20260406-122531.json").exists()
    assert '"version": "vUnknown"' not in web_data
    assert '"date": "2026-04-06 12:25:34"' not in web_data
    assert '"score": 0.571593' not in web_data


def test_committed_web_data_matches_database_reports(tmp_path):
    generated_file = tmp_path / "web_data.json"

    generated_rows = generate_web_data(output_file=generated_file)
    committed_rows = json.loads(read("docs/assets/web_data.json"))

    assert generated_rows == committed_rows


def test_published_atomic_results_use_maps_units():
    rows = json.loads(read("docs/assets/web_data.json"))
    atomic_units = {row["unit"] for row in rows if row.get("test") == "atomic_virus"}

    assert atomic_units == {"MAPS"}


def test_ci_checks_generated_data_drift_and_dependency_health():
    ci = read(".github/workflows/ci.yml")
    deploy = read(".github/workflows/deploy.yml")
    mirror = read(".github/workflows/mirror-pantheon-release.yml")

    assert 'python-version: ["3.11", "3.12"]' in ci
    assert "python -m pip check" in ci
    assert "git diff --exit-code -- docs/assets/web_data.json" in ci
    assert "python -m mkdocs build --strict" in ci
    assert "cancel-in-progress: true" in ci
    assert "python -m pip check" in deploy
    assert "git diff --exit-code -- docs/assets/web_data.json" in deploy
    assert "python -m pip check" in mirror
    assert "git diff --exit-code -- docs/assets/web_data.json" in mirror


def test_mirror_release_workflow_accepts_manual_and_dispatch_events_and_validates_assets():
    workflow = read(".github/workflows/mirror-pantheon-release.yml")

    assert "workflow_dispatch:" in workflow
    assert "repository_dispatch:" in workflow
    assert "types: [pantheongpu_released]" in workflow
    assert "actions/checkout@v4" in workflow
    assert "ref: ${{ github.ref_name }}" in workflow
    assert "Resolve workflow options" in workflow
    assert "github.event.client_payload.tag" in workflow
    assert "github.event.inputs.tag" in workflow
    assert "saqibkh/pantheongpu" in workflow
    assert "repos/saqibkh/pantheongpu/releases/latest" in workflow
    assert "repos/saqibkh/pantheongpu/releases/tags/" in workflow
    assert "repos/saqibkh/pantheongpu/releases/assets/" in workflow
    assert "gh release download" not in workflow
    assert "PANTHEON_SOURCE_REPO_TOKEN" in workflow
    assert "GH_REPO: ${{ github.repository }}" in workflow
    assert "Check source repository token access" in workflow
    assert "Scope: repo" in workflow
    assert ".deb$" in workflow
    assert "Source release is missing a .deb asset." in workflow
    assert "Source release is missing a .tar.gz asset." in workflow
    assert "Source release is missing a .zip asset." in workflow
    assert 'dpkg-deb --info "${package}"' in workflow
    assert 'tar -tzf "${archive}"' in workflow
    assert 'zip -T "${archive}"' in workflow
    assert "Reject source repository files in release bundles" in workflow
    assert 'blocked_exact = {"pantheon.py", "tuning.py", "monitor.py"}' in workflow
    assert 'blocked_dirs = {".git", "kernels", "tests", "website_utils"}' in workflow
    assert "Release bundles include files from the private source repository:" in workflow
    assert "overwrite" in workflow
    assert "Check mirrored release status" in workflow
    assert "exists=true" in workflow
    assert "steps.options.outputs.overwrite == 'true'" in workflow
    assert "steps.mirrored.outputs.exists != 'true'" in workflow
    assert "gh release create" in workflow
    assert "Fetch website release list" in workflow
    assert 'repos/${GITHUB_REPOSITORY}/releases' in workflow
    assert "website-releases.json" in workflow
    assert "source-releases.json" not in workflow
    assert "website_utils/update_release_page.py" in workflow
    assert "--releases-json website-releases.json" in workflow
    assert "git add docs/release.md" in workflow
    assert 'git push origin HEAD:"${GITHUB_REF_NAME}"' in workflow
    assert "mkdocs gh-deploy --force" in workflow


def test_release_page_generator_is_available():
    script = read("website_utils/update_release_page.py")

    assert "def build_page" in script
    assert "docs/release.md" not in script
    assert "def build_release_section" in script
    assert "def asset_sort_value" in script
    assert "def build_version_nav" not in script
    assert "def release_anchor" not in script
    assert "releases-json" in script
    assert 'name.endswith(".deb")' in script


def test_release_page_generator_writes_all_releases_latest_first(tmp_path):
    module_path = ROOT / "website_utils/update_release_page.py"
    spec = importlib.util.spec_from_file_location("update_release_page", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "pantheongpu_1.0.8_amd64.deb").write_bytes(b"deb")
    (assets_dir / "pantheon-1.0.8.tar.gz").write_bytes(b"tar")
    (assets_dir / "pantheon-1.0.8.zip").write_bytes(b"zip")
    release = {
        "tag_name": "v1.0.8",
        "name": "Pantheon v1.0.8",
        "published_at": "2026-05-21T05:00:02Z",
        "body": "## What's Changed\n* Fixed releases",
        "assets": [
            {"name": "pantheongpu_1.0.8_amd64.deb", "size": 12345},
            {"name": "pantheon-1.0.8.tar.gz", "size": 999},
            {"name": "pantheon-1.0.8.zip", "size": 999},
        ],
    }
    older_release = {
        "tag_name": "v1.0.7",
        "name": "Pantheon v1.0.7",
        "published_at": "2026-04-06T05:00:02Z",
        "body": "Previous release",
        "assets": [
            {"name": "pantheon-1.0.7.tar.gz", "size": 2048},
            {"name": "pantheon-1.0.7.zip", "size": 4096},
        ],
    }

    page = module.build_page(
        release,
        assets_dir,
        "saqibkh/pantheongpu_website",
        [older_release, release],
    )

    assert "## Pantheon v1.0.8 (Latest)" in page
    assert "## Pantheon v1.0.7 (Latest)" not in page
    assert "## Pantheon v1.0.7" in page
    assert 'class="release-version-nav"' not in page
    assert '<section id=' not in page
    assert page.index("## Pantheon v1.0.8 (Latest)") < page.index("## Pantheon v1.0.7")
    assert "**Release Date:** May 21, 2026" in page
    assert "#### What's Changed" in page
    assert "Pantheon v1.0.8 Debian Package" in page
    assert "pantheongpu_1.0.8_amd64.deb" in page
    assert "12.1 KB" in page
    assert "pantheon-1.0.8.tar.gz" in page
    assert "pantheon-1.0.8.zip" in page
    assert "Tarball" in page
    assert "ZIP Bundle" in page
    assert page.index("pantheongpu_1.0.8_amd64.deb") < page.index("pantheon-1.0.8.tar.gz")
    assert "pantheon-1.0.7.tar.gz" in page
    assert "pantheon-1.0.7.zip" in page
    assert "2.0 KB" in page
    assert "4.0 KB" in page


def test_wide_layout_is_scoped_to_benchmark_page():
    css = read("docs/css/extra.css")

    assert "body:has(#benchmarkTable) .md-grid" in css
    assert "\n.md-grid {\n  max-width: 95vw" not in css


def test_report_pages_have_figures_and_wider_layout():
    css = read("docs/css/extra.css")

    assert "body:has(.report-byline) .md-grid" in css
    assert "max-width: min(1760px, 98vw)" in css
    assert "body:has(.report-byline) .md-main__inner" in css
    assert "column-gap: 2.4rem" in css
    assert "body:has(.report-byline) .md-content__inner" in css
    assert "max-width: 900px" in css
    assert ".report-figure" in css
    assert ".report-chart-svg" in css
    assert ".report-chart-title" in css
    assert "reportChartGradient" not in css


def test_release_page_uses_builtin_table_of_contents():
    release = read("docs/release.md")
    css = read("docs/css/extra.css")

    latest = re.search(r"^## Pantheon (v[\d.]+) \(Latest\)$", release, re.MULTILINE)

    assert latest is not None
    latest_tag = latest.group(1)
    latest_version = latest_tag.removeprefix("v")
    assert release.count("(Latest)") == 1
    assert f"Pantheon {latest_tag} Debian Package" in release
    assert f"pantheongpu_{latest_version}_amd64.tar.gz" in release
    assert "## Pantheon v1.0.8" in release
    assert "## Pantheon v1.0.8 (Latest)" not in release
    assert "v1.0.9" not in release
    assert "## v1.0.7" in release
    assert "Download stable binary builds" in release
    assert "TarFile" not in release
    assert "ZipFile" not in release
    assert 'class="release-version-nav"' not in release
    assert ".release-page" not in css
    assert ".release-version-nav" not in css


def test_readme_documents_release_mirroring_secret():
    readme = read("README.md")

    assert "Mirror Pantheon Releases" in readme
    assert "PANTHEON_SOURCE_REPO_TOKEN" in readme
    assert "PANTHEON_WEBSITE_RELEASE_TOKEN" in readme
    assert "Public Binary Downloads" in readme
    assert "VERSION=1.0.12" in readme
    assert "pantheon --test baseline_metrics --duration 10" in readme
    assert "tag like `v1.0.12`" in readme
    assert "tag like `v1.0.8`" not in readme
    assert "`*.deb`" in readme
    assert "repository dispatch" in readme
    assert "private source repository paths" in readme
    assert "public website repo" in readme
    assert "saqibkh/pantheongpu" in readme
    assert "overwrite" in readme


def test_no_known_mojibake_in_user_facing_sources():
    paths = [
        "README.md",
        "docs/benchmarks.md",
        "docs/release.md",
        "docs/reports.md",
        "docs/reports/silicon-segregation.md",
        "docs/reports/tensor-lineage.md",
        "docs/js/tables.js",
        "docs/js/charts.js",
    ]

    for path in paths:
        text = read(path)
        assert "Â" not in text, path
        assert "ðŸ" not in text, path
