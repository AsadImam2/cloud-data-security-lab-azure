import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIRS = [
    PROJECT_ROOT / "data" / "encrypted",
    PROJECT_ROOT / "keys",
]

BACKUP_ROOT = PROJECT_ROOT / "data" / "backups"


def create_backup(include_key_material=False):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = BACKUP_ROOT / f"backup_{timestamp}"

    backup_dir.mkdir(parents=True, exist_ok=False)

    try:
        for source_dir in SOURCE_DIRS:
            if not source_dir.exists():
                raise FileNotFoundError(
                    f"Required source directory is missing: {source_dir}"
                )

            destination = backup_dir / source_dir.relative_to(PROJECT_ROOT)

            if source_dir.name == "keys" and not include_key_material:
                destination.mkdir(parents=True, exist_ok=True)

                manifest_file = source_dir / "key_manifest.json"

                if manifest_file.exists():
                    shutil.copy2(
                        manifest_file,
                        destination / manifest_file.name,
                    )

                continue

            shutil.copytree(source_dir, destination)

        manifest = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "backup_name": backup_dir.name,
            "included_directories": [
                "data/encrypted",
                "keys/key_manifest.json",
            ],
            "contains_raw_key_material": include_key_material,
            "warning": (
                "Contains raw encryption keys. Keep this backup private."
                if include_key_material
                else (
                    "Raw encryption keys are excluded. "
                    "Keep them separately in a protected location "
                    "to preserve decryption and recovery capability."
                )
            ),
        }

        with (backup_dir / "backup_manifest.json").open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(manifest, file, indent=2)

    except Exception:
        # Do not leave a partial backup that looks complete.
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise

    print("Backup created successfully.")
    print(f"Backup location: {backup_dir}")
    print("Included: encrypted data and key manifest.")

    if include_key_material:
        print("Included: raw encryption key files.")
        print("Warning: this backup contains sensitive key material.")
    else:
        print("Raw encryption keys were excluded.")
        print(
            "Ensure keys are stored separately in a protected location "
            "for recovery."
        )


if __name__ == "__main__":
    create_backup()