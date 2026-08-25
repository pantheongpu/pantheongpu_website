let benchmarkCharts = {};
let lastChartData = [];
// All comparison charts share one validated accent hue (see getChartTheme);
// per-chart colors would decorate rather than encode anything.
const BENCHMARK_CHARTS = [
    { testName: "memory_read_agg", elementId: "chart-memory-read", title: "Memory Read Bandwidth", unit: "GB/s" },
    { testName: "memory_write_agg", elementId: "chart-memory", title: "Memory Write Bandwidth", unit: "GB/s" },
    { testName: "pcie_bandwidth", elementId: "chart-pcie", title: "PCIe Bandwidth", unit: "GB/s" },
    { testName: "tensor_virus", elementId: "chart-tensor", title: "Tensor Compute Throughput", unit: "TFLOPS" },
    { testName: "fp64_virus", elementId: "chart-fp64", title: "FP64 Compute Throughput", unit: "TFLOPS" },
    { testName: "int_virus", elementId: "chart-integer", title: "Integer Compute Throughput", unit: "TOPS" },
    { testName: "mma_virus", elementId: "chart-mma", title: "MMA Compute Throughput", unit: "TFLOPS" },
    { testName: "rt_virus", elementId: "chart-rt", title: "Ray Tracing Throughput", unit: "GRays/s" },
    { testName: "scheduler", elementId: "chart-scheduler", title: "Scheduler Throughput", unit: "KIPS" },
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
    lastChartData = data;
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

// ApexCharts drops a value label back to the plot origin whenever its bar is
// shorter than the label text. Re-anchor every label just past its bar end;
// the axis headroom from niceAxisMax guarantees the room for it.
function alignBarValueLabels(chartContext) {
    const root = chartContext && chartContext.el;
    if (!root) return;
    const bars = root.querySelectorAll(".apexcharts-bar-area");
    const labels = root.querySelectorAll(".apexcharts-datalabels text");
    bars.forEach((bar, index) => {
        const label = labels[index];
        if (!label) return;
        const box = bar.getBBox();
        label.setAttribute("x", box.x + box.width + 8);
    });
}

// Round the axis ceiling up to a clean step with enough headroom that every
// value label fits on the surface past its bar instead of flipping onto it.
function niceAxisMax(peak) {
    const raw = peak * 1.25;
    const magnitude = Math.pow(10, Math.floor(Math.log10(raw)));
    for (const step of [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]) {
        if (step * magnitude >= raw) return step * magnitude;
    }
    return 10 * magnitude;
}

function getChartTheme() {
    const scheme = document.body.getAttribute("data-md-color-scheme");
    const dark = scheme !== "default";
    const styles = getComputedStyle(document.body);
    const token = name => (styles.getPropertyValue(name) || "").trim();
    return {
        mode: dark ? "dark" : "light",
        foreground: dark ? "#e5e7eb" : "#111827",
        muted: dark ? "#9ca3af" : "#4b5563",
        grid: dark ? "#27272a" : "#e5e7eb",
        tooltipTheme: dark ? "dark" : "light",
        // Contrast-validated bar hue for each scheme.
        accent: token("--pantheon-chart-accent") || (dark ? "#6b82ea" : "#4057d6"),
    };
}

function renderChart(rawData, chartConfig) {
    const { testName, elementId, title, unit: expectedUnit } = chartConfig;
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
    const compact = window.matchMedia("(max-width: 600px)").matches;

    if (benchmarkCharts[elementId]) {
        benchmarkCharts[elementId].destroy();
        delete benchmarkCharts[elementId];
    }

    if (categories.length === 0) {
        if (container) container.classList.add("chart-container--empty");
        element.setAttribute("role", "status");
        element.removeAttribute("aria-label");
        element.innerHTML = `<p class="chart-empty">No ${title.toLowerCase()} data matches the current filters.</p>`;
        return;
    }

    if (container) container.classList.remove("chart-container--empty");
    element.setAttribute("role", "img");
    element.setAttribute("aria-label", `${title}. Best reported result per GPU in ${unit}.`);
    element.innerHTML = "";

    const options = {
        chart: {
            type: 'bar',
            height: Math.max(320, categories.length * (compact ? 30 : 34) + (compact ? 84 : 96)),
            background: 'transparent',
            foreColor: theme.foreground,
            fontFamily: 'Inter, Roboto, sans-serif',
            toolbar: { show: false },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 450,
            },
            events: {
                mounted: alignBarValueLabels,
                updated: alignBarValueLabels,
                animationEnd: alignBarValueLabels,
            },
        },
        theme: { mode: theme.mode },
        series: [{
            name: unit ? `${title} (${unit})` : title,
            data: seriesData
        }],
        dataLabels: {
            enabled: true,
            formatter: value => `${formatChartValue(value)}${unit ? ` ${unit}` : ""}`,
            offsetX: 8,
            textAnchor: 'start',
            style: {
                colors: [theme.foreground],
                fontSize: compact ? '10px' : '12px',
                fontWeight: 700,
            },
        },
        xaxis: {
            categories: categories,
            min: 0,
            max: niceAxisMax(Math.max(...seriesData)),
            tickAmount: 5,
            forceNiceScale: false,
            labels: {
                formatter: value => formatChartValue(Number(value)),
                style: { colors: theme.muted },
            },
            axisBorder: { show: false },
            axisTicks: { show: false },
        },
        yaxis: {
            labels: {
                maxWidth: compact ? 112 : 180,
                style: {
                    colors: theme.foreground,
                    fontSize: compact ? '10px' : '12px',
                    fontWeight: 600,
                },
            }
        },
        title: {
            text: unit ? `${title} (${unit})` : title,
            align: 'left',
            margin: 18,
            style: {
                color: theme.foreground,
                fontSize: compact ? '15px' : '17px',
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
        colors: [theme.accent],
        plotOptions: {
            bar: {
                borderRadius: 5,
                borderRadiusApplication: 'end',
                barHeight: '68%',
                horizontal: true,
                // Values sit past the bar end on the chart surface, so one
                // foreground ink stays readable for long and short bars alike.
                // The axis headroom above guarantees room, so Apex must not
                // "helpfully" flip labels back onto the bar fill.
                dataLabels: { position: 'top', hideOverflowingLabels: false },
            }
        },
        grid: {
            borderColor: theme.grid,
            strokeDashArray: 4,
            xaxis: { lines: { show: true } },
            yaxis: { lines: { show: false } },
            padding: { top: 0, right: compact ? 52 : 96, bottom: 0, left: compact ? 0 : 4 },
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

let chartResizeTimer;
window.addEventListener("resize", () => {
    if (!lastChartData.length) return;
    window.clearTimeout(chartResizeTimer);
    chartResizeTimer = window.setTimeout(() => renderBenchmarkCharts(lastChartData), 150);
});

const chartThemeObserver = new MutationObserver(mutations => {
    if (!lastChartData.length) return;
    if (mutations.some(mutation => mutation.attributeName === "data-md-color-scheme")) {
        renderBenchmarkCharts(lastChartData);
    }
});

chartThemeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"],
});
