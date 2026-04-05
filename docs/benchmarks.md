# Performance Database

Complete registry of stress test results.

<div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
  
  <div style="position: relative; display: inline-block; flex: 1; min-width: 120px;">
    <button onclick="toggleMenu('gpuMenu')" style="width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; cursor: pointer;">GPUs &#9662;</button>
    <div id="gpuMenu" style="display: none; position: absolute; background-color: #1a1a1a; min-width: 200px; max-height: 400px; overflow-y: auto; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5); z-index: 2; padding: 10px; border: 1px solid #444; border-radius: 4px;"></div>
  </div>

  <div style="position: relative; display: inline-block; flex: 1; min-width: 120px;">
    <button onclick="toggleMenu('testMenu')" style="width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; cursor: pointer;">Tests &#9662;</button>
    <div id="testMenu" style="display: none; position: absolute; background-color: #1a1a1a; min-width: 200px; max-height: 400px; overflow-y: auto; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5); z-index: 2; padding: 10px; border: 1px solid #444; border-radius: 4px;"></div>
  </div>

  <div style="position: relative; display: inline-block; flex: 1; min-width: 120px;">
    <button onclick="toggleMenu('versionMenu')" style="width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; cursor: pointer;">Versions &#9662;</button>
    <div id="versionMenu" style="display: none; position: absolute; background-color: #1a1a1a; min-width: 150px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5); z-index: 2; padding: 10px; border: 1px solid #444; border-radius: 4px;"></div>
  </div>

  <div style="position: relative; display: inline-block; flex: 1; min-width: 120px;">
    <button onclick="toggleMenu('columnMenu')" style="width: 100%; padding: 10px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; cursor: pointer;">Columns &#9662;</button>
    <div id="columnMenu" style="display: none; position: absolute; background-color: #1a1a1a; min-width: 200px; max-height: 400px; overflow-y: auto; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5); z-index: 2; padding: 10px; border: 1px solid #444; border-radius: 4px;"></div>
  </div>

  <button onclick="exportToCSV()" style="padding: 10px; background: var(--pantheon-neon-green, #00e396); color: #000; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; flex: 1; min-width: 140px; transition: 0.2s;">
    &#11123; Export Excel
  </button>

  <input type="text" id="textSearch" onkeyup="applyFilters()" placeholder="Search..." style="padding: 10px; flex-grow: 3; min-width: 200px; background: #222; color: #fff; border: 1px solid #444; border-radius: 4px;">

</div>

<div style="overflow-x:auto;">
  <table id="benchmarkTable">
    <thead></thead>
    <tbody></tbody>
  </table>
</div>

<script src="../js/tables.js"></script>
