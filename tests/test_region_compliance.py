
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

from region_compliance import check_compliance


POLICY = {
    "allowed_regions": ["local-pakistan"],
    "restricted_sensitivity_levels": [
        "Confidential",
        "Highly Confidential",
    ],
}


def test_approved_region_has_no_region_violation():
    records = [{
        "record_id": "REC-TEST-1",
        "storage_region": "local-pakistan",
        "sensitivity": "Internal",
    }]

    findings = check_compliance(records, POLICY)

    assert not any(
        finding["finding_type"] == "unapproved_storage_region"
        for finding in findings
    )


def test_unapproved_region_is_flagged():
    records = [{
        "record_id": "REC-TEST-2",
        "storage_region": "aws-us-east-1",
        "sensitivity": "Internal",
    }]

    findings = check_compliance(records, POLICY)

    assert any(
        finding["finding_type"] == "unapproved_storage_region"
        and finding["record_id"] == "REC-TEST-2"
        for finding in findings
    )


def test_restricted_data_is_flagged_for_review():
    records = [{
        "record_id": "REC-TEST-3",
        "storage_region": "local-pakistan",
        "sensitivity": "Confidential",
    }]

    findings = check_compliance(records, POLICY)

    assert any(
        finding["finding_type"] == "restricted_data_requires_review"
        for finding in findings
    )
def test_main_writes_audit_event(tmp_path, monkeypatch):
    import json
    import region_compliance
    import audit_logger

    inventory_file = tmp_path / "inventory.json"
    policy_file = tmp_path / "policy.json"
    report_file = tmp_path / "region_report.json"
    audit_file = tmp_path / "audit_log.jsonl"

    inventory_file.write_text(
        json.dumps([
            {
                "record_id": "REC-TEST-4",
                "storage_region": "local-pakistan",
                "sensitivity": "Internal",
            }
        ]),
        encoding="utf-8",
    )

    policy_file.write_text(
        json.dumps({
            "policy_name": "Test Policy",
            "policy_version": "1.0",
            "allowed_regions": ["local-pakistan"],
            "restricted_sensitivity_levels": ["Confidential"],
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(region_compliance, "INVENTORY_FILE", inventory_file)
    monkeypatch.setattr(region_compliance, "POLICY_FILE", policy_file)
    monkeypatch.setattr(region_compliance, "REPORT_FILE", report_file)
    monkeypatch.setattr(audit_logger, "AUDIT_LOG", audit_file)

    region_compliance.main()

    events = [
        json.loads(line)
        for line in audit_file.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["event_type"] == "data_residency_scan"
    assert events[0]["status"] == "success"
    assert events[0]["metadata"]["finding_count"] == 0