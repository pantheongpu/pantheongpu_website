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

    assert 'elementId: "chart-memory-read"' in charts_js
    assert 'elementId: "chart-memory"' in charts_js
    assert 'elementId: "chart-tensor"' in charts_js
    assert 'elementId: "chart-fp64"' in charts_js
    assert "BENCHMARK_CHARTS.some" in charts_js
    assert "getChartAssetUrl" in charts_js
    assert 'id="chart-memory-read"' in benchmarks
    assert 'id="chart-memory"' in benchmarks
    assert 'id="chart-tensor"' in benchmarks
    assert 'id="chart-fp64"' in benchmarks


def test_benchmark_charts_follow_table_filters_and_expected_units():
    charts_js = read("docs/js/charts.js")
    tables_js = read("docs/js/tables.js")

    assert "window.renderBenchmarkCharts = renderBenchmarkCharts" in charts_js
    assert 'window.renderBenchmarkCharts(filtered)' in tables_js
    assert 'testName: "memory_read_agg"' in charts_js
    assert 'testName: "memory_write_agg"' in charts_js
    assert 'testName: "tensor_virus"' in charts_js
    assert 'testName: "fp64_virus"' in charts_js
    assert 'title: "Memory Read Bandwidth"' in charts_js
    assert 'title: "FP64 Compute Throughput"' in charts_js
    assert "d.unit === expectedUnit" in charts_js
    assert "chart-empty" in charts_js


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
    assert "website_utils/update_release_page.py" in workflow
    assert "git add docs/release.md" in workflow
    assert 'git push origin HEAD:"${GITHUB_REF_NAME}"' in workflow
    assert "mkdocs gh-deploy --force" in workflow


def test_release_page_generator_is_available():
    script = read("website_utils/update_release_page.py")

    assert "def build_page" in script
    assert "docs/release.md" not in script
    assert "GitHub Releases page" in script


def test_release_page_generator_writes_latest_release(tmp_path):
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

    page = module.build_page(release, assets_dir, "saqibkh/pantheongpu_website")

    assert "## Pantheon v1.0.8 (Latest)" in page
    assert "**Release Date:** May 21, 2026" in page
    assert "#### What's Changed" in page
    assert "pantheon-1.0.8.tar.gz" in page
    assert "pantheon-1.0.8.zip" in page


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
