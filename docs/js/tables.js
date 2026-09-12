// --- CONFIGURATION: Define all available columns ---
const COL_DEFS = [
    { key: "gpu",         label: "GPU Model",   visible: true },
    { key: "manufacturer",label: "Vendor",      visible: true },
    { key: "test",        label: "Test Name",   visible: true },
    { key: "version",     label: "Ver",         visible: true },
    { key: "score",       label: "Score",       visible: false },
    { key: "throughput",  label: "Throughput",  visible: true },
    { key: "throughput_variance", label: "Throughput Variance", visible: false },
    { key: "duration",    label: "Duration",    visible: true },
    { key: "temp_max",    label: "Peak Temp",   visible: true },
    { key: "power_max",   label: "Peak Power",  visible: true },
    { key: "clock_avg",   label: "Avg Clock",   visible: true },
    { key: "gpu_util_avg",label: "Avg GPU Util",visible: true },
    { key: "memory_peak", label: "Peak Memory", visible: true },
    { key: "energy_wh",   label: "Energy",      visible: true },
    { key: "date",        label: "Date",        visible: true },
    // --- Hidden by default (Pro Metrics) ---
    { key: "efficiency",  label: "Efficiency (MB/J)", visible: false },
    { key: "temp_mem",    label: "Mem Temp",    visible: false },
    { key: "fan_max",     label: "Fan %",       visible: false },
    { key: "pcie_gen",    label: "PCIe Gen",    visible: false },
    { key: "pcie_width",  label: "PCIe Width",  visible: false },
    { key: "throttle",    label: "Limit Reason",visible: false },
    { key: "clock_min",   label: "Min Clock",   visible: false },
    { key: "clock_max",   label: "Max Clock",   visible: false },
    { key: "gpu_util_max",label: "Peak GPU Util",visible: false },
    { key: "memory_total",label: "Total Memory",visible: false },
    { key: "thermal_rise",label: "Thermal Rise",visible: false },
    { key: "throttle_time",label: "Throttle Time",visible: false },
    { key: "volts_core",  label: "Core (mV)",   visible: false },
    { key: "volts_soc",   label: "SoC (mV)",    visible: false },
    { key: "vram",     label: "VRAM",    visible: false },
    // The vendor the board's VBIOS memory table was configured for, as the
    // driver reports it: one value per card, not a survey of the chips.
    { key: "memory_vendor", label: "Mem Vendor", visible: true },
    { key: "memory_type",   label: "Mem Type",   visible: false },
    { key: "driver",   label: "Driver",  visible: false },
    { key: "toolkit",  label: "Toolkit", visible: false },
    
    { key: "power_limit", label: "TDP (W)",     visible: true }, 

    // The GPU UUID the driver reported, published verbatim (decided
    // 2026-08-31): it identifies the card, not a host, and it is what per-card
    // history and dedup join on. Host identifiers are stripped upstream.
    { key: "uuid",        label: "GPU ID",      visible: false },
];

let rawData = [];
let bestRuns = [];
let currentFilteredData = [];

// The table used to build every filtered row at once. At 4,000+ results and
// 16 visible columns that is ~64,000 DOM nodes in one synchronous pass, and
// the page visibly stalls. Only a page's worth is rendered now.
//
// Note this does NOT reduce the download: web_data.json is fetched and
// parsed whole either way. It fixes the render, which is the part that
// blocks the browser.
const PAGE_SIZES = [50, 100, 250, "All"];
let pageSize = 100;
let currentPage = 1;
let currentSort = { key: 'version', dir: 'desc' };

function getUrlSelections(parameter, availableValues) {
    const rawValue = new URLSearchParams(window.location.search).get(parameter);
    if (!rawValue) return null;

    const available = new Set(availableValues);
    const selected = rawValue.split(",").map(value => value.trim()).filter(value => available.has(value));
    return selected.length > 0 ? selected : null;
}

