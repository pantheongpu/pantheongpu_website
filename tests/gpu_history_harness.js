// Runs docs/js/gpu-history.js against a stub DOM and a stub ApexCharts, so a
// test can see which series the page would draw for one card and workload.
//
//   node tests/gpu_history_harness.js docs/js/gpu-history.js runs.json <card> <test>
//
// It prints one JSON object: the series names, their points, and the status
// line. Only what the script touches is stubbed; this is not a browser.
"use strict";

const fs = require("fs");
const vm = require("vm");

const [scriptPath, dataPath, card, test] = process.argv.slice(2);
const runs = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const elements = {};
const listeners = {};

function element(id) {
    if (!elements[id]) {
        elements[id] = {
            id, value: "", innerHTML: "", textContent: "", children: [],
            appendChild(child) {
                this.children.push(child);
                if (this.children.length === 1) this.value = child.value;
            },
            addEventListener(name, handler) { (listeners[id] = listeners[id] || {})[name] = handler; },
        };
    }
    return elements[id];
}

let captured = null;

class ApexCharts {
    constructor(target, config) { captured = config; }
    render() {}
    destroy() {}
}

const documentStub = {
    currentScript: null,
    scripts: [],
    baseURI: "http://localhost/gpu-history/",
    body: { getAttribute: () => "slate" },
    getElementById: element,
    createElement: () => ({ value: "", textContent: "" }),
    querySelector: () => null,
    addEventListener(name, handler) { listeners.document = listeners.document || {}; listeners.document[name] = handler; },
};

const sandbox = {
    document: documentStub,
    console,
    Date, Map, Set, Array, Number, String, Math, Object, Promise, URL, JSON, RegExp,
    MutationObserver: class { observe() {} },
    fetch: async () => ({ ok: true, json: async () => runs }),
};
sandbox.window = sandbox;
sandbox.window.ApexCharts = ApexCharts;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(scriptPath, "utf8"), sandbox);

async function settle() {
    for (let i = 0; i < 5; i++) await new Promise(resolve => setImmediate(resolve));
}

(async () => {
    element("gpuHistoryChart");
    element("gpuHistoryCard");
    element("gpuHistoryTest");
    element("gpuHistoryStatus");
    listeners.document.DOMContentLoaded();
    await settle();

    // Pick the card, then the workload, the way the page's two selects do.
    element("gpuHistoryCard").value = card;
    listeners.gpuHistoryCard.change();
    element("gpuHistoryTest").value = test;
    captured = null;
    listeners.gpuHistoryTest.change();
    await settle();

    const series = captured
        ? captured.series.map(s => ({
            name: s.name,
            points: s.data.map(p => ({ version: p.version, y: p.y })),
        }))
        : [];
    process.stdout.write(JSON.stringify({
        series,
        status: element("gpuHistoryStatus").textContent,
    }));
})().catch(error => { console.error(error); process.exit(1); });
