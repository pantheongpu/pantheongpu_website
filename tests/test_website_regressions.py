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

    assert 'document.getElementById("chart-memory")' in charts_js
    assert 'document.getElementById("chart-tensor")' in charts_js
    assert "getChartAssetUrl" in charts_js
    assert 'id="chart-memory"' in benchmarks
    assert 'id="chart-tensor"' in benchmarks


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
