"""Strip host identifiers from benchmark reports before they are published.

This covers two places a host can leak: the JSON body, and the FILENAME.
Reports have shipped with the benchmark host's IP embedded in the name
(``a100_129.153.20.126_pantheon_report_...``) and with a PowerShell artifact
where ``$Host`` interpolated to its type name instead of the hostname. Scrubbing
only the body leaves those in a public git tree.

Pantheon releases up to v1.0.16 record the benchmark host's hostname and IP
address in a ``network_info`` block. This repository is public, so that block
must never be committed.

A report also records the command lines that launched it, and those carry the
benchmark user's home directory (``/home/alice/.cache/...``). That names a
person, so every ``/home/<name>`` is rewritten to ``/home/user`` in every string
of the report, except the generic ``ubuntu``, ``user`` and ``root`` homes. The
rewrite is done on the file text, so JSON formatting and key order are kept
and the diff is only the replaced paths. Git history keeps whatever was
committed before this scrub existed.

GPU identifiers -- the UUID and serial in ``gpu_static_info`` -- are NOT
scrubbed: the owner decided (2026-08-31) to publish them verbatim. They are
load-bearing for per-card identity, dedup and history on the dashboards, and
they identify a card, not a host. Only host identifiers are removed.

Run this after copying new reports into ``database/``:

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

try:  # run as a script (python3 website_utils/sanitize_reports.py)
    from gpu_identity import public_gpu_id as _public_gpu_id
except ImportError:  # imported as a package (tests, other modules)
    from website_utils.gpu_identity import public_gpu_id as _public_gpu_id
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "database"

PS_HOST_ARTIFACT = "System.Management.Automation.Internal.Host.InternalHost"
_DOTTED_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# Home directories that name no one and stay as they are.
GENERIC_HOMES = {"ubuntu", "user", "root"}
NEUTRAL_HOME = "/home/user"
# macOS and Windows homes too: a Windows machine running Pantheon under WSL
# shows its account as /mnt/c/Users/<name>.
_HOME_PATH = re.compile(r"(?:/mnt/[a-z])?/(?:home|Users)/([A-Za-z0-9_][A-Za-z0-9_.-]*)")


def scrub_home_paths(text):
    """Replace ``/home/<name>``, ``/Users/<name>`` and ``/mnt/<drive>/Users/<name>``
    with ``/home/user`` unless <name> is generic.

    Works on any text, including raw JSON, and touches nothing else.
    """
    def replace(match):
        if match.group(1) in GENERIC_HOMES:
            return match.group(0)
        return NEUTRAL_HOME

    return _HOME_PATH.sub(replace, text)


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


def public_gpu_id(raw):
    """The published GPU id: the UUID, verbatim. See website_utils.gpu_identity."""
    return _public_gpu_id(raw)


def sanitize_report(path):
    """Remove host identifiers and user home paths from one report.

    Returns True if the file changed.

    GPU UUIDs and serials are left exactly as the report recorded them.
    """
    # newline="" keeps CRLF files byte-identical apart from the scrubbed text.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        raw = handle.read()
    data = json.loads(raw)

    text = raw
    if "network_info" in data:
        del data["network_info"]
        indent_match = re.search(r'\n(\s+)"', raw)
        indent = len(indent_match.group(1)) if indent_match else 4
        trailing = "\n" if raw.endswith("\n") else ""
        text = json.dumps(data, indent=indent) + trailing
    text = scrub_home_paths(text)
    if text == raw:
        return False
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return True


def main():
    changed = 0
    # Scan every JSON under database/ recursively: report filenames and
    # placement have drifted (host prefixes, host-named subdirectories), and a
    # privacy scrub must not depend on a naming convention.
    for path in sorted(DB_DIR.rglob("*.json")):
        if sanitize_report(path):
            print(f"[SANITIZED] host identifiers or home paths removed: {path.name}")
            changed += 1
    print(f"[Sanitize] {changed} report(s) rewritten.")

    renamed = rename_host_named_reports()
    for old, new in renamed:
        print(f"[SANITIZED] host identifier in filename: {old} -> {new}")
    print(f"[Sanitize] {len(renamed)} report(s) renamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
