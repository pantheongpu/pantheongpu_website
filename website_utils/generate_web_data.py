import os
import json
import glob
import math
from pathlib import Path

try:  # run as a script (python3 website_utils/generate_web_data.py)
    from gpu_identity import public_gpu_id as _public_gpu_id
except ImportError:  # imported as a package (tests, other modules)
    from website_utils.gpu_identity import public_gpu_id as _public_gpu_id

try:
    import numpy as np
except ImportError:
    np = None

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "database"
OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "web_data.json"
UNSUPPORTED_OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "unsupported_workloads.json"
HISTORY_OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "gpu_history.json"
METHODOLOGY_FILE = ROOT_DIR / "docs" / "methodology.md"

COVERAGE_START = "<!-- TOOLKIT_COVERAGE:START -->"
COVERAGE_END = "<!-- TOOLKIT_COVERAGE:END -->"

KNOWN_TEST_UNITS = {
    "atomic_virus": "MAPS",
    "fp64_virus": "TFLOPS",
    "int_virus": "TOPS",
    "memory_bank_thrash": "GB/s",
    "memory_cache_fracture": "GB/s",
    "memory_pc_pingpong": "GB/s",
    "memory_read": "GB/s",
    "memory_read_agg": "GB/s",
    "memory_retention_bake": "GB/s",
    "memory_tsv_thrasher": "GB/s",
    "memory_write": "GB/s",
    "memory_write_agg": "GB/s",
    "mma_virus": "TFLOPS",
    "pcie_bandwidth": "GB/s",
    "ras_validator": "GB/s",
    "rt_virus": "GRays/s",
    "scheduler": "KIPS",
    "tlb_avalanche": "GB/s",
    "transformer_virus": "TFLOPS",
}

# Keep multi-GPU/interconnect workloads in raw reports and documentation, but
# do not present single-GPU-incompatible results in the public leaderboard.
PUBLIC_EXCLUDED_TESTS = {"all_reduce", "p2p_thrasher"}

# Ten AI workloads shared a single kernel body before v1.0.19 -- six of them
# compiled to byte-identical SASS -- yet each published its own invented unit,
# as though it had measured something the others had not. The numbers are real
# throughput, but the metric names describe work that never happened, so these
# runs stay in the raw reports and out of the public leaderboard. v1.0.19
# replaced the lot with one honest unit, and no release since emits these
# strings, so matching on the unit needs no version arithmetic.
RETIRED_AI_UNITS = {
    "attention-tiles/s",
    "cache-updates/s",
    "embedding-vectors/s",
    "graph-steps/s",
    "image-tiles/s",
    "prompt-tokens/s",
    "quantized-ops/s",
    "requests/s",
    "routed-tokens/s",
    "tokens/s",
    "train-steps/s",
    "verified-tokens/s",
}

# A sensor that was never read is not a reading of zero. Pantheon recorded an
# absent sensor as 0 until v1.1.0, and this generator defaulted the same fields
# to 0 when the key was missing, so the published data asserted measurements
# nobody took: 0 mV core voltage on every row, 0 C memory temperature on most.
#
# Only fields where zero cannot occur while a workload runs belong here.
# throttle_time and thermal_rise are deliberately absent: "never throttled" and
# "no measurable rise" are results, and reporting them as unknown would discard
# a real measurement.
ABSENT_WHEN_ZERO = {
    "clock_max",
    "clock_min",
    "energy_wh",
    "gpu_util_avg",
    "gpu_util_max",
    "memory_peak",
    "power_max",
    "temp_max",
    "temp_mem",
    "volts_core",
    "volts_soc",
}


# Every run of a card, rather than its best. Kept deliberately narrow: this
# file grows with every benchmark ever published, and the leaderboard already
# carries the full detail for the run it selected.
HISTORY_FIELDS = (
    "uuid",
    "gpu",
    "test",
    "version",
    "unit",
    "score",
    "date",
    "temp_max",
    "power_max",
    "clock_avg",
    "throttle_time",
)


def dedupe_history(history):
    """Collapse the several files a single run writes into one point.

    Each run emits a per-test record and a summary that repeats it, stamped
    minutes apart, so a chart drawn from the raw list plots every measurement
    two or three times. Only the certain duplicates are removed:

    * where a group mixes a per-test record with summaries repeating it, the
      per-test records win -- that is the file the run actually wrote;
    * otherwise entries identical down to the timestamp collapse to one.

    Two genuinely separate runs that happen to score the same are left alone
    unless they also share a timestamp, because at that point they are the
    same measurement counted twice.
    """
    groups = {}
    for run in history:
        key = (run["card"], run.get("test"), run.get("version"),
               str(run.get("score")), run.get("unit"))
        groups.setdefault(key, []).append(run)

    kept = []
    for group in groups.values():
        authoritative = [r for r in group if r.get("_kind") == "completed_workload"]
        if authoritative and len(authoritative) < len(group):
            group = authoritative

        seen_dates = set()
        for run in sorted(group, key=lambda r: str(r.get("date"))):
            if run.get("date") in seen_dates:
                continue
            seen_dates.add(run.get("date"))
            kept.append({k: v for k, v in run.items() if k != "_kind"})
    return kept


