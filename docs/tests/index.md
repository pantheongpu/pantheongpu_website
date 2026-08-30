# Test Documentation Hub

Pantheon includes focused GPU diagnostics for compute, memory, interconnect,
and AI execution paths. Choose a test for its target subsystem and failure mode.

---

## Core & Compute

<div class="grid cards" markdown>

- [:material-fire: **Omni Virus**](omni_virus.md)

    ---

    Asynchronously overlaps memory sweeps, FP16 tensor math, FP32 vector math, and SFU work to load multiple GPU pipelines together.

- [:material-flash: **Voltage Virus**](voltage.md)

    ---

    Uses volatile math to force rapid ALU state switching and expose voltage-rail and VRM stability limits.

- [:material-waveform: **Pulse Virus**](pulse_virus.md)

    ---

    Alternates heavy FMA load and short idle periods to create repeated transient power ramps.

- [:material-matrix: **Tensor Virus**](tensor_virus.md)

    ---

    Saturates FP16 arithmetic with continuous fused multiply-add chains to expose half-precision datapath, power, and thermal issues.

- [:material-cpu-64-bit: **MMA Virus**](mma_virus.md)

    ---

    Uses physical matrix multiply-accumulate instructions to push matrix cores toward sustained thermal and power limits.

- [:material-vector-combine: **Transformer Virus**](transformer_virus.md)

    ---

    Uses platform-specific matrix instructions to exercise modern transformer-engine and matrix-core execution paths.

- [:material-calculator-variant: **FP64 Chokehold**](fp64_virus.md)

    ---

    Runs sustained FP64 fused multiply-add work to expose double-precision throughput, clocks, and power behavior.

- [:material-numeric: **Integer Virus**](int_virus.md)

    ---

    Saturates INT32 ALUs with bit operations, rotations, and XOR cascades to isolate integer-specific datapaths.

- [:material-function-variant: **SFU Virus**](sfu_stress.md)

    ---

    Hammers high-latency SIN, COS, EXP, LOG, and reciprocal-square-root operations to exercise special-function units.

- [:material-fire-alert: **Incinerator**](incinerator.md)

    ---

    Combines vector ALU work with local-memory bank conflicts for dense thermal and SRAM pressure.

</div>

---

## Fixed-Function & Accelerators

<div class="grid cards" markdown>

- [:material-ray-vertex: **RT Virus**](rt_virus.md)

    ---

    Floods dedicated ray-tracing hardware with non-coherent intersection work and BVH traversal.

- [:material-video-input-component: **Media Encoder Virus**](media_enc_virus.md)

    ---

    Feeds high-entropy input into the hardware video encoder to exercise fixed-function media logic.

</div>

---

## Memory & Cache

<div class="grid cards" markdown>

- [:material-lock-pattern: **Atomic Virus**](atomic_virus.md)

    ---

    Forces concurrent wide-stride atomic read-modify-write operations to stress L2 arbitration and contention handling.

- [:material-chart-timeline: **Cache Latency**](cache_lat.md)

    ---

    Defeats prefetching with dependent pointer-chasing random walks across the memory pool.

- [:material-memory: **Memory Write, Aggressive**](memory_write_agg.md)

    ---

    Bypasses cache and heavily unrolls writes with alternating patterns to maximize physical write-path pressure.

- [:material-memory: **Memory Write, Standard**](memory_write.md)

    ---

    Measures standard sequential VRAM write bandwidth with non-temporal stores and rail-to-rail patterns.

- [:material-database-search: **Memory Read, Aggressive**](memory_read_agg.md)

    ---

    Uses heavily unrolled volatile pointer accesses to force direct memory fetches without relying on cache reuse.

- [:material-database-search: **Memory Read, Standard**](memory_read.md)

    ---

    Measures standard sequential VRAM read bandwidth using wide, coalesced device reads.

- [:material-table-row: **Memory Bank Thrasher**](memory_bank_thrash.md)

    ---

    Strides reads across large page boundaries to drive row-buffer misses in the memory subsystem.

- [:material-grain: **Memory Cache Fracturing**](memory_cache_fracture.md)

    ---

    Forces large numbers of uncoalesced reads to overload memory-controller queues and cache arbitration.

- [:material-thermometer-lines: **Memory Retention Bake**](memory_retention_bake.md)

    ---

    Writes a known payload, heats the device with compute work, then checks whether memory retention errors occurred.

- [:material-gradient-vertical: **Memory Asymmetric Thermal**](memory_thermal_asym.md)

    ---

    Hammers an isolated memory region while drawing compute power to create a severe package thermal gradient.

</div>

---

## Memory Diagnostics

Structured cell-level diagnostics from memory-test literature. Where the
bandwidth workloads ask *how fast does this move data*, these ask *which cell is
bad, and why*. They compose as a funnel: sweep memory with the linear tests,
record failing addresses with `--fault_map`, then aim the quadratic GALPAT at
what they implicate.

<div class="grid cards" markdown>

- [:material-format-list-numbered: **March Test**](march_test.md)

    ---

    Runs a March C- sequence in both address directions with per-thread private chunks, finding stuck-at, transition, and coupling faults that order-independent tests cannot see.

