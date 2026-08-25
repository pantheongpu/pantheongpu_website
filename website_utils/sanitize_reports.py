"""Strip host identifiers from benchmark reports before they are published.

Pantheon releases up to v1.0.16 record the benchmark host's hostname and IP
address in a ``network_info`` block. This repository is public, so that block
must never be committed. Run this after copying new reports into ``database/``:

    python3 website_utils/sanitize_reports.py

The script rewrites offending ``database/pantheon_report_*.json`` files in
place, preserving each file's indentation style, and prints what it changed.
It exits 0 whether or not anything needed fixing, so it is safe to run
unconditionally in an import pipeline before ``generate_web_data.py``.
"""

import json
import re
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "database"


def sanitize_report(path):
    """Remove host identifiers from one report. Returns True if changed."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if "network_info" not in data:
        return False

    del data["network_info"]
    indent_match = re.search(r'\n(\s+)"', raw)
    indent = len(indent_match.group(1)) if indent_match else 4
    trailing = "\n" if raw.endswith("\n") else ""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent)
        handle.write(trailing)
    return True


def main():
    changed = 0
    for path in sorted(DB_DIR.glob("pantheon_report_*.json")):
        if sanitize_report(path):
            print(f"[SANITIZED] removed network_info: {path.name}")
            changed += 1
    print(f"[Sanitize] {changed} report(s) rewritten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
