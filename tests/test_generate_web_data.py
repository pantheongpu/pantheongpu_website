import json

import pytest

from website_utils.generate_web_data import first_present, infer_unit, is_unknown_version, main, record_key, to_float


def write_report(db_dir, name, gpu_info, test_results, version="1.0.0"):
    report = {
        "pantheon_version": version,
        "timestamp": "2026-05-20 10:00:00",
        "toolkit_version": "12.4",
        "gpu_static_info": gpu_info,
        "test_results": test_results,
    }
    path = db_dir / name
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


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