- [:material-hammer: **Memory Hammer**](memory_hammer.md)

    ---

    Reads aggressor pairs bracketing an untouched victim, looking for cells disturbed by activity on their neighbours rather than by anything written to them.

- [:material-grid: **GALPAT**](galpat.md)

    ---

    Gallops one flipped cell against every other cell in a bounded region, exposing address-decoder faults. Quadratic coverage, so aimed at a region another test implicated.

- [:material-timer-sand: **Memory Retention**](memory_retention.md)

    ---

    Writes a payload, leaves it untouched for a chosen interval, then verifies it, finding cells that lose charge with time rather than with heat.

</div>

---

## Interconnect & Architecture

<div class="grid cards" markdown>

- [:material-server-network: **P2P Thrasher**](p2p_thrasher.md)

    ---

    Saturates peer-to-peer DMA links across NVLink, Infinity Fabric, or PCIe where available.

- [:material-call-split: **All-Reduce**](all_reduce.md)

    ---

    Validates a two-GPU sum-and-broadcast collective with direct peer DMA where available and a clearly reported host-staged fallback otherwise.

- [:material-layers-triple: **TLB Avalanche**](tlb_avalanche.md)

    ---

    Performs pseudo-random jumps across page boundaries to force translation-cache misses and page walks.

- [:material-transit-connection-horizontal: **PCIe Thrasher**](pcie_bandwidth.md)

    ---

    Floods the bus with asynchronous host-to-device and device-to-host DMA transfers.

- [:material-shield-check: **RAS Validator**](ras_validator.md)

    ---

    Continuously reads a pristine pattern to detect uncorrectable errors and observe active ECC-scrub behavior.

- [:material-current-ac: **Memory TSV Thrasher**](memory_tsv_thrasher.md)

    ---

    Alternates high and low data patterns to maximize physical memory-bus toggle rate and TSV or PHY stress.

- [:material-table-tennis: **Memory PC Ping-Pong**](memory_pc_pingpong.md)

    ---

    Reads from one memory region and writes another to exercise crossbar and pseudo-channel traffic.

- [:material-clock-fast: **Scheduler Virus**](scheduler.md)

    ---

    Launches micro-kernels across many streams to pressure dispatcher multiplexing and scheduling behavior.

- [:material-sleep: **Baseline Metrics**](baseline_metrics.md)

    ---

    Initializes the GPU without compute or memory work so telemetry captures an idle baseline for comparison.

</div>

---

## AI & ML

<div class="grid cards" markdown>

- [:material-brain: **AI Workload Suites**](../ai-workloads.md)

    ---

    Lists the inference, training, runtime, RAG, and vision suites, including their commands, telemetry guidance, and diagnostic scope.

- [:material-message-processing: **LLM Decode**](llm_decode.md)

    ---

    Uses dependent KV-cache gathers and projection-like math to isolate the cache, memory, and compute pressure of autoregressive generation.

- [:material-text-long: **LLM Prefill**](llm_prefill.md)

    ---

    Combines causal context scans and projection-like math to isolate the throughput-oriented pressure of long prompt processing.

- [:material-database-sync: **KV Cache Churn**](kv_cache_churn.md)

    ---

    Performs sparse page reads and updates across a synthetic cache to resemble ragged requests and paged KV-cache maintenance.

- [:material-eye: **Fused Attention**](fused_attention.md)

    ---

    Exercises the combined compute and memory-access pattern of causal fused attention, including context-window reuse.

- [:material-rotate-3d: **RoPE Stress**](rope_stress.md)

    ---

    Applies paired rotary-position-style math to exercise the embedding transform path used by modern transformers.

- [:material-calculator: **Quantized GEMM**](quantized_gemm.md)

    ---

    Unpacks low-precision values and applies projection-style arithmetic to expose quantization and dequantization overhead.

- [:material-server: **Serving Mix**](serving_mix.md)

    ---

    Creates mixed execution pressure representative of requests with different prompt and generation demands, without claiming queue-level serving metrics.

- [:material-source-branch: **Speculative Decode**](speculative_decode.md)

    ---

    Exercises the alternating draft and verification style of speculative decoding to reveal its compute and cache interaction.

- [:material-graph-outline: **MoE Router**](moe_router.md)

    ---

    Uses sparse Top-K-style routing and gated accumulation to exercise the local compute path behind mixture-of-experts inference.

- [:material-school: **Transformer Train Step**](transformer_train_step.md)

    ---

    Applies forward, backward, gradient, and optimizer-style arithmetic to create a controlled training-step pressure profile.

- [:material-memory: **Allocation Fragmentation**](allocation_fragmentation.md)

    ---

    Repeatedly drives a working-set allocation pattern to help expose allocator pressure and memory-management instability.

- [:material-graph: **Graph Replay**](graph_replay.md)

    ---

    Repeats a compact launch sequence to stress graph-capture and replay-adjacent runtime behavior without requiring a model framework.

- [:material-vector-line: **RAG Embedding**](rag_embedding.md)

    ---

    Applies embedding-vector projection work to stress the dense math and memory behavior relevant to retrieval and RAG pipelines.

- [:material-image: **Vision Encoder**](vision_encoder.md)

    ---

    Applies image-tile projection work to stress the dense compute and memory behavior common in vision encoder front ends.

</div>
