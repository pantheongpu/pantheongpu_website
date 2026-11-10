// Runs docs/js/tables.js against a stub DOM so a test can see what the benchmark explorer would show for a few rows:
// the text of each cell, the spreadsheet header and cells, which columns the column chooser offers, and which late
// columns are on by default.
//
//   node tests/tables_columns_harness.js docs/js/tables.js input.json
//
// input.json: {"rows": [...], "cells": [[rowIndex, key], ...], "xlsx": {"keys": [...], "row": rowIndex}}
// It prints one JSON object. Only what the script touches is stubbed; this is not a browser.
"use strict";

const fs = require("fs");
const vm = require("vm");

const [scriptPath, inputPath] = process.argv.slice(2);
const input = JSON.parse(fs.readFileSync(inputPath, "utf8"));

function makeElement(id) {
    return {
        id, innerHTML: "", textContent: "", value: "", style: {}, children: [],
        appendChild(child) { this.children.push(child); return child; },
        setAttribute() {}, addEventListener() {}, removeAttribute() {},
        classList: { add() {}, remove() {}, toggle() {} },
    };
}

const elements = {};
const document = {
    getElementById(id) { return (elements[id] = elements[id] || makeElement(id)); },
    createElement() { return makeElement(null); },
    createTextNode(text) { return { text }; },
    addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; },
    body: makeElement("body"), currentScript: null, scripts: [],
};
const context = vm.createContext({
    document, console, URL, URLSearchParams, setTimeout, clearTimeout,
    window: { location: { search: "", href: "http://localhost/benchmarks/" }, addEventListener() {} },
    fetch: () => new Promise(() => {}),
});

vm.runInContext(fs.readFileSync(scriptPath, "utf8"), context);
context.__rows = input.rows;
const run = code => vm.runInContext(code, context);

run("rawData = __rows;");
const out = {};
out.cells = (input.cells || []).map(([index, key]) => run(`formatCellValue(__rows[${index}], ${JSON.stringify(key)})`));
out.lateKeys = run("COL_DEFS.filter(c => c.late).map(c => c.key)");
out.lateVisibleByDefault = run("COL_DEFS.filter(c => c.late && c.visible).map(c => c.key)");
out.lateUnitKeys = run("Object.keys(LATE_COLUMN_UNITS)");

run("initColumnMenu();");
out.chooser = elements["columnMenu"].children.slice(1).map(div => div.children[0].children[1].text);

if (input.xlsx) {
    const keys = JSON.stringify(input.xlsx.keys);
    out.xlsxHeader = run(`xlsxHeader(COL_DEFS.filter(c => ${keys}.includes(c.key)))`);
    out.xlsxRow = run(`xlsxRow(__rows[${input.xlsx.row}], COL_DEFS.filter(c => ${keys}.includes(c.key)))`);
}
process.stdout.write(JSON.stringify(out));