function syncFilterUrl(selectedGPUs, selectedTests, selectedVersions, searchValue) {
    const url = new URL(window.location.href);
    const allGPUs = getCheckedValues("gpuMenu").length === document.querySelectorAll("#gpuMenu input.filter-item").length;
    const allTests = getCheckedValues("testMenu").length === document.querySelectorAll("#testMenu input.filter-item").length;
    const allVersions = getCheckedValues("versionMenu").length === document.querySelectorAll("#versionMenu input.filter-item").length;

    const setParameter = (name, values, include) => {
        if (include && values.length > 0) {
            url.searchParams.set(name, values.join(","));
        } else {
            url.searchParams.delete(name);
        }
    };

    setParameter("gpu", selectedGPUs, !allGPUs);
    setParameter("test", selectedTests, !allTests);
    setParameter("version", selectedVersions, !allVersions);
    setParameter("q", [searchValue], Boolean(searchValue));
    window.history.replaceState(null, "", url);
}

function trackBenchmarkEvent(eventName, parameters = {}) {
    if (typeof window.gtag === "function") {
        window.gtag("event", eventName, parameters);
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("benchmarkTable");
    if (!table) return;

    const searchInput = document.getElementById("textSearch");
    if (searchInput) {
        searchInput.value = new URLSearchParams(window.location.search).get("q") || "";
        searchInput.addEventListener("input", applyFilters);
    }

    const dataUrl = getBenchmarkAssetUrl("web_data.json");

    fetch(dataUrl)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status} loading ${dataUrl}`);
            return response.json();
        })
        .then(data => {
            rawData = data;
            bestRuns = rawData;
            //bestRuns = getBestRunsOnly(rawData);
            
            initColumnMenu();     
            populateFilters(bestRuns);
            applyFilters();
        })
        .catch(err => {
            console.error("Error loading benchmark data:", err);
            setBenchmarkStatus("Benchmark data could not be loaded. Please refresh the page or try again later.", true);
        });
});

function getBenchmarkAssetUrl(fileName) {
    const script = document.currentScript || Array.from(document.scripts).find(s => s.src && s.src.includes("/js/tables.js"));
    if (script && script.src) {
        return new URL(`../assets/${fileName}`, script.src).href;
    }
    return new URL(`assets/${fileName}`, document.baseURI).href;
}

function getBestRunsOnly(data) {
    // Group by version and unit as well as GPU and workload. Without them this
    // compared numbers that are not comparable: a workload whose metric changed
    // between releases had its "best" run picked from whichever version
    // produced the larger figure, and a run recorded in Watts could out-rank
    // the same workload's TFLOPS runs purely because the number was bigger.
    // The generator already keys on version for exactly this reason.
    const groups = {};
    data.forEach(row => {
        const key = `${row.gpu}|${row.test}|${row.version || "Legacy"}|${row.unit || ""}`;
        const current = groups[key];
        const score = parseFloat(row.score);
        if (!current || (Number.isFinite(score) && score > parseFloat(current.score))) {
            groups[key] = row;
        }
    });
    return Object.values(groups);
}

function isMissingValue(val) {
    return val === undefined || val === null || val === "" || val === "N/A";
}

function normalizeVersion(value) {
    if (isMissingValue(value) || value === "Legacy") return [];
    return String(value).replace(/^v/i, "").split(".").map(part => {
        const match = part.match(/\d+/);
        const parsed = match ? parseInt(match[0], 10) : 0;
        return Number.isFinite(parsed) ? parsed : 0;
    });
}

function compareVersions(a, b) {
    const legacyA = isMissingValue(a) || a === "Legacy";
    const legacyB = isMissingValue(b) || b === "Legacy";
    if (legacyA && legacyB) return 0;
    if (legacyA) return -1;
    if (legacyB) return 1;

    const vA = normalizeVersion(a);
    const vB = normalizeVersion(b);
    const length = Math.max(vA.length, vB.length);
    for (let i = 0; i < length; i++) {
        const partA = vA[i] || 0;
        const partB = vB[i] || 0;
        if (partA !== partB) return partA > partB ? 1 : -1;
    }
    return String(a).localeCompare(String(b));
}

function compareDates(a, b) {
    const timeA = Date.parse(a || "");
    const timeB = Date.parse(b || "");
    if (Number.isNaN(timeA) && Number.isNaN(timeB)) return 0;
    if (Number.isNaN(timeA)) return -1;
    if (Number.isNaN(timeB)) return 1;
    return timeA - timeB;
}

function compareValues(a, b, key) {
    if (key === "version") return compareVersions(a || "Legacy", b || "Legacy");
    if (key === "date") return compareDates(a, b);

    let valA = a;
    let valB = b;

    if (isMissingValue(valA)) valA = -999999;
    if (isMissingValue(valB)) valB = -999999;

    let numA = parseFloat(valA);
    let numB = parseFloat(valB);

    if (!isNaN(numA) && !isNaN(numB)) {
        return numA - numB;
    }

    valA = String(valA).toLowerCase();
    valB = String(valB).toLowerCase();
    if (valA < valB) return -1;
    if (valA > valB) return 1;
    return 0;
}

// Absence is decided in the generator, which knows which sensors a run
// actually read. Treating every zero as missing here discarded real results:
// a throttle time of 0s means the GPU never throttled, and 1173 of 1315 rows
// reported that outcome as though it were unknown.
function formatMetric(value, unit) {
    if (isMissingValue(value)) return "N/A";
    return unit ? `${value} ${unit}` : String(value);
}

// Display-only compaction so 13361400000 reads as 13.36B in table cells.
// CSV export passes display=false, so it keeps full precision.
function compactNumber(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return value;
    const abs = Math.abs(num);
    const trim = n => String(Number(n.toFixed(2)));
    if (abs >= 1e9) return `${trim(num / 1e9)}B`;
    if (abs >= 1e6) return `${trim(num / 1e6)}M`;
    if (abs >= 1e4) return num.toLocaleString("en-US", { maximumFractionDigits: 0 });
    return trim(num);
}

function formatCellValue(row, key, display = false) {
    let val = row[key];

    if (key === "uuid") {
        // Reports before v1.0.8 carried no UUID. Say so rather than print
        // "Unknown" as though it were an identifier shared by every such card.
        return isMissingValue(val) || val === "Unknown" ? "no GPU ID" : val;
    }
    if (key === "score" || key === "throughput") {
        if (row.unit === "Watts") {
            // No throughput was recorded for this run, so the generator kept
            // peak power to keep the run visible. Watts in a throughput column
            // read as a result; label what they are.
            if (isMissingValue(val)) return "N/A";
            return `${display ? compactNumber(val) : val} W (power only, no throughput)`;
        }
        if (display && !isMissingValue(val)) val = compactNumber(val);
        return formatMetric(val, row.unit);
    }
    if (key === "throughput_variance") {
        return formatMetric(val, "%");
    }
    if (key === "duration") {
        return isMissingValue(val) ? "N/A" : `${val}s`;
    }
    if (key.includes("temp")) {
        return formatMetric(val, "°C");
    }
    if (key.includes("power")) {
        return formatMetric(val, "W");
    }
    if (key.includes("gpu_util")) {
        return formatMetric(val, "%");
    }
    // Sizes only. memory_vendor and memory_type match the same prefix but
    // are names, not quantities: v1.2.1 fills them with "Samsung" and
    // "GDDR6", which this would render as "Samsung MiB". Invisible until
    // now only because every published run predates that release and left
    // both fields null.
    if (key === "memory_peak" || key === "memory_total") {
        return formatMetric(val, "MiB");
    }
    if (key === "energy_wh") {
        return formatMetric(val, "Wh");
    }
    if (key === "clock_min" || key === "clock_max") {
        return formatMetric(val, "MHz");
    }
    if (key === "thermal_rise") {
        return formatMetric(val, "°C");
    }
    if (key === "throttle_time") {
        return formatMetric(val, "s");
    }
    if (key === "version") {
        return val || "Legacy";
    }
    if (isMissingValue(val)) {
        return "N/A";
    }
    return val;
}

function setBenchmarkStatus(message, isError = false) {
    const status = document.getElementById("benchmarkStatus");
    if (!status) return;
    status.textContent = message;
    status.classList.toggle("benchmark-status--error", isError);
}

function sortDirectionFor(key) {
    if (currentSort.key !== key) return "none";
    return currentSort.dir === "asc" ? "ascending" : "descending";
}

// --- 2. Dynamic Table Rendering ---
function renderTable(data) {
    const table = document.getElementById("benchmarkTable");
    if (!table) return;

    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    if (!thead || !tbody) return;

    thead.innerHTML = "";
    let headerRow = document.createElement("tr");
    headerRow.style.cursor = "pointer";

    COL_DEFS.forEach(col => {
        if (col.visible) {
            let th = document.createElement("th");
            th.setAttribute("scope", "col");
            th.setAttribute("aria-sort", sortDirectionFor(col.key));

            const button = document.createElement("button");
            button.type = "button";
            button.className = "benchmark-sort-button";
            button.dataset.sortKey = col.key;
            button.textContent = col.label;
            button.setAttribute(
                "aria-label",
                `Sort by ${col.label}${currentSort.key === col.key ? `, currently ${currentSort.dir === "asc" ? "ascending" : "descending"}` : ""}`
            );

            const indicator = document.createElement("span");
            indicator.className = "benchmark-sort-indicator";
            indicator.setAttribute("aria-hidden", "true");
            indicator.textContent = currentSort.key === col.key
                ? (currentSort.dir === "asc" ? "↑" : "↓")
                : "↕";

            button.appendChild(indicator);
            button.addEventListener("click", () => sortData(col.key));
            th.appendChild(button);
            headerRow.appendChild(th);
        }
    });
    thead.appendChild(headerRow);

    tbody.innerHTML = "";
    if (data.length === 0) {
        let visibleCount = COL_DEFS.filter(c => c.visible).length;
        tbody.innerHTML = `<tr><td colspan='${visibleCount}' style='text-align:center; padding: 20px;'>No results found</td></tr>`;
        return;
    }

    const total = data.length;
    const pages = pageSize === "All" ? 1 : Math.max(1, Math.ceil(total / pageSize));
    if (currentPage > pages) currentPage = pages;
    const from = pageSize === "All" ? 0 : (currentPage - 1) * pageSize;
    const to = pageSize === "All" ? total : Math.min(from + pageSize, total);

    // One fragment, one insertion: appending each row to a live tbody forces
    // the browser to reflow per row.
    const frag = document.createDocumentFragment();
    data.slice(from, to).forEach(row => {
        const tr = document.createElement("tr");
        
        COL_DEFS.forEach(col => {
            if (col.visible) {
                let td = document.createElement("td");
                let val = formatCellValue(row, col.key, true);

                if (col.key === "score") {
                    td.style.fontWeight = "bold";
                }
                else if (col.key === "gpu") {
                    td.style.fontWeight = "bold";
                }
                else if (col.key === "test") {
                    td.className = "benchmark-cell-test";
                }
                else if (col.key.includes("temp")) {
                    const tempColor = getColorForTemp(row[col.key]);
                    if (tempColor) td.style.color = tempColor;
                }
                else if (col.key === "version") {
                    td.className = "benchmark-cell-version";
                }

                td.textContent = val;
                tr.appendChild(td);
            }
        });
        frag.appendChild(tr);
    });
    tbody.appendChild(frag);
    renderPager(total, from, to, pages);
}

// Page controls, built once below the table and updated in place.
//
// Kept out of benchmarks.md so the markup does not have to know about
// pagination; the page only supplies the table.
function renderPager(total, from, to, pages) {
    const wrap = document.querySelector(".benchmark-table-wrap");
    if (!wrap) return;
    let bar = document.getElementById("benchmarkPager");
    if (!bar) {
        bar = document.createElement("div");
        bar.id = "benchmarkPager";
        bar.className = "benchmark-pager";
        wrap.insertAdjacentElement("afterend", bar);
    }
    if (total === 0) { bar.innerHTML = ""; return; }

    const button = (label, page, disabled, current) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = label;
        b.disabled = !!disabled;
        if (current) b.setAttribute("aria-current", "page");
        if (!disabled && !current) {
            b.addEventListener("click", () => {
                currentPage = page;
                renderTable(currentFilteredData);
                // Back to the top of the table, not the top of the document:
                // jumping to the page header loses the reader's place.
                document.getElementById("benchmarkTable")
                    ?.scrollIntoView({ block: "start", behavior: "smooth" });
            });
        }
        return b;
    };

    bar.innerHTML = "";
    const count = document.createElement("span");
    count.className = "benchmark-pager__count";
    count.textContent = pageSize === "All"
        ? `all ${total.toLocaleString()} results`
        : `${(from + 1).toLocaleString()}\u2013${to.toLocaleString()} of ${total.toLocaleString()}`;
    bar.appendChild(count);

    if (pageSize !== "All" && pages > 1) {
        bar.appendChild(button("\u2039 Prev", currentPage - 1, currentPage === 1));
        // A window around the current page: 200 numbered buttons is its own
        // rendering problem.
        const span = 2;
        let start = Math.max(1, currentPage - span);
        let end = Math.min(pages, currentPage + span);
        if (start > 1) {
            bar.appendChild(button("1", 1, false, currentPage === 1));
            if (start > 2) {
                const gap = document.createElement("span");
                gap.className = "benchmark-pager__gap";
                gap.textContent = "\u2026";
                bar.appendChild(gap);
            }
        }
        for (let i = start; i <= end; i++) {
            bar.appendChild(button(String(i), i, false, i === currentPage));
        }
        if (end < pages) {
            if (end < pages - 1) {
                const gap = document.createElement("span");
                gap.className = "benchmark-pager__gap";
                gap.textContent = "\u2026";
                bar.appendChild(gap);
            }
            bar.appendChild(button(String(pages), pages, false, currentPage === pages));
        }
        bar.appendChild(button("Next \u203a", currentPage + 1, currentPage === pages));
    }

    const label = document.createElement("label");
    label.className = "benchmark-pager__size";
    label.textContent = "per page ";
    const select = document.createElement("select");
    PAGE_SIZES.forEach(size => {
        const option = document.createElement("option");
        option.value = String(size);
        option.textContent = String(size);
        option.selected = String(size) === String(pageSize);
        select.appendChild(option);
    });
    select.addEventListener("change", () => {
        pageSize = select.value === "All" ? "All" : Number(select.value);
        currentPage = 1;
        renderTable(currentFilteredData);
    });
    label.appendChild(select);
    bar.appendChild(label);
}


function sortData(key) {
    if (currentSort.key === key) {
        currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.key = key;
        currentSort.dir = 'desc';
    }
    applyFilters();
}

// --- Multi-Select Menu Helpers ---
function getCheckedValues(menuId) {
    // We use a specific class (.filter-item) so we don't accidentally grab the "Select All" checkbox's value
    const checkboxes = document.querySelectorAll(`#${menuId} input.filter-item:checked`);
    return Array.from(checkboxes).map(cb => cb.value);
}

