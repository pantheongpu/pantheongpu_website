// Per-card history.
//
// The leaderboard keeps one row per card, workload and release, so a card that
// slows down over time cannot be seen there: the good early run wins and every
// later, worse run is dropped. This page plots every run of one card instead.
//
// A series is split by unit. When a workload's metric changed between releases
// the numbers are not comparable, and drawing them as one line would show a
// step that is a units change rather than a change in the hardware.

(function () {
    let historyRuns = [];
    let chart = null;

    function historyTheme() {
        const dark = document.body.getAttribute("data-md-color-scheme") !== "default";
        return {
            mode: dark ? "dark" : "light",
            foreground: dark ? "#e5e7eb" : "#111827",
            muted: dark ? "#9ca3af" : "#4b5563",
            grid: dark ? "#27272a" : "#e5e7eb",
        };
    }

    // ApexCharts is 245 KB. Load it here, next to this script, only on the pages
    // that draw a chart, instead of shipping it to every page from mkdocs.yml.
    function ensureApexCharts(ownScript, callback) {
        if (window.ApexCharts) { callback(); return; }
        const self = Array.from(document.scripts).find(s => s.src && s.src.includes(`/js/${ownScript}`));
        const src = self ? new URL("apexcharts.min.js", self.src).href
                         : new URL("js/apexcharts.min.js", document.baseURI).href;
        let tag = document.querySelector("script[data-apexcharts]");
        if (!tag) {
            tag = document.createElement("script");
            tag.src = src;
            tag.async = true;
            tag.dataset.apexcharts = "1";
            document.head.appendChild(tag);
        }
        tag.addEventListener("load", () => callback(), { once: true });
        tag.addEventListener("error", () => console.error(`Failed to load ${src}`), { once: true });
    }

    function assetUrl(fileName) {
        const script = document.currentScript
            || Array.from(document.scripts).find(s => s.src && s.src.includes("/js/gpu-history.js"));
        if (script && script.src) return new URL(`../assets/${fileName}`, script.src).href;
        return new URL(`assets/${fileName}`, document.baseURI).href;
    }

    function cardLabel(card) {
        const runs = historyRuns.filter(run => run.card === card);
        const model = runs.length ? runs[0].gpu : "Unknown GPU";
        // Cards without a UUID are identified by their attributes, which makes
        // for a long opaque string; show the model and how many runs it has.
        const id = card.startsWith("GPU-") ? card : "no GPU ID";
        return `${model} — ${id} (${runs.length} runs)`;
    }

    function fill(select, values, labelFor) {
        select.innerHTML = "";
        values.forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = labelFor ? labelFor(value) : value;
            select.appendChild(option);
        });
    }

    function setStatus(message) {
        const status = document.getElementById("gpuHistoryStatus");
        if (status) status.textContent = message || "";
    }

    function seriesFor(card, test) {
        const runs = historyRuns
            .filter(run => run.card === card && run.test === test)
            .sort((a, b) => String(a.date).localeCompare(String(b.date)));

        const byUnit = new Map();
        runs.forEach(run => {
            const unit = run.unit || "";
            if (!byUnit.has(unit)) byUnit.set(unit, []);
            byUnit.get(unit).push({
                x: new Date(String(run.date).replace(" ", "T")).getTime(),
                y: Number(run.score),
                version: run.version,
            });
        });
        return byUnit;
    }

    function draw() {
        const cardSelect = document.getElementById("gpuHistoryCard");
        const testSelect = document.getElementById("gpuHistoryTest");
        const target = document.getElementById("gpuHistoryChart");
        if (!cardSelect || !testSelect || !target) return;

        const byUnit = seriesFor(cardSelect.value, testSelect.value);
        const theme = historyTheme();
        const series = Array.from(byUnit.entries())
            .map(([unit, points]) => ({ name: unit || "score", data: points }));
        const total = series.reduce((sum, s) => sum + s.data.length, 0);

        if (chart) { chart.destroy(); chart = null; }

        if (total >= 2 && !window.ApexCharts) {
            ensureApexCharts("gpu-history.js", draw);
            return;
        }

        if (total < 2) {
            target.innerHTML = "";
            setStatus(total === 1
                ? "Only one run recorded for this workload on this card, so there is no trend to draw yet."
                : "No runs recorded for this workload on this card.");
            return;
        }
        setStatus(series.length > 1
            ? "This workload's metric changed between releases, so each unit is drawn as its own series. Values in different units are not comparable."
            : "");

        chart = new ApexCharts(target, {
            chart: {
                type: "line", height: 380, foreColor: theme.foreground,
                toolbar: { show: false }, animations: { enabled: false },
                fontFamily: "inherit",
                // Material's slate palette is navy; ApexCharts' own dark
                // background is grey and sat on the page as a box.
                background: "transparent",
            },
            theme: { mode: theme.mode },
            series,
            stroke: { width: 2, curve: "straight" },
            markers: { size: 5 },
            xaxis: {
                type: "datetime",
                labels: { style: { colors: theme.muted } },
                axisBorder: { color: theme.grid },
                axisTicks: { color: theme.grid },
            },
            yaxis: {
                // A degradation of a few per cent is the interesting signal, so
                // do not force the axis to zero and flatten it away.
                forceNiceScale: true,
                labels: { style: { colors: theme.muted } },
            },
            grid: { borderColor: theme.grid },
            legend: { labels: { colors: theme.foreground } },
            tooltip: {
                theme: theme.mode,
                x: { format: "yyyy-MM-dd HH:mm" },
                y: {
                    formatter: (value, opts) => {
                        const point = opts?.w?.config?.series?.[opts.seriesIndex]
                            ?.data?.[opts.dataPointIndex];
                        const unit = opts?.w?.config?.series?.[opts.seriesIndex]?.name || "";
                        return point?.version
                            ? `${value} ${unit} (v${point.version})`
                            : `${value} ${unit}`;
                    },
                },
            },
        });
        chart.render();
    }

    function populateTests() {
        const cardSelect = document.getElementById("gpuHistoryCard");
        const testSelect = document.getElementById("gpuHistoryTest");
        if (!cardSelect || !testSelect) return;

        const counts = new Map();
        historyRuns
            .filter(run => run.card === cardSelect.value)
            .forEach(run => counts.set(run.test, (counts.get(run.test) || 0) + 1));

        // Workloads with a single run cannot show a trend; list them last.
        const tests = Array.from(counts.keys()).sort((a, b) => {
            const diff = (counts.get(b) > 1) - (counts.get(a) > 1);
            return diff || a.localeCompare(b);
        });
        fill(testSelect, tests, test => `${test} (${counts.get(test)})`);
    }

    document.addEventListener("DOMContentLoaded", function () {
        const target = document.getElementById("gpuHistoryChart");
        if (!target) return;

        const cardSelect = document.getElementById("gpuHistoryCard");
        const testSelect = document.getElementById("gpuHistoryTest");

        fetch(assetUrl("gpu_history.json"))
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                historyRuns = data;

                const repeats = new Map();
                historyRuns.forEach(run => {
                    const key = `${run.card}|${run.test}`;
                    repeats.set(key, (repeats.get(key) || 0) + 1);
                });
                // Lead with the cards that actually have a history to show.
                const depth = new Map();
                historyRuns.forEach(run => {
                    const runs = repeats.get(`${run.card}|${run.test}`) || 0;
                    depth.set(run.card, Math.max(depth.get(run.card) || 0, runs));
                });
                const cards = Array.from(depth.keys())
                    .sort((a, b) => depth.get(b) - depth.get(a)
                        || cardLabel(a).localeCompare(cardLabel(b)));

                fill(cardSelect, cards, cardLabel);
                populateTests();
                draw();

                cardSelect.addEventListener("change", () => { populateTests(); draw(); });
                testSelect.addEventListener("change", draw);
                // Material swaps the palette without reloading, and ApexCharts
                // bakes its colours in at render time.
                new MutationObserver(() => draw()).observe(document.body, {
                    attributes: true, attributeFilter: ["data-md-color-scheme"],
                });
            })
            .catch(err => {
                console.error("Error loading per-card history:", err);
                setStatus("Per-card history could not be loaded. Please refresh and try again.");
            });
    });
})();
