import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_FILE = PROJECT_ROOT / "data" / "sample" / "inventory.json"
REPORT_FILE = PROJECT_ROOT / "reports" / "inventory_report.json"

ALLOWED_SENSITIVITY = {
    "Public",
    "Internal",
    "Confidential",
    "Highly Confidential",
}

REQUIRED_FIELDS = {
    "record_id",
    "data_type",
    "owner",
    "sensitivity",
    "storage_region",
    "retention_days",
}


def load_inventory():
    with INVENTORY_FILE.open("r", encoding="utf-8-sig") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Inventory must contain a JSON list.")

    return records


def validate_record(record):
    if not isinstance(record, dict):
        return ["Record must be a JSON object."]

    errors = []

    missing_fields = REQUIRED_FIELDS - record.keys()
    if missing_fields:
        errors.append(
            f"Missing fields: {', '.join(sorted(missing_fields))}"
        )

    if record.get("sensitivity") not in ALLOWED_SENSITIVITY:
        errors.append("Invalid or missing sensitivity label.")

    retention = record.get("retention_days")
    if type(retention) is not int or retention < 0:
        errors.append("retention_days must be a non-negative integer.")

    return errors


def main():
    records = load_inventory()
    counts = Counter()
    valid_records = []
    invalid_records = []

    for record in records:
        errors = validate_record(record)

        if errors:
            invalid_records.append({
                "record_id": (
                    record.get("record_id", "UNKNOWN")
                    if isinstance(record, dict)
                    else "UNKNOWN"
                ),
                "errors": errors,
            })
            continue

        valid_records.append(record)
        counts[record["sensitivity"]] += 1

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "data/sample/inventory.json",
        "total_records": len(records),
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "sensitivity_counts": {
            label: counts[label]
            for label in sorted(ALLOWED_SENSITIVITY)
        },
        "invalid_record_details": invalid_records,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("=== Data Inventory Report ===")
    print(f"Total records: {report['total_records']}")
    print(f"Valid records: {report['valid_records']}")
    print(f"Invalid records: {report['invalid_records']}")
    print("\nSensitivity counts:")

    for label, count in report["sensitivity_counts"].items():
        print(f"  {label}: {count}")

    print(f"\nReport saved to: {REPORT_FILE}")

    if invalid_records:
        print("WARNING: Invalid records require review.")
    else:
        print("All inventory records passed validation.")


if __name__ == "__main__":
    main()
