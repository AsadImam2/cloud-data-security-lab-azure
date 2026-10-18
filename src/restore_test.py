import json
import shutil
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_ROOT / "data" / "backups" / "backup_20261018T110635Z"
RESTORE_DIR = PROJECT_ROOT / "reports" / "restore_test"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from encryption import decrypt_data


def main():
    if not BACKUP_DIR.is_dir():
        raise FileNotFoundError(f"Backup not found: {BACKUP_DIR}")

    if RESTORE_DIR.exists():
        raise FileExistsError(
            f"Restore destination already exists: {RESTORE_DIR}"
        )

    # Restore copies into an isolated test directory.
    shutil.copytree(BACKUP_DIR / "data", RESTORE_DIR / "data")
    shutil.copytree(BACKUP_DIR / "keys", RESTORE_DIR / "keys")

    with (RESTORE_DIR / "keys" / "key_manifest.json").open(
        "r", encoding="utf-8"
    ) as file:
        manifest = json.load(file)

    for filename in ["sample.enc", "sample_v2.enc"]:
        encrypted_path = RESTORE_DIR / "data" / "encrypted" / filename

        with encrypted_path.open("r", encoding="utf-8") as file:
            record = json.load(file)

        key_id = record["key_id"]
        entry = next(
            (item for item in manifest["keys"]
             if item["key_id"] == key_id),
            None,
        )

        if entry is None:
            raise ValueError(f"Key not found in restored manifest: {key_id}")

        key_path = RESTORE_DIR / "keys" / entry["key_file"]
        key = key_path.read_bytes()

        if len(key) != 32:
            raise ValueError(f"Invalid key size for {key_id}")

        plaintext = decrypt_data(record, key)

        print(f"RESTORE PASS: {filename} using {key_id}")
        print(f"  Recovered plaintext bytes: {len(plaintext)}")

    print("Disaster recovery test completed successfully.")
    print(f"Restored test files: {RESTORE_DIR}")


if __name__ == "__main__":
    main()