def sensor_reading(value):
    """Return the reading, or "N/A" when the value encodes an absent sensor."""
    if value is None or value == "":
        return "N/A"
    try:
        return "N/A" if float(value) == 0.0 else value
    except (TypeError, ValueError):
        return value

GPU_NAME_ALIASES = {
    "nvidia h100 80gb memory3": "NVIDIA H100 80GB HBM3",
}


def unsupported_workload_reason(test_name, gpu_name):
    """Return a capability reason for a workload, or None when applicable."""
    test_key = normalize(test_name, "").lower()
    gpu_key = normalize(gpu_name, "").lower()
    if test_key == "media_enc_virus" and "a100" in gpu_key:
        return "NVIDIA A100 does not expose an NVENC encoder"
    return None


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if np is not None:
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def normalize(value, default="Unknown"):
    value = str(value if value is not None else default).strip()
    return value or default


def normalize_gpu_name(value, default="Unknown GPU"):
    """Use stable public names for equivalent GPU metadata variants."""
    name = normalize(value, default)
    lookup = " ".join(name.split()).casefold()
    return GPU_NAME_ALIASES.get(lookup, name)


def public_gpu_id(raw):
    """Stable pseudonym for a GPU UUID. See website_utils.gpu_identity."""
    return _public_gpu_id(raw)


def card_identity(row):
    """Identify one physical card.

    Reports without a UUID still describe a specific card, so fall back to the
    attributes that distinguish one. Grouping those under the shared string
    "Unknown" would merge every anonymous card into a single series, and a
    history chart drawn from it would show other people's hardware as though
    it were one card swinging wildly.
    """
    uuid = normalize(row.get("uuid"))
    if uuid.lower() not in {"unknown", "n/a", "none"}:
        return uuid
    return "|".join([
        normalize(row.get("gpu")),
        normalize(row.get("serial")),
        normalize(row.get("vram"), "N/A"),
        normalize(row.get("driver"), "N/A"),
    ])


def record_key(row):
    test = normalize(row.get("test"), "unknown").lower()
    version = normalize(row.get("version"), "1.0.0")
    return f"{card_identity(row)}|{test}|{version}"


def to_float(value, default=0.0):
    if value in (None, "", "N/A"):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default

    return parsed if math.isfinite(parsed) else default


def first_present(mapping, keys, default=0):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def is_unknown_version(value):
    return normalize(value, "").lower() in {"", "unknown", "vunknown", "n/a", "none"}


def infer_unit(test_name, declared_unit, raw_score):
    declared_unit = normalize(declared_unit, "")
    if declared_unit:
        return declared_unit

    if to_float(raw_score, default=None) is not None:
        known_unit = KNOWN_TEST_UNITS.get(normalize(test_name, "").lower())
        if known_unit:
            return known_unit

    return "Watts"


def toolkit_platform(row):
    """Name the toolkit platform for a benchmark row without guessing."""
    manufacturer = normalize(row.get("manufacturer"), "").lower()
    gpu_name = normalize(row.get("gpu"), "").lower()
    if manufacturer == "nvidia" or gpu_name.startswith("nvidia"):
        return "CUDA"
    if manufacturer in {"amd", "advanced micro devices"} or gpu_name.startswith("amd"):
        return "ROCm"
    return "Unknown"


def toolkit_sort_key(value):
    parts = []
    for part in str(value).split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return parts


def render_toolkit_coverage(rows):
    """Render the hardware toolkit/driver coverage table from published rows.

    The output is deterministic for a given dataset, so the committed page
    stays byte-stable under the CI data-freshness check.
    """
    coverage = {}
    for row in rows:
        toolkit = normalize(row.get("toolkit"), "N/A")
        if toolkit in {"N/A", "Unknown"}:
            continue
        key = (toolkit_platform(row), toolkit)
        entry = coverage.setdefault(key, {"drivers": set(), "gpus": set()})
        driver = normalize(row.get("driver"), "N/A")
        if driver not in {"N/A", "Unknown"}:
            entry["drivers"].add(driver)
        entry["gpus"].add(normalize(row.get("gpu")))

    lines = [
        COVERAGE_START,
        "## Toolkit and driver coverage",
        "",
        "Every published benchmark records the toolkit and driver it ran under.",
        "This table is generated from the live dataset and lists the versions",
        "that have real hardware results behind them.",
        "",
        "| Platform | Toolkit | Driver versions | GPU models tested |",
        "| --- | --- | --- | --- |",
    ]
    for (platform, toolkit), entry in sorted(
        coverage.items(), key=lambda item: (item[0][0], toolkit_sort_key(item[0][1]))
    ):
        drivers = ", ".join(sorted(entry["drivers"], key=toolkit_sort_key)) or "not recorded"
        lines.append(f"| {platform} | {toolkit} | {drivers} | {len(entry['gpus'])} |")
    if not any(platform == "ROCm" for platform, _ in coverage):
        lines.extend([
            "",
            "No AMD ROCm hardware runs have been published yet; ROCm support is",
            "currently validated through the compile matrix in the Pantheon",
            "repository rather than through published benchmark results.",
        ])
    lines.append(COVERAGE_END)
    return "\n".join(lines)


