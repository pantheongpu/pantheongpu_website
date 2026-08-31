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


def test_site_includes_crawler_and_social_discovery_metadata():
    mkdocs = read("mkdocs.yml")
    robots = read("docs/robots.txt")
    template = read("overrides/main.html")

    assert "custom_dir: overrides" in mkdocs
    assert "Sitemap: https://pantheongpu.com/sitemap.xml" in robots
    assert 'property="og:title"' in template
    assert 'name="twitter:card"' in template
    assert '"@type": "SoftwareApplication"' in template


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


def test_charts_use_a_vendored_versioned_dependency():
    mkdocs = read("mkdocs.yml")
    apexcharts = ROOT / "docs/js/apexcharts.min.js"

    assert "- js/apexcharts.min.js" in mkdocs
    assert "cdn.jsdelivr.net/npm/apexcharts" not in mkdocs
    assert apexcharts.exists()
    assert apexcharts.stat().st_size > 500_000


def test_test_documentation_index_places_ai_category_last():
    tests_index = read("docs/tests/index.md")

    assert "## AI & ML" in tests_index
    assert tests_index.index("## AI & ML") > tests_index.index("## Interconnect & Architecture")
    assert "**Vision Encoder**](vision_encoder.md)" in tests_index


def test_all_reduce_is_documented_in_the_interconnect_navigation():
    nav = read("mkdocs.yml")
    tests_index = read("docs/tests/index.md")
    test_page = read("docs/tests/all_reduce.md")

    assert "- All-Reduce: tests/all_reduce.md" in nav
    assert "**All-Reduce**](all_reduce.md)" in tests_index
    assert "host-staged fallback" in test_page
    assert "--inject_error" in test_page


def test_performance_comparisons_are_nested_under_benchmarks_nav():
    mkdocs = read("mkdocs.yml")

    assert "  - Benchmarks:" in mkdocs
    assert "    - Live Benchmarks: benchmarks.md" in mkdocs
    assert "    - Comparisons: benchmark-comparisons.md" in mkdocs
    assert "    - Methodology: methodology.md" in mkdocs


def test_benchmarks_support_shareable_filtered_views_and_document_methodology():
    benchmarks = read("docs/benchmarks.md")
    tables_js = read("docs/js/tables.js")
    methodology = read("docs/methodology.md")

    assert 'id="benchmarkShareButton"' in benchmarks
    assert "copyBenchmarkLink" in tables_js
    assert "URLSearchParams" in tables_js
    assert "syncFilterUrl" in tables_js
    assert "trackBenchmarkEvent" in tables_js
    assert '"benchmark_export"' in tables_js
    assert '"benchmark_share"' in tables_js
    assert "# Benchmark Methodology" in methodology
    assert "Pantheon results are workload-specific measurements" in methodology
    assert "--verify" in methodology
    assert "--profile" in methodology


def test_home_offers_product_and_pilot_onboarding_paths():
    home = read("docs/index.md")
    community = read("docs/community.md")

    assert "GPU health and performance validation for AI infrastructure" in home
    assert 'href="fleet-validation/"' in home
    assert "Request a Free Fleet Validation Pilot" in home
    assert "Member of NVIDIA Inception" in home
    assert "template=benchmark-submission.yml" in community
    assert "template=hardware-regression.yml" in community


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

    assert "  - Research:" in mkdocs
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


def test_telemetry_columns_are_available_for_new_benchmark_rows():
    tables_js = read("docs/js/tables.js")
    generator = read("website_utils/generate_web_data.py")

    for key in ("gpu_util_avg", "memory_peak", "energy_wh", "clock_min", "clock_max", "thermal_rise", "throttle_time", "throughput_variance"):
        assert ('"' + key + '"') in tables_js or ('key: "' + key + '"') in tables_js
    assert '"Avg GPU Util (%)"' in generator
    assert '"Peak Memory (MiB)"' in generator
    assert '"Energy (Wh)"' in generator
    assert '"Throughput Variance (%)"' in generator


def test_throughput_variance_is_hidden_by_default():
    tables_js = read("docs/js/tables.js")

    assert '{ key: "throughput_variance", label: "Throughput Variance", visible: false }' in tables_js


def test_comparison_charts_use_two_columns_on_desktop():
    css = read("docs/css/extra.css")

    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in css
    assert "@media (max-width: 760px)" in css


def test_benchmark_ui_uses_the_single_accent_system():
    charts_js = read("docs/js/charts.js")
    tables_js = read("docs/js/tables.js")
    modern_css = read("docs/css/modern.css")

    # Charts share one validated accent hue; per-chart colors were decoration.
    assert 'color: "#' not in charts_js
    assert "--pantheon-chart-accent" in charts_js
    assert "alignBarValueLabels" in charts_js
    assert "hideOverflowingLabels: false" in charts_js
    assert "niceAxisMax" in charts_js

    # Table cells use tokened classes, not hardcoded dark-only inline colors.
    assert "benchmark-cell-version" in tables_js
    assert "benchmark-cell-test" in tables_js
    assert '"#aaa"' not in tables_js
    assert '"#1a1a1a"' not in tables_js
    assert "compactNumber" in tables_js

    # Solid controls draw from the WCAG-checked button accent in both schemes.
    assert modern_css.count("--pantheon-accent-btn:") == 2
    assert "background: var(--pantheon-accent-btn)" in modern_css


def test_release_nav_is_generated_from_the_page_not_hardcoded():
    release_nav = read("docs/js/release-nav.js")

    # A hardcoded version list goes stale on every release: it advertised
    # v1.0.16 as current, omitted newer releases, and linked to anchors that
    # no longer existed. The nav must derive its entries from the page.
    assert "querySelectorAll" in release_nav
    assert "VERSION_PATTERN" in release_nav
    assert '"v1.0.' not in release_nav
    assert "#pantheon-v10" not in release_nav


