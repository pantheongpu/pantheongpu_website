---
hide:
  - navigation
---

# Per-card history

<div class="page-intro">
  <p class="page-intro__eyebrow">One card over time</p>
  <p>The leaderboard keeps a single row per card, workload and release: the best run wins, and every later run is dropped. That is the right view for comparing hardware, and the wrong one for watching a card age. This page plots every run of one card instead, so a part that is slowing down shows up as a slope rather than disappearing behind its own best result.</p>
</div>

!!! note "Reading these charts"
    Cards are identified by the GPU UUID the driver reports, published as-is.
    A UUID names one physical card, not the machine it sat in, and it follows
    the card across releases and owners, which is what a history needs. Host
    details (hostnames, network information) are removed before a report is
    published. Cards from early reports that carried no UUID are grouped by
    model, memory size and driver instead and labelled as having no GPU ID.

    When a workload's metric changed between releases, each unit is drawn as its
    own series. Values in different units are not comparable, and joining them
    into one line would show a step that is a change of units rather than a
    change in the hardware.

<div class="benchmark-controls">
  <label for="gpuHistoryCard">Card</label>
  <select id="gpuHistoryCard" aria-label="Select a GPU to plot"></select>

  <label for="gpuHistoryTest">Workload</label>
  <select id="gpuHistoryTest" aria-label="Select a workload to plot"></select>
</div>

<p id="gpuHistoryStatus" class="benchmark-status" role="status" aria-live="polite"></p>

<div id="gpuHistoryChart"></div>

Runs come from the same reports as the leaderboard. A single benchmark writes
both a per-test record and a summary repeating it, so those are collapsed to one
point; two separate runs are only merged when they share a timestamp as well as
a score, at which point they are the same measurement counted twice.

[Back to the benchmark explorer](benchmarks.md){ .md-button }
