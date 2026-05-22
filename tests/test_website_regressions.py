import importlib.util
from pathlib import Path


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

    assert "sudo pip install" not in index
    assert "nvidia-cuda-toolkit (replace" not in index
    assert "python3 -m venv .venv" in index
    assert "python -m pip install -r requirements.txt" in index
    assert "sudo apt-get install -y nvidia-cuda-toolkit" in index
    assert "# sudo apt-get install -y hipcc" in index
    assert "python3 pantheon.py --test all --duration 30 --verify" in index
    assert "./pantheon --test all --duration 30 --verify" in index


def test_mkdocs_points_to_pantheongpu_repository():
    mkdocs = read("mkdocs.yml")

    assert "repo_url: https://github.com/saqibkh/pantheongpu" in mkdocs
    assert "repo_name: saqibkh/pantheongpu" in mkdocs
    assert "saqibkh/pantheon\n" not in mkdocs


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
    assert "closeBenchmarkMenus" in tables_js
    assert 'event.key === "Escape"' in tables_js


def test_benchmark_version_filter_defaults_to_all_versions():
    tables_js = read("docs/js/tables.js")

    assert 'buildCheckboxMenu("versionMenu", versions);' in tables_js
    assert "latestVersion" not in tables_js
    assert 'buildCheckboxMenu("versionMenu", versions, latestVersion' not in tables_js


def test_mirror_release_workflow_is_manual_and_validates_assets():
    workflow = read(".github/workflows/mirror-pantheon-release.yml")

    assert "workflow_dispatch:" in workflow
    assert "actions/checkout@v4" in workflow
    assert "ref: ${{ github.ref_name }}" in workflow
    assert "saqibkh/pantheongpu" in workflow
    assert "repos/saqibkh/pantheongpu/releases/latest" in workflow
    assert "repos/saqibkh/pantheongpu/releases/tags/" in workflow
    assert "repos/saqibkh/pantheongpu/releases/assets/" in workflow
    assert "gh release download" not in workflow
    assert "PANTHEON_SOURCE_REPO_TOKEN" in workflow
    assert "GH_REPO: ${{ github.repository }}" in workflow
    assert "Check source repository token access" in workflow
    assert "Scope: repo" in workflow
    assert "Source release is missing a .tar.gz asset." in workflow
    assert "Source release is missing a .zip asset." in workflow
    assert 'tar -tzf "${archive}"' in workflow
    assert 'zip -T "${archive}"' in workflow
    assert "overwrite" in workflow
    assert "Check mirrored release status" in workflow
    assert "exists=true" in workflow
    assert "steps.mirrored.outputs.exists != 'true'" in workflow
    assert "gh release create" in workflow
    assert "Fetch source release list" in workflow
    assert "source-releases.json" in workflow
    assert "website_utils/update_release_page.py" in workflow
    assert "--releases-json source-releases.json" in workflow
    assert "git add docs/release.md" in workflow
    assert 'git push origin HEAD:"${GITHUB_REF_NAME}"' in workflow
    assert "mkdocs gh-deploy --force" in workflow


def test_release_page_generator_is_available():
    script = read("website_utils/update_release_page.py")

    assert "def build_page" in script
    assert "docs/release.md" not in script
    assert "def build_release_section" in script
    assert "releases-json" in script


def test_release_page_generator_writes_all_releases_latest_first(tmp_path):
    module_path = ROOT / "website_utils/update_release_page.py"
    spec = importlib.util.spec_from_file_location("update_release_page", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "pantheon-1.0.8.tar.gz").write_bytes(b"tar")
    (assets_dir / "pantheon-1.0.8.zip").write_bytes(b"zip")
    release = {
        "tag_name": "v1.0.8",
        "name": "Pantheon v1.0.8",
        "published_at": "2026-05-21T05:00:02Z",
        "body": "## What's Changed\n* Fixed releases",
        "assets": [
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
    assert page.index("## Pantheon v1.0.8 (Latest)") < page.index("## Pantheon v1.0.7")
    assert "**Release Date:** May 21, 2026" in page
    assert "#### What's Changed" in page
    assert "pantheon-1.0.8.tar.gz" in page
    assert "pantheon-1.0.8.zip" in page
    assert "pantheon-1.0.7.tar.gz" in page
    assert "pantheon-1.0.7.zip" in page
    assert "2.0 KB" in page
    assert "4.0 KB" in page


def test_wide_layout_is_scoped_to_benchmark_page():
    css = read("docs/css/extra.css")

    assert "body:has(#benchmarkTable) .md-grid" in css
    assert "\n.md-grid {\n  max-width: 95vw" not in css


def test_readme_documents_release_mirroring_secret():
    readme = read("README.md")

    assert "Mirror Pantheon Releases" in readme
    assert "PANTHEON_SOURCE_REPO_TOKEN" in readme
    assert "saqibkh/pantheongpu" in readme
    assert "overwrite" in readme


def test_no_known_mojibake_in_user_facing_sources():
    paths = [
        "README.md",
        "docs/benchmarks.md",
        "docs/release.md",
        "docs/js/tables.js",
        "docs/js/charts.js",
    ]

    for path in paths:
        text = read(path)
        assert "Â" not in text, path
        assert "ðŸ" not in text, path
