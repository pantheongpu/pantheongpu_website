# Tracing the Tensor Lineage: Ampere, Hopper and Blackwell Under the Same Kernels

<div class="report-byline">
  <span>By Saqib Khan</span>
  <a href="https://www.linkedin.com/in/saqib-khan-2a0ab164/">LinkedIn</a>
</div>

Every new data center GPU arrives with a headline number that is hard to check. We wanted the other kind of number: the same small kernel, run the same way, on every generation we could rent, with the card's own counters recording what happened. Pantheon is our open source suite for exactly that. Each workload leans on one part of the chip and leaves the rest alone.

This is what it found across five cards: the A100, the H100 in both its PCIe and SXM forms, the GH200, and the B200. Where we had more than one card of a model, the bar is the median across cards and the count is on the chart.

## 1. The tensor cores

Our matrix kernel feeds the tensor cores FP16 inputs with FP32 accumulation through the WMMA interface, the one interface that works on every generation, and checks the accumulator bit for bit against a golden pass.

<figure class="report-figure">
  <figcaption>Matrix throughput through the WMMA interface, the path every generation supports. Hopper doubles Ampere; Blackwell holds the line on this path and keeps its new instructions for itself.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="Matrix throughput chart" viewBox="0 0 760 298">
    <text x="0" y="22" class="report-chart-title">Tensor core matrix throughput, FP16 in, FP32 accumulate (TFLOPS)</text>
    <text x="0" y="68">A100 SXM4</text><rect x="150" y="48" width="276" height="26" rx="5"></rect><text x="442" y="67">584 (20 cards)</text>
    <text x="0" y="118">H100 PCIe</text><rect x="150" y="98" width="410" height="26" rx="5"></rect><text x="576" y="117">867 (4 cards)</text>
    <text x="0" y="168">H100 SXM5</text><rect x="150" y="148" width="545" height="26" rx="5"></rect><text x="711" y="167">1,152 (11 cards)</text>
    <text x="0" y="218">GH200</text><rect x="150" y="198" width="540" height="26" rx="5"></rect><text x="706" y="217">1,142 (7 cards)</text>
    <text x="0" y="268">B200</text><rect x="150" y="248" width="509" height="26" rx="5"></rect><text x="675" y="267">1,075 (1 card)</text>
  </svg>
</figure>

Hopper doubles Ampere: 584 TFLOPS on the A100 becomes 1,152 on the H100 SXM5, with the GH200 alongside it. The PCIe H100, on the same die with a 350 W limit instead of 700 W, delivers 867, three quarters of the module.

Blackwell does not move on this path. The B200 lands at 1,075, level with Hopper. That is not the chip running out of steam. Blackwell's new tensor instructions, and the FP8 and FP4 formats that carry its headline figures, are simply not reachable through the interface that older generations share. A kernel written for the common path gets Hopper-class throughput on Blackwell, and nothing more. Anyone porting code between the two should know which path they are on.

## 2. The vector pipes

Matrix math is only part of a model. Layer norms, activations, indexing and the glue between layers run on the ordinary integer and floating point pipes, and on the special function units that handle transcendentals.

<figure class="report-figure">
  <figcaption>Integer throughput. Each generation adds to it, and the PCIe H100 gives up a quarter of the SXM part.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="INT32 throughput chart" viewBox="0 0 760 298">
    <text x="0" y="22" class="report-chart-title">INT32 throughput (TOPS)</text>
    <text x="0" y="68">A100 SXM4</text><rect x="150" y="48" width="274" height="26" rx="5"></rect><text x="440" y="67">21.1 (18 cards)</text>
    <text x="0" y="118">H100 PCIe</text><rect x="150" y="98" width="347" height="26" rx="5"></rect><text x="513" y="117">26.7 (3 cards)</text>
    <text x="0" y="168">H100 SXM5</text><rect x="150" y="148" width="471" height="26" rx="5"></rect><text x="637" y="167">36.2 (8 cards)</text>
    <text x="0" y="218">GH200</text><rect x="150" y="198" width="468" height="26" rx="5"></rect><text x="634" y="217">36.0 (5 cards)</text>
    <text x="0" y="268">B200</text><rect x="150" y="248" width="545" height="26" rx="5"></rect><text x="711" y="267">41.9 (1 card)</text>
  </svg>
</figure>

<figure class="report-figure">
  <figcaption>Special function units. Hopper doubled Ampere; Blackwell adds another fifth.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="SFU throughput chart" viewBox="0 0 760 298">
    <text x="0" y="22" class="report-chart-title">Transcendental throughput, sin, cos, exp, log, rsqrt (TFLOPS)</text>
    <text x="0" y="68">A100 SXM4</text><rect x="150" y="48" width="208" height="26" rx="5"></rect><text x="374" y="67">1.6 (7 cards)</text>
    <text x="0" y="118">H100 PCIe</text><rect x="150" y="98" width="342" height="26" rx="5"></rect><text x="508" y="117">2.6 (3 cards)</text>
    <text x="0" y="168">H100 SXM5</text><rect x="150" y="148" width="459" height="26" rx="5"></rect><text x="625" y="167">3.5 (8 cards)</text>
    <text x="0" y="218">GH200</text><rect x="150" y="198" width="453" height="26" rx="5"></rect><text x="619" y="217">3.4 (5 cards)</text>
    <text x="0" y="268">B200</text><rect x="150" y="248" width="545" height="26" rx="5"></rect><text x="711" y="267">4.1 (1 card)</text>
  </svg>
</figure>

Here the generations keep climbing. INT32 goes from 21 TOPS on Ampere to 36 on Hopper and 42 on Blackwell. Transcendentals go from 1.6 TFLOPS to 3.5 and then 4.1. The Hopper step is the large one, roughly a doubling; Blackwell adds another fifth. The PCIe H100 gives up about a quarter of the SXM module on both, which is the power limit doing its job.

