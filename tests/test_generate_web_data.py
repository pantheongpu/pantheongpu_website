import json

import pytest

from website_utils.generate_web_data import (
    first_present,
    infer_unit,
    is_retired_metric,
    is_unknown_version,
    main,
    normalize_gpu_name,
    record_key,
    to_float,
    unsupported_workload_reason,
)


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
    }

    assert record_key(row) == "GPU-UUID|memory_write|1.0.7"


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
