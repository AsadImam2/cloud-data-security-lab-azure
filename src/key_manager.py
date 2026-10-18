import json
from datetime import datetime, timezone
from pathlib import Path
from audit_logger import log_event
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEY_DIR = PROJECT_ROOT / "keys"
MANIFEST_FILE = KEY_DIR / "key_manifest.json"


def load_manifest():
    if MANIFEST_FILE.exists():
        with MANIFEST_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    # Register the existing key without replacing it.
    existing_key_file = KEY_DIR / "demo_key_v1.key"

    if existing_key_file.exists():
        key = existing_key_file.read_bytes()

        if len(key) != 32:
            raise ValueError(
                "Existing demo_key_v1 is not a valid 32-byte AES-256 key."
            )

        return {
            "active_key_id": "demo_key_v1",
            "keys": [
                {
                    "key_id": "demo_key_v1",
                    "key_file": existing_key_file.name,
                    "registered_at_utc": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "status": "active",
                }
            ],
        }

    return {
        "active_key_id": None,
        "keys": [],
    }

def save_manifest(manifest):
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    with MANIFEST_FILE.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)


def create_key(version):
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    key_id = f"demo_key_v{version}"
    key_file = KEY_DIR / f"{key_id}.key"

    if key_file.exists():
        raise FileExistsError(
            f"{key_id} already exists; refusing to overwrite a key."
        )

    key = AESGCM.generate_key(bit_length=256)

    with key_file.open("xb") as file:
        file.write(key)

    return key_id, key_file


def rotate_key():
    manifest = load_manifest()
    existing_versions = [
        int(item["key_id"].rsplit("v", 1)[1])
        for item in manifest["keys"]
    ]

    version = max(existing_versions, default=0) + 1
    key_id, key_file = create_key(version)

    manifest["keys"].append({
        "key_id": key_id,
        "key_file": key_file.name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    })

    previous_id = manifest["active_key_id"]

    for item in manifest["keys"]:
        if item["key_id"] == previous_id:
            item["status"] = "retired_for_encryption"
    previous_id = manifest["active_key_id"]

    for item in manifest["keys"]:
        if item["key_id"] == previous_id:
            item["status"] = "retired_for_encryption"

    manifest["active_key_id"] = key_id
    save_manifest(manifest)

    log_event(
        event_type="key_rotation",
        status="success",
        resource="keys/key_manifest.json",
        metadata={
            "key_id": key_id,
            "reason_code": "KEY_ROTATED",
        },
    )

    return key_id


def get_key(key_id):
    manifest = load_manifest()

    matching = [
        item for item in manifest["keys"]
        if item["key_id"] == key_id
    ]

    if not matching:
        raise KeyError(f"Key ID is not registered: {key_id}")

    key_file = KEY_DIR / matching[0]["key_file"]
    key = key_file.read_bytes()

    if len(key) != 32:
        raise ValueError(f"Invalid AES-256 key size for {key_id}")

    return key


if __name__ == "__main__":
    new_key_id = rotate_key()
    print(f"New active key: {new_key_id}")
    print(f"Manifest saved to: {MANIFEST_FILE}")
