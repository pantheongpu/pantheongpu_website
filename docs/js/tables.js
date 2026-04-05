// --- CONFIGURATION: Define all available columns ---
const COL_DEFS = [
    { key: "gpu",         label: "GPU Model",   visible: true },
    { key: "manufacturer",label: "Vendor",      visible: true },
    { key: "test",        label: "Test Name",   visible: true },
    { key: "version",     label: "Ver",         visible: true },
    { key: "score",       label: "Score",       visible: true },
    { key: "throughput",  label: "Throughput",  visible: true },
    { key: "duration",    label: "Duration",    visible: true },
    { key: "temp_max",    label: "Peak Temp",   visible: true },
    { key: "power_max",   label: "Peak Power",  visible: true },
    { key: "clock_avg",   label: "Avg Clock",   visible: true },
    { key: "date",        label: "Date",        visible: true },
    // --- Hidden by default (Pro Metrics) ---
    { key: "efficiency",  label: "Efficiency (MB/J)", visible: false },
    { key: "temp_mem",    label: "Mem Temp",    visible: false },
    { key: "fan_max",     label: "Fan %",       visible: false },
    { key: "pcie_gen",    label: "PCIe Gen",    visible: false },
    { key: "pcie_width",  label: "PCIe Width",  visible: false },
    { key: "throttle",    label: "Limit Reason",visible: false },
    { key: "volts_core",  label: "Core (mV)",   visible: false },
    { key: "volts_soc",   label: "SoC (mV)",    visible: false },
    { key: "vram",     label: "VRAM",    visible: false },
    { key: "driver",   label: "Driver",  visible: false },
    { key: "toolkit",  label: "Toolkit", visible: false },
    
    { key: "power_limit", label: "TDP (W)",     visible: true }, 

    { key: "uuid",        label: "UUID",        visible: false },
    { key: "serial",      label: "Serial",      visible: false },
];

let rawData = [];
let bestRuns = [];
let currentFilteredData = [];
let currentSort = { key: 'score', dir: 'desc' };


document.addEventListener("DOMContentLoaded", function () {
    const dataUrl = "../assets/web_data.json";

    fetch(dataUrl)
        .then(response => response.json())
        .then(data => {
            rawData = data;
	    bestRuns = rawData;
	    //bestRuns = getBestRunsOnly(rawData);
            
            initColumnMenu();     
            populateFilters(bestRuns);
            applyFilters();
        })
        .catch(err => console.error("Error loading benchmark data:", err));
});

function getBestRunsOnly(data) {
    const groups = {};
    data.forEach(row => {
        const key = `${row.gpu}|${row.test}`;
        if (!groups[key] || parseFloat(row.score) > parseFloat(groups[key].score)) {
            groups[key] = row;
        }
    });
    return Object.values(groups);
}