function buildCheckboxMenu(menuId, items, defaultChecked = null) {
    const menu = document.getElementById(menuId);
    if (!menu) return;

    menu.innerHTML = "";

    // Determine if "Select All" should be checked on load
    let isAllChecked = defaultChecked === null || defaultChecked.length === items.length;

    // --- ADD SEARCH BAR ---
    // Only add a search bar if there are enough items to warrant searching
    if (items.length > 5) {
        let searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.placeholder = "Search...";
        searchInput.setAttribute("aria-label", `Search ${menuId.replace("Menu", "").toLowerCase()} options`);
        searchInput.className = "benchmark-menu-search";

        // The live filtering logic
        searchInput.oninput = (e) => {
            const term = e.target.value.toLowerCase();
            // Select all individual item rows (skipping the Select All row)
            const rows = menu.querySelectorAll('.menu-item-row');
            rows.forEach(row => {
                const labelText = row.innerText.toLowerCase();
                if (labelText.includes(term)) {
                    row.style.display = "block";
                } else {
                    row.style.display = "none";
                }
            });
        };
        menu.appendChild(searchInput);
    }

    // --- Create "Select All" Checkbox ---
    let selectAllDiv = document.createElement("div");
    selectAllDiv.style.marginBottom = "8px";
    selectAllDiv.style.paddingBottom = "8px";
    selectAllDiv.style.borderBottom = "1px solid var(--pantheon-line)";
    
    let selectAllLabel = document.createElement("label");
    selectAllLabel.style.cursor = "pointer";
    selectAllLabel.style.display = "flex";
    selectAllLabel.style.alignItems = "center";
    selectAllLabel.style.fontWeight = "bold";
    
    let selectAllCheck = document.createElement("input");
    selectAllCheck.type = "checkbox";
    selectAllCheck.checked = isAllChecked;
    selectAllCheck.style.marginRight = "10px";

    selectAllLabel.appendChild(selectAllCheck);
    selectAllLabel.appendChild(document.createTextNode("Select All"));
    selectAllDiv.appendChild(selectAllLabel);
    menu.appendChild(selectAllDiv);

    // --- Create Individual Items ---
    let itemCheckboxes = [];

    items.forEach(item => {
        let div = document.createElement("div");
        div.className = "menu-item-row"; // Tagged so the search bar can find it
        div.style.marginBottom = "5px";
        
        let label = document.createElement("label");
        label.style.cursor = "pointer";
        label.style.display = "flex";
        label.style.alignItems = "center";
        
        let check = document.createElement("input");
        check.type = "checkbox";
        check.value = item;
        check.checked = defaultChecked === null ? true : defaultChecked.includes(item);
        check.className = "filter-item"; 
        check.style.marginRight = "10px";
        
        check.onchange = () => {
            selectAllCheck.checked = itemCheckboxes.every(c => c.checked);
            applyFilters();
        };
        
        itemCheckboxes.push(check);
        label.appendChild(check);
        label.appendChild(document.createTextNode(item));
        div.appendChild(label);
        menu.appendChild(div);
    });

    selectAllCheck.onchange = () => {
        let isChecked = selectAllCheck.checked;
        itemCheckboxes.forEach(c => {
            // Only toggle the visible ones! (So search + select all works together)
            if (c.closest('.menu-item-row').style.display !== "none") {
                c.checked = isChecked;
            }
        });
        applyFilters();
    };
}