def test_no_version_pinned_selectors_in_stylesheets():
    # `html:has(#pantheon-v1013-latest)` silently stopped matching after
    # v1.0.13, leaving the release page's sidebar rules dead.
    for sheet in ("docs/css/modern.css", "docs/css/extra.css"):
        css = read(sheet)
        assert "pantheon-v10" not in css, sheet


def test_documentation_pages_keep_the_navigation_sidebar():
    # Only the landing page and the two full-width data pages hide the
    # sidebar; prose documentation pages must keep it so the layout does not
    # jump between pages.
    for page in ("docs/methodology.md", "docs/getting-started.md",
                 "docs/community.md", "docs/programs-support.md"):
        assert "hide:" not in read(page).split("# ")[0], page


def test_export_button_is_labeled_as_csv():
    benchmarks = read("docs/benchmarks.md")
    tables_js = read("docs/js/tables.js")

    assert "Export CSV" in benchmarks
    assert "Export Excel" not in benchmarks
    assert "Export to CSV" in tables_js


def test_getting_started_uses_valid_install_commands():
    getting_started = read("docs/getting-started.md")
    mkdocs = read("mkdocs.yml")

    assert "sudo pip install" not in getting_started
    assert "nvidia-cuda-toolkit (replace" not in getting_started
    assert "python3 -m venv .venv" not in getting_started
    assert "python -m pip install -r requirements.txt" not in getting_started
    # Source entrypoints belong only in the build-from-source tab. Someone who
    # installed the package must not be told to run pantheon.py. Find the
    # package block by its own markers so this does not depend on tab order,
    # which is a positioning choice and has already changed once.
    import re as _re
    package_block = _re.search(
        r'=== "Install the package"(.*?)(?=\n=== |\n## )', getting_started, _re.S)
    assert package_block, "the package-install tab should exist"
    assert "python3 pantheon.py" not in package_block.group(1)
    assert "python3 pantheon.py" in getting_started, "the source path should exist"
    assert "pantheon-tuning" not in getting_started
    assert "./pantheon --test all" not in getting_started
    assert '=== "NVIDIA CUDA"' in getting_started
    assert '=== "AMD ROCm/HIP"' in getting_started
    assert "  - pymdownx.tabbed:" in mkdocs
    assert "      alternate_style: true" in mkdocs
    assert "sudo apt-get install -y make g++" in getting_started
    assert "sudo apt-get install -y nvidia-cuda-toolkit" in getting_started
    assert "sudo apt-get install -y hipcc" in getting_started
    # The documented download must name a version that actually has a wheel
    # attached, or the install page hands the reader a 404.
    assert "VERSION=1.2.0" in getting_started
    assert 'wget "${BASE}/pantheon_gpu-${VERSION}-py3-none-any.whl"' in getting_started
    assert 'pipx install "./pantheon_gpu-${VERSION}-py3-none-any.whl"' in getting_started
    # The container and COPR channels are documented against the names they
    # actually publish under; a rename on either side must update this page.
    assert "ghcr.io/pantheongpu/pantheon:latest" in getting_started
    assert "dnf copr enable saqibkhanpantheongpu/pantheon-gpu" in getting_started
    assert "pantheongpu_${VERSION}_amd64.deb" not in getting_started, (
        "releases from 1.1.0 on ship no .deb")
    assert "pantheon --test baseline_metrics --duration 10" in getting_started
    assert "pantheon --test fp64_virus --duration 30 --gpu 0" in getting_started
    assert "PantheonGPU automatically detects CUDA, ROCm/HIP, or mock mode." in getting_started
    assert "pipx uninstall pantheon-gpu" in getting_started
    assert "sudo apt-get remove pantheongpu" in getting_started
    assert "curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh" in getting_started


def test_clean_uninstall_script_covers_package_portable_and_cache_files():
    uninstall = read("docs/uninstall.sh")
    container_test = read("tests/test_uninstall_in_container.sh")
    workflow = read(".github/workflows/ci.yml")

    assert "apt-get purge -y pantheongpu" in uninstall
    assert "dpkg --purge pantheongpu" in uninstall
    assert "/usr/local/bin/pantheon" in uninstall
    assert "rm -rf /opt/pantheongpu" in uninstall
    assert 'rm -rf "${cache_home}/pantheongpu"' in uninstall
    assert "SUDO_USER" in uninstall
    assert "uninstall_home=/root" in uninstall
    assert "apt-get remove -y pantheongpu" in container_test
    assert 'sh "${repo_root}/docs/uninstall.sh"' in container_test
    assert "docker run" not in container_test
    assert "uninstall-smoke:" in workflow


def test_all_workflow_jobs_use_self_hosted_linux_runners():
    workflow_dir = ROOT / ".github/workflows"
    workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    assert workflows
    for workflow_path in workflows:
        workflow = workflow_path.read_text(encoding="utf-8")
        runs_on_lines = [
            line.strip() for line in workflow.splitlines()
            if line.strip().startswith("runs-on:")
        ]
        assert runs_on_lines, f"{workflow_path.name} does not define a runner"
        assert all(
            line == "runs-on: [self-hosted, Linux, X64]"
            for line in runs_on_lines
        ), f"{workflow_path.name} contains a non-self-hosted runner"
        # Jobs run in a pinned container so the self-hosted runner's own
        # packages cannot drift into a build -- except where a job must run
        # outside one, as the PyPI upload does, because its publishing action
        # is a Docker action and that is not dependable inside a container.
        containers = workflow.count("container:")
        assert containers == workflow.count("image: ubuntu:24.04")
        assert containers <= len(runs_on_lines)
        if containers < len(runs_on_lines):
            assert "pypa/gh-action-pypi-publish" in workflow, (
                f"{workflow_path.name} has a job outside a container without "
                "a reason recorded here")
        assert "ubuntu-latest" not in workflow
        assert "windows-latest" not in workflow
        assert "macos-latest" not in workflow


