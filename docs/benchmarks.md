# Performance Database

Complete registry of stress test results.

!!! note "Data provenance"
    Benchmark results are collected from third-party cloud and community systems, including providers such as Vast.ai and RunPod. They are not collected, certified, or endorsed by NVIDIA, AMD, or their employees.

[Compare GPU memory bandwidth across releases and devices.](benchmark-comparisons.md){ .md-button }

<div class="benchmark-controls">
  
  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('gpuMenu')" aria-controls="gpuMenu" aria-expanded="false" aria-haspopup="true">GPUs &#9662;</button>
    <div id="gpuMenu" class="benchmark-menu" role="group" aria-label="GPU filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('testMenu')" aria-controls="testMenu" aria-expanded="false" aria-haspopup="true">Tests &#9662;</button>
    <div id="testMenu" class="benchmark-menu" role="group" aria-label="Test filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('versionMenu')" aria-controls="versionMenu" aria-expanded="false" aria-haspopup="true">Versions &#9662;</button>
    <div id="versionMenu" class="benchmark-menu benchmark-menu--compact" role="group" aria-label="Version filters"></div>
  </div>

  <div class="benchmark-filter">
    <button type="button" class="benchmark-filter-button" onclick="toggleMenu('columnMenu')" aria-controls="columnMenu" aria-expanded="false" aria-haspopup="true">Columns &#9662;</button>
    <div id="columnMenu" class="benchmark-menu" role="group" aria-label="Column filters"></div>
  </div>

  <button type="button" class="benchmark-export-button" onclick="exportToCSV()">
    &#11123; Export CSV
  </button>

  <input type="search" id="textSearch" placeholder="Search..." aria-label="Search benchmarks" autocomplete="off">

</div>

<p id="benchmarkStatus" class="benchmark-status" role="status" aria-live="polite">Loading benchmark results…</p>

<div class="benchmark-table-wrap">
  <table id="benchmarkTable">
    <thead></thead>
    <tbody></tbody>
  </table>
</div>