function populateFilters(data) {
    const gpuSet = new Set();
    const testSet = new Set();
    const versionSet = new Set();

    data.forEach(row => {
        if (row.gpu) gpuSet.add(row.gpu);
        if (row.test) testSet.add(row.test);
        versionSet.add(row.version || "Legacy");
    });

    // Extract and sort versions semantically, newest first.
    let versions = Array.from(versionSet);
    versions.sort((a, b) => compareVersions(b, a));

    const gpus = Array.from(gpuSet).sort();
    const tests = Array.from(testSet).sort();
    buildCheckboxMenu("gpuMenu", gpus, getUrlSelections("gpu", gpus));
    buildCheckboxMenu("testMenu", tests, getUrlSelections("test", tests));
    buildCheckboxMenu("versionMenu", versions, getUrlSelections("version", versions));
}

function applyFilters() {
    const searchInput = document.getElementById("textSearch");
    if (!searchInput) return;

    const searchVal = searchInput.value.toLowerCase();
    const selectedGPUs = getCheckedValues("gpuMenu");
    const selectedTests = getCheckedValues("testMenu");
    const selectedVersions = getCheckedValues("versionMenu");

    syncFilterUrl(selectedGPUs, selectedTests, selectedVersions, searchInput.value.trim());

    let filtered = bestRuns.filter(row => {
        const ver = row.version || "Legacy";
        const gpuMatch = selectedGPUs.includes(row.gpu);
        const testMatch = selectedTests.includes(row.test);
        const versionMatch = selectedVersions.includes(ver);
        const searchMatch = Object.values(row).join(" ").toLowerCase().includes(searchVal);
        
        return gpuMatch && testMatch && versionMatch && searchMatch;
    });

    filtered.sort((a, b) => {
        if (currentSort.key !== "version") {
            const versionCompare = compareVersions(a.version || "Legacy", b.version || "Legacy");
            if (versionCompare !== 0) return -versionCompare;
        }

        const valueCompare = compareValues(a[currentSort.key], b[currentSort.key], currentSort.key);
        if (valueCompare !== 0) return currentSort.dir === 'asc' ? valueCompare : -valueCompare;

        const dateCompare = compareDates(a.date, b.date);
        if (dateCompare !== 0) return -dateCompare;

        return compareValues(a.gpu, b.gpu, "gpu");
    });

    currentFilteredData = filtered;
    // A filter or sort change invalidates the position: page 7 of the old
    // result set means nothing in the new one.
    currentPage = 1;
    renderTable(filtered);
    const totalLabel = bestRuns.length === 1 ? "result" : "results";
    const filteredLabel = filtered.length === 1 ? "result" : "results";
    setBenchmarkStatus(
        filtered.length === bestRuns.length
            ? `${bestRuns.length} ${totalLabel}`
            : `${filtered.length} ${filteredLabel} shown out of ${bestRuns.length}`
    );
    if (window.renderBenchmarkCharts) {
        window.renderBenchmarkCharts(filtered);
    }
}