def update_methodology_coverage(rows, methodology_file):
    contents = Path(methodology_file).read_text(encoding="utf-8")
    start = contents.find(COVERAGE_START)
    end = contents.find(COVERAGE_END)
    if start < 0 or end < start:
        raise RuntimeError(f"{methodology_file} is missing toolkit coverage markers.")
    end += len(COVERAGE_END)
    updated = contents[:start] + render_toolkit_coverage(rows) + contents[end:]
    Path(methodology_file).write_text(updated, encoding="utf-8")


def main(db_dir=DB_DIR, output_file=OUTPUT_FILE, methodology_file=None):
    db_dir = Path(db_dir)
    output_file = Path(output_file)
    best_runs = {}
    history = []
    errors = []
    unsupported = []

    # 1. PROCESS SOURCE REPORTS
    files = sorted(glob.glob(str(db_dir / "pantheon_report_*.json")))

    for f in files:
        try:
            with open(f, 'r', encoding="utf-8") as fp:
                data = json.load(fp)

                run_status = str(data.get("run_status", "complete")).lower()
                if run_status in {"partial", "failed", "incomplete"}:
                    print(f"[SKIPPED] {run_status} benchmark report: {f}")
                    continue

                # Store the entire GPU info dictionary by ID
                gpu_info_map = {}
                if data.get("gpu_static_info"):
                    for g in data["gpu_static_info"]:
                        gpu_info_map[g.get("id", 0)] = g

                for test in data.get("test_results", []):
                    test_name = test.get("Test Name", "unknown")
                    if normalize(test_name, "").lower() in PUBLIC_EXCLUDED_TESTS:
                        continue
                    gid = test.get("GPU ID", 0)
                    
                    # Fetch the specific GPU's info safely
                    g_info = gpu_info_map.get(gid, {})

                    gpu_name = normalize_gpu_name(g_info.get("name", f"Unknown GPU {gid}"))
                    capability_reason = unsupported_workload_reason(test_name, gpu_name)
                    if capability_reason:
                        report_version = first_present(data, ["Version", "pantheon_version"], "1.0.0")
                        unsupported.append({
                            "gpu": gpu_name,
                            "manufacturer": g_info.get("manufacturer", "Unknown"),
                            "test": test_name,
                            "version": test.get("Version", report_version),
                            "status": "UNSUPPORTED",
                            "reason": capability_reason,
                            "source_report": Path(f).name,
                        })
                        continue
                    manufacturer = g_info.get("manufacturer", "Unknown") 
                    uuid = g_info.get("uuid", "Unknown") 
                    serial = g_info.get("serial", "Unknown")
                    power_limit = g_info.get("power_limit", "N/A")
                    vram = g_info.get("memory_total", "N/A")
                    driver = g_info.get("driver_version", "N/A")
                    toolkit = data.get("toolkit_version", "N/A")

                    # Score Normalization
                    raw_score = test.get("Score", test.get("Throughput (GB/s)", "N/A"))
                    score_val = to_float(raw_score, default=None)
                    if score_val is None:
                        score_val = to_float(test.get("Max Power (W)", 0))
                        unit = "Watts"
                    else:
                        unit = infer_unit(test_name, test.get("Unit"), raw_score)

                    if unit in RETIRED_AI_UNITS:
                        print(f"[SKIPPED] retired metric {unit!r} in {f}: {test_name}")
                        continue

                    report_version = first_present(data, ["Version", "pantheon_version"], "1.0.0")
                    version_str = test.get("Version", report_version)
                    if is_unknown_version(version_str) and not is_unknown_version(report_version):
                        version_str = report_version
                    if is_unknown_version(version_str):
                        print(f"[SKIPPED] Unknown Pantheon version in {f}: {test_name}")
                        continue

                    # --- CAPTURE ALL FIELDS ---
                    record = {
                        "gpu": gpu_name,
                        "manufacturer": manufacturer,
                        "uuid": public_gpu_id(uuid),
                        "power_limit": power_limit,
                        "test": test_name,
                        "version": version_str,
                        "score": score_val,
                        "unit": unit,
                        "throughput": raw_score,
                        "throughput_variance": test.get("Throughput Variance (%)", "N/A"),
                        "duration": test.get("Duration (s)", 0),
                        "temp_max": test.get("Max Temp (C)", 0),
                        "power_max": test.get("Max Power (W)", 0),
                        "clock_avg": first_present(test, ["Avg Clock (MHz)", "Avg Clock(MHz)"], 0),
                        "clock_min": test.get("Min Clock (MHz)", 0),
                        "clock_max": test.get("Max Clock (MHz)", 0),
                        "gpu_util_avg": test.get("Avg GPU Util (%)", 0),
                        "gpu_util_max": test.get("Max GPU Util (%)", 0),
                        "memory_peak": test.get("Peak Memory (MiB)", 0),
                        "memory_total": test.get("Memory Total (MiB)", vram),
                        "energy_wh": test.get("Energy (Wh)", 0),
                        "thermal_rise": test.get("Thermal Rise (C)", 0),
                        "throttle_time": test.get("Throttle Time (s)", 0),
                        "date": data.get("timestamp", "Unknown"),
                        "efficiency": first_present(test, ["Efficiency (MB/J)", "Efficiency"], 0),
                        "pcie_gen": test.get("PCIe Gen", 0),
                        "pcie_width": test.get("PCIe Width", 0),
                        "throttle": test.get("Limit Reason", "N/A"),
                        "temp_mem": test.get("Max Mem Temp (C)", 0),
                        "fan_max": test.get("Max Fan (%)", 0),
                        "volts_core": test.get("Volts Core (mV)", 0),
                        "volts_soc": test.get("Volts SoC (mV)", 0),
                        "vram": vram,
                        "driver": driver,
                        "toolkit": toolkit
                    }

                    # An absent sensor must not reach the site as a reading.
                    for field in ABSENT_WHEN_ZERO:
                        record[field] = sensor_reading(record[field])

                    # The leaderboard keeps one row per card, workload and
                    # release, so a card that slows down over time is invisible
                    # there: the good early run wins and every later, worse run
                    # is dropped. Keep every run here, with its timestamp, so a
                    # single card can be followed across releases and dates.
                    run = {
                        field: record[field]
                        for field in HISTORY_FIELDS
                        if field in record
                    }
                    run["card"] = card_identity(record)
                    run["_kind"] = data.get("record_kind")
                    history.append(run)

                    # TRACK BY UNIQUE SILICON AND SOFTWARE VERSION
                    key = record_key(record)

                    if key not in best_runs:
                        print(f"[NEW ID] Added: {key} (Score: {score_val})")
                        best_runs[key] = record
                    else:
                        if score_val > best_runs[key]["score"]:
                            print(f"[UPDATE] High Score for {key}! ({best_runs[key]['score']} -> {score_val})")
                            best_runs[key] = record
                        else:
                            # Optional: Uncomment this if you want to see every skipped run too
                            # print(f"[SKIPPED] Lower score for {key} ({score_val} < {best_runs[key]['score']})")
                            pass

        except Exception as e:
            errors.append(f"{f}: {e}")

    if errors:
        details = "\n".join(errors)
        raise RuntimeError(f"Failed to parse benchmark report(s):\n{details}")

    # 2. SAVE
    output_file.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(best_runs.values(), key=record_key)

    with open(output_file, 'w', encoding="utf-8") as f:
        json.dump(rows, f, indent=2, cls=NumpyEncoder, allow_nan=False)

    history = dedupe_history(history)
    # Sorted so the committed file is byte-stable for the CI freshness check.
    history.sort(key=lambda run: (
        str(run.get("card")), str(run.get("test")),
        str(run.get("date")), str(run.get("version"))))
    history_output = output_file.with_name(HISTORY_OUTPUT_FILE.name)
    with open(history_output, 'w', encoding="utf-8") as f:
        json.dump(history, f, indent=2, cls=NumpyEncoder, allow_nan=False)

    unsupported_output = output_file.with_name(UNSUPPORTED_OUTPUT_FILE.name)
    with open(unsupported_output, 'w', encoding="utf-8") as f:
        json.dump(unsupported, f, indent=2, cls=NumpyEncoder, allow_nan=False)

    if methodology_file is not None:
        update_methodology_coverage(rows, methodology_file)
        print(f"[Generate] Toolkit coverage updated in {methodology_file}.")

    print(f"[Generate] Database updated with {len(rows)} records.")
    return rows

if __name__ == "__main__":
    main(methodology_file=METHODOLOGY_FILE)
