// Per-card history.
//
// The leaderboard keeps one row per card, workload and release, so a card that
// slows down over time cannot be seen there: the good early run wins and every
// later, worse run is dropped. This page plots every run of one card instead.
//
// A series is split by unit, by run length and by scoring change. When a
// workload's metric changed between releases the numbers are not comparable,
// and drawing them as one line would show a step that is a units change rather
// than a change in the hardware. A 30 s run and a 3600 s run of the same
// workload are not comparable either (an hour-long run heat-soaks the card), so
// each run length is its own line. The same goes for a workload that was
// reworked on purpose: its results before and after the release that reworked
// it are different measurements, so they are drawn apart (SCORING_CHANGES).

(function () {
    let historyRuns = [];
    let chart = null;

    // Workloads whose scoring was changed on purpose, by the release that
    // changed it. A result from that release on is not comparable with an
    // earlier one: the same card scores differently because the test is a
    // different test. Keep this in step with the table in docs/methodology.md;
    // tests/test_website_regressions.py checks that the two agree.
    const SCORING_CHANGES = {
        "1.2.3": [
            "voltage", "incinerator", "fp64_virus", "pulse_virus", "tensor_virus",
            "sfu_stress", "memory_thermal_asym", "memory_retention_bake",
            "mma_virus", "omni_virus", "galpat",
        ],
    };

    function versionParts(version) {
        const match = /^v?(\d+)\.(\d+)(?:\.(\d+))?/.exec(String(version || "").trim());
        return match ? [Number(match[1]), Number(match[2]), Number(match[3] || 0)] : null;
    }

    // True when `version` is `floor` or newer. A version that cannot be read
    // ("Legacy", blank) counts as older than everything.
    function versionAtLeast(version, floor) {
        const have = versionParts(version);
        const need = versionParts(floor);
        if (!have || !need) return false;
        for (let i = 0; i < 3; i++) {
            if (have[i] !== need[i]) return have[i] > need[i];
        }
        return true;
    }

    // The newest scoring change that applies to this result, or "" when the
    // result predates every change to this workload.
    function scoringEpoch(test, version) {
        let epoch = "";
        Object.keys(SCORING_CHANGES).forEach(changed => {
            if (SCORING_CHANGES[changed].includes(test) && versionAtLeast(version, changed)
                && (!epoch || versionAtLeast(changed, epoch))) {
                epoch = changed;
            }
        });
        return epoch;
    }

    // The oldest release that changed this workload's scoring, or "".
    function firstScoringChange(test) {
        let first = "";
        Object.keys(SCORING_CHANGES).forEach(changed => {
            if (SCORING_CHANGES[changed].includes(test) && (!first || versionAtLeast(first, changed))) {
                first = changed;
            }
        });
        return first;
    }

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

    function hasGpuId(card) {
        const id = String(card || "").trim();
        if (!id || id.includes("|")) return false;
        if (/^(unknown|n\/a|none)$/i.test(id)) return false;
        // Placeholder hex ids such as 0x0 or 0x0000000000000000.
        if (/^0x0*$/i.test(id)) return false;
        return true;
    }

    function cardLabel(card) {
        const runs = historyRuns.filter(run => run.card === card);
        const model = runs.length ? runs[0].gpu : "Unknown GPU";
        // Cards without an ID are identified by their attributes, which makes
        // for a long opaque string (it contains "|"); show the model and how
        // many runs it has. Any real ID is shown as published: NVIDIA UUIDs
        // ("GPU-...") and AMD unique IDs ("0x...") alike. "0x0" is what a
        // driver reports when it has no ID, so it counts as none.
        const id = hasGpuId(card) ? card : "no GPU ID";
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

    function durationLabel(duration) {
        return duration > 0 ? `${duration} s` : "length not recorded";
    }

    function seriesFor(card, test) {
        const runs = historyRuns
            .filter(run => run.card === card && run.test === test)
            .sort((a, b) => String(a.date).localeCompare(String(b.date)));

        // One series per (unit, run length, scoring change). Reports published
        // before the run length was kept in the history have none; they share
        // one series.
        const bySeries = new Map();
        runs.forEach(run => {
            const unit = run.unit || "";
            const duration = Number(run.duration) || 0;
            const epoch = scoringEpoch(test, run.version);
            const key = `${unit}|${duration}|${epoch}`;
            if (!bySeries.has(key)) bySeries.set(key, { unit, duration, epoch, points: [] });
            bySeries.get(key).points.push({
                x: new Date(String(run.date).replace(" ", "T")).getTime(),
                y: Number(run.score),
                version: run.version,
                unit,
            });
        });
        // Longest runs last, so the legend reads from short to long.
        return Array.from(bySeries.values())
            .sort((a, b) => a.unit.localeCompare(b.unit) || a.duration - b.duration
                || a.epoch.localeCompare(b.epoch, undefined, { numeric: true }));
    }

    function draw() {
        const cardSelect = document.getElementById("gpuHistoryCard");
        const testSelect = document.getElementById("gpuHistoryTest");
        const target = document.getElementById("gpuHistoryChart");
        if (!cardSelect || !testSelect || !target) return;

        const groups = seriesFor(cardSelect.value, testSelect.value);
        const theme = historyTheme();
        const units = new Set(groups.map(g => g.unit));
        const durations = new Set(groups.map(g => g.duration));
        const epochs = new Set(groups.map(g => g.epoch));
        const firstChange = firstScoringChange(testSelect.value);
        const series = groups.map(g => {
            const unitName = g.unit || "score";
            // Name a series by what tells it apart from the others.
            const parts = [];
            if (units.size > 1) parts.push(unitName);
            if (durations.size > 1) parts.push(durationLabel(g.duration));
            if (epochs.size > 1) parts.push(g.epoch ? `from ${g.epoch}` : `before ${firstChange}`);
            return { name: parts.length ? parts.join(", ") : unitName, data: g.points };
        });
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
        const notes = [];
        if (units.size > 1) {
            notes.push("This workload's metric changed between releases, so each unit is drawn as its own series. Values in different units are not comparable.");
        }
        if (durations.size > 1) {
            notes.push("Runs of different lengths are drawn as separate series: a longer run heat-soaks the card, so a 300 s result and a 3600 s result are not comparable.");
        }
        if (epochs.size > 1) {
            notes.push(`This workload's scoring changed in Pantheon ${firstChange}, so results from that release on are drawn as their own series. They are not comparable with earlier results.`);
        }
        setStatus(notes.join(" "));

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
                        const unit = point?.unit || "";
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