// --- Menu Toggling ---
function toggleMenu(menuId) {
    const menus = ["gpuMenu", "testMenu", "versionMenu", "columnMenu"];
    menus.forEach(id => {
        const m = document.getElementById(id);
        if (!m) return;
        const button = document.querySelector(`[aria-controls="${id}"]`);

        if (id === menuId) {
            const willOpen = m.style.display !== "block";
            m.style.display = willOpen ? "block" : "none";
            if (button) button.setAttribute("aria-expanded", String(willOpen));
        } else {
            m.style.display = "none";
            if (button) button.setAttribute("aria-expanded", "false");
        }
    });
}

function closeBenchmarkMenus() {
    const menus = ["gpuMenu", "testMenu", "versionMenu", "columnMenu"];
    menus.forEach(id => {
        const menu = document.getElementById(id);
        const button = document.querySelector(`[aria-controls="${id}"]`);
        if (menu) menu.style.display = "none";
        if (button) button.setAttribute("aria-expanded", "false");
    });
}

function initColumnMenu() {
    const menu = document.getElementById("columnMenu");
    if (!menu) return;

    menu.innerHTML = "";

    // --- Create "Select All" Checkbox ---
    let selectAllDiv = document.createElement("div");
    selectAllDiv.style.marginBottom = "8px";
    selectAllDiv.style.paddingBottom = "8px";
    selectAllDiv.style.borderBottom = "1px solid var(--pantheon-line)";
    
    let selectAllLabel = document.createElement("label");
    selectAllLabel.style.cursor = "pointer";
    selectAllLabel.style.display = "flex";
    selectAllLabel.style.alignItems = "center";
    selectAllLabel.style.fontWeight = "bold";
    
    let selectAllCheck = document.createElement("input");
    selectAllCheck.type = "checkbox";
    selectAllCheck.checked = COL_DEFS.every(c => c.visible);
    selectAllCheck.style.marginRight = "10px";

    selectAllLabel.appendChild(selectAllCheck);
    selectAllLabel.appendChild(document.createTextNode("Select All"));
    selectAllDiv.appendChild(selectAllLabel);
    menu.appendChild(selectAllDiv);

    // --- Create Individual Columns ---
    let itemCheckboxes = [];

    COL_DEFS.forEach((col, index) => {
        let div = document.createElement("div");
        div.style.marginBottom = "5px";
        let label = document.createElement("label");
        label.style.cursor = "pointer";
        label.style.display = "flex";
        label.style.alignItems = "center";
        
        let check = document.createElement("input");
        check.type = "checkbox";
        check.checked = col.visible;
        check.style.marginRight = "10px";
        
        // When an individual column is toggled
        check.onchange = () => {
            COL_DEFS[index].visible = check.checked;
            selectAllCheck.checked = itemCheckboxes.every(c => c.checked);
            applyFilters(); 
        };

        itemCheckboxes.push(check);
        label.appendChild(check);
        label.appendChild(document.createTextNode(col.label));
        div.appendChild(label);
        menu.appendChild(div);
    });

    // When "Select All" is clicked
    selectAllCheck.onchange = () => {
        let isChecked = selectAllCheck.checked;
        itemCheckboxes.forEach((c, index) => {
            c.checked = isChecked;
            COL_DEFS[index].visible = isChecked;
        });
        applyFilters();
    };
}

