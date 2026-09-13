"""The version literals on the site drifted two releases behind the channels
because nothing regenerated them. These pin the tool that now does."""
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "website_utils"))
import sync_version_strings as svs  # noqa: E402


@pytest.fixture
def tree(tmp_path):
    for rel, _ in svs.TARGETS:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, dest)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / svs.RELEASE_PAGE).write_text(
        "# Releases\n\n---\n\n## Pantheon v9.8.7 (Latest)\n**Release Date:** x\n\n---\n\n## Pantheon v9.8.6\n",
        encoding="utf-8")
    return tmp_path


def test_latest_release_version_reads_the_latest_heading(tree):
    assert svs.latest_release_version(tree) == "9.8.7"


def test_sync_rewrites_every_covered_literal_and_is_idempotent(tree):
    changed = svs.sync("9.8.7", tree)
    assert sorted(changed) == sorted(rel for rel, _ in svs.TARGETS)
    for rel, versions in svs.literals(tree).items():
        assert versions, rel
        assert set(versions) == {"9.8.7"}, (rel, versions)
    assert svs.sync("9.8.7", tree) == []             # second pass touches nothing
    assert svs.drift("9.8.7", tree) == {}


def test_sync_leaves_unrelated_version_strings_alone(tree):
    page = tree / "docs/getting-started.md"
    page.write_text(page.read_text() + "\nCUDA 12.8.1 and driver 570.148.08 stay as they are.\n")
    svs.sync("9.8.7", tree)
    text = page.read_text()
    assert "CUDA 12.8.1 and driver 570.148.08" in text
    assert "VERSION=9.8.7" in text and "(`9.8.7-cuda" in text


def test_drift_names_the_stale_file_and_what_it_says(tree):
    svs.sync("9.8.7", tree)
    hero = tree / "docs/index.md"
    hero.write_text(hero.read_text().replace("v9.8.7 now on", "v1.0.0 now on"))
    stale = svs.drift("9.8.7", tree)
    assert list(stale) == ["docs/index.md"] and stale["docs/index.md"] == ["1.0.0"]


def test_cli_check_mode_exits_nonzero_on_drift(tree, capsys):
    svs.sync("9.8.7", tree)
    assert svs.main(["--check", "--root", str(tree)]) == 0
    spec = tree / "packaging/rpm/pantheon-gpu.spec"
    spec.write_text(spec.read_text().replace("Version:        9.8.7", "Version:        1.0.0"))
    assert svs.main(["--check", "--root", str(tree)]) == 1
    assert "pantheon-gpu.spec: says 1.0.0" in capsys.readouterr().out


def test_sync_refuses_a_non_release_version(tree):
    with pytest.raises(SystemExit):
        svs.sync("latest", tree)
