# Benchmark Explorer

<div class="page-intro">
  <p class="page-intro__eyebrow">Performance database</p>
  <p>Explore submitted Pantheon runs across hardware, driver stacks, releases, and targeted workloads. Filter for the signal you need, then export the slice for your own analysis.</p>
</div>

!!! note "Data provenance"
    Benchmark results are collected from third-party cloud and community systems, including providers such as Vast.ai and RunPod. They are not collected, certified, or endorsed by NVIDIA, AMD, or their employees.

!!! note "Runs without a result"
    Some runs have no result to publish, and none of them appears here as a
    zero. Each is listed with its reason in
    [unsupported_workloads.json](assets/unsupported_workloads.json) under one of
    three statuses:

    - `UNSUPPORTED`: the card cannot run the workload at all (for example, an
      A100 has no video encoder).
    - `NO_MEASUREMENT`: the workload reported zero throughput, so its measured
      path never ran (ray tracing without an OptiX SDK, video encode without an
      encoder).
    - `FAILED`: the workload reported a failure (status FAIL, unit ERR). The
      report does not say why, so a failure is not a statement about the card.

[Compare leaders by workload](benchmark-comparisons.md){ .md-button .md-button--primary }
[Read the benchmark methodology](methodology.md){ .md-button }

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
    Export CSV
  </button>

  <button type="button" class="benchmark-export-button" onclick="exportToXLSX()">
    Export XLSX
  </button>

  <button type="button" id="benchmarkShareButton" class="benchmark-share-button" onclick="copyBenchmarkLink()">
    Copy filtered link
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