def test_readme_pairs_install_commands_with_native_uninstall_commands():
    readme = read("README.md")

    assert 'sudo apt install "./pantheongpu_${VERSION}_amd64.deb"' in readme
    assert "sudo apt-get remove pantheongpu" in readme
    assert "sudo ./install.sh" in readme
    assert "sudo rm -f /usr/local/bin/pantheon && sudo rm -rf /opt/pantheongpu" in readme
    assert "curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh" in readme


def test_mkdocs_points_to_pantheongpu_repository():
    """The site links to the public source repository.

    This previously asserted the absence of repo_url entirely, from when the
    source was private and any link would have 404'd. The source is public now,
    so the guard is that the link points at the right repository -- not at a
    personal fork, and not at the private repository it was exported from.
    """
    mkdocs = read("mkdocs.yml")

    assert "repo_url: https://github.com/pantheongpu/pantheon\n" in mkdocs
    assert "repo_name: pantheongpu/pantheon\n" in mkdocs
    assert "saqibkh/pantheon" not in mkdocs
    assert "pantheongpu/pantheongpu\n" not in mkdocs


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


def test_brand_assets_are_sized_for_web_delivery():
    icon = ROOT / "docs/assets/icon.png"
    logo = ROOT / "docs/assets/logo.png"

    assert icon.stat().st_size < 100_000
    assert logo.stat().st_size < 1_000_000


def test_homepage_does_not_repeat_the_header_logo():
    index = read("docs/index.md")

    assert 'class="home-logo"' not in index
    assert 'src="assets/logo.png"' not in index


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

    assert 'buildCheckboxMenu("versionMenu", versions, getUrlSelections("version", versions));' in tables_js
    assert "if (!rawValue) return null;" in tables_js
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


def test_committed_toolkit_coverage_matches_database_reports(tmp_path):
    methodology_copy = tmp_path / "methodology.md"
    methodology_copy.write_text(read("docs/methodology.md"), encoding="utf-8")

    generate_web_data(output_file=tmp_path / "web_data.json", methodology_file=methodology_copy)

    assert methodology_copy.read_text(encoding="utf-8") == read("docs/methodology.md")


def test_toolkit_coverage_lists_only_hardware_backed_versions():
    methodology = read("docs/methodology.md")

    assert "<!-- TOOLKIT_COVERAGE:START -->" in methodology
    assert "## Toolkit and driver coverage" in methodology
    assert "| Platform | Toolkit | Driver versions | GPU models tested |" in methodology
    assert "| CUDA | 12.8 |" in methodology
    # No published AMD runs yet: the section must say so rather than
    # showing an empty or fabricated ROCm row.
    assert "| ROCm |" not in methodology
    assert "No AMD ROCm hardware runs have been published yet" in methodology


def test_database_reports_contain_no_host_identifiers():
    # This repository is public: benchmark reports must not disclose the
    # hostname or IP address of the machines that produced them. Pantheon
    # releases up to v1.0.16 still emit network_info, so run
    # website_utils/sanitize_reports.py after importing new reports.
    for report_path in sorted((ROOT / "database").rglob("*.json")):
        report = json.loads(report_path.read_text(encoding="utf-8"))

        assert "network_info" not in report, report_path.name
        flattened = json.dumps(report).lower()
        assert '"hostname"' not in flattened, report_path.name
        assert '"ip_address"' not in flattened, report_path.name


def test_report_sanitizer_is_available():
    sanitizer = read("website_utils/sanitize_reports.py")

    assert "network_info" in sanitizer
    assert "pantheon_report_*.json" in sanitizer


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
    assert "cmp -s /tmp/pantheon-web-data-before.json docs/assets/web_data.json" in ci
    assert "python -m mkdocs build --strict" in ci
    assert "cancel-in-progress: true" in ci
    assert "python -m pip check" in deploy
    assert "cmp -s /tmp/pantheon-web-data-before.json docs/assets/web_data.json" in deploy
    assert 'git config --global --add safe.directory "$GITHUB_WORKSPACE"' in deploy
    assert "python -m pip check" in mirror
    assert "git diff --exit-code -- docs/assets/web_data.json" in mirror
    assert 'git config --global --add safe.directory "$GITHUB_WORKSPACE"' in mirror


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
    assert "pantheongpu/pantheongpu" in workflow
    assert "repos/pantheongpu/pantheongpu/releases/latest" in workflow
    assert "repos/pantheongpu/pantheongpu/releases/tags/" in workflow
    assert "repos/pantheongpu/pantheongpu/releases/assets/" in workflow
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
    # The release page is proposed as a pull request now, so the staging and
    # the push live in the shared action rather than here.
    assert "./.github/actions/propose-to-main" in workflow
    assert "paths: docs/release.md" in workflow
    assert "git push" not in workflow
    assert "cache: pip" not in workflow
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
        "pantheongpu/pantheongpu_website",
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


def test_release_page_uses_version_navigation_without_a_second_content_column():
    release = read("docs/release.md")
    css = read("docs/css/modern.css")
    release_nav = read("docs/js/release-nav.js")

    latest = re.search(r"^## Pantheon (v[\d.]+) \(Latest\)$", release, re.MULTILINE)

    assert latest is not None
    latest_tag = latest.group(1)
    latest_version = latest_tag.removeprefix("v")
    assert release.count("(Latest)") == 1
    # Assert the latest release offers downloads, not that it offers one
    # particular packaging format: 1.1.0 replaced the Debian package with a
    # wheel, and pinning the old shape here only dated the test.
    latest_section = release.split(f"## Pantheon {latest_tag}", 1)[1].split("\n---", 1)[0]
    assert f"releases/download/{latest_tag}/" in latest_section
    assert f"Pantheon {latest_tag} Checksums" in latest_section
    assert latest_version in latest_section
    assert "## Pantheon v1.0.8" in release
    assert "## Pantheon v1.0.8 (Latest)" not in release
    assert "v1.0.9" not in release
    assert "## Pantheon v1.0.7" in release
    assert "Download stable releases" in release
    assert "TarFile" not in release
    assert "ZipFile" not in release
    assert 'class="release-version-nav"' not in release
    assert ".release-page" not in css
    assert ".md-sidebar--primary .release-version-nav" in css
    # The nav is generated from the page's release headings. It previously
    # hardcoded a version list, and these assertions pinned that stale list in
    # place, which is why the drift went unnoticed for several releases.
    assert "release-version-nav" in release_nav
    assert ".md-typeset h2[id]" in release_nav


