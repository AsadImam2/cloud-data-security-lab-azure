import json
import sys
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

from encryption import decrypt_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKUP_DIR = (
    PROJECT_ROOT
    / "data"
    / "backups"
    / "backup_20261018T121814Z"
)

KEY_DIR = PROJECT_ROOT / "keys"


@pytest.mark.parametrize(
    ("filename", "key_id"),
    [
        ("sample.enc", "demo_key_v1"),
        ("sample_v2.enc", "demo_key_v2"),
    ],
)
def test_backup_recovery_with_correct_key(filename, key_id):
    encrypted_file = (
        BACKUP_DIR / "data" / "encrypted" / filename
    )

    key_file = KEY_DIR / f"{key_id}.key"

    assert encrypted_file.exists()
    assert key_file.exists()

    encrypted_record = json.loads(
        encrypted_file.read_text(encoding="utf-8")
    )
    key = key_file.read_bytes()

    assert encrypted_record["key_id"] == key_id
    assert len(key) == 32

    recovered = decrypt_data(encrypted_record, key)

    assert recovered
    assert isinstance(recovered, bytes)


def test_backup_recovery_rejects_wrong_key():
    encrypted_file = (
        BACKUP_DIR / "data" / "encrypted" / "sample.enc"
    )
    wrong_key_file = KEY_DIR / "demo_key_v2.key"

    encrypted_record = json.loads(
        encrypted_file.read_text(encoding="utf-8")
    )
    wrong_key = wrong_key_file.read_bytes()

    with pytest.raises(InvalidTag):
        decrypt_data(encrypted_record, wrong_key)