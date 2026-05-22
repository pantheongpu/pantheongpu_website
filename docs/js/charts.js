let benchmarkCharts = {};
const BENCHMARK_CHARTS = [
    { testName: "memory_read_agg", elementId: "chart-memory-read", title: "Memory Read Bandwidth", unit: "GB/s" },
    { testName: "memory_write_agg", elementId: "chart-memory", title: "Memory Write Bandwidth", unit: "GB/s" },
    { testName: "tensor_virus", elementId: "chart-tensor", title: "Tensor Compute Throughput", unit: "TFLOPS" },
    { testName: "fp64_virus", elementId: "chart-fp64", title: "FP64 Compute Throughput", unit: "TFLOPS" },
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
        renderChart(data, chart.testName, chart.elementId, chart.title, chart.unit);
    });
}

function getChartScore(row) {
    const score = Number(row.score);
    if (Number.isFinite(score) && score > 0) return score;

    const throughput = Number(row.throughput);
    if (Number.isFinite(throughput) && throughput > 0) return throughput;

    return null;
}

function renderChart(rawData, testName, elementId, title, expectedUnit) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const filtered = rawData.filter(d => d.test === testName && (!expectedUnit || d.unit === expectedUnit));
    
    const bestScores = {};
    filtered.forEach(r => {
        const score = getChartScore(r);
        if (score === null) return;

        if (!bestScores[r.gpu] || score > bestScores[r.gpu]) {
            bestScores[r.gpu] = score;
        }
    });

    const categories = Object.keys(bestScores);
    const seriesData = Object.values(bestScores);
    const unit = expectedUnit || "";

    if (benchmarkCharts[elementId]) {
        benchmarkCharts[elementId].destroy();
        delete benchmarkCharts[elementId];
    }

    if (categories.length === 0) {
        element.innerHTML = `<p class="chart-empty">No ${title.toLowerCase()} data matches the current filters.</p>`;
        return;
    }

    element.innerHTML = "";

    const options = {
        chart: {
            type: 'bar',
            height: 350,
            background: 'transparent',
            toolbar: { show: false }
        },
        theme: { mode: 'dark' }, // Auto-matches the Slate theme
        series: [{
            name: 'Throughput',
            data: seriesData
        }],
        xaxis: {
            categories: categories,
            labels: { style: { colors: '#b8b8b8' } }
        },
        yaxis: {
            title: { text: unit },
            labels: { style: { colors: '#b8b8b8' } }
        },
        title: {
            text: unit ? `${title} (${unit})` : title,
            align: 'center',
            style: { color: '#fff', fontSize: '18px' }
        },
        colors: ['#00E396'], // Cyberpunk Green
        plotOptions: {
            bar: {
                borderRadius: 4,
                horizontal: true,
            }
        },
        grid: {
             borderColor: '#444' 
        }
    };

    const chart = new ApexCharts(element, options);
    benchmarkCharts[elementId] = chart;
    chart.render();
}

window.renderBenchmarkCharts = renderBenchmarkCharts;