def test_readme_documents_release_mirroring_secret():
    readme = read("README.md")

    assert "Mirror Pantheon Releases" in readme
    assert "PANTHEON_SOURCE_REPO_TOKEN" in readme
    assert "PANTHEON_WEBSITE_RELEASE_TOKEN" in readme
    assert "Public Binary Downloads" in readme
    assert "VERSION=1.0.18" in readme
    assert "pantheon --test baseline_metrics --duration 10" in readme
    assert "tag like `v1.0.18`" in readme
    assert "tag like `v1.0.8`" not in readme
    assert "`*.deb`" in readme
    assert "repository dispatch" in readme
    assert "private source repository paths" in readme
    assert "public website repo" in readme
    assert "pantheongpu/pantheongpu" in readme
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


def test_no_report_filename_carries_a_host_identifier():
    """This repository is public. A host IP in a filename is as much a leak as
    one in the file body, and the body scrub never looked at names."""
    import re
    db = Path(__file__).resolve().parent.parent / "database"
    ip = re.compile(r"(?<!\d)\d{1,3}([._]\d{1,3}){3}(?!\d)")
    def leaks(name):
        m = ip.search(name)
        if m and all(0 <= int(p) <= 255 for p in re.split(r"[._]", m.group(0))):
            return True
        return "InternalHost" in name
    offenders = sorted(p.name for p in db.rglob("*.json") if leaks(p.name))
    assert offenders == [], (
        "Report filenames still carry a host identifier. Run:\n"
        "    python3 website_utils/sanitize_reports.py\n"
        f"and commit the result. First offenders: {offenders[:5]}")


def test_host_free_name_preserves_model_and_timestamp():
    import importlib.util
    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "sr", root / "website_utils" / "sanitize_reports.py")
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)

    assert sr.host_free_name(
        "a100_129.153.20.126_pantheon_report_20260826-164123_0001_memory_read_gpu0.json"
    ) == "a100_pantheon_report_20260826-164123_0001_memory_read_gpu0.json"
    assert sr.host_free_name(
        "a100_129_153_20_126_cache_lat_191356_gpu0.json"
    ) == "a100_cache_lat_191356_gpu0.json"
    # An already-clean name must be left exactly alone.
    clean = "a100_pantheon_report_20260826-164123_0001_memory_read_gpu0.json"
    assert sr.host_free_name(clean) == clean


def test_published_uuids_match_the_reports():
    """The id shown on the site must be findable in database/.

    GPU UUIDs are published verbatim by the owner's decision (2026-08-31):
    they identify a card, not a host, and hashing them left the site showing
    ids that matched nothing in the reports. Every published uuid must appear
    exactly as some report's uuid. Reports imported while the pipeline hashed
    ids only have the pseudonym left, so those match on the pseudonym itself.
    """
    root = Path(__file__).resolve().parent.parent
    data = json.loads((root / "docs" / "assets" / "web_data.json").read_text())

    report_uuids = set()
    for path in (root / "database").rglob("*.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for gpu in report.get("gpu_static_info") or []:
            if isinstance(gpu, dict) and gpu.get("uuid"):
                report_uuids.add(str(gpu["uuid"]).strip())

    orphans = sorted({
        row["uuid"] for row in data
        if isinstance(row.get("uuid"), str)
        and row["uuid"] != "Unknown"
        and row["uuid"] not in report_uuids
    })
    assert orphans == [], f"published uuids not found in any report: {orphans[:3]}"


def test_sanitizer_preserves_gpu_identity(tmp_path):
    """Only host identifiers are scrubbed; GPU uuid and serial pass verbatim.

    The uuid keys per-card identity and history across the dashboards, and the
    owner decided (2026-08-31) that uuid and serial are published as recorded.
    A sanitizer change that hashes, redacts or renames either would silently
    split a card's history on the next import, so pin the contract here.
    """
    import importlib.util
    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "sr", root / "website_utils" / "sanitize_reports.py")
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)

    report = tmp_path / "pantheon_report_20260831-000000.json"
    report.write_text(json.dumps({
        "pantheon_version": "1.1.0",
        "network_info": {"hostname": "bench-host", "ip_address": "10.0.0.5"},
        "gpu_static_info": [{
            "name": "Example GPU",
            "uuid": "GPU-58e902aa-1111-2222-3333-444444444444",
            "serial": "1650123456789",
        }],
        "test_results": [],
    }, indent=4) + "\n")

    assert sr.sanitize_report(report) is True
    data = json.loads(report.read_text())
    assert "network_info" not in data, "host identifiers must still be scrubbed"
    gpu = data["gpu_static_info"][0]
    assert gpu["uuid"] == "GPU-58e902aa-1111-2222-3333-444444444444"
    assert gpu["serial"] == "1650123456789"


