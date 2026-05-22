# Tracing the Tensor Lineage: How Ampere, Hopper, and Blackwell Scale at the Silicon Level

<div class="report-byline">
  <span>By Saqib Khan</span>
  <a href="https://www.linkedin.com/in/saqib-khan-2a0ab164/">LinkedIn</a>
</div>

When NVIDIA introduced the Volta architecture in 2017, it quietly changed the trajectory of the entire semiconductor industry by introducing the Tensor Core. But it was not until the subsequent data center architectures that we saw what this silicon was truly built to do.

To measure exactly how NVIDIA's architectural philosophy has scaled over the last few generations, we deployed Pantheon, a custom diagnostic suite of low-level, orthogonal micro-kernels designed to bypass driver abstractions and directly attack specific hardware subsystems.

By analyzing the telemetry from Ampere, represented by the A100, Hopper, represented by the H100, and the latest Blackwell, represented by the B200, we can map the exact physical evolution of the modern AI accelerator, exposing exactly where NVIDIA shifted its transistor budget.

## 1. The Tensor Core Explosion and Plateau

The primary differentiator of modern NVIDIA architectures is how aggressively they process dense matrix math. By running Pantheon's `tensor_virus`, which strictly isolates and saturates the matrix math pipelines with continuous FP16 Fused Multiply-Add instructions, we see an interesting narrative.

**Third-Gen Ampere A100:** The A100 was the undisputed king of the early AI boom. Under total saturation, its 3rd-generation Tensor Cores managed 34.35 TFLOPS of sustained FP16 compute.

**Fourth-Gen Hopper H100:** Hopper fundamentally redesigned the Streaming Multiprocessor to feed the beast. Under the exact same workload, the H100 delivered 57.84 TFLOPS, a massive approximately 68% physical throughput increase over Ampere.

**The FP16 Plateau Blackwell B200:** Interestingly, running standard FP16 math on the B200 yielded 58.48 TFLOPS, a shockingly marginal bump over Hopper. This exposes NVIDIA's architectural pivot: Blackwell's true power lies not in legacy FP16, but in its physically distinct FP8 and FP4 hardware Transformer Engines, requiring entirely new instruction sets to unlock its density.

<figure class="report-figure">
  <figcaption>FP16 tensor throughput rises sharply from Ampere to Hopper, then plateaus on Blackwell.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="FP16 tensor throughput chart" viewBox="0 0 760 230">
    <text x="0" y="22" class="report-chart-title">FP16 Tensor Throughput (TFLOPS)</text>
    <text x="0" y="68">A100</text><rect x="150" y="48" width="320" height="26" rx="5"></rect><text x="486" y="67">34.35</text>
    <text x="0" y="118">H100</text><rect x="150" y="98" width="539" height="26" rx="5"></rect><text x="706" y="117">57.84</text>
    <text x="0" y="168">B200</text><rect x="150" y="148" width="545" height="26" rx="5"></rect><text x="712" y="167">58.48</text>
  </svg>
</figure>

## 2. The Vector Math Reality: INT32 and Transcendentals

AI is not purely matrix multiplication. Operations like memory indexing, layer normalization, and activation functions such as Softmax and GELU heavily rely on Integer INT32 and Special Function Units. Pantheon exposes how NVIDIA treats these legacy pipelines.

**The Hopper Leap:** When running the `sfu_stress` test, which hammers high-latency transcendental math like EXP and RSQRT, the H100 delivered 3.73 TFLOPS, more than double the A100's 1.67 TFLOPS. Similarly, the `int_virus` test showed INT32 performance jumping from 21.90 TOPS on A100 to 37.62 TOPS on H100. Hopper was a massive across-the-board upgrade.

**The Blackwell Specialization:** Conversely, the B200 only saw marginal gains in these areas, hitting 4.10 TFLOPS on SFU and 41.93 TOPS on INT32. NVIDIA is heavily indicating that the transistor budget on Blackwell was dedicated entirely to memory and low-precision AI hardware, leaving the traditional vector and integer ALUs virtually identical to Hopper's.

## 3. Cache Arbiters and the Atomic Bottleneck

Deep learning frequently requires massive scatter/gather operations across memory, which rely on hardware Atomic Read-Modify-Write instructions. If the L2 cache arbiters lock up, the entire GPU stalls, no matter how fast the Tensor Cores are. This is where Blackwell hides its greatest architectural leap.

