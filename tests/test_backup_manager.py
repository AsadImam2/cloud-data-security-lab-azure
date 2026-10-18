import json
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

import backup_manager


def setup_backup_environment(tmp_path, monkeypatch):
    project_root = tmp_path
    encrypted_dir = project_root / "data" / "encrypted"
    keys_dir = project_root / "keys"
    backup_root = project_root / "data" / "backups"

    encrypted_dir.mkdir(parents=True)
    keys_dir.mkdir(parents=True)

    (encrypted_dir / "sample.enc").write_text(
        "encrypted sample",
        encoding="utf-8",
    )
    (keys_dir / "demo_key_v1.key").write_text(
        "demo test key",
        encoding="utf-8",
    )
    (keys_dir / "key_manifest.json").write_text(
        '{"active_key_id": "demo_key_v1"}',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_manager,
        "PROJECT_ROOT",
        project_root,
    )
    monkeypatch.setattr(
        backup_manager,
        "SOURCE_DIRS",
        [encrypted_dir, keys_dir],
    )
    monkeypatch.setattr(
        backup_manager,
        "BACKUP_ROOT",
        backup_root,
    )

    return backup_root


def test_backup_excludes_raw_keys_by_default(
    tmp_path,
    monkeypatch,
):
    backup_root = setup_backup_environment(
        tmp_path,
        monkeypatch,
    )

    backup_manager.create_backup()

    backups = list(backup_root.iterdir())
    assert len(backups) == 1

    backup_dir = backups[0]

    assert (
        backup_dir / "data" / "encrypted" / "sample.enc"
    ).exists()
    assert (
        backup_dir / "keys" / "key_manifest.json"
    ).exists()
    assert not (
        backup_dir / "keys" / "demo_key_v1.key"
    ).exists()


def test_backup_manifest_records_key_exclusion(
    tmp_path,
    monkeypatch,
):
    backup_root = setup_backup_environment(
        tmp_path,
        monkeypatch,
    )

    backup_manager.create_backup()

    backup_dir = next(backup_root.iterdir())
    manifest_path = backup_dir / "backup_manifest.json"

    assert manifest_path.exists()

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    assert manifest["backup_name"] == backup_dir.name
    assert "created_at_utc" in manifest
    assert manifest["contains_raw_key_material"] is False
    assert "Raw encryption keys are excluded" in manifest["warning"]


def test_backup_can_include_raw_keys_explicitly(
    tmp_path,
    monkeypatch,
):
    backup_root = setup_backup_environment(
        tmp_path,
        monkeypatch,
    )

    backup_manager.create_backup(include_key_material=True)

    backup_dir = next(backup_root.iterdir())

    assert (
        backup_dir / "keys" / "demo_key_v1.key"
    ).exists()

    manifest = json.loads(
        (backup_dir / "backup_manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["contains_raw_key_material"] is True
    assert "Contains raw encryption keys" in manifest["warning"]
def test_missing_source_removes_partial_backup(
    tmp_path,
    monkeypatch,
):
    project_root = tmp_path
    encrypted_dir = project_root / "data" / "encrypted"
    missing_keys_dir = project_root / "keys"
    backup_root = project_root / "data" / "backups"

    encrypted_dir.mkdir(parents=True)
    (encrypted_dir / "sample.enc").write_text(
        "encrypted sample",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        backup_manager,
        "PROJECT_ROOT",
        project_root,
    )
    monkeypatch.setattr(
        backup_manager,
        "SOURCE_DIRS",
        [encrypted_dir, missing_keys_dir],
    )
    monkeypatch.setattr(
        backup_manager,
        "BACKUP_ROOT",
        backup_root,
    )

    with pytest.raises(FileNotFoundError):
        backup_manager.create_backup()

    assert list(backup_root.iterdir()) == []