document.addEventListener("click", function(event) {
    if (!event.target.closest(".benchmark-filter")) {
        closeBenchmarkMenus();
    }
});

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        closeBenchmarkMenus();
    }
});

function getColorForTemp(temp) {
    // Healthy temperatures stay in the default ink; color only flags concern.
    if (!temp || temp === "N/A" || temp < 60) return "";
    if (temp < 80) return "var(--pantheon-temp-warn)";
    return "var(--pantheon-temp-crit)";
}

// --- 6. Export ---

// Units that belong to a whole column, so the cell can hold a number and the
// unit can live in the header. A spreadsheet that stores "72 °C" cannot
// average a temperature column; one that stores 72 can.
//
// score and throughput are deliberately absent: their unit varies per row
// (GB/s, TFLOPS, ns), so they get a Unit column beside them instead.
// memory_vendor and memory_type are absent because they are names, not
// quantities, despite matching the same "memory" prefix elsewhere.
const XLSX_COLUMN_UNITS = {
    throughput_variance: "%", duration: "s", throttle_time: "s",
    temp_max: "\u00b0C", temp_mem: "\u00b0C", thermal_rise: "\u00b0C",
    power_max: "W", energy_wh: "Wh",
    clock_avg: "MHz", clock_min: "MHz", clock_max: "MHz",
    gpu_util_avg: "%", gpu_util_max: "%",
    memory_peak: "MiB", memory_total: "MiB", vram: "MiB",
    // These four are numbers whose label already names the unit, so they
    // map to "" -- a suffix would render "Fan % (%)" and "Core (mV) (mV)".
    fan_max: "", volts_core: "", volts_soc: "", power_limit: "",
};

