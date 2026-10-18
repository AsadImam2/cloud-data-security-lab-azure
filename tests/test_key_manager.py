import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import key_manager


def setup_test_keys(tmp_path, monkeypatch):
    key_dir = tmp_path / "keys"
    key_dir.mkdir()

    manifest_file = key_dir / "key_manifest.json"
    old_key_file = key_dir / "demo_key_v1.key"

    old_key = AESGCM.generate_key(bit_length=256)
    old_key_file.write_bytes(old_key)

    monkeypatch.setattr(key_manager, "KEY_DIR", key_dir)
    monkeypatch.setattr(key_manager, "MANIFEST_FILE", manifest_file)

    return old_key


def test_rotation_preserves_old_key_and_activates_new_key(
    tmp_path, monkeypatch
):
    old_key = setup_test_keys(tmp_path, monkeypatch)

    new_key_id = key_manager.rotate_key()
    manifest = key_manager.load_manifest()

    assert new_key_id == "demo_key_v2"
    assert manifest["active_key_id"] == "demo_key_v2"

    statuses = {
        item["key_id"]: item["status"]
        for item in manifest["keys"]
    }

    assert statuses["demo_key_v1"] == "retired_for_encryption"
    assert statuses["demo_key_v2"] == "active"

    # The original key must remain unchanged for old encrypted data.
    assert key_manager.get_key("demo_key_v1") == old_key
    assert len(key_manager.get_key("demo_key_v2")) == 32


def test_unknown_key_id_is_rejected(tmp_path, monkeypatch):
    setup_test_keys(tmp_path, monkeypatch)

    key_manager.rotate_key()

    with pytest.raises(KeyError):
        key_manager.get_key("demo_key_v99")


def test_existing_key_is_not_overwritten(tmp_path, monkeypatch):
    old_key = setup_test_keys(tmp_path, monkeypatch)

    with pytest.raises(FileExistsError):
        key_manager.create_key(1)

    old_key_file = tmp_path / "keys" / "demo_key_v1.key"
    assert old_key_file.read_bytes() == old_key