// --- 2. Dynamic Table Rendering ---
function renderTable(data) {
    const table = document.getElementById("benchmarkTable");
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");

    thead.innerHTML = "";
    let headerRow = document.createElement("tr");
    headerRow.style.cursor = "pointer";

    COL_DEFS.forEach(col => {
        if (col.visible) {
            let th = document.createElement("th");
            th.innerHTML = `${col.label} &#8597;`;
            th.onclick = () => sortData(col.key);
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

    data.forEach(row => {
        const tr = document.createElement("tr");
        
        COL_DEFS.forEach(col => {
            if (col.visible) {
                let td = document.createElement("td");
                let val = row[col.key];

                // Formatting
                if (col.key === "score") {
                    val = (val === "N/A" || val === undefined) ? "N/A" : `${val} ${row.unit}`;
                    td.style.fontWeight = "bold";
                }
                else if (col.key === "throughput") {
                    val = (val !== "N/A" && val !== undefined && val !== 0) ? `${val} GB/s` : "N/A";
                }
                else if (col.key === "duration") {
                    val = val + "s";
                }
                else if (col.key === "gpu") {
                    td.style.fontWeight = "bold";
                }
                else if (col.key === "test") {
                    td.style.color = "var(--pantheon-test-color)";
                }
                else if (col.key.includes("temp")) {
                    td.style.color = getColorForTemp(val);
                    if(val) val += "°C";
                }
                else if (col.key.includes("power")) {
                    if(val !== "N/A" && val !== undefined) val += " W";
                }
                else if (col.key === "version") {
                    td.style.fontSize = "0.8em";
                    td.style.color = "#aaa";
                    if(!val) val = "Legacy";
                }
                
                if (val === undefined || val === 0 || val === "0") val = "N/A";
                td.textContent = val;
                tr.appendChild(td);
            }
        });
        tbody.appendChild(tr);
    });
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
    menu.innerHTML = "";

    // Determine if "Select All" should be checked on load
    let isAllChecked = defaultChecked === null || defaultChecked.length === items.length;

    // --- ADD SEARCH BAR ---
    // Only add a search bar if there are enough items to warrant searching
    if (items.length > 5) {
        let searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.placeholder = "Search...";
        searchInput.style.width = "100%";
        searchInput.style.marginBottom = "8px";
        searchInput.style.padding = "6px";
        searchInput.style.boxSizing = "border-box";
        searchInput.style.background = "#1a1a1a"; 
        searchInput.style.color = "#fff";
        searchInput.style.border = "1px solid #444";
        searchInput.style.borderRadius = "4px";
        
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
    selectAllDiv.style.borderBottom = "1px solid #444";
    
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

    // Extract and sort versions mathematically
    let versions = Array.from(versionSet);
    versions.sort((a, b) => {
        if (a === "Legacy") return 1;
        if (b === "Legacy") return -1;
        const vA = a.replace(/[^0-9.]/g, '').split('.').map(Number);
        const vB = b.replace(/[^0-9.]/g, '').split('.').map(Number);
        for (let i = 0; i < Math.max(vA.length, vB.length); i++) {
            if ((vA[i] || 0) > (vB[i] || 0)) return -1;
            if ((vA[i] || 0) < (vB[i] || 0)) return 1;
        }
        return 0;
    });

    // The first item is guaranteed to be the newest version
    const latestVersion = versions.length > 0 ? versions[0] : null;

    buildCheckboxMenu("gpuMenu", Array.from(gpuSet).sort());
    buildCheckboxMenu("testMenu", Array.from(testSet).sort());

    // Pass ONLY the latest version to be checked by default
    buildCheckboxMenu("versionMenu", versions, latestVersion ? [latestVersion] : null);
}

function applyFilters() {
    const searchVal = document.getElementById("textSearch").value.toLowerCase();
    const selectedGPUs = getCheckedValues("gpuMenu");
    const selectedTests = getCheckedValues("testMenu");
    const selectedVersions = getCheckedValues("versionMenu");

    let filtered = bestRuns.filter(row => {
        const ver = row.version || "Legacy";
        const gpuMatch = selectedGPUs.includes(row.gpu);
        const testMatch = selectedTests.includes(row.test);
        const versionMatch = selectedVersions.includes(ver);
        const searchMatch = Object.values(row).join(" ").toLowerCase().includes(searchVal);
        
        return gpuMatch && testMatch && versionMatch && searchMatch;
    });

    filtered.sort((a, b) => {
        let valA = a[currentSort.key];
        let valB = b[currentSort.key];

        if (valA === undefined || valA === "N/A") valA = -999999;
        if (valB === undefined || valB === "N/A") valB = -999999;

        let numA = parseFloat(valA);
        let numB = parseFloat(valB);

        if (!isNaN(numA) && !isNaN(numB)) {
            valA = numA;
            valB = numB;
        } else {
            valA = String(valA).toLowerCase();
            valB = String(valB).toLowerCase();
        }

        if (valA < valB) return currentSort.dir === 'asc' ? -1 : 1;
        if (valA > valB) return currentSort.dir === 'asc' ? 1 : -1;
        return 0;
    });

    currentFilteredData = filtered;
    renderTable(filtered);
}

// --- Menu Toggling ---
function toggleMenu(menuId) {
    const menus = ["gpuMenu", "testMenu", "versionMenu", "columnMenu"];
    menus.forEach(id => {
        const m = document.getElementById(id);
        if (id === menuId) {
            m.style.display = m.style.display === "block" ? "none" : "block";
        } else {
            if (m) m.style.display = "none";
        }
    });
}

function initColumnMenu() {
    const menu = document.getElementById("columnMenu");
    menu.innerHTML = "";

    // --- Create "Select All" Checkbox ---
    let selectAllDiv = document.createElement("div");
    selectAllDiv.style.marginBottom = "8px";
    selectAllDiv.style.paddingBottom = "8px";
    selectAllDiv.style.borderBottom = "1px solid #444";
    
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

// Close menus if clicked outside
window.onclick = function(event) {
    if (!event.target.matches('button')) {
        const menus = ["gpuMenu", "testMenu", "versionMenu", "columnMenu"];
        menus.forEach(id => {
            const menu = document.getElementById(id);
            if (menu && menu.style.display === "block" && !menu.contains(event.target)) {
                menu.style.display = "none";
            }
        });
    }
}

function getColorForTemp(temp) {
    if (!temp || temp === "N/A") return "var(--pantheon-text-default)";
    if (temp < 60) return "var(--pantheon-temp-good)";
    if (temp < 80) return "var(--pantheon-temp-warn)";
    if (temp >= 80) return "var(--pantheon-temp-crit)";
    return "var(--pantheon-text-default)";
}

// --- 6. Export to Excel (CSV) ---
function exportToCSV() {
    if (currentFilteredData.length === 0) {
        alert("No data available to export!");
        return;
    }

    // 1. Get the currently visible columns to build the header
    const visibleCols = COL_DEFS.filter(c => c.visible);
    const headers = visibleCols.map(c => `"${c.label}"`).join(",");

    // 2. Map the filtered data rows
    const csvRows = currentFilteredData.map(row => {
        return visibleCols.map(col => {
            let val = row[col.key];

            // Apply the exact same formatting as the HTML table
            if (col.key === "score") {
                val = (val === "N/A" || val === undefined) ? "N/A" : `${val} ${row.unit}`;
            } else if (col.key === "throughput") {
                val = (val !== "N/A" && val !== undefined && val !== 0) ? `${val} GB/s` : "N/A";
            } else if (col.key === "duration") {
                val = val + "s";
            } else if (col.key.includes("temp") && val) {
                val += "°C";
            } else if (col.key.includes("power") && val !== "N/A" && val !== undefined) {
                val += " W";
            } else if (val === undefined || val === 0 || val === "0") {
                val = "N/A";
            }

            // Escape quotes by doubling them (CSV standard) and wrap in quotes
            let strVal = String(val).replace(/"/g, '""');
            return `"${strVal}"`;
        }).join(",");
    });

    // 3. Combine headers and rows
    const csvContent = [headers, ...csvRows].join("\n");

    // 4. Create a Blob and trigger the download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    // Create a dynamic filename with today's date
    const dateStr = new Date().toISOString().split('T')[0];
    link.setAttribute("href", url);
    link.setAttribute("download", `pantheon_benchmarks_${dateStr}.csv`);

    // Append, click, and cleanup
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
