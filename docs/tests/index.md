# Test Documentation Hub

Pantheon includes dozens of highly specialized micro-kernels designed to isolate and stress specific components of modern GPU architectures. Select a test below to view a deep dive into its execution mechanics, target subsystems, and common failure symptoms.

---

## Core & Compute
Tests designed to maximize Thermal Design Power (TDP), test specific ALU pipelines, and stress voltage regulator modules (VRMs).

<div class="grid cards" markdown>

-   [:material-fire: **Omni Virus**](omni_virus.md)
    ---
    Asynchronously overlaps Memory memory sweeps, FP16 Tensor math, FP32 Vector math, and SFU transcendental math to achieve 100% pipeline saturation.

-   [:material-flash: **Voltage Virus**](voltage.md)
    ---
    Uses volatile math to force rapid ALU state switching, inducing massive di/dt droop on the Logic Rail (VDD_GFX).

-   [:material-waveform: **Pulse Virus**](pulse_virus.md)
    ---
    Induces rapid transient power spikes by violently toggling the GPU between 100% heavy FMA load and 0% sleep states at 10Hz.

-   [:material-matrix: **Tensor Virus**](tensor_virus.md)
    ---
    Saturates matrix math pipelines by spamming continuous FP16 (Half-Precision) Fused Multiply-Add (FMA) instructions.

-   [:material-cpu-64-bit: **MMA Virus**](mma_virus.md)
    ---
    Leverages physical WMMA (Warp Matrix Multiply and Accumulate) instructions to push hardware Matrix Cores to their absolute thermal limits.

-   [:material-Vector-combine: **Transformer Virus**](transformer_virus.md)
    ---
    Leverages low-level PTX and MFMA intrinsics to execute relentless FP8/FP4 Matrix Multiply-Accumulate operations on next-gen Transformer Engines.

-   [:material-calculator-variant: **FP64 Chokehold**](fp64_virus.md)
    ---
    Unleashes a barrage of Double Precision (FP64) FMAs to expose the physical limits of the FP64 datapath.

-   [:material-numeric: **Integer Virus**](int_virus.md)
    ---
    Saturates the INT32 ALUs using bit-bashing, bitwise rotations, and XOR cascades to stress integer-specific datapaths.

-   [:material-function-variant: **SFU Virus**](sfu_stress.md)
    ---
    Hammers the math pipelines with complex, high-latency transcendental functions (SIN, COS, EXP, LOG, RSQRT).

-   [:material-fire-alert: **Incinerator**](incinerator.md)
    ---
    Maximizes thermal density by simultaneously running Vector ALU math and forcing intentional SRAM/LDS bank conflicts.

</div>

---

## Fixed-Function & Accelerators
Tests targeting specialized hardware blocks and "dark silicon" outside of the primary compute shaders.

<div class="grid cards" markdown>

-   [:material-ray-vertex: **RT Virus**](rt_virus.md)
    ---
    Floods dedicated Ray Tracing cores with billions of non-coherent intersection tests to force continuous BVH traversal.

-   [:material-video-input-component: **Media Encoder Virus**](media_enc_virus.md)
    ---
    Feeds high-entropy noise into hardware video encoders (NVENC/VCN) to stress fixed-function edge silicon.

</div>

---

## Memory & Cache
Tests targeting VRAM bandwidth, Memory physical characteristics, queue limits, and cache arbiters.

<div class="grid cards" markdown>

-   [:material-lock-pattern: **Atomic Virus**](atomic_virus.md)
    ---
    Overwhelms the L2 cache arbiters by forcing thousands of concurrent, wide-stride Atomic Read-Modify-Write operations.

-   [:material-chart-timeline: **Cache Latency**](cache_lat.md)
    ---
    Defeats hardware prefetchers by performing fully dependent pointer-chasing (random walks) across the memory pool.

-   [:material-memory: **Memory Write (Aggressive)**](memory_write_agg.md)
    ---
    Maximizes write operations by bypassing L2 cache and aggressively unrolling instructions with alternating bit patterns to induce signal crosstalk.

-   [:material-memory: **Memory Write (Standard)**](memory_write.md)
    ---
    Tests standard sequential VRAM bandwidth using Non-Temporal Stores with rail-to-rail patterns.

-   [:material-database-search: **Memory Read (Aggressive)**](memory_read_agg.md)
    ---
    Maximizes read operations using heavily unrolled, volatile pointer accesses to force continuous, direct memory fetches without caching.

-   [:material-database-search: **Memory Read (Standard)**](memory_read.md)
    ---
    Tests standard sequential VRAM read bandwidth using volatile reads decomposed into 32-bit chunks.

-   [:material-table-row: **Memory Bank Thrasher**](memory_bank_thrash.md)
    ---
    Forces continuous row-buffer misses by striding memory reads across exact 2MB page boundaries.

-   [:material-grain: **Memory Cache Fracturing**](memory_cache_fracture.md)
    ---
    Forces massive uncoalesced reads (256-byte stride offset) to intentionally overwhelm the Unified Memory Controller (UMC) queues.

-   [:material-thermometer-lines: **Memory Retention Bake**](memory_retention_bake.md)
    ---
    Writes a payload, runs a heavy ALU virus to heat the die, then checks if the physical Memory capacitors leaked charge due to thermal stress.

-   [:material-gradient-vertical: **Memory Asymmetric Thermal**](memory_thermal_asym.md)
    ---
    Hammers a tiny, isolated memory region while drawing maximum compute power to create a severe physical temperature gradient across the package.

</div>

---

## Interconnect & Architecture
Tests targeting bus interfaces, crossbars, hardware schedulers, and memory management units.

<div class="grid cards" markdown>

-   [:material-server-network: **P2P Thrasher**](p2p_thrasher.md)
    ---
    Saturates NVLink, Infinity Fabric, and PCIe bridges with massive peer-to-peer DMA copies between multiple GPUs.

-   [:material-layers-triple: **TLB Avalanche**](tlb_avalanche.md)
    ---
    Forces a near 100% Translation Lookaside Buffer (TLB) miss rate by performing pseudo-random jumps across 4KB and 2MB page boundaries.

-   [:material-transit-connection-horizontal: **PCIe Thrasher**](pcie_bandwidth.md)
    ---
    Floods the bus using bidirectional, asynchronous Host-to-Device (H2D) and Device-to-Host (D2H) DMA memory copies.

-   [:material-shield-check: **RAS Validator**](ras_validator.md)
    ---
    Continuously reads a pristine pattern to detect Uncorrectable Errors (UEs) or expose the latency jitter of active ECC hardware scrubbing.

-   [:material-current-ac: **Memory TSV Thrasher**](memory_tsv_thrasher.md)
    ---
    Alternates driving the bus completely HIGH and LOW to maximize Data Bus Inversion (DBI) stress and TSV crosstalk on the physical interposer.

-   [:material-table-tennis: **Memory PC Ping-Pong**](memory_pc_pingpong.md)
    ---
    Forces data to cross the Infinity Fabric crossbar by reading from one physical memory stack and writing to a completely separate one.

-   [:material-clock-fast: **Scheduler Virus**](scheduler.md)
    ---
    Spams micro-kernels across 64 concurrent streams to force the GPU dispatcher into multiplexing mode and trigger context switch locks.

-   [:material-sleep: **Baseline Metrics**](baseline_metrics.md)
    ---
    Initializes the GPU but executes zero compute/memory instructions, allowing the monitor to capture resting idle metrics.

</div>
