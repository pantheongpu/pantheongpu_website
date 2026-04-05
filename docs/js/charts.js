document.addEventListener("DOMContentLoaded", function () {
    const dataUrl = "../assets/web_data.json";

    fetch(dataUrl)
        .then(response => response.json())
        .then(data => {
            renderChart(data, "memory_write_agg", "chart-memory", "Memory Write Bandwidth (GB/s)");
            renderChart(data, "tensor_virus", "chart-tensor", "Tensor Compute Throughput");
        })
        .catch(err => console.error("Error loading benchmark data:", err));
});

function renderChart(rawData, testName, elementId, title) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Filter data for this specific test
    const filtered = rawData.filter(d => d.test === testName);
    
    // Group by GPU and take the MAX score (best run)
    const bestScores = {};
    filtered.forEach(r => {
        if (!bestScores[r.gpu] || r.throughput > bestScores[r.gpu]) {
            bestScores[r.gpu] = r.throughput;
        }
    });

    // Prepare arrays for ApexCharts
    const categories = Object.keys(bestScores);
    const seriesData = Object.values(bestScores);

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
            title: { text: 'GB/s' },
            labels: { style: { colors: '#b8b8b8' } }
        },
        title: {
            text: title,
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
    chart.render();
}