def test_best_run_grouping_does_not_cross_versions_or_units():
    """The best-run view must not compare numbers that are not comparable.

    Grouping only by GPU and workload let a workload whose metric changed
    between releases show whichever version produced the larger figure, and let
    a run recorded in Watts out-rank the same workload's TFLOPS runs purely
    because the number was bigger. On the published dataset that affected 151
    of 580 groups, 33 of which were being won by a wattage reading.

    generate_web_data.py already keys on version for the same reason; this
    keeps the client side consistent with it.
    """
    tables = read("docs/js/tables.js")
    grouping = re.search(r"function getBestRunsOnly\(data\)\s*\{(.*?)\n\}", tables, re.S)
    assert grouping, "getBestRunsOnly should exist"
    body = grouping.group(1)
    key_line = re.search(r"const key = `([^`]+)`", body)
    assert key_line, "the grouping key should be a template literal"
    key = key_line.group(1)
    for field in ("row.gpu", "row.test", "row.version", "row.unit"):
        assert field in key, f"the best-run key must include {field}: {key}"


def test_brand_marks_have_no_white_frame():
    """The header logo shipped inside an opaque white frame.

    icon.png was a 77px mark centred in a 128px canvas, the surrounding 26px
    filled with opaque white, and favicon.png padded the same way. The site
    header is the page surface, so on the dark scheme that frame rendered as a
    white box around the logo.
    """
    from PIL import Image

    for name in ("icon.png", "favicon.png"):
        image = Image.open(ROOT / "docs" / "assets" / name).convert("RGBA")
        width, height = image.size
        pixels = image.load()

        border = [pixels[x, y]
                  for x in range(width) for y in (0, height - 1)]
        border += [pixels[x, y]
                   for y in range(height) for x in (0, width - 1)]

        framed = [p for p in border if p[3] > 200 and min(p[:3]) > 235]
        assert not framed, (
            f"{name} has {len(framed)} opaque near-white border pixels; the "
            "mark should reach the edge of its canvas")


def test_social_image_has_no_empty_band():
    """logo.png carried 131px of fully transparent rows below the artwork.

    Social platforms flatten transparency, so that dead space rendered as a
    bar across the bottom of every link preview.
    """
    from PIL import Image

    image = Image.open(ROOT / "docs" / "assets" / "logo.png").convert("RGBA")
    assert image.getbbox() == (0, 0, *image.size), (
        "logo.png has fully transparent rows or columns at its edges")
def test_release_page_lists_the_wheel():
    """The wheel is the install path a 1.1.0 reader needs.

    The generator filtered assets through an allowlist of .deb/.tar.gz/.zip,
    so the wheel was dropped from the download table without any error --
    the release page simply did not offer the artifact the release exists to
    deliver.
    """
    release_page = read("docs/release.md")
    assert "pantheon_gpu-1.1.0-py3-none-any.whl" in release_page
    assert "`.whl`" in release_page
    # Two different .tar.gz files ship in the same release; identical labels
    # would leave a reader choosing between two rows claiming to be the same.
    assert "Pantheon v1.1.0 Source Tarball" in release_page
    assert "Pantheon v1.1.0 Source Distribution" in release_page
    assert release_page.count("Pantheon v1.1.0 Tarball") == 0


def test_release_workflow_updates_and_deploys_the_release_page():
    """Publishing a release has to leave docs/release.md describing it.

    The Release workflow published 1.1.0 without touching the page, so the
    newest release sat on the releases tab while the site kept describing the
    previous one. The page was only correct because it was regenerated by
    hand afterwards.
    """
    workflow = read(".github/workflows/release.yml")

    assert "website_utils/update_release_page.py" in workflow, (
        "publishing must regenerate the release page")
    # The page is proposed as a pull request rather than pushed, so that main
    # can be protected; the push itself now lives in the shared action.
    assert "./.github/actions/propose-to-main" in workflow

    # A push authenticated with GITHUB_TOKEN does not start another workflow,
    # so without an explicit dispatch the regenerated page never deploys.
    assert "actions/workflows/deploy.yml/dispatches" in workflow
    assert "actions: write" in workflow

    # The dry run renders the page too. The generator once dropped the wheel
    # from the download table silently, which a build-only dry run would miss.
    assert "dry-run-release.md" in workflow
    assert "the release page would not list" in workflow


def _published_rows():
    return json.loads(read("docs/assets/web_data.json"))


def test_published_data_never_reports_an_absent_sensor_as_zero():
    """A sensor that was never read is not a reading of zero.

    Pantheon recorded absent sensors as 0 until v1.1.0, and the generator
    defaulted the same fields to 0 when the key was missing. The published
    dataset therefore asserted measurements nobody took: 0 mV core voltage on
    every one of 1317 rows, and 0 C memory temperature on 1234 of them.
    """
    from website_utils.generate_web_data import ABSENT_WHEN_ZERO

    offenders = {}
    for row in _published_rows():
        for field in ABSENT_WHEN_ZERO:
            value = row.get(field)
            if str(value) in ("0", "0.0"):
                offenders.setdefault(field, 0)
                offenders[field] += 1

    assert not offenders, f"absent sensors published as zero: {offenders}"


def test_published_data_keeps_measured_zeros():
    """The opposite failure: discarding a real result because it is zero.

    A throttle time of 0s means the GPU never throttled, which is the good
    outcome and the common one. It must stay a number.
    """
    rows = _published_rows()
    measured_zero = [r for r in rows if str(r.get("throttle_time")) in ("0", "0.0")]

    assert measured_zero, "expected runs that never throttled"
    assert not any(r.get("throttle_time") == "N/A" for r in rows), (
        "throttle_time must not be reported as unknown")

    tables = read("docs/js/tables.js")
    assert 'value === 0 || value === "0"' not in tables, (
        "formatMetric must not treat every zero as a missing value")


def test_published_data_carries_no_retired_metric_units():
    """Ten AI workloads shared one kernel before v1.0.19.

    Six compiled to byte-identical SASS, yet each published its own invented
    unit as though it measured something distinct. The throughput numbers are
    real; the metric names describe work that never happened.
    """
    from website_utils.generate_web_data import RETIRED_AI_UNITS

    published = {row.get("unit") for row in _published_rows()}
    leaked = published & RETIRED_AI_UNITS

    assert not leaked, f"retired metric units on the leaderboard: {sorted(leaked)}"
    # scheduler and atomic_virus were never part of that change.
    assert "KIPS" in published and "MAPS" in published