// Both exports read this, so the CSV and the workbook cannot drift apart in
// which rows or columns they carry.
function exportColumns() {
    return COL_DEFS.filter(c => c.visible);
}

function exportFilename(extension) {
    const dateStr = new Date().toISOString().split("T")[0];
    return `pantheon_benchmarks_${dateStr}.${extension}`;
}

function downloadBlob(blob, filename) {
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// One benchmark row, typed for a spreadsheet rather than formatted for a
// cell. Numbers stay numbers; a value the run never measured becomes a blank
// rather than the text "N/A", which would turn its column into text and
// break every formula in it.
function xlsxRow(row, columns) {
    const cells = [];
    columns.forEach(col => {
        const raw = row[col.key];
        if (col.key === "score" || col.key === "throughput") {
            const num = Number(raw);
            // A run that recorded no throughput leaves this blank; the Unit
            // column beside it still says why. "N/A" here would make the
            // whole column text for the sake of 50 rows out of 3,363.
            cells.push(isMissingValue(raw) ? ""
                : (Number.isFinite(num) ? num : formatCellValue(row, col.key)));
            cells.push(row.unit === "Watts"
                ? "Watts (power only, no throughput)"
                : (row.unit || ""));
            return;
        }
        if (col.key in XLSX_COLUMN_UNITS) {
            const num = Number(raw);
            cells.push(isMissingValue(raw) || !Number.isFinite(num) ? "" : num);
            return;
        }
        const formatted = formatCellValue(row, col.key);
        cells.push(formatted === "N/A" ? "" : formatted);
    });
    return cells;
}

function xlsxHeader(columns) {
    const headers = [];
    columns.forEach(col => {
        const unit = XLSX_COLUMN_UNITS[col.key];
        headers.push(unit ? `${col.label} (${unit})` : col.label);

        if (col.key === "score" || col.key === "throughput") headers.push("Unit");
    });
    return headers;
}

async function exportToXLSX() {
    if (currentFilteredData.length === 0) {
        alert("No data available to export!");
        return;
    }
    if (!window.PantheonXLSX) {
        alert("The spreadsheet writer did not load. The CSV export still works.");
        return;
    }

    trackBenchmarkEvent("benchmark_export_xlsx",
                        { result_count: currentFilteredData.length });

    const columns = exportColumns();
    const sheets = [{
        name: "Benchmarks",
        rows: [xlsxHeader(columns),
               ...currentFilteredData.map(row => xlsxRow(row, columns))],
    }];

    const blob = await window.PantheonXLSX.buildWorkbook(sheets);
    downloadBlob(blob, exportFilename("xlsx"));
}

// --- Export to CSV ---
function exportToCSV() {
    if (currentFilteredData.length === 0) {
        alert("No data available to export!");
        return;
    }

    trackBenchmarkEvent("benchmark_export", { result_count: currentFilteredData.length });

    const visibleCols = exportColumns();
    const headers = visibleCols.map(c => `"${c.label}"`).join(",");

    const csvRows = currentFilteredData.map(row =>
        visibleCols.map(col => {
            // Escape quotes by doubling them (CSV standard) and wrap in quotes
            const val = String(formatCellValue(row, col.key)).replace(/"/g, '""');
            return `"${val}"`;
        }).join(",")
    );

    const csvContent = [headers, ...csvRows].join("\n");
    downloadBlob(new Blob([csvContent], { type: "text/csv;charset=utf-8;" }),
                 exportFilename("csv"));
}

async function copyBenchmarkLink() {
    const button = document.getElementById("benchmarkShareButton");
    const originalLabel = button ? button.textContent : "";

    try {
        await navigator.clipboard.writeText(window.location.href);
        trackBenchmarkEvent("benchmark_share", { result_count: currentFilteredData.length });
        if (button) button.textContent = "Link copied";
    } catch (error) {
        window.prompt("Copy this filtered benchmark link:", window.location.href);
    }

    if (button) {
        window.setTimeout(() => {
            button.textContent = originalLabel;
        }, 1800);
    }
}
