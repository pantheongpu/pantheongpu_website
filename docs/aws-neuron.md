---
title: "AWS Neuron: Early Access"
description: Early validation results for AWS Trainium and Inferentia2 from Pantheon Neuron, a separate diagnostics suite for AWS's custom ML accelerators.
---

<div class="page-intro" markdown>
<p class="page-intro__eyebrow">Early access &middot; AWS Trainium &amp; Inferentia2</p>

# AWS Neuron accelerators

Pantheon diagnoses NVIDIA CUDA and AMD ROCm GPUs. AWS Trainium and Inferentia2 are not GPUs, they're a separate class of accelerator with their own toolchain, so we built a separate suite for them: [Pantheon Neuron](https://github.com/pantheongpu/pantheonneuron).
</div>

!!! warning "This is a status report, not a leaderboard"
    Pantheon Neuron is at v0.1.0. Of 25 planned workloads, 2 have a working kernel, and only one of those is verified end-to-end on hardware. Everything below comes from a single device of each type, not repeated runs across a fleet the way the [GPU benchmark database](benchmarks.md) is. Read it as where the suite stands today, not a comparison.

## Validation status

| Chip | Device | Status |
| --- | --- | --- |
| Inferentia2 (`inf2`) | NeuronCore-v2, 2 cores/device | **Verified**, inf2.xlarge, 2026-08-26 |
| Trainium1 (`trn1`) | NeuronCore-v2, 2 cores/device | **Verified**, trn1.2xlarge, 2026-08-27 |
| Trainium1n (`trn1n`) | NeuronCore-v2, 2 cores/device | Assumed, same silicon as trn1 with more network; not run |
| Trainium2 (`trn2`) | NeuronCore-v3, 8 cores/device | Assumed, least confident; not run |

Device generation does not track product naming: Trainium1 reports NeuronDevice v2 and Inferentia2 reports v3, but both run NeuronCore v2. The counter sets also differ between chips, so a kernel can't assume a counter that exists on one exists on the other.

## Kernel status

| Workload | Status |
| --- | --- |
| `baseline_metrics` | Telemetry only, no load |
| `memory_read` | **Verified on trn1.2xlarge** |
| `memory_write` | Written, primitives verified, this arrangement untested on hardware |
| Remaining 23 workloads | No kernel yet |

## What's actually been measured

Two numbers below came from a real kernel doing real work, not a diagnostic probe:

| Measurement | Value | Chip | Source |
| --- | --- | --- | --- |
| Sustained HBM read bandwidth | 264.15 GB/s | Trainium1 (trn1.2xlarge) | `memory_read` NKI kernel, 1024 MiB bf16 buffer, 20 passes, device barrier inside the timed region |
| Training throughput | 23.25 train-steps/s | Trainium1 (trn1.2xlarge) | 2-layer 1024&times;1024 MLP, batch 16, SGD, 50 steps; confirms the training capability path works |

Both are single runs on a single device, not medians over repeated samples. Read them as "this works, and roughly what it does," not as a Score to set against another chip.

!!! note "What we're deliberately not showing"
    An early bring-up pass also ran on inf2.xlarge and read counters like `effective_flops` and `mfu_estimated_percent` from `neuron-monitor`. We're not publishing those numbers here: the load behind them was an untuned matmul running at roughly 0.005% of the chip's compute capability, and Pantheon Neuron's own data file [flags them explicitly](https://github.com/pantheongpu/pantheonneuron/blob/main/data/baselines.json) as proof the counters are readable, not a measurement of Inferentia2's throughput. A number your own source says not to compare isn't a benchmark, so it stays out until a real kernel runs on inf2 the way `memory_read` did on trn1.

## Follow the build

Pantheon Neuron is developed in the open. Full methodology, kernel source, and raw probe data are in the repository.

[View Pantheon Neuron on GitHub](https://github.com/pantheongpu/pantheonneuron){ .md-button .md-button--primary }
[GPU benchmark database](benchmarks.md){ .md-button }

This page grows into a full leaderboard as more workloads get verified kernels. Until then, it's an honest snapshot of where the suite stands.
