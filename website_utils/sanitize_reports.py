"""Strip host identifiers from benchmark reports before they are published.

This covers two places a host can leak: the JSON body, and the FILENAME.
Reports have shipped with the benchmark host's IP embedded in the name
(``a100_129.153.20.126_pantheon_report_...``) and with a PowerShell artifact
where ``$Host`` interpolated to its type name instead of the hostname. Scrubbing
only the body leaves those in a public git tree.

Pantheon releases up to v1.0.16 record the benchmark host's hostname and IP
address in a ``network_info`` block. This repository is public, so that block
must never be committed. Run this after copying new reports into ``database/``:

    python3 website_utils/sanitize_reports.py

The script rewrites offending ``database/pantheon_report_*.json`` files in
place, preserving each file's indentation style, and prints what it changed.
It exits 0 whether or not anything needed fixing, so it is safe to run
unconditionally in an import pipeline before ``generate_web_data.py``.
"""

import os
import hashlib
import json
import re
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "database"

PS_HOST_ARTIFACT = "System.Management.Automation.Internal.Host.InternalHost"
_DOTTED_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _is_octet(token):
    return token.isdigit() and len(token) <= 3 and int(token) <= 255


def host_free_name(name):
    """Return `name` with any embedded host identifier removed.

    Handles an IP written as one dotted token and as four underscore-separated
    tokens, plus the PowerShell artifact. Non-host digits are preserved: the
    GPU model in `a100_...` and timestamps must survive.
    """
    name = name.replace(PS_HOST_ARTIFACT + "_", "").replace("_" + PS_HOST_ARTIFACT, "")
    stem, dot, ext = name.rpartition(".")
    tokens = (stem or name).split("_")
    out, i = [], 0
    while i < len(tokens):
        if _DOTTED_IP.match(tokens[i]):
            i += 1
            continue
        if i + 3 < len(tokens) and all(_is_octet(t) for t in tokens[i:i + 4]):
            i += 4
            continue
        out.append(tokens[i])
        i += 1
    cleaned = "_".join(out) + (dot + ext if dot else "")
    cleaned = re.sub(r"^pantheon_report_(?=pantheon_report_)", "", cleaned)
    return re.sub(r"_{2,}", "_", cleaned)


def rename_host_named_reports(db_dir=DB_DIR):
    """Rename reports whose filename carries a host identifier.

    Every file is preserved. Two reports whose names collide once the host is
    stripped are disambiguated by content hash, never merged or dropped -- two
    machines can legitimately produce the same model, test and timestamp.
    """
    taken = {p.name for p in db_dir.glob("*.json")}
    renamed = []
    for path in sorted(db_dir.glob("*.json")):
        want = host_free_name(path.name)
        if want == path.name:
            continue
        taken.discard(path.name)
        if want in taken:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
            stem, dot, ext = want.rpartition(".")
            want = f"{stem}_{digest}{dot}{ext}"
            suffix = 2
            while want in taken:
                want = f"{stem}_{digest}_{suffix}{dot}{ext}"
                suffix += 1
        path.rename(path.with_name(want))
        taken.add(want)
        renamed.append((path.name, want))
    return renamed


PUBLIC_ID_SALT = os.environ.get("PANTHEON_ID_SALT", "")
_UNKNOWN = {"unknown", "n/a", "none", "[n/a]", ""}
# A value already in pseudonym form must be left alone. Hashing it again yields
# a different id on every run, so the same physical GPU drifts to a new identity
# each time the sanitizer runs -- and a card seen before and after an import
# splits into two.
_PSEUDONYM = re.compile(r"^GPU-[0-9a-f]{12}$")


def public_gpu_id(raw):
    """Stable pseudonym for a GPU UUID. Mirrors generate_web_data.public_gpu_id.

    Identity is only ever compared for equality, so a hash preserves dedup,
    grouping and per-card history exactly. Keep PANTHEON_ID_SALT stable, or
    previously published pseudonyms will not match new ones.
    """
    text = str(raw or "").strip()
    if text.lower() in _UNKNOWN:
        return text or "Unknown"
    if _PSEUDONYM.match(text):
        return text
    return "GPU-" + hashlib.sha256((PUBLIC_ID_SALT + text).encode("utf-8")).hexdigest()[:12]


def scrub_gpu_identifiers(data):
    """Pseudonymise GPU UUIDs and drop serials in place. Returns True if changed.

    The serial is dropped rather than hashed: it resolves no identity anywhere
    in the pipeline, and it is the field a vendor can map back to a purchaser.
    """
    changed = False
    for gpu in data.get("gpu_static_info") or []:
        if not isinstance(gpu, dict):
            continue
        uuid = gpu.get("uuid")
        if uuid is not None and str(uuid).strip().lower() not in _UNKNOWN:
            pseudonym = public_gpu_id(uuid)
            if pseudonym != uuid:
                gpu["uuid"] = pseudonym
                changed = True
        if "serial" in gpu and str(gpu["serial"]).strip().lower() not in _UNKNOWN:
            gpu["serial"] = "[REDACTED]"
            changed = True
    return changed


def sanitize_report(path):
    """Remove host identifiers from one report. Returns True if changed."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    changed = scrub_gpu_identifiers(data)
    if "network_info" in data:
        del data["network_info"]
        changed = True
    if not changed:
        return False
    indent_match = re.search(r'\n(\s+)"', raw)
    indent = len(indent_match.group(1)) if indent_match else 4
    trailing = "\n" if raw.endswith("\n") else ""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent)
        handle.write(trailing)
    return True


def main():
    changed = 0
    # Scan every JSON under database/ recursively: report filenames and
    # placement have drifted (host prefixes, host-named subdirectories), and a
    # privacy scrub must not depend on a naming convention.
    for path in sorted(DB_DIR.rglob("*.json")):
        if sanitize_report(path):
            print(f"[SANITIZED] removed network_info: {path.name}")
            changed += 1
    print(f"[Sanitize] {changed} report(s) rewritten.")

    renamed = rename_host_named_reports()
    for old, new in renamed:
        print(f"[SANITIZED] host identifier in filename: {old} -> {new}")
    print(f"[Sanitize] {len(renamed)} report(s) renamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
