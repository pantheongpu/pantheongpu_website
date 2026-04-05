import json
import os
import glob
import numpy as np

# Paths
DB_DIR = "database"
OUTPUT_FILE = "docs/assets/web_data.json"

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def main():
    best_runs = {}

    # 1. LOAD EXISTING
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_data = json.load(f)
                for row in existing_data:
                    # STRICT NORMALIZATION: Strip whitespace and match casing
                    c_uuid = str(row.get("uuid", "Unknown")).strip()
                    c_test = str(row.get("test", "unknown")).strip().lower()
                    c_ver  = str(row.get("version", "1.0.0")).strip()

                    key = f"{c_uuid}|{c_test}|{c_ver}"
                    best_runs[key] = row
        except: pass

    # 2. PROCESS NEW REPORTS
    files = glob.glob(os.path.join(DB_DIR, "pantheon_report_*.json"))

    for f in files:
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)

                # Store the entire GPU info dictionary by ID
                gpu_info_map = {}
                if data.get("gpu_static_info"):
                    for g in data["gpu_static_info"]:
                        gpu_info_map[g["id"]] = g

                for test in data.get("test_results", []):
                    test_name = test["Test Name"]
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
                        score_val = float(raw_score)
                    else:
                        score_val = float(test.get("Max Power (W)", 0))
                        unit = "Watts"

                    # --- CAPTURE ALL FIELDS ---
                    record = {
                        "gpu": gpu_name,
                        "manufacturer": manufacturer,
                        "uuid": uuid,
                        "serial": serial,
                        "power_limit": power_limit,
                        "test": test_name,
                        "version": data.get("pantheon_version", "1.0.0"),
                        "score": score_val,
                        "unit": unit,
                        "throughput": raw_score,
                        "duration": test.get("Duration (s)", 0),
                        "temp_max": test.get("Max Temp (C)", 0),
                        "power_max": test.get("Max Power (W)", 0),
                        "clock_avg": test.get("Avg Clock (MHz)", 0),
                        "date": data["timestamp"],
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
                    version_str = data.get("Version", data.get("pantheon_version", "1.0.0"))

                    # STRICT NORMALIZATION: Prevent invisible whitespace duplicates
                    c_uuid = str(uuid).strip()
                    c_test = str(test_name).strip().lower()
                    c_ver  = str(version_str).strip()

                    key = f"{c_uuid}|{c_test}|{c_ver}"

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
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir): os.makedirs(output_dir, exist_ok=True)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(list(best_runs.values()), f, indent=2, cls=NumpyEncoder)

    print(f"[Generate] Database updated with {len(best_runs)} records.")

if __name__ == "__main__":
    main()