def test_no_workflow_pushes_straight_to_main():
    """Automation must go through a pull request, like a person does.

    main cannot be protected while workflows push to it: a ruleset rejects
    them, and on a free organisation GitHub Actions cannot be granted a
    bypass on a repository ruleset. Routing automation through pull requests
    is what makes protecting the branch possible at all.
    """
    import glob

    # Pushing to a pull request's own branch is fine -- that is how the
    # sanitizer scrubs a sweep in place. Only main is off limits.
    offenders = [
        Path(path).name
        for path in sorted(glob.glob(str(ROOT / ".github" / "workflows" / "*.yml")))
        if "HEAD:main" in Path(path).read_text(encoding="utf-8")
        or "push origin main" in Path(path).read_text(encoding="utf-8")
    ]

    assert not offenders, (
        f"these workflows push to main directly instead of using the "
        f"propose-to-main action: {offenders}")


def test_writers_to_main_use_the_pull_request_action():
    action = read(".github/actions/propose-to-main/action.yml")

    # The fallback exists so this can merge before the token is created, but
    # it has to announce itself rather than look healthy.
    assert "::warning::No bot token configured" in action

    for name in ("sanitize-imports", "release", "mirror-pantheon-release"):
        workflow = read(f".github/workflows/{name}.yml")
        assert "./.github/actions/propose-to-main" in workflow, (
            f"{name}.yml still writes to main on its own")
        assert "PANTHEON_BOT_TOKEN" in workflow

    # release and mirror build in a workspace holding the Pantheon checkout,
    # build venvs and downloaded assets, so they stage one file rather than
    # everything -- otherwise the whole build would be committed.
    for name in ("release", "mirror-pantheon-release"):
        assert "paths: docs/release.md" in read(f".github/workflows/{name}.yml")


def test_gpu_identity_is_defined_once_and_does_not_rehash():
    """The published GPU id must match the id in the reports.

    The sanitizer and the generator each carried their own copy of the
    identity function once, and the copies drifted: every id was hashed twice
    on its way to the leaderboard, so a card with 152 reports could not be
    found under the id those reports carry. The identity is now the UUID
    verbatim (owner decision, 2026-08-31), and it must stay defined once in
    website_utils.gpu_identity so it cannot drift again.
    """
    from website_utils.gpu_identity import public_gpu_id
    from website_utils.generate_web_data import public_gpu_id as generator_id
    from website_utils.sanitize_reports import public_gpu_id as sanitizer_id

    raw = "GPU-9da9ed85-1507-6d1d-da6f-f630d9ab14dc"

    assert public_gpu_id(raw) == raw, "the published id is the uuid, verbatim"
    assert generator_id(raw) == sanitizer_id(raw) == raw
    # Applying it twice must be a no-op, or a card splits in two on re-import.
    assert public_gpu_id(public_gpu_id(raw)) == raw
    # Legacy pseudonyms from the era the pipeline hashed ids pass unchanged.
    legacy = "GPU-3b7b76365f4d"
    assert public_gpu_id(legacy) == legacy

    # Neither module may grow its own identity hashing again. The salt was the
    # marker of a private hashing copy: sanitize_reports also hashes file
    # contents for filenames, which is unrelated.
    for module in ("generate_web_data", "sanitize_reports"):
        source = read(f"website_utils/{module}.py")
        assert "PUBLIC_ID_SALT" not in source, (
            f"{module} must use website_utils.gpu_identity, not hash its own")


