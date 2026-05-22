let benchmarkCharts = {};
const BENCHMARK_CHARTS = [
    { testName: "memory_read_agg", elementId: "chart-memory-read", title: "Memory Read Bandwidth", unit: "GB/s", color: "#2563eb" },
    { testName: "memory_write_agg", elementId: "chart-memory", title: "Memory Write Bandwidth", unit: "GB/s", color: "#0f9f6e" },
    { testName: "pcie_bandwidth", elementId: "chart-pcie", title: "PCIe Bandwidth", unit: "GB/s", color: "#7c3aed" },
    { testName: "tensor_virus", elementId: "chart-tensor", title: "Tensor Compute Throughput", unit: "TFLOPS", color: "#db2777" },
    { testName: "fp64_virus", elementId: "chart-fp64", title: "FP64 Compute Throughput", unit: "TFLOPS", color: "#ea580c" },
    { testName: "int_virus", elementId: "chart-integer", title: "Integer Compute Throughput", unit: "TOPS", color: "#ca8a04" },
    { testName: "mma_virus", elementId: "chart-mma", title: "MMA Compute Throughput", unit: "TFLOPS", color: "#16a34a" },
    { testName: "rt_virus", elementId: "chart-rt", title: "Ray Tracing Throughput", unit: "GRays/s", color: "#4f46e5" },
    { testName: "scheduler", elementId: "chart-scheduler", title: "Scheduler Throughput", unit: "KIPS", color: "#64748b" },
];

document.addEventListener("DOMContentLoaded", function () {
    if (!BENCHMARK_CHARTS.some(chart => document.getElementById(chart.elementId))) return;
    if (document.getElementById("benchmarkTable")) return;

    const dataUrl = getChartAssetUrl("web_data.json");

    fetch(dataUrl)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status} loading ${dataUrl}`);
            return response.json();
        })
        .then(data => {
            renderBenchmarkCharts(data);
        })
        .catch(err => console.error("Error loading benchmark data:", err));
});

function getChartAssetUrl(fileName) {
    const script = document.currentScript || Array.from(document.scripts).find(s => s.src && s.src.includes("/js/charts.js"));
    if (script && script.src) {
        return new URL(`../assets/${fileName}`, script.src).href;
    }
    return new URL(`assets/${fileName}`, document.baseURI).href;
}

function renderBenchmarkCharts(data) {
    BENCHMARK_CHARTS.forEach(chart => {
        renderChart(data, chart);
    });
}

function getChartScore(row) {
    const score = Number(row.score);
    if (Number.isFinite(score) && score > 0) return score;

    const throughput = Number(row.throughput);
    if (Number.isFinite(throughput) && throughput > 0) return throughput;

    return null;
}

function formatChartValue(value) {
    if (value >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
    if (value >= 100) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function getChartTheme() {
    const scheme = document.documentElement.getAttribute("data-md-color-scheme");
    const dark = scheme !== "default";
    return {
        mode: dark ? "dark" : "light",
        foreground: dark ? "#e5e7eb" : "#111827",
        muted: dark ? "#9ca3af" : "#4b5563",
        grid: dark ? "#27272a" : "#e5e7eb",
        tooltipTheme: dark ? "dark" : "light",
    };
}

function renderChart(rawData, chartConfig) {
    const { testName, elementId, title, unit: expectedUnit, color } = chartConfig;
    const element = document.getElementById(elementId);
    if (!element) return;
    const container = element.closest(".chart-container");

    const filtered = rawData.filter(d => d.test === testName && (!expectedUnit || d.unit === expectedUnit));

    const bestScores = {};
    filtered.forEach(r => {
        const score = getChartScore(r);
        if (score === null) return;

        if (!bestScores[r.gpu] || score > bestScores[r.gpu]) {
            bestScores[r.gpu] = score;
        }
    });

    const sortedScores = Object.entries(bestScores)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12);
    const categories = sortedScores.map(([gpu]) => gpu);
    const seriesData = sortedScores.map(([, score]) => Number(score.toFixed(2)));
    const unit = expectedUnit || "";
    const theme = getChartTheme();

    if (benchmarkCharts[elementId]) {
        benchmarkCharts[elementId].destroy();
        delete benchmarkCharts[elementId];
    }

    if (categories.length === 0) {
        if (container) container.classList.add("chart-container--empty");
        element.innerHTML = `<p class="chart-empty">No ${title.toLowerCase()} data matches the current filters.</p>`;
        return;
    }

    if (container) container.classList.remove("chart-container--empty");
    element.innerHTML = "";

    const options = {
        chart: {
            type: 'bar',
            height: Math.max(320, categories.length * 34 + 96),
            background: 'transparent',
            foreColor: theme.foreground,
            fontFamily: 'Roboto, sans-serif',
            toolbar: { show: false },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 450,
            },
        },
        theme: { mode: theme.mode },
        series: [{
            name: unit ? `${title} (${unit})` : title,
            data: seriesData
        }],
        dataLabels: {
            enabled: false,
        },
        xaxis: {
            categories: categories,
            labels: {
                formatter: value => formatChartValue(Number(value)),
                style: { colors: theme.muted },
            },
            axisBorder: { show: false },
            axisTicks: { show: false },
        },
        yaxis: {
            labels: {
                maxWidth: 180,
                style: { colors: theme.foreground, fontWeight: 600 },
            }
        },
        title: {
            text: unit ? `${title} (${unit})` : title,
            align: 'left',
            margin: 18,
            style: {
                color: theme.foreground,
                fontSize: '17px',
                fontWeight: 800,
            },
        },
        subtitle: {
            text: 'Best reported result per GPU',
            align: 'left',
            margin: 14,
            style: {
                color: theme.muted,
                fontSize: '12px',
            },
        },
        colors: [color || '#2563eb'],
        plotOptions: {
            bar: {
                borderRadius: 5,
                borderRadiusApplication: 'end',
                barHeight: '68%',
                horizontal: true,
            }
        },
        grid: {
            borderColor: theme.grid,
            strokeDashArray: 4,
            xaxis: { lines: { show: true } },
            yaxis: { lines: { show: false } },
            padding: { top: 0, right: 14, bottom: 0, left: 4 },
        },
        tooltip: {
            theme: theme.tooltipTheme,
            y: {
                formatter: value => `${formatChartValue(value)}${unit ? ` ${unit}` : ""}`,
            },
        },
        states: {
            hover: { filter: { type: 'lighten', value: 0.08 } },
            active: { filter: { type: 'none' } },
        },
    };

    const chart = new ApexCharts(element, options);
    benchmarkCharts[elementId] = chart;
    chart.render();
}

window.renderBenchmarkCharts = renderBenchmarkCharts;
