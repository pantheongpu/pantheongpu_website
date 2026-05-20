import json
import glob
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "database"
OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "web_data.json"

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
        return float(value)
    except (TypeError, ValueError):
        return default


def main(db_dir=DB_DIR, output_file=OUTPUT_FILE):
    db_dir = Path(db_dir)
    output_file = Path(output_file)
    best_runs = {}

    # 1. LOAD EXISTING
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
                for row in existing_data:
                    best_runs[record_key(row)] = row
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not load existing {output_file}: {e}")

    # 2. PROCESS NEW REPORTS
    files = sorted(glob.glob(str(db_dir / "pantheon_report_*.json")))

    for f in files:
        try:
            with open(f, 'r') as fp:
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
                    unit = test.get("Unit", "GB/s")
                    score_val = 0.0

                    if raw_score != "N/A":
                        score_val = to_float(raw_score)
                    else:
                        score_val = to_float(test.get("Max Power (W)", 0))
                        unit = "Watts"

                    version_str = data.get("Version", data.get("pantheon_version", "1.0.0"))

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
                        "clock_avg": test.get("Avg Clock (MHz)", 0),
                        "date": data.get("timestamp", "Unknown"),
                        "efficiency": test.get("Efficiency (MB/J)", 0),
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
            print(f"Skipping {f}: {e}")

    # 3. SAVE
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(list(best_runs.values()), f, indent=2, cls=NumpyEncoder)

    print(f"[Generate] Database updated with {len(best_runs)} records.")
    return list(best_runs.values())

if __name__ == "__main__":
    main()
