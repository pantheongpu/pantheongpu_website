import json
from pathlib import Path

import pytest

from website_utils.generate_web_data import (
    first_present,
    infer_manufacturer,
    infer_unit,
    is_retired_metric,
    card_identity,
    clean_driver,
    is_failed_workload,
    is_unknown_id,
    is_unmeasured,
    is_unknown_version,
    main,
    normalize_gpu_name,
    record_key,
    MIN_LEADERBOARD_DURATION_S,
    to_float,
    unsupported_workload_reason,
)


ROOT = Path(__file__).resolve().parents[1]


def write_report(db_dir, name, gpu_info, test_results, version="1.0.0", run_status=None):
    report = {
        "pantheon_version": version,
        "timestamp": "2026-05-20 10:00:00",
        "toolkit_version": "12.4",
        "gpu_static_info": gpu_info,
        "test_results": test_results,
    }
    if run_status is not None:
        report["run_status"] = run_status
    path = db_dir / name
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_partial_reports_are_not_published(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_partial.json",
        [{"id": 0, "name": "Incomplete GPU", "memory_total": "98304 MiB"}],
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 20, "Unit": "GB/s"}],
        run_status="partial",
    )

    assert main(db_dir=db_dir, output_file=output_file) == []


def test_multi_gpu_workloads_are_excluded_from_public_benchmark_data(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_multi_gpu.json",
        [{"id": 0, "name": "Single GPU", "uuid": "GPU-UUID"}],
        [
            {"Test Name": "all_reduce", "GPU ID": 0, "Score": 0, "Unit": "GB/s"},
            {"Test Name": "p2p_thrasher", "GPU ID": 0, "Score": 0, "Unit": "GB/s"},
            {"Test Name": "memory_write", "GPU ID": 0, "Score": 100, "Unit": "GB/s"},
        ],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert [row["test"] for row in rows] == ["memory_write"]


def test_h100_name_variants_use_one_public_name(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    assert normalize_gpu_name("NVIDIA H100 80GB Memory3") == "NVIDIA H100 80GB HBM3"
    assert normalize_gpu_name("NVIDIA H100 80GB HBM3") == "NVIDIA H100 80GB HBM3"

    write_report(
        db_dir,
        "pantheon_report_h100_names.json",
        [
            {"id": 0, "name": "NVIDIA H100 80GB Memory3", "uuid": "GPU-MEMORY3"},
            {"id": 1, "name": "NVIDIA H100 80GB HBM3", "uuid": "GPU-HBM3"},
        ],
        [
            {"Test Name": "memory_write", "GPU ID": 0, "Score": 100, "Unit": "GB/s"},
            {"Test Name": "memory_write", "GPU ID": 1, "Score": 110, "Unit": "GB/s"},
        ],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert {row["gpu"] for row in rows} == {"NVIDIA H100 80GB HBM3"}


def test_unsupported_workloads_are_excluded_and_recorded(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    assert unsupported_workload_reason(
        "media_enc_virus", "NVIDIA A100-SXM4-40GB"
    ) == "NVIDIA A100 does not expose an NVENC encoder"

    write_report(
        db_dir,
        "pantheon_report_unsupported.json",
        [{"id": 0, "name": "NVIDIA A100-SXM4-40GB", "uuid": "GPU-A100"}],
        [{"Test Name": "media_enc_virus", "GPU ID": 0, "Score": 0, "Unit": "FPS"}],
        version="1.0.16",
    )

    assert main(db_dir=db_dir, output_file=output_file) == []
    unsupported = json.loads(
        (output_file.parent / "unsupported_workloads.json").read_text(encoding="utf-8")
    )
    assert unsupported == [{
        "gpu": "NVIDIA A100-SXM4-40GB",
        "manufacturer": "Unknown",
        "test": "media_enc_virus",
        "version": "1.0.16",
        "status": "UNSUPPORTED",
        "reason": "NVIDIA A100 does not expose an NVENC encoder",
        "source_report": "pantheon_report_unsupported.json",
    }]


def test_unknown_uuid_uses_gpu_metadata_to_keep_cards_separate(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_a.json",
        [{
            "id": 0,
            "name": "GPU Alpha",
            "uuid": "Unknown",
            "serial": "Unknown",
            "memory_total": "12288 MB",
            "driver_version": "580.1",
        }],
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 100, "Unit": "GB/s"}],
    )
    write_report(
        db_dir,
        "pantheon_report_b.json",
        [{
            "id": 0,
            "name": "GPU Beta",
            "uuid": "Unknown",
            "serial": "Unknown",
            "memory_total": "24576 MB",
            "driver_version": "580.1",
        }],
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 200, "Unit": "GB/s"}],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert len(rows) == 2
    assert {row["gpu"] for row in rows} == {"GPU Alpha", "GPU Beta"}
    assert json.loads(output_file.read_text(encoding="utf-8")) == rows


def test_same_gpu_test_and_version_keeps_highest_score(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    gpu = [{
        "id": 0,
        "name": "GPU Alpha",
        "uuid": "GPU-UUID",
        "serial": "S1",
        "memory_total": "12288 MB",
        "driver_version": "580.1",
    }]

    write_report(
        db_dir,
        "pantheon_report_low.json",
        gpu,
        [{"Test Name": "tensor_virus", "GPU ID": 0, "Score": 10, "Unit": "TFLOPS"}],
    )
    write_report(
        db_dir,
        "pantheon_report_high.json",
        gpu,
        [{"Test Name": "tensor_virus", "GPU ID": 0, "Score": 25, "Unit": "TFLOPS"}],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert len(rows) == 1
    assert rows[0]["score"] == 25


def test_existing_output_is_rebuilt_from_source_reports(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    output_file.parent.mkdir(parents=True)
    output_file.write_text(
        json.dumps([{
            "gpu": "Stale GPU",
            "uuid": "GPU-STALE",
            "test": "fp64_virus",
            "version": "vUnknown",
            "score": 0.571593,
        }]),
        encoding="utf-8",
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows == []
    assert json.loads(output_file.read_text(encoding="utf-8")) == []


def test_generated_rows_are_written_in_stable_key_order(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    gpu_beta = [{
        "id": 0,
        "name": "GPU Beta",
        "uuid": "GPU-BETA",
        "serial": "S2",
        "memory_total": "24576 MB",
        "driver_version": "580.1",
    }]
    gpu_alpha = [{
        "id": 0,
        "name": "GPU Alpha",
        "uuid": "GPU-ALPHA",
        "serial": "S1",
        "memory_total": "12288 MB",
        "driver_version": "580.1",
    }]

    write_report(
        db_dir,
        "pantheon_report_b.json",
        gpu_beta,
        [{"Test Name": "tensor_virus", "GPU ID": 0, "Score": 20, "Unit": "TFLOPS"}],
    )
    write_report(
        db_dir,
        "pantheon_report_a.json",
        gpu_alpha,
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 10, "Unit": "GB/s"}],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert [record_key(row) for row in rows] == sorted(record_key(row) for row in rows)


def test_missing_score_falls_back_to_power_metric(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_power.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{"Test Name": "pulse_virus", "GPU ID": 0, "Score": "N/A", "Max Power (W)": 350}],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["score"] == 350
    assert rows[0]["unit"] == "Watts"


def test_null_score_falls_back_to_power_metric_and_unit(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_null_score.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{
            "Test Name": "atomic_virus",
            "GPU ID": 0,
            "Score": None,
            "Unit": "MAPS",
            "Max Power (W)": 350,
        }],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["score"] == 350
    assert rows[0]["unit"] == "Watts"


def test_missing_test_version_falls_back_to_report_version(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_missing_test_version.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{
            "Test Name": "fp64_virus",
            "GPU ID": 0,
            "Version": None,
            "Score": 1.25,
            "Unit": "TFLOPS",
        }],
        version="1.0.13",
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["version"] == "1.0.13"


def test_legacy_score_without_unit_uses_known_test_unit(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_legacy_atomic.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{
            "Test Name": "atomic_virus",
            "GPU ID": 0,
            "Throughput (GB/s)": 1408.96,
            "Max Power (W)": 189.3,
        }],
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["score"] == 1408.96
    assert rows[0]["throughput"] == 1408.96
    assert rows[0]["unit"] == "MAPS"


def test_report_parser_accepts_historical_telemetry_keys(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_legacy_keys.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{
            "Test Name": "fp64_virus",
            "Version": "1.0.9",
            "GPU ID": 0,
            "Score": 1.25,
            "Unit": "TFLOPS",
            "Avg Clock(MHz)": 1875.5,
            "Efficiency": 8.25,
        }],
        version="vUnknown",
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["version"] == "1.0.9"
    assert rows[0]["clock_avg"] == 1875.5
    assert rows[0]["efficiency"] == 8.25


def test_unknown_version_reports_are_not_published(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(
        db_dir,
        "pantheon_report_unknown_version.json",
        [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID"}],
        [{"Test Name": "fp64_virus", "GPU ID": 0, "Score": 1.25, "Unit": "TFLOPS"}],
        version="vUnknown",
    )

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows == []
    assert json.loads(output_file.read_text(encoding="utf-8")) == []


def test_malformed_report_fails_generation(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    (db_dir / "pantheon_report_bad.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(RuntimeError, match="pantheon_report_bad.json"):
        main(db_dir=db_dir, output_file=output_file)


def test_record_key_normalizes_test_name_and_version():
    row = {
        "uuid": " GPU-UUID ",
        "test": " Memory_Write ",
        "version": " 1.0.7 ",
        "duration": 300,
        "unit": "GB/s",
    }

    assert record_key(row) == "GPU-UUID|memory_write|1.0.7|300s|GB/s"


def test_record_key_keeps_run_lengths_apart():
    short = {"uuid": "GPU-UUID", "test": "memory_read", "version": "1.2.2",
             "duration": 300}
    long = dict(short, duration="3600")

    assert record_key(short) != record_key(long)
    assert "|3600s|" in record_key(long)
    assert "|0s|" in record_key(dict(short, duration="N/A"))


def test_long_and_short_runs_on_one_card_both_reach_the_leaderboard(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    gpu = [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-UUID", "serial": "S1",
            "memory_total": "12288 MB", "driver_version": "580.1"}]

    def run(name, seconds, score):
        write_report(db_dir, name, gpu, [{
            "Test Name": "memory_read", "GPU ID": 0, "Score": score,
            "Unit": "GB/s", "Duration (s)": seconds}])

    run("pantheon_report_5min.json", 300, 900)
    run("pantheon_report_1h.json", 3600, 850)      # heat-soaked, scores lower
    run("pantheon_report_debug.json", 1, 950)      # start-up, not the card

    rows = main(db_dir=db_dir, output_file=output_file)

    assert sorted((row["duration"], row["score"]) for row in rows) == [
        (300, 900), (3600, 850)]
    assert MIN_LEADERBOARD_DURATION_S > 1


def test_to_float_returns_default_for_bad_values():
    assert to_float("12.5") == 12.5
    assert to_float("N/A") == 0.0
    assert to_float("not-a-number", default=-1.0) == -1.0
    assert to_float("NaN", default=-1.0) == -1.0
    assert to_float("Infinity", default=-1.0) == -1.0


def test_first_present_returns_first_existing_key_even_when_value_is_zero():
    assert first_present({"new": 0, "old": 5}, ["new", "old"], default=9) == 0
    assert first_present({"old": 5}, ["new", "old"], default=9) == 5
    assert first_present({}, ["new", "old"], default=9) == 9


def test_is_unknown_version_identifies_unpublishable_versions():
    assert is_unknown_version("vUnknown")
    assert is_unknown_version("unknown")
    assert is_unknown_version("")
    assert not is_unknown_version("1.0.9")


def test_infer_unit_preserves_declared_unit_and_falls_back_to_power():
    assert infer_unit("atomic_virus", "MAPS", 123) == "MAPS"
    assert infer_unit("atomic_virus", None, 123) == "MAPS"
    assert infer_unit("unknown_test", None, 123) == "Watts"
    assert infer_unit("tensor_virus", "", "N/A") == "Watts"


def test_reports_are_discovered_by_shape_not_name(tmp_path):
    """Discovery must not depend on a naming convention.

    Report filenames have drifted -- model prefixes (a100_...), host-scrub
    renames that lost the pantheon_report stem entirely, per-card
    subdirectories -- and a strict prefix glob once left 538 valid reports
    silently invisible to the leaderboard. A report is recognised by its
    shape; JSON in the tree that is not a report must be skipped, not fatal.
    """
    db_dir = tmp_path / "database"
    subdir = db_dir / "gh200_runs"
    subdir.mkdir(parents=True)
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    gpu = [{"id": 0, "name": "Some GPU", "uuid": "GPU-11112222333344445555",
            "memory_total": "98304 MiB"}]
    write_report(db_dir, "a100_pantheon_report_20260826.json", gpu,
                 [{"Test Name": "memory_write", "GPU ID": 0, "Score": 10, "Unit": "GB/s"}])
    write_report(db_dir, "a100_cache_lat_191356_gpu0.json", gpu,
                 [{"Test Name": "cache_lat", "GPU ID": 0, "Score": 20, "Unit": "GB/s"}])
    write_report(subdir, "pantheon_report_20260826.json", gpu,
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 30, "Unit": "GB/s"}])
    (db_dir / "profiler_artifact.json").write_text('["not", "a", "report"]',
                                                   encoding="utf-8")

    rows = main(db_dir=db_dir, output_file=output_file)
    assert {row["test"] for row in rows} == {"memory_write", "cache_lat", "memory_read"}
    written = json.loads(output_file.read_text(encoding="utf-8"))
    assert {row["test"] for row in written} == {"memory_write", "cache_lat", "memory_read"}


def test_retired_ai_units_are_skipped_only_before_the_fix_release(tmp_path):
    """The shared pre-v1.0.19 AI kernel is retired; the rewritten workloads are not.

    llm_prefill, llm_decode, kv_cache_churn and graph_replay became real,
    distinct kernels after v1.0.19 and legitimately report the same unit
    strings the retired kernel invented. Filtering on the unit alone threw
    away every one of their v1.1.0 and v1.2.0 runs.
    """
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    result = {"Test Name": "llm_prefill", "GPU ID": 0, "Score": 4321.0, "Unit": "prompt-tokens/s"}

    write_report(db_dir, "pantheon_report_old.json",
                 [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-OLD"}], [dict(result)], version="1.0.18")
    write_report(db_dir, "pantheon_report_new.json",
                 [{"id": 0, "name": "GPU Alpha", "uuid": "GPU-NEW"}], [dict(result)], version="1.2.0")

    rows = main(db_dir=db_dir, output_file=output_file)

    assert [row["uuid"] for row in rows] == ["GPU-NEW"]
    assert rows[0]["unit"] == "prompt-tokens/s"
    assert rows[0]["score"] == 4321.0


def test_is_retired_metric_needs_both_the_unit_and_an_old_release():
    assert is_retired_metric("tokens/s", "1.0.18")
    assert is_retired_metric("tokens/s", "v1.0.18")
    assert not is_retired_metric("tokens/s", "1.0.19")
    assert not is_retired_metric("prompt-tokens/s", "1.2.0")
    assert not is_retired_metric("MAPS", "1.0.0")


def test_zero_throughput_runs_are_recorded_as_unmeasured_not_published(tmp_path):
    """0 GRays/s is not a slow card, it is a workload that never ran.

    rt_virus without an OptiX SDK and media_enc_virus without an encoder
    report a score of exactly zero; the explorer showed them as "0 GRays/s"
    and "0 FPS" under real cards. baseline_metrics is idle by design."""
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(db_dir, "pantheon_report_zero.json",
                 [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-ZERO"}],
                 [{"Test Name": "rt_virus", "GPU ID": 0, "Score": 0.0, "Unit": "GRays/s", "Max Power (W)": 92.9},
                  {"Test Name": "baseline_metrics", "GPU ID": 0, "Score": 0.0, "Unit": "GB/s"},
                  {"Test Name": "memory_read", "GPU ID": 0, "Score": 1500.0, "Unit": "GB/s"}],
                 version="1.2.0")

    rows = main(db_dir=db_dir, output_file=output_file)

    assert sorted(row["test"] for row in rows) == ["baseline_metrics", "memory_read"]
    unsupported = json.loads((output_file.parent / "unsupported_workloads.json").read_text())
    assert [(u["test"], u["status"]) for u in unsupported] == [("rt_virus", "NO_MEASUREMENT")]
    assert "OptiX" in unsupported[0]["reason"]
    assert is_unmeasured("rt_virus", 0.0, "GRays/s")
    assert not is_unmeasured("baseline_metrics", 0.0, "GB/s")
    assert not is_unmeasured("pulse_virus", 0.0, "Watts")
    assert not is_unmeasured("rt_virus", 12.5, "GRays/s")


def test_unknown_vendor_is_inferred_from_the_product_name(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"

    write_report(db_dir, "pantheon_report_t4.json",
                 [{"id": 0, "name": "Tesla T4", "uuid": "Unknown", "manufacturer": "Unknown"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 300.0, "Unit": "GB/s"}])

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["manufacturer"] == "NVIDIA"
    assert infer_manufacturer("Unknown", "AMD Instinct MI300X") == "AMD"
    assert infer_manufacturer("Unknown", "NVIDIA GeForce RTX 3060") == "NVIDIA"
    assert infer_manufacturer("Advanced Micro Devices", "Radeon RX 7900") == "Advanced Micro Devices"
    assert infer_manufacturer("Unknown", "Mystery Accelerator") == "Unknown"


def test_pre_fix_units_of_the_two_late_rewrites_are_retired_too():
    assert is_retired_metric("allocation-events/s", "1.0.18")
    assert is_retired_metric("rotary-tokens/s", "1.0.18")
    assert not is_retired_metric("alloc-events/s", "1.0.18")
    assert not is_retired_metric("ai-ops/s", "1.2.0")


def test_declared_memory_fields_are_published_and_default_to_na(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    write_report(db_dir, "pantheon_report_new.json",
                 [{"id": 0, "name": "NVIDIA L4", "uuid": "GPU-NEW", "memory_type": "GDDR6",
                   "memory_vendor": "SK hynix", "memory_vendor_source": "nvidia-rm"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 250.0, "Unit": "GB/s"}], version="1.2.1")
    write_report(db_dir, "pantheon_report_old.json",
                 [{"id": 0, "name": "NVIDIA Unlisted Prototype", "uuid": "GPU-OLD"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 250.0, "Unit": "GB/s"}], version="1.2.0")

    rows = {row["uuid"]: row for row in main(db_dir=db_dir, output_file=output_file)}

    assert rows["GPU-NEW"]["memory_type"] == "GDDR6"
    assert rows["GPU-NEW"]["memory_vendor"] == "SK hynix"
    assert "memory_type_source" not in rows["GPU-NEW"]
    # A model the specification table does not list has nothing to fill from.
    assert rows["GPU-OLD"]["memory_type"] == "N/A"
    assert rows["GPU-OLD"]["memory_vendor"] == "N/A"
    assert "memory_type_source" not in rows["GPU-OLD"]


def test_memory_type_is_filled_from_the_specification_but_the_vendor_never_is(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    # Reports with no memory fields at all: releases before 1.2.1, and 570-series drivers that refused the query.
    write_report(db_dir, "pantheon_report_a100.json",
                 [{"id": 0, "name": "NVIDIA A100-SXM4-80GB", "uuid": "GPU-A100",
                   "memory_type": "N/A", "memory_vendor": "N/A",
                   "memory_vendor_source": "unavailable: FB_GET_INFO_V2 returned status 0x1f"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 1500.0, "Unit": "GB/s"}], version="1.2.4")
    write_report(db_dir, "pantheon_report_rx.json",
                 [{"id": 1, "name": "AMD Radeon RX 6700 XT", "uuid": "0x0"}],
                 [{"Test Name": "memory_read", "GPU ID": 1, "Score": 280.0, "Unit": "GB/s"}], version="1.2.0")
    # The driver answered, and its answer differs from the table's spelling: the driver wins.
    write_report(db_dir, "pantheon_report_measured.json",
                 [{"id": 0, "name": "NVIDIA A100-SXM4-80GB", "uuid": "GPU-MEASURED",
                   "memory_type": "HBM2", "memory_vendor": "SK hynix", "memory_vendor_source": "nvidia-rm"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 1500.0, "Unit": "GB/s"}], version="1.2.5")

    rows = {row["uuid"]: row for row in main(db_dir=db_dir, output_file=output_file)}

    assert rows["GPU-A100"]["memory_type"] == "HBM2e"
    assert rows["GPU-A100"]["memory_type_source"] == "specification"
    assert rows["GPU-A100"]["memory_vendor"] == "N/A"
    assert rows["0x0"]["memory_type"] == "GDDR6"
    assert rows["0x0"]["memory_type_source"] == "specification"
    assert rows["0x0"]["memory_vendor"] == "N/A"
    assert rows["GPU-MEASURED"]["memory_type"] == "HBM2"
    assert rows["GPU-MEASURED"]["memory_vendor"] == "SK hynix"
    assert "memory_type_source" not in rows["GPU-MEASURED"]


def test_specification_memory_types_are_well_formed_and_agree_with_every_measured_card():
    from website_utils.memory_specs import SPEC_MEMORY_TYPES, spec_memory_type

    kinds = {"GDDR6", "GDDR6X", "GDDR7", "HBM2", "HBM2e", "HBM3", "HBM3e"}
    assert set(SPEC_MEMORY_TYPES.values()) <= kinds
    assert spec_memory_type("  nvidia   a100-sxm4-80gb ") == "HBM2e"
    assert spec_memory_type("NVIDIA Unlisted Prototype") is None
    assert spec_memory_type(None) is None

    # The table must never contradict what a driver measured. The driver names the generation (HBM2 for
    # HBM2e), so compare on that. A row with a vendor was measured: the vendor is never filled in.
    def family(kind):
        return kind[:-1] if kind.endswith("e") else kind

    data = json.loads((ROOT / "docs" / "assets" / "web_data.json").read_text(encoding="utf-8"))
    measured = {}
    for row in data:
        if row.get("memory_vendor") in (None, "", "N/A", "Unknown") or "memory_type_source" in row:
            continue
        spec = spec_memory_type(row["gpu"])
        if spec:
            measured.setdefault(row["gpu"], set()).add(row["memory_type"])
            assert family(row["memory_type"]) == family(spec), (row["gpu"], row["memory_type"], spec)
    assert measured, "no measured card matched the table, so the check above proved nothing"


def _write_json(db_dir, name, report):
    path = db_dir / name
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_a_mock_report_from_another_suite_is_not_published(tmp_path):
    """Reproduces the trial run: a pantheontt MOCK report went in as a real card,
    'Unknown GPU 0', with a made-up mma_virus score of 100."""
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    _write_json(db_dir, "pantheon_tt_report_mock.json", {
        "pantheon_tt_version": "0.1.0", "timestamp": "2026-09-24 16:18:20",
        "mock": True, "backend": "mock", "publishable": False,
        "devices": [{"index": 0, "board_id": "mock-0000", "board_type": "mock"}],
        "test_results": [{"Test Name": "mma_virus", "Devices": [0], "Score": 100.0,
                          "Unit": "TFLOPS", "Duration (s)": 0.05}],
    })
    assert main(db_dir=db_dir, output_file=output_file) == []


def test_a_real_report_from_a_suite_this_page_cannot_identify_is_skipped(tmp_path):
    """Even a physical Tenstorrent card would appear as 'Unknown GPU 0' credited
    to Pantheon 1.0.0, because it has no gpu_static_info. Skip it until the site
    decides how non-GPU accelerators are shown, rather than defaulting into that."""
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    _write_json(db_dir, "pantheon_tt_report_real.json", {
        "pantheon_tt_version": "0.1.0", "timestamp": "2026-09-24 16:18:20",
        "mock": False, "backend": "hardware", "publishable": True,
        "devices": [{"index": 0, "board_id": "0000040000000001", "board_type": "p150a"}],
        "test_results": [{"Test Name": "memory_read", "Devices": [0], "Score": 410.0,
                          "Unit": "GB/s", "Duration (s)": 300}],
    })
    assert main(db_dir=db_dir, output_file=output_file) == []


def test_a_simulator_report_is_not_a_measurement(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    write_report(
        db_dir, "pantheon_report_sim.json",
        [{"id": 0, "name": "Simulated GPU", "memory_total": "98304 MiB"}],
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 20, "Unit": "GB/s",
          "Duration (s)": 300}],
        version="1.2.2",
    )
    report = json.loads((db_dir / "pantheon_report_sim.json").read_text())
    report["backend"] = "ttsim"
    (db_dir / "pantheon_report_sim.json").write_text(json.dumps(report))
    assert main(db_dir=db_dir, output_file=output_file) == []


def test_ordinary_gpu_reports_are_untouched_by_the_guard(tmp_path):
    """No backend, no mock flag, no other-suite version: exactly what every
    published GPU report looks like. It must still be published."""
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    write_report(
        db_dir, "pantheon_report_gpu.json",
        [{"id": 0, "name": "NVIDIA RTX 4090", "uuid": "GPU-1234", "memory_total": "24564 MiB"}],
        [{"Test Name": "memory_write", "GPU ID": 0, "Score": 900, "Unit": "GB/s",
          "Duration (s)": 300}],
        version="1.2.2",
    )
    assert len(main(db_dir=db_dir, output_file=output_file)) == 1


def _read_assets(output_file):
    folder = output_file.parent
    return {
        name: json.loads((folder / name).read_text(encoding="utf-8"))
        for name in ("unsupported_workloads.json", "gpu_history.json")
    }


def _setup(tmp_path):
    db_dir = tmp_path / "database"
    db_dir.mkdir()
    return db_dir, tmp_path / "docs" / "assets" / "web_data.json"


def test_zero_style_ids_are_unknown():
    for value in ("0x0", "0x00", "0", "00", "", "N/A", "None", "unknown", None, " 0x0 "):
        assert is_unknown_id(value), value
    for value in ("GPU-58e902aa-1111", "0xfd3d6d912de3c917", "1650123456789"):
        assert not is_unknown_id(value), value


def test_cards_without_a_uuid_are_not_merged_by_a_zero_uuid(tmp_path):
    """AMD reports give 0x0; every such card used to collapse into one."""
    db_dir, output_file = _setup(tmp_path)
    amd = {"id": 0, "name": "AMD Radeon RX 6700 XT", "uuid": "0x0",
           "memory_total": "12272 MB", "driver_version": "ROCm Driver"}
    write_report(db_dir, "pantheon_report_a.json",
                 [dict(amd, serial="SER-A")],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 10.0, "Unit": "GB/s"}])
    write_report(db_dir, "pantheon_report_b.json",
                 [dict(amd, serial="SER-B")],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 20.0, "Unit": "GB/s"}])
    write_report(db_dir, "pantheon_report_c.json",
                 [dict(amd, name="AMD Radeon Graphics", serial="N/A")],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 5.0, "Unit": "GB/s"}])

    rows = main(db_dir=db_dir, output_file=output_file)

    assert sorted(r["score"] for r in rows) == [5.0, 10.0, 20.0]
    cards = {r["card"] for r in _read_assets(output_file)["gpu_history.json"]}
    assert len(cards) == 3
    # The serial is carried only where it identifies the card, and an unusable
    # serial is not repeated.
    by_score = {r["score"]: r for r in rows}
    assert by_score[10.0]["serial"] == "SER-A"
    assert "serial" not in by_score[5.0]


def test_real_uuid_identity_is_untouched_and_serial_is_not_copied(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    write_report(db_dir, "pantheon_report_a.json",
                 [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-REAL-1", "serial": "999"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 10.0, "Unit": "GB/s"}])

    rows = main(db_dir=db_dir, output_file=output_file)

    assert rows[0]["uuid"] == "GPU-REAL-1"
    assert "serial" not in rows[0]
    assert card_identity(rows[0]) == "GPU-REAL-1"


def test_fallback_identity_uses_the_serial_only_when_it_is_real():
    base = {"uuid": "0x0", "gpu": "G", "vram": "1 MB", "driver": "1"}
    assert card_identity(dict(base, serial="S1")) != card_identity(dict(base, serial="S2"))
    assert card_identity(dict(base, serial="0")) == card_identity(dict(base, serial="N/A"))
    assert card_identity(dict(base)) == card_identity(dict(base, uuid="Unknown"))


def test_failed_workloads_have_their_own_status_and_no_score(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    write_report(db_dir, "pantheon_report_fail.json",
                 [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-F"}],
                 [{"Test Name": "memory_read", "GPU ID": 0, "Score": 0.0, "Unit": "ERR", "Status": "FAIL"},
                  {"Test Name": "baseline_metrics", "GPU ID": 0, "Score": 0.0, "Unit": "ERR", "Status": "FAIL"},
                  {"Test Name": "rt_virus", "GPU ID": 0, "Score": 0.0, "Unit": "GRays/s"},
                  {"Test Name": "memory_write", "GPU ID": 0, "Score": 900.0, "Unit": "GB/s"}],
                 version="1.2.0")

    rows = main(db_dir=db_dir, output_file=output_file)
    assets = _read_assets(output_file)

    assert [r["test"] for r in rows] == ["memory_write"]
    assert all(r["test"] == "memory_write" for r in assets["gpu_history.json"])
    statuses = {u["test"]: u for u in assets["unsupported_workloads.json"]}
    assert statuses["memory_read"]["status"] == "FAILED"
    assert statuses["baseline_metrics"]["status"] == "FAILED"
    assert statuses["rt_virus"]["status"] == "NO_MEASUREMENT"
    assert "did not run" not in statuses["memory_read"]["reason"]
    assert "FAIL" in statuses["memory_read"]["reason"]
    assert is_failed_workload({"Status": "FAIL"})
    assert is_failed_workload({"Unit": "ERR", "Score": 0})
    assert not is_failed_workload({"Status": "PASS", "Unit": "GB/s"})
    assert not is_failed_workload({})


def test_repeated_unsupported_entries_are_listed_once(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    for i in range(3):
        write_report(db_dir, f"pantheon_report_rt_{i}.json",
                     [{"id": 0, "name": "NVIDIA H100", "uuid": f"GPU-{i}"}],
                     [{"Test Name": "rt_virus", "GPU ID": 0, "Score": 0.0, "Unit": "GRays/s"}],
                     version="1.0.16")
    write_report(db_dir, "pantheon_report_rt_new.json",
                 [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-9"}],
                 [{"Test Name": "rt_virus", "GPU ID": 0, "Score": 0.0, "Unit": "GRays/s"}],
                 version="1.2.0")

    main(db_dir=db_dir, output_file=output_file)
    entries = _read_assets(output_file)["unsupported_workloads.json"]

    assert sorted(e["version"] for e in entries) == ["1.0.16", "1.2.0"]


def test_history_keeps_run_length_apart(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    for name, duration, stamp in (("short", 30, "2026-05-20 10:00:00"),
                                  ("long", 3600, "2026-05-20 10:00:00")):
        path = write_report(
            db_dir, f"pantheon_report_{name}.json",
            [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-H"}],
            [{"Test Name": "memory_read", "GPU ID": 0, "Score": 1500.0, "Unit": "GB/s",
              "Duration (s)": duration}])
        report = json.loads(path.read_text())
        report["timestamp"] = stamp
        path.write_text(json.dumps(report))

    main(db_dir=db_dir, output_file=output_file)
    history = _read_assets(output_file)["gpu_history.json"]

    # Same card, workload, release, score and timestamp: only the run length
    # tells them apart, so neither may be collapsed into the other.
    assert sorted(run["duration"] for run in history) == [30, 3600]


def test_history_chart_draws_one_series_per_run_length():
    from pathlib import Path
    script = (Path(__file__).resolve().parent.parent / "docs" / "js" / "gpu-history.js").read_text()
    assert "run.duration" in script
    # Run length is one part of the series key; the scoring change is the other.
    assert "`${unit}|${duration}|${epoch}`" in script


def test_amd_placeholders_are_not_published_as_readings(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    methodology = tmp_path / "methodology.md"
    methodology.write_text("<!-- TOOLKIT_COVERAGE:START -->\n<!-- TOOLKIT_COVERAGE:END -->\n")
    path = write_report(
        db_dir, "pantheon_report_amd.json",
        [{"id": 0, "name": "AMD Radeon RX 6700 XT", "uuid": "0xabc",
          "driver_version": "ROCm Driver", "memory_total": "12272 MB"}],
        [{"Test Name": "memory_read", "GPU ID": 0, "Score": 10.0, "Unit": "GB/s",
          "Memory Total (MiB)": 0.0, "Max Fan (%)": 0.0}])
    report = json.loads(path.read_text())
    report["toolkit_version"] = "7.2.0"
    path.write_text(json.dumps(report))

    rows = main(db_dir=db_dir, output_file=output_file, methodology_file=methodology)

    assert rows[0]["memory_total"] == "N/A"
    assert rows[0]["fan_max"] == "N/A"
    assert rows[0]["driver"] == "N/A"
    assert "ROCm Driver" not in methodology.read_text()
    assert "| ROCm | 7.2.0 | not recorded | 1 |" in methodology.read_text()
    assert clean_driver("ROCm Driver") == "N/A"
    assert clean_driver("595.97") == "595.97"
    assert clean_driver(None) == "N/A"


def test_a100_match_does_not_catch_the_rtx_a1000():
    for name in ("NVIDIA A100-SXM4-80GB", "NVIDIA A100 80GB PCIe", "NVIDIA A100"):
        assert unsupported_workload_reason("media_enc_virus", name), name
    for name in ("NVIDIA RTX A1000", "NVIDIA RTX A1000 Laptop GPU"):
        assert unsupported_workload_reason("media_enc_virus", name) is None, name


def test_power_fallback_and_throughput_rows_do_not_compete(tmp_path):
    db_dir, output_file = _setup(tmp_path)
    write_report(db_dir, "pantheon_report_a.json",
                 [{"id": 0, "name": "NVIDIA H100", "uuid": "GPU-W"}],
                 [{"Test Name": "tensor_virus", "GPU ID": 0, "Score": "N/A", "Max Power (W)": 700.0},
                  {"Test Name": "tensor_virus", "GPU ID": 0, "Score": 400.0, "Unit": "TFLOPS"}],
                 version="1.2.0")

    rows = main(db_dir=db_dir, output_file=output_file)

    assert sorted(r["unit"] for r in rows) == ["TFLOPS", "Watts"]
    base = {"uuid": "U", "test": "t", "version": "1", "duration": 5}
    assert record_key(dict(base, unit="Watts")) != record_key(dict(base, unit="TFLOPS"))


# --- What a Pantheon newer than 1.2.4 adds: clocks, limits, start state, rated specs ----------------
# Values below are from real runs on a Tesla T4 (driver 570) and an RX 6700 XT (ROCm 7.2).

T4_STATIC = {"id": 0, "type": "NVIDIA", "name": "Tesla T4", "uuid": "GPU-t4", "memory_total": "15360 MB",
             "memory_type": "GDDR6", "memory_vendor": "Samsung", "max_graphics_clock_mhz": 1590,
             "max_memory_clock_mhz": 5001, "memory_bus_width_bits": 256, "pcie_max_gen": 3, "pcie_max_width": 16,
             "cuda_cores": 2560, "compute_units": "N/A", "vbios_version": "90.04.96.00.02", "temp_slowdown_c": 93}
T4_ROW = {"Test Name": "memory_read", "GPU ID": 0, "Score": 261.34, "Unit": "GB/s", "Avg Mem Clock (MHz)": 4928.2,
          "Max Mem Clock (MHz)": 5000.0, "Max Edge Temp (C)": 42.0, "Max Hotspot Temp (C)": "N/A",
          "Thermal Margin (C)": 51.0, "Throttle Power (s)": 63.7, "Throttle Thermal (s)": 0.0,
          "Throttle Power Brake (s)": 0.0, "Power Violation (s)": 63.97, "Thermal Violation (s)": 0.0,
          "Start Temp (C)": 22.0, "Start Power (W)": 10.6, "Start GPU Util (%)": 0.0, "Start Mem Used (MiB)": 446.3,
          "Start Clock (MHz)": 300.0, "Start Mem Clock (MHz)": 405.0, "Other GPU Processes": 0,
          "Host Load 1m (start)": 1.04, "Avg CPU Util (%)": 5.0, "Avg Busiest Core (%)": 12.6,
          "Avg CPU Clock (MHz)": 2802.5}
RX6700_STATIC = {"id": 1, "type": "AMD", "name": "AMD Radeon RX 6700 XT", "uuid": "0x0", "memory_total": "12272 MB",
                 "memory_type": "GDDR6", "memory_vendor": "Samsung", "max_graphics_clock_mhz": 2855,
                 "max_memory_clock_mhz": 1000, "memory_bus_width_bits": 192, "pcie_max_gen": 4, "pcie_max_width": 16,
                 "cuda_cores": "N/A", "compute_units": 40, "vbios_version": "113-D5121100-101", "temp_slowdown_c": 110}
RX6700_ROW = {"Test Name": "memory_read", "GPU ID": 1, "Score": 381.734, "Unit": "GB/s", "Avg Mem Clock (MHz)": 969.9,
              "Max Mem Clock (MHz)": 1000.0, "Max Edge Temp (C)": 65.0, "Max Hotspot Temp (C)": 78.0,
              "Thermal Margin (C)": 32.0, "Throttle Power (s)": "N/A", "Throttle Thermal (s)": "N/A",
              "Power Violation (s)": "N/A", "Other GPU Processes": "N/A", "Start GPU Util (%)": 0.0}


def _published_rows(tmp_path, static, row, **overrides):
    db_dir = tmp_path / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    output_file = tmp_path / "docs" / "assets" / "web_data.json"
    write_report(db_dir, "pantheon_report_x.json", [static], [dict(row, **overrides)], version="1.2.5")
    return main(db_dir=db_dir, output_file=output_file)


def test_new_run_columns_and_rated_specs_are_published_when_the_report_carries_them(tmp_path):
    (row,) = _published_rows(tmp_path, T4_STATIC, T4_ROW)

    assert row["mem_clock_avg"] == 4928.2 and row["mem_clock_max"] == 5000.0
    assert row["temp_edge"] == 42.0 and row["thermal_margin"] == 51.0
    assert (row["throttle_power_s"], row["power_violation_s"]) == (63.7, 63.97)
    assert (row["start_temp"], row["start_mem_used"], row["start_mem_clock"]) == (22.0, 446.3, 405.0)
    assert row["host_load"] == 1.04 and row["cpu_busiest_avg"] == 12.6 and row["cpu_util_avg"] == 5.0
    assert (row["max_clock_mhz"], row["max_mem_clock_mhz"], row["bus_width_bits"]) == (1590, 5001, 256)
    assert (row["pcie_max_gen"], row["pcie_max_width"], row["cuda_cores"]) == (3, 16, 2560)
    assert row["vbios"] == "90.04.96.00.02" and row["temp_slowdown"] == 93
    # A reading the tool wrote as N/A is left out, not published as the text "N/A".
    assert "temp_hotspot" not in row and "compute_units" not in row


def test_a_measured_zero_is_published_but_na_never_is(tmp_path):
    # Zero seconds throttled, an idle card at the start, no other process: all measurements, all kept. (The
    # ABSENT_WHEN_ZERO rule is for fields where an old tool wrote 0 for "no sensor"; these are written as N/A.)
    (row,) = _published_rows(tmp_path, T4_STATIC, T4_ROW)
    assert row["throttle_thermal_s"] == 0.0 and row["throttle_brake_s"] == 0.0 and row["thermal_violation_s"] == 0.0
    assert row["start_util"] == 0.0 and row["other_gpu_procs"] == 0

    (amd,) = _published_rows(tmp_path / "amd", RX6700_STATIC, RX6700_ROW)
    for absent in ("throttle_power_s", "throttle_thermal_s", "power_violation_s", "other_gpu_procs"):
        assert absent not in amd, absent
    assert amd["temp_hotspot"] == 78.0 and amd["compute_units"] == 40 and "cuda_cores" not in amd


def test_reports_without_the_new_fields_publish_none_of_them(tmp_path):
    from website_utils.generate_web_data import DEVICE_SPEC_FIELDS, RUN_CONTEXT_FIELDS

    old_static = {"id": 0, "type": "NVIDIA", "name": "Tesla T4", "uuid": "GPU-old", "memory_total": "15360 MB"}
    old_row = {"Test Name": "memory_read", "GPU ID": 0, "Score": 261.34, "Unit": "GB/s", "Avg Power (W)": 60.0}
    (row,) = _published_rows(tmp_path, old_static, old_row)

    new_keys = {k for k, _ in RUN_CONTEXT_FIELDS} | {k for k, _ in DEVICE_SPEC_FIELDS} | {"peak_bandwidth_gbs", "bandwidth_pct"}
    assert not (new_keys & set(row)), sorted(new_keys & set(row))


def test_peak_memory_bandwidth_and_the_share_of_it_a_run_reached(tmp_path):
    (t4,) = _published_rows(tmp_path / "t4", T4_STATIC, T4_ROW)
    assert t4["peak_bandwidth_gbs"] == 320.1                       # 256 bit / 8 x 5001 MHz x 2, the T4's published 320 GB/s
    assert t4["bandwidth_pct"] == 81.6                              # 261.34 / 320.1

    (rx,) = _published_rows(tmp_path / "rx", RX6700_STATIC, RX6700_ROW)
    assert rx["peak_bandwidth_gbs"] == 384.0                        # 192 bit / 8 x 1000 MHz x 16, the 6700 XT's published 384 GB/s
    assert rx["bandwidth_pct"] == 99.4


def test_the_share_of_peak_is_only_for_device_memory_bandwidth_workloads(tmp_path):
    # pcie_bandwidth is also GB/s, but it measures the PCIe link: its share of DRAM peak would be meaningless.
    (pcie,) = _published_rows(tmp_path / "a", T4_STATIC, T4_ROW, **{"Test Name": "pcie_bandwidth", "Score": 12.0})
    assert pcie["peak_bandwidth_gbs"] == 320.1 and "bandwidth_pct" not in pcie
    (write,) = _published_rows(tmp_path / "b", T4_STATIC, T4_ROW, **{"Test Name": "memory_write", "Score": 220.6})
    assert write["bandwidth_pct"] == 68.9
    (compute,) = _published_rows(tmp_path / "c", T4_STATIC, T4_ROW, **{"Test Name": "memory_read", "Score": 12.0, "Unit": "TFLOPS"})
    assert "bandwidth_pct" not in compute


def test_the_share_of_peak_is_not_claimed_for_a_run_that_shared_the_card(tmp_path):
    # Real runs: a second process held the card, so the score is the share this run got, not what the card can do.
    (row,) = _published_rows(tmp_path, T4_STATIC, T4_ROW, **{"Other GPU Processes": 1, "Score": 116.467})
    assert row["other_gpu_procs"] == 1 and row["peak_bandwidth_gbs"] == 320.1
    assert "bandwidth_pct" not in row
    # An unknown count (AMD, or no NVML) does not suppress it: nothing says the card was shared.
    (amd,) = _published_rows(tmp_path / "amd", RX6700_STATIC, RX6700_ROW)
    assert amd["bandwidth_pct"] == 99.4


def test_no_peak_is_claimed_where_the_clock_convention_is_unknown_or_a_number_is_missing(tmp_path):
    from website_utils.generate_web_data import peak_bandwidth_gbs

    assert peak_bandwidth_gbs(T4_STATIC, "GDDR6") == 320.1
    assert peak_bandwidth_gbs(RX6700_STATIC, "GDDR6") == 384.0
    assert peak_bandwidth_gbs(dict(RX6700_STATIC), "HBM3") is None             # AMD, not GDDR6: no rule
    assert peak_bandwidth_gbs(dict(T4_STATIC, type="MOCK"), "GDDR6") is None   # an unknown vendor has no rule
    for broken in ({"memory_bus_width_bits": "N/A"}, {"max_memory_clock_mhz": "N/A"}, {"max_memory_clock_mhz": 0},
                   {"memory_bus_width_bits": None}, {"memory_bus_width_bits": True}):
        assert peak_bandwidth_gbs(dict(T4_STATIC, **broken), "GDDR6") is None, broken


def test_reading_present_keeps_zero_and_drops_placeholders():
    from website_utils.generate_web_data import reading_present

    for kept in (0, 0.0, 12.5, "94.02.91.00.07", "Enabled"):
        assert reading_present(kept), kept
    for dropped in (None, "", "N/A", "n/a", " unknown ", "None", True):
        assert not reading_present(dropped), dropped