**Ampere and Hopper:** During Pantheon's `atomic_virus`, which forces thousands of concurrent, wide-stride atomic updates, the A100 managed 171,532 MAPS, or Million Atomic Operations Per Second. The H100 offered a solid improvement, reaching 239,792 MAPS.

**The Blackwell Breakthrough:** The B200 absolutely obliterated this test, jumping to an astonishing 572,143 MAPS, more than double the Hopper architecture. This telemetry proves NVIDIA fundamentally redesigned the L2 cache pathways and atomic arbiters in Blackwell to ensure the execution engines are never starved by memory locks.

<figure class="report-figure">
  <figcaption>Atomic throughput is where Blackwell's cache fabric makes the biggest jump.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="Atomic throughput chart" viewBox="0 0 760 230">
    <text x="0" y="22" class="report-chart-title">Atomic Throughput (MAPS)</text>
    <text x="0" y="68">A100</text><rect x="150" y="48" width="164" height="26" rx="5"></rect><text x="330" y="67">171,532</text>
    <text x="0" y="118">H100</text><rect x="150" y="98" width="228" height="26" rx="5"></rect><text x="394" y="117">239,792</text>
    <text x="0" y="168">B200</text><rect x="150" y="148" width="545" height="26" rx="5"></rect><text x="712" y="167">572,143</text>
  </svg>
</figure>

## 4. Feeding the Beast: The HBM Memory Wall

You cannot quadruple compute without quadrupling the data pipes. Testing the High Bandwidth Memory controllers across these architectures reveals the brute-force engineering required to feed modern models.

**Ampere HBM2e:** Pantheon's aggressive read kernels saturated the A100's physical bus at 1,912 GB/s. At the time, breaking the 1.5 TB/s barrier was a monumental achievement.

**Hopper HBM3:** The H100 widened the highway significantly, pushing a verifiable 3,162 GB/s of true physical read throughput.

**Blackwell HBM3e:** The B200 completely shatters previous limits, achieving an astonishing 7,213 GB/s. To move 7.2 terabytes of data every single second across a silicon interposer is a marvel of signal integrity and physical packaging.

<figure class="report-figure">
  <figcaption>HBM bandwidth scales faster than legacy FP16 throughput.</figcaption>
  <svg class="report-chart-svg" role="img" aria-label="HBM bandwidth chart" viewBox="0 0 760 230">
    <text x="0" y="22" class="report-chart-title">HBM Read Bandwidth (GB/s)</text>
    <text x="0" y="68">A100</text><rect x="150" y="48" width="144" height="26" rx="5"></rect><text x="310" y="67">1,912</text>
    <text x="0" y="118">H100</text><rect x="150" y="98" width="239" height="26" rx="5"></rect><text x="405" y="117">3,162</text>
    <text x="0" y="168">B200</text><rect x="150" y="148" width="545" height="26" rx="5"></rect><text x="712" y="167">7,213</text>
  </svg>
</figure>

## 5. Thermal Density and the Death of Air Cooling

Perhaps the most telling metric of architectural evolution is how the silicon manages heat. As we pack more transistors into roughly the same reticle limit, thermal density skyrockets.

**The Air-Cooled Era A100:** Under extreme integer stress testing, the A100 maxed out at 396 Watts while peaking at a very manageable 63 C. It was the pinnacle of passive server-rack cooling.

**The Efficiency Masterclass H100:** Hopper draws significantly more power, peaking at 526.9 Watts under our heaviest loads, but its internal thermal routing is so efficient that it peaked at just 52.0 C.

**The Liquid Future B200:** Blackwell represents the threshold where traditional cooling physics tap out. Operating under a massive 1000 W limit, the B200 requires direct-to-chip liquid cooling. Despite the insane wattage, the liquid loop kept the B200's core absolutely locked down, hovering between 35 C and 47 C even under the most brutal combinatorial sweeps.

## The Takeaway

Tracing the lineage from Ampere to Blackwell reveals a clear physical reality: we are no longer just scaling clock speeds or adding more cores. NVIDIA's architectural evolution is defined by a shift away from traditional vector math towards hyper-specialized low-precision hardware, radically wider atomic and memory pathways, and the absolute necessity of liquid cooling to sustain modern AI power density.

[Read the documentation and run the suite](https://pantheongpu.com/)