def test_published_ids_match_the_reports():
    published = {row["uuid"] for row in _published_rows()}

    stored = set()
    for path in (ROOT / "database").glob("pantheon_report_*.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        info = report.get("gpu_static_info")
        if isinstance(info, list):
            info = info[0] if info else {}
        identifier = str((info or {}).get("uuid", "")).strip()
        if identifier.startswith("GPU-") and len(identifier) == 16:
            stored.add(identifier)

    assert stored, "expected pseudonymised ids in the reports"

    # A card is legitimately absent when every one of its runs was excluded --
    # an incomplete run, a multi-GPU workload, or a retired metric. Anything
    # else means the id does not join, which is the bug this guards.
    from website_utils.generate_web_data import (
        PUBLIC_EXCLUDED_TESTS, RETIRED_AI_UNITS)

    publishable = set()
    for path in (ROOT / "database").glob("*pantheon_report_*.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if report.get("run_status") not in (None, "complete"):
            continue
        info = report.get("gpu_static_info")
        if isinstance(info, list):
            info = info[0] if info else {}
        identifier = str((info or {}).get("uuid", "")).strip()
        results = report.get("test_results", [])
        if isinstance(results, dict):
            results = list(results.values())
        for result in results:
            if not isinstance(result, dict):
                continue
            name = str(result.get("Test Name", "")).lower()
            if name and name not in PUBLIC_EXCLUDED_TESTS \
                    and str(result.get("Unit")) not in RETIRED_AI_UNITS:
                publishable.add(identifier)

    unexplained = (stored & publishable) - published
    assert not unexplained, (
        f"cards with publishable runs missing from the site: {sorted(unexplained)}")


def test_per_card_history_keeps_every_run():
    """The leaderboard drops the runs a degradation view needs.

    It keeps the best run per card, workload and release, so a card that
    slows down is invisible there: the good early run wins and later, worse
    runs are discarded.
    """
    history = json.loads(read("docs/assets/gpu_history.json"))
    leaderboard = _published_rows()

    assert history, "expected a per-card history dataset"
    assert not any("_kind" in run for run in history), (
        "provenance is internal to the generator and must not be published")

    series = {}
    for run in history:
        series.setdefault((run["card"], run["test"]), []).append(run)
    repeated = [runs for runs in series.values() if len(runs) > 1]
    assert repeated, "history must retain more than one run per card and workload"

    # Cards without a UUID must not collapse into a single shared series, or
    # the chart shows unrelated hardware as one card swinging wildly.
    assert "Unknown" not in {run["card"] for run in history}

    published_tests = {row["test"] for row in leaderboard}
    assert {run["test"] for run in history} <= published_tests, (
        "history must not surface workloads the leaderboard excludes")


def test_history_collapses_the_files_one_run_writes():
    """A single run writes a per-test record and a summary repeating it."""
    from website_utils.generate_web_data import dedupe_history

    shared = {"card": "GPU-abc123abc123", "test": "memory_read",
              "version": "1.1.0", "unit": "GB/s", "score": 327.29}
    runs = [
        dict(shared, date="2026-08-30 17:02:24", _kind="completed_workload"),
        dict(shared, date="2026-08-30 17:07:55", _kind=None),
    ]
    kept = dedupe_history(runs)
    assert len(kept) == 1
    assert kept[0]["date"] == "2026-08-30 17:02:24", (
        "the per-test record is when the run happened; the summary repeats it")

    # Two runs that merely score alike are different measurements.
    distinct = dedupe_history([
        dict(shared, date="2026-08-01 10:00:00", _kind="completed_workload"),
        dict(shared, date="2026-08-20 10:00:00", _kind="completed_workload"),
    ])
    assert len(distinct) == 2


def test_history_page_is_reachable_and_wired():
    mkdocs = read("mkdocs.yml")
    assert "js/gpu-history.js" in mkdocs
    assert "gpu-history.md" in mkdocs, "the page must be in the nav"

    page = read("docs/gpu-history.md")
    for element in ("gpuHistoryChart", "gpuHistoryCard", "gpuHistoryTest"):
        assert element in page
        assert element in read("docs/js/gpu-history.js")


def test_sanitizer_also_runs_on_pull_requests():
    """A sweep arriving on a branch was bypassing the sanitizer entirely.

    It only fired on pushes to main, so 55 filenames carrying two hosts' IP
    addresses reached a pull request, and every new commit re-broke CI faster
    than they could be scrubbed by hand.
    """
    workflow = read(".github/workflows/sanitize-imports.yml")

    assert "pull_request:" in workflow
    assert '- "database/**"' in workflow, "only report imports need scrubbing"

    # The default checkout on a pull request is a detached merge commit, which
    # cannot be pushed back.
    assert "github.event.pull_request.head.ref" in workflow
    assert 'git push origin "HEAD:refs/heads/${HEAD_REF}"' in workflow

    # A fork's token is read-only, so there is nothing to push back with.
    assert "github.event.pull_request.head.repo.full_name == github.repository" in workflow

    # Without the token the push lands but the failed checks do not re-run,
    # leaving a red pull request on a clean tree. Say so.
    assert "the failed checks will not re-run on their own" in workflow

    # main keeps going through the pull-request action, not a direct push.
    assert "./.github/actions/propose-to-main" in workflow


def test_container_workflows_declare_bash():
    """`set -euo pipefail` needs bash, and container jobs default to sh.

    The self-hosted runner gives container jobs `sh`, which has no pipefail,
    so such a step exits 2 before running any of its own logic. That silently
    disabled the nightly storage prune for two nights and killed the first
    release dry run at its first step.
    """
    import glob
    import re

    offenders = []
    for path in sorted(glob.glob(str(ROOT / ".github" / "workflows" / "*.yml"))):
        body = Path(path).read_text(encoding="utf-8")
        if "image:" not in body or "pipefail" not in body:
            continue
        if not re.search(r"(?m)^\s*shell: bash\s*$", body):
            offenders.append(Path(path).name)

    assert not offenders, (
        f"container workflows using pipefail without declaring bash: {offenders}")


def test_wheel_does_not_require_a_spreadsheet_writer():
    """openpyxl reaches one call, which already tolerates its absence.

    pantheon.py wraps df.to_excel in try/except and warns, so a machine that
    only reads the CSV and JSON written beside it should not be made to
    install a spreadsheet writer.
    """
    builder = read("packaging/wheel/build_wheel.py")

    dependencies = builder.split("dependencies = [", 1)[1].split("]", 1)[0]
    assert "openpyxl" not in dependencies, "openpyxl belongs in an extra"
    assert '"pandas"' in dependencies, (
        "pandas is imported at module scope and used throughout; it is not "
        "optional without a refactor")

    assert "[project.optional-dependencies]" in builder
    assert 'reports = ["openpyxl"]' in builder


def test_wheel_offers_the_project_named_command():
    """"pantheon" is a taken name in Debian and Ubuntu.

    elementary OS ships a desktop environment called Pantheon, so those
    archives already carry a family of pantheon-* packages. Offering
    pantheon-gpu as well lets a distribution install only that one.
    """
    builder = read("packaging/wheel/build_wheel.py")
    scripts = builder.split("[project.scripts]", 1)[1].split("[tool.setuptools]", 1)[0]

    assert "pantheon = " in scripts
    assert "pantheon-gpu = " in scripts


def test_pypi_upload_is_on_by_default_and_runs_outside_the_container():
    """The publishing action is a Docker action.

    The release job runs inside a container, where that is not dependable, so
    the upload is a separate job. Since v1.2.0 a trusted publisher is
    configured on PyPI, so the upload rides along with every release by
    default; the input stays so a GitHub-and-apt-only release is still one
    untick away. PyPI versions are immutable, which is why the upload must
    skip duplicates: a release re-run would otherwise fail on the last step
    after everything else succeeded.
    """
    workflow = read(".github/workflows/release.yml")

    assert "publish_pypi:" in workflow
    pypi_input = workflow.split("publish_pypi:", 1)[1].split("type: boolean", 1)[0]
    assert "default: true" in pypi_input
    assert "id-token: write" in workflow

    publish = workflow.split("publish-pypi:", 1)[1]
    assert "needs: release" in publish
    assert "container:" not in publish, (
        "a Docker action cannot be relied on inside a container job")
    assert "pypa/gh-action-pypi-publish" in publish
    assert "skip-existing: true" in publish


def test_debian_package_declares_honest_dependencies():
    """pandas and numpy are imported at module scope; pynvml and psutil are not.

    pantheon.py imports pynvml and psutil inside try/except and degrades when
    they are absent, so making them hard dependencies would force them onto
    installs that do not need them.
    """
    builder = read("packaging/deb/build_deb.py")

    depends = builder.split("Depends:", 1)[1].split("\n", 1)[0]
    assert "python3-numpy" in depends and "python3-pandas" in depends
    assert "g++" in depends and "make" in depends, (
        "the workloads compile on first run")
    assert "pynvml" not in depends and "psutil" not in depends

    recommends = builder.split("Recommends:", 1)[1].split("\n", 1)[0]
    assert "python3-pynvml" in recommends and "python3-psutil" in recommends
    assert "python3-openpyxl" in recommends

    # CUDA is not in Debian main, so the package cannot be in main either.
    assert "Section: contrib/utils" in builder


def test_apt_repository_is_signed_when_a_key_exists():
    """apt refuses an unsigned repository unless the user opts in."""
    builder = read("packaging/apt/build_repo.py")
    workflow = read(".github/workflows/release.yml")

    assert "InRelease" in builder and "Release.gpg" in builder
    assert "pantheon-archive-keyring.asc" in builder
    # A missing key must be loud, not silently produce something unusable.
    assert "unsigned" in builder
    assert "PANTHEON_APT_SIGNING_KEY" in workflow
    assert "the apt repository" in workflow

    # The repository is committed with the release page, so it reaches the site.
    assert "paths: docs/release.md docs/apt" in workflow


def test_release_ships_and_documents_the_debian_package():
    workflow = read(".github/workflows/release.yml")
    assert "packaging/deb/build_deb.py" in workflow
    assert "dist/pantheon-gpu_${{ env.VERSION }}_all.deb" in workflow
    # Built on dry runs too, so a broken package stops the release.
    build_step = workflow.split("Build the Debian package", 1)[1].split("- name:", 1)[0]
    assert "inputs.dry_run" not in build_step

    getting_started = read("docs/getting-started.md")
    assert 'signed-by=/usr/share/keyrings/pantheon-archive-keyring.asc' in getting_started
    assert "sudo apt install pantheon-gpu" in getting_started

    # The publishing step is skipped on a dry run, so the dry run indexes the
    # package itself. Otherwise the first apt indexing would be a real release.
    summary = workflow.split("Dry run summary", 1)[1]
    assert "packaging/apt/build_repo.py" in summary
    assert "the apt index would not list pantheon-gpu" in summary


def test_aur_package_builds_from_the_sdist():
    """The source repository is not a Python package.

    It carries no pyproject.toml -- the packaging metadata is generated at
    release time -- so a PKGBUILD pointed at a git tag cannot build it.
    """
    pkgbuild = read("packaging/aur/PKGBUILD")
    assert "pantheon_gpu-${pkgver}.tar.gz" in pkgbuild
    assert "archive/refs/tags" not in pkgbuild, "a git tag has no build system"
    assert "python-pandas" in pkgbuild and "python-numpy" in pkgbuild
    assert "python-pynvml" in pkgbuild.split("optdepends", 1)[1]


def test_release_publishes_container_images():
    """The image exists so a user never installs a toolkit.

    It must be built from the published wheel -- the bytes users download,
    not a build artifact -- smoke-tested before any push, and pushed under
    the version tag as well as latest. The job drives the host's docker
    daemon, so it cannot run in a container, and it checks out on the shared
    self-hosted workspace, so it reclaims root-owned leftovers first.
    """
    workflow = read(".github/workflows/release.yml")
    dockerfile = read("packaging/docker/Dockerfile.cuda")

    assert "publish-containers:" in workflow
    job = workflow.split("publish-containers:", 1)[1]
    assert "packages: write" in job
    assert "releases/download" in job, "build from the published wheel"
    assert "--platform mock --test baseline_metrics" in job
    assert job.index("docker run --rm") < job.index("docker push"), (
        "the image must be smoke-tested before anything is pushed")
    assert "chown -R" in job
    assert "ghcr.io/pantheongpu/pantheon" in workflow

    assert "FROM nvidia/cuda:" in dockerfile
    assert 'ENTRYPOINT ["pantheon"]' in dockerfile
    assert "--no-install-recommends" in dockerfile


def test_release_notes_list_what_changed():
    """Every release must say what changed.

    The notes are generated from the source repository's log since the
    previous tag -- the commit subjects there are written to carry exactly
    this weight -- so nobody has to remember a hand-kept changelog. A shallow
    checkout cannot see the previous tag and would silently produce empty
    notes, and a step gated on dry_run would let a broken changelog reach a
    real release unrehearsed.
    """
    workflow = read(".github/workflows/release.yml")

    checkout = workflow.split("Check out Pantheon source", 1)[1].split("- name:", 1)[0]
    assert "fetch-depth: 0" in checkout

    notes = workflow.split("Write the release notes", 1)[1].split("- name:", 1)[0]
    assert "Changes since" in notes
    assert "--sort=-v:refname" in notes
    assert "grep -v '^- Release '" in notes, "the version-bump commit is noise"
    assert "inputs.dry_run" not in notes

    publish = workflow.split("Publish release", 1)[1].split("- name:", 1)[0]
    assert "body_path: release-body.md" in publish