## 3. Double precision

<figure class="report-figure">
  <figcaption>Double precision. The big step was Hopper; Blackwell adds a little.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="FP64 throughput chart" viewBox="0 0 760 298">
    <text x="0" y="22" class="report-chart-title">FP64 throughput (TFLOPS)</text>
    <text x="0" y="68">A100 SXM4</text><rect x="150" y="48" width="229" height="26" rx="5"></rect><text x="395" y="67">9.6 (20 cards)</text>
    <text x="0" y="118">H100 PCIe</text><rect x="150" y="98" width="390" height="26" rx="5"></rect><text x="556" y="117">16.3 (4 cards)</text>
    <text x="0" y="168">H100 SXM5</text><rect x="150" y="148" width="519" height="26" rx="5"></rect><text x="685" y="167">21.8 (10 cards)</text>
    <text x="0" y="218">GH200</text><rect x="150" y="198" width="522" height="26" rx="5"></rect><text x="688" y="217">21.9 (7 cards)</text>
    <text x="0" y="268">B200</text><rect x="150" y="248" width="545" height="26" rx="5"></rect><text x="711" y="267">22.9 (1 card)</text>
  </svg>
</figure>

FP64 follows the same shape: 9.6 TFLOPS on the A100, 21.8 on the H100 SXM5, 22.9 on the B200. Hopper was the leap and Blackwell is an increment. For scientific codes that live in double precision, the Hopper and Blackwell modules are within five percent of each other, and the PCIe H100 at 16.3 is the value option.

## 4. The memory wall

<figure class="report-figure">
  <figcaption>Memory bandwidth outpaces everything else on this page. Each bar also shows the share of the datasheet figure a plain read kernel reaches.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="HBM bandwidth chart" viewBox="0 0 760 298">
    <text x="0" y="22" class="report-chart-title">HBM read bandwidth (GB/s)</text>
    <text x="0" y="68">A100 SXM4</text><rect x="150" y="48" width="116" height="26" rx="5"></rect><text x="282" y="67">1,496 (96% of datasheet)</text>
    <text x="0" y="118">H100 PCIe</text><rect x="150" y="98" width="152" height="26" rx="5"></rect><text x="318" y="117">1,971 (99% of datasheet)</text>
    <text x="0" y="168">H100 SXM5</text><rect x="150" y="148" width="235" height="26" rx="5"></rect><text x="401" y="167">3,048 (91% of datasheet)</text>
    <text x="0" y="218">GH200</text><rect x="150" y="198" width="286" height="26" rx="5"></rect><text x="452" y="217">3,705 (93% of datasheet)</text>
    <text x="0" y="268">B200</text><rect x="150" y="248" width="545" height="26" rx="5"></rect><text x="711" y="267">7,058 (88% of datasheet)</text>
  </svg>
</figure>

This is where the generations really separate. A plain read kernel pulls 1,496 GB/s from the A100's HBM2e, 3,048 from the H100's HBM3, 3,705 from the GH200, and 7,058 from the B200's HBM3e. From Ampere to Blackwell that is nearly five times the bandwidth, against roughly double the matrix throughput and double the vector throughput. NVIDIA's transistor budget went to the memory system, and the numbers say so plainly.

Every card also gets close to its datasheet. The HBM parts read at 88 to 99 percent of the published figure, the PCIe H100 nearest to its number and the B200 furthest from its 8 TB/s. That gap on the B200 is one card and a short run; we will revisit it.

## 5. Power and heat

Under the matrix kernel the A100 averages 201 W of its 400 W limit and peaks at 56 C. The H100 SXM5 averages 439 W of 700 and peaks at 53 C. The GH200 averages 396 W of a 900 W module budget at 59 C. The PCIe H100 is the one that runs warm: 276 W of 350 and 68 C, up to 79 C on the hottest card, because a 350 W air-cooled card in a rented server has far less cooling behind it than a module on a baseboard. Under the integer kernel, the heaviest load here, the SXM H100 draws 537 W and still peaks at only 58 C.

The B200 is a different world. Its runs stayed between 36 and 46 C throughout, including under the matrix and integer kernels, because the machine was liquid cooled. At a 1,000 W module budget there is no other way to run it, and the temperatures show what a cold plate buys.

## What this says

Across three generations the pattern is consistent. Hopper was the broad upgrade: matrix, vector, double precision and memory all roughly doubled over Ampere. Blackwell kept the vector and FP64 gains modest, left the common matrix path where Hopper had it, and put the budget into memory bandwidth and into new low-precision instructions that only new code can reach. If your kernels are written for the shared path, an H100 module and a B200 are close on compute and far apart on bandwidth. If they are written for Blackwell, that is a different measurement, and one we have not made yet.

## How we measured

Pantheon 1.0.10 through 1.2.2 on single-GPU instances rented from public clouds. A100 SXM4 40 GB, up to 20 cards. H100 PCIe, 4. H100 SXM5 80 GB, up to 11. GH200, up to 7. The count behind each bar is on its chart, because not every card ran every workload. Runs of 300 seconds per workload at 99 percent of free VRAM, one card per machine; each bar is the median across cards of that card's own median. The B200 figures come from one card and 30-second runs on an earlier build of the suite. The five kernels on this page have not changed since that build, which is why the B200 can share these charts; two other kernels have, and they are not used here. Two H100s that were thermally impaired when we rented them are excluded. Every run is public at pantheongpu.com under the card's UUID, and anyone can rerun any of it with `pantheon --test mma_virus --duration 300`.

[Read the documentation and run the suite](https://pantheongpu.com/)
