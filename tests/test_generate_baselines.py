"""The distributions behind Pantheon's end-of-run percentiles. Wrong ones tell
a renter a bad card is fine, so the rules that build them are pinned here."""
import json

from website_utils import generate_baselines as gb


def run(card, gpu="NVIDIA H100 PCIe", test="memory_read", score=1970.0, unit="GB/s",
        version="1.2.0", duration=300, date="2026-09-04 00:05:37"):
    return {"card": card, "uuid": card, "gpu": gpu, "test": test, "score": score,
            "unit": unit, "version": version, "duration": duration, "date": date}


def test_one_value_per_card_is_the_median_of_that_cards_runs():
    history = [run("A", score=1960), run("A", score=1970), run("A", score=2100),
               run("B", score=1925), run("C", score=1974)]
    data = gb.build_baselines(history)
    entry = data["models"]["NVIDIA H100 PCIe"]["tests"]["memory_read"]
    assert entry["cards"] == 3
    assert entry["values"] == [1925.0, 1970.0, 1974.0]      # A counts once, as its median
    assert entry["unit"] == "GB/s"
    assert data["models"]["NVIDIA H100 PCIe"]["cards"] == 3


def test_old_kernels_short_runs_and_non_throughput_units_are_left_out():
    history = [run("A"), run("B", version="1.0.16"), run("C", duration=30),
               run("D", unit="Watts"), run("E", unit="ERR", score=0),
               run("F", test="memory_retention", unit="retained-MiB", score=11536),
               run("G", score=0.0), run("H", gpu="")]
    data = gb.build_baselines(history)
    tests = data["models"]["NVIDIA H100 PCIe"]["tests"]
    assert list(tests) == ["memory_read"]
    assert tests["memory_read"]["cards"] == 1 and tests["memory_read"]["values"] == [1970.0]


def test_history_rows_without_duration_still_count():
    row = run("A"); del row["duration"]
    assert gb.build_baselines([row])["models"]["NVIDIA H100 PCIe"]["tests"]["memory_read"]["cards"] == 1


def test_values_are_thinned_evenly_but_keep_the_extremes():
    history = [run(f"card{i:03d}", score=1000 + i) for i in range(200)]
    entry = gb.build_baselines(history)["models"]["NVIDIA H100 PCIe"]["tests"]["memory_read"]
    assert entry["cards"] == 200
    assert len(entry["values"]) == gb.MAX_VALUES
    assert entry["values"][0] == 1000 and entry["values"][-1] == 1199
    assert gb.MAX_VALUES == 32
    assert entry["values"] == sorted(entry["values"])


def test_generated_date_is_the_newest_report_not_today():
    history = [run("A", date="2026-09-01 03:54:39"), run("B", date="2026-09-10 19:58:54")]
    assert gb.build_baselines(history)["generated"] == "2026-09-10"
    assert gb.build_baselines([])["generated"] == ""


def test_output_is_deterministic_and_carries_the_schema(tmp_path):
    history = [run("B"), run("A", score=1925)]
    first = gb.write_baselines(history, tmp_path / "b.json")
    text_first = (tmp_path / "b.json").read_text()
    gb.write_baselines(list(reversed(history)), tmp_path / "b.json")
    assert (tmp_path / "b.json").read_text() == text_first
    data = json.loads(text_first)
    assert data["schema"] == 1 and data["min_pantheon_version"] == "1.1.0"
    assert data["source"] == "https://pantheongpu.com"
    assert first == data


def test_mixed_units_for_one_workload_take_the_majority_unit():
    history = [run("A", unit="GB/s"), run("B", unit="GB/s"), run("C", unit="MB/s", score=1.0)]
    entry = gb.build_baselines(history)["models"]["NVIDIA H100 PCIe"]["tests"]["memory_read"]
    assert entry["unit"] == "GB/s" and entry["cards"] == 3


def test_values_carry_four_significant_figures_and_the_file_is_compact(tmp_path):
    history = [run("A", score=3045.4567), run("B", test="llm_decode", unit="tokens/s", score=3776380123.0)]
    data = gb.write_baselines(history, tmp_path / "b.json")
    tests = data["models"]["NVIDIA H100 PCIe"]["tests"]
    assert tests["memory_read"]["values"] == [3045.0]
    assert tests["llm_decode"]["values"] == [3776000000.0]
    text = (tmp_path / "b.json").read_text()
    assert "\n" not in text.strip() and ": " not in text      # one line, no padding

