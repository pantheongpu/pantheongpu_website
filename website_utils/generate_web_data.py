import json
import glob
import math
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "database"
OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "web_data.json"

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


def record_key(row):
    uuid = normalize(row.get("uuid"))
    test = normalize(row.get("test"), "unknown").lower()
    version = normalize(row.get("version"), "1.0.0")
    if uuid.lower() not in {"unknown", "n/a", "none"}:
        identity = uuid
    else:
        identity = "|".join([
            normalize(row.get("gpu")),
            normalize(row.get("serial")),
            normalize(row.get("vram"), "N/A"),
            normalize(row.get("driver"), "N/A"),
        ])
    return f"{identity}|{test}|{version}"


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

    if raw_score not in (None, "", "N/A"):
        known_unit = KNOWN_TEST_UNITS.get(normalize(test_name, "").lower())
        if known_unit:
            return known_unit

    return "Watts"


def main(db_dir=DB_DIR, output_file=OUTPUT_FILE):
    db_dir = Path(db_dir)
    output_file = Path(output_file)
    best_runs = {}
    errors = []

    # 1. PROCESS SOURCE REPORTS
    files = sorted(glob.glob(str(db_dir / "pantheon_report_*.json")))

    for f in files:
        try:
            with open(f, 'r', encoding="utf-8") as fp:
                data = json.load(fp)

                # Store the entire GPU info dictionary by ID
                gpu_info_map = {}
                if data.get("gpu_static_info"):
                    for g in data["gpu_static_info"]:
                        gpu_info_map[g.get("id", 0)] = g

                for test in data.get("test_results", []):
                    test_name = test.get("Test Name", "unknown")
                    gid = test.get("GPU ID", 0)
                    
                    # Fetch the specific GPU's info safely
                    g_info = gpu_info_map.get(gid, {})

                    gpu_name = g_info.get("name", f"Unknown GPU {gid}")
                    manufacturer = g_info.get("manufacturer", "Unknown") 
                    uuid = g_info.get("uuid", "Unknown") 
                    serial = g_info.get("serial", "Unknown")
                    power_limit = g_info.get("power_limit", "N/A")
                    vram = g_info.get("memory_total", "N/A")
                    driver = g_info.get("driver_version", "N/A")
                    toolkit = data.get("toolkit_version", "N/A")

                    # Score Normalization
                    raw_score = test.get("Score", test.get("Throughput (GB/s)", "N/A"))
                    unit = infer_unit(test_name, test.get("Unit"), raw_score)
                    score_val = 0.0

                    if raw_score != "N/A":
                        score_val = to_float(raw_score)
                    else:
                        score_val = to_float(test.get("Max Power (W)", 0))

                    version_str = first_present(
                        test,
                        ["Version"],
                        first_present(data, ["Version", "pantheon_version"], "1.0.0"),
                    )
                    if is_unknown_version(version_str):
                        print(f"[SKIPPED] Unknown Pantheon version in {f}: {test_name}")
                        continue

                    # --- CAPTURE ALL FIELDS ---
                    record = {
                        "gpu": gpu_name,
                        "manufacturer": manufacturer,
                        "uuid": uuid,
                        "serial": serial,
                        "power_limit": power_limit,
                        "test": test_name,
                        "version": version_str,
                        "score": score_val,
                        "unit": unit,
                        "throughput": raw_score,
                        "duration": test.get("Duration (s)", 0),
                        "temp_max": test.get("Max Temp (C)", 0),
                        "power_max": test.get("Max Power (W)", 0),
                        "clock_avg": first_present(test, ["Avg Clock (MHz)", "Avg Clock(MHz)"], 0),
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

    print(f"[Generate] Database updated with {len(rows)} records.")
    return rows

if __name__ == "__main__":
    main()
