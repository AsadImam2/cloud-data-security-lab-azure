import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from inventory import validate_record


def valid_record():
    return {
        "record_id": "TEST-001",
        "data_type": "test_data",
        "owner": "Security",
        "sensitivity": "Confidential",
        "storage_region": "local-pakistan",
        "retention_days": 30,
    }


def test_valid_record_is_accepted():
    assert validate_record(valid_record()) == []


def test_invalid_sensitivity_is_rejected():
    record = valid_record()
    record["sensitivity"] = "Top Secret"

    errors = validate_record(record)

    assert "Invalid or missing sensitivity label." in errors


def test_missing_required_field_is_rejected():
    record = valid_record()
    del record["owner"]

    errors = validate_record(record)

    assert any("Missing fields" in error for error in errors)


def test_negative_retention_is_rejected():
    record = valid_record()
    record["retention_days"] = -1

    errors = validate_record(record)

    assert "retention_days must be a non-negative integer." in errors
