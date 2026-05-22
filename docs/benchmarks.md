# Performance Database

Complete registry of stress test results.

<div class="benchmark-controls">
  
  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('gpuMenu')" aria-controls="gpuMenu" aria-expanded="false">GPUs &#9662;</button>
    <div id="gpuMenu" class="benchmark-menu" role="group" aria-label="GPU filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('testMenu')" aria-controls="testMenu" aria-expanded="false">Tests &#9662;</button>
    <div id="testMenu" class="benchmark-menu" role="group" aria-label="Test filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('versionMenu')" aria-controls="versionMenu" aria-expanded="false">Versions &#9662;</button>
    <div id="versionMenu" class="benchmark-menu benchmark-menu--compact" role="group" aria-label="Version filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('columnMenu')" aria-controls="columnMenu" aria-expanded="false">Columns &#9662;</button>
    <div id="columnMenu" class="benchmark-menu" role="group" aria-label="Column filters"></div>
  </div>

  <button type="button" class="benchmark-export-button" onclick="exportToCSV()">
    &#11123; Export CSV
  </button>

  <input type="text" id="textSearch" onkeyup="applyFilters()" placeholder="Search..." aria-label="Search benchmarks">

</div>

<div class="benchmark-chart-grid">
  <div class="chart-container">
    <div id="chart-memory-read"></div>
  </div>
  <div class="chart-container">
    <div id="chart-memory"></div>
  </div>
</div>

<div class="benchmark-table-wrap">
  <table id="benchmarkTable">
    <thead></thead>
    <tbody></tbody>
  </table>
</div>
