"""Per-model, per-workload distributions for Pantheon's end-of-run verdict.

Pantheon prints, after every run, where each throughput sits among every
other card of the same model in the public database. That needs a compact
file it can carry inside the wheel and read offline: for each (model,
workload), the sorted per-card medians of the score. This module builds it
from the same per-run history that feeds the GPU history page, and
`generate_web_data.main` writes it beside the other three generated assets.

What goes in, and why:

- Runs from Pantheon 1.1.0 onward only. Kernels changed shape between 1.0.x
  and 1.1.0, so an older number is not the same measurement.
- Runs of at least 60 seconds. Shorter runs never reach thermal steady state
  and read high.
- Throughput units only: nothing in Watts, nothing marked ERR, nothing sized
  in MiB (retention scores scale with the allocation, not the card).
- One value per physical card: the median of that card's runs, so a card
  measured fifty times counts once, the same as a card measured once.

The generated date is the newest report date in the history, not today, so
regenerating from an unchanged database produces a byte-identical file and
the drift test can compare it.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT_DIR / "docs" / "assets" / "baselines.json"

SCHEMA = 1
MIN_VERSION = (1, 1, 0)
MIN_DURATION_S = 60
MIN_CARDS = 1          # the consumer decides how many make a distribution
MAX_VALUES = 64        # per (model, workload); thinned evenly beyond this
EXCLUDED_UNITS = {"ERR", "Watts", "", None}


def version_tuple(value) -> tuple:
    parts = []
    for piece in str(value or "0").split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts[:3]) or (0,)


def _number(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None


def eligible(run: dict) -> bool:
    unit = run.get("unit")
    if unit in EXCLUDED_UNITS or str(unit).endswith("MiB"):
        return False
    score = _number(run.get("score"))
    if score is None or score <= 0:
        return False
    if version_tuple(run.get("version")) < MIN_VERSION:
        return False
    duration = _number(run.get("duration"))
    if duration is not None and duration < MIN_DURATION_S:
        return False
    if not run.get("gpu") or not run.get("test"):
        return False
    return True


def thin(values: list[float], limit: int = MAX_VALUES) -> list[float]:
    """Keep at most ``limit`` values, evenly spaced through the sorted list,
    always including the smallest and the largest."""
    values = sorted(values)
    if len(values) <= limit:
        return values
    step = (len(values) - 1) / (limit - 1)
    picked = [values[round(i * step)] for i in range(limit)]
    picked[0], picked[-1] = values[0], values[-1]
    return picked


def build_baselines(history: list[dict]) -> dict:
    per_card: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    units: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    model_cards: dict[str, set] = defaultdict(set)
    newest = ""
    for run in history:
        if not eligible(run):
            continue
        model, test = str(run["gpu"]), str(run["test"])
        card = str(run.get("card") or run.get("uuid") or "")
        if not card or card.lower() in {"unknown", "n/a", "none"}:
            continue
        per_card[(model, test)][card].append(float(run["score"]))
        units[(model, test)][str(run.get("unit"))] += 1
        model_cards[model].add(card)
        newest = max(newest, str(run.get("date") or ""))

    models: dict[str, dict] = {}
    for (model, test), cards in sorted(per_card.items()):
        unit = max(units[(model, test)].items(), key=lambda kv: kv[1])[0]
        medians = [statistics.median(v) for v in cards.values()]
        if len(medians) < MIN_CARDS:
            continue
        entry = models.setdefault(model, {"cards": 0, "tests": {}})
        entry["tests"][test] = {
            "unit": unit,
            "cards": len(medians),
            "values": [round(v, 4) for v in thin(medians)],
        }
    for model, entry in models.items():
        entry["cards"] = len(model_cards[model])

    return {
        "schema": SCHEMA,
        "generated": newest[:10] if newest else "",
        "source": "https://pantheongpu.com",
        "min_pantheon_version": ".".join(str(p) for p in MIN_VERSION),
        "min_duration_s": MIN_DURATION_S,
        "models": models,
    }


def write_baselines(history: list[dict], path: Path = OUTPUT_FILE) -> dict:
    data = build_baselines(history)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    import sys
    history_file = ROOT_DIR / "docs" / "assets" / "gpu_history.json"
    data = write_baselines(json.loads(history_file.read_text(encoding="utf-8")))
    print(f"[Baselines] {len(data['models'])} models -> {OUTPUT_FILE}", file=sys.stderr